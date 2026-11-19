"""Small, optional failure demonstrations against the actual local containers."""
import time
import httpx
import pytest
from tools.dev import compose
from conftest import query, submit, terminal

pytestmark=pytest.mark.disruption


def test_broker_outage_preserves_pending_order(client, product):
    pid=product(stock=3)
    compose('stop','kafka')
    try:
        r=submit(client,pid);assert r.status_code==202
        oid=r.json()['id']
        time.sleep(1)
        assert client.get('/orders/'+oid).json()['status']=='PENDING'
        assert query('orders',"SELECT * FROM outbox WHERE NOT sent AND event->>'order_id'=%s",(oid,))
    finally:
        compose('start','kafka')
    assert terminal(client,oid,timeout=90)['status']=='COMPLETED'


def test_redis_outage_falls_back_to_database():
    compose('stop','redis')
    try:
        r=httpx.get('http://localhost:8001/products',timeout=5,trust_env=False)
        assert r.status_code==200 and r.headers['x-cache']=='BYPASS'
    finally:
        compose('start','redis')
