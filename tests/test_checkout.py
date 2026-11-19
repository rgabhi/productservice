from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import time
import json
import httpx
import pytest
from confluent_kafka import Producer
from common.events import event
from common.db import transaction
from services.inventory.service import handle_event as reserve
from conftest import query, dsn, submit, terminal


def test_success_and_price_snapshot(client, product):
    pid=product(stock=5,price=19900)
    r=submit(client,pid,quantity=2)
    assert r.status_code==202 and r.headers['location'].endswith(r.json()['id'])
    order=terminal(client,r.json()['id'])
    assert order['status']=='COMPLETED' and order['total_paise']==39800
    assert [h['status'] for h in order['history']]==['PENDING','RESERVED','PAID','COMPLETED']
    assert query('inventory','SELECT stock FROM products WHERE id=%s',(pid,))[0]['stock']==3
    assert query('inventory','SELECT status FROM reservations WHERE order_id=%s',(order['id'],))[0]['status']=='CONFIRMED'
    assert query('payments','SELECT * FROM payments WHERE order_id=%s',(order['id'],))[0]['status']=='CHARGED'


def test_decline_compensates_inventory(client, product):
    pid=product(stock=3)
    order=terminal(client,submit(client,pid,outcome='decline',quantity=2).json()['id'])
    assert order['status']=='CANCELLED' and order['reason']=='payment_declined'
    assert [h['status'] for h in order['history']]==['PENDING','RESERVED','COMPENSATING','CANCELLED']
    assert query('inventory','SELECT stock FROM products WHERE id=%s',(pid,))[0]['stock']==3
    assert query('inventory','SELECT status FROM reservations WHERE order_id=%s',(order['id'],))[0]['status']=='RELEASED'
    assert query('payments','SELECT status FROM payments WHERE order_id=%s',(order['id'],))[0]['status']=='DECLINED'


def test_sold_out_never_calls_payments(client, product):
    pid=product(stock=0)
    order=terminal(client,submit(client,pid).json()['id'])
    assert order['status']=='CANCELLED' and order['reason']=='out_of_stock'
    assert query('payments','SELECT * FROM payments WHERE order_id=%s',(order['id'],))==[]


def test_same_idempotency_key_under_concurrency(client, product):
    pid=product(stock=10);key=str(uuid4())
    with ThreadPoolExecutor(max_workers=8) as pool:
        responses=list(pool.map(lambda _:submit(client,pid,key=key),range(12)))
    assert all(r.status_code==202 for r in responses)
    ids={r.json()['id'] for r in responses}
    assert len(ids)==1
    order=terminal(client,ids.pop())
    assert order['status']=='COMPLETED'
    assert query('inventory','SELECT stock FROM products WHERE id=%s',(pid,))[0]['stock']==9


def test_idempotency_conflict_and_customer_scope(client, product):
    pid=product(stock=5);key=str(uuid4())
    first=submit(client,pid,key=key,customer='alice');assert first.status_code==202
    assert submit(client,pid,key=key,quantity=2,customer='alice').status_code==409
    other=submit(client,pid,key=key,customer='bob');assert other.status_code==202
    assert other.json()['id']!=first.json()['id']
    assert client.get(f'/orders/{first.json()["id"]}',headers={'X-Demo-Customer':'bob'}).status_code==404
    terminal(client,first.json()['id'],customer='alice');terminal(client,other.json()['id'],customer='bob')


def test_twenty_buyers_for_last_unit(client, product):
    pid=product(stock=1)
    with ThreadPoolExecutor(max_workers=8) as pool:
        responses=list(pool.map(lambda _:submit(client,pid),range(20)))
    assert all(r.status_code==202 for r in responses)
    orders=[terminal(client,r.json()['id']) for r in responses]
    assert sum(o['status']=='COMPLETED' for o in orders)==1
    assert sum(o['reason']=='out_of_stock' for o in orders)==19
    assert query('inventory','SELECT stock FROM products WHERE id=%s',(pid,))[0]['stock']==0


def publish(destination,value):
    p=Producer({'bootstrap.servers':'localhost:19092'})
    ack=[]
    p.produce('student-checkout.'+destination,key=value['order_id'],value=json.dumps(value),
              on_delivery=lambda error,msg:ack.append(error))
    assert p.flush(10)==0 and ack==[None]


def await_receipt(service,event_id):
    for _ in range(200):
        if query(service,'SELECT * FROM inbox WHERE event_id=%s',(event_id,)):
            return
        time.sleep(.05)
    raise AssertionError('Replayed event was not handled')


def test_duplicate_events_and_business_operations(client, product):
    pid=product(stock=5)
    order=terminal(client,submit(client,pid).json()['id'])
    original=query('orders',"SELECT event FROM outbox WHERE event->>'order_id'=%s ORDER BY seq LIMIT 1",(order['id'],))[0]['event']
    publish('inventory',original);publish('inventory',original)
    barrier=event('inventory.reserve',order['id'],{'product_id':pid,'quantity':1})
    publish('inventory',barrier);await_receipt('inventory',barrier['event_id'])
    charge=event('payment.charge',order['id'],{'total_paise':order['total_paise'],'outcome':'approve'})
    publish('payments',charge);await_receipt('payments',charge['event_id'])
    assert query('inventory','SELECT stock FROM products WHERE id=%s',(pid,))[0]['stock']==4
    assert len(query('inventory','SELECT * FROM reservations WHERE order_id=%s',(order['id'],)))==1
    assert len(query('payments','SELECT * FROM payments WHERE order_id=%s',(order['id'],)))==1
    assert client.get(f'/orders/{order["id"]}').json()['status']=='COMPLETED'


def test_failed_transaction_rolls_back_effect_inbox_and_outbox(product, monkeypatch):
    pid=product(stock=5);oid=str(uuid4());value=event('inventory.reserve',oid,{'product_id':pid,'quantity':2})
    def fail_outbox(*args, **kwargs):
        raise RuntimeError('simulated crash before commit')
    # Fail after the stock/reservation writes: the SERVICE must roll back the whole unit.
    monkeypatch.setattr('services.inventory.service.messages.enqueue', fail_outbox)
    with pytest.raises(RuntimeError,match='simulated crash'):
        reserve(dsn('inventory'), value)
    assert query('inventory','SELECT stock FROM products WHERE id=%s',(pid,))[0]['stock']==5
    assert query('inventory','SELECT * FROM reservations WHERE order_id=%s',(oid,))==[]
    assert query('inventory','SELECT * FROM inbox WHERE event_id=%s',(value['event_id'],))==[]
    assert query('inventory',"SELECT * FROM outbox WHERE event->>'order_id'=%s",(oid,))==[]


@pytest.mark.parametrize('body',[{'product_id':1,'quantity':0},{'product_id':1,'quantity':11},
                                 {'product_id':True,'quantity':1},{'product_id':1,'quantity':1,'payment_outcome':'timeout'}])
def test_invalid_request(client,body):
    assert client.post('/orders',json=body,headers={'Idempotency-Key':str(uuid4())}).status_code==422


def test_missing_key_and_product(client):
    assert client.post('/orders',json={'product_id':1,'quantity':1}).status_code==422
    assert submit(client,2147483647).status_code==404


def test_catalog_cache_keeps_stock_authoritative():
    with httpx.Client(base_url='http://localhost:8001',timeout=5,trust_env=False) as c:
        assert c.get('/products').status_code==200
        second=c.get('/products');assert second.headers['x-cache']=='HIT'
        assert all('stock' not in item for item in second.json())
        assert 'stock' in c.get('/products/1').json()


def test_atomic_reservation_with_simultaneous_database_transactions(client, product):
    """Exercise real SQL contention, independently of the demo's serial consumer."""
    pid=product(stock=1,price=5000)
    ids=[str(uuid4()) for _ in range(10)]
    # Valid pending-order fixtures let the ordinary saga consume the resulting replies.
    with transaction(dsn('orders')) as conn:
        for oid in ids:
            conn.execute('''INSERT INTO orders(id,customer,idempotency_key,request_hash,product_id,
                quantity,total_paise,payment_outcome,status)
                VALUES (%s,'sql-race',%s,'fixture',%s,1,5000,'approve','PENDING')''',(oid,oid,pid))
            conn.execute("INSERT INTO order_history(order_id,status,note) VALUES (%s,'PENDING','concurrency test fixture')",(oid,))

    def compete(oid):
        value=event('inventory.reserve',oid,{'product_id':pid,'quantity':1})
        reserve(dsn('inventory'), value)

    with ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(compete,ids))
    results=[terminal(client,oid,customer='sql-race') for oid in ids]
    assert sum(o['status']=='COMPLETED' for o in results)==1
    assert sum(o['reason']=='out_of_stock' for o in results)==9
    assert query('inventory','SELECT stock FROM products WHERE id=%s',(pid,))[0]['stock']==0
