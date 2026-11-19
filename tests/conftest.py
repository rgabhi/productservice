import os
import sys
from pathlib import Path
import time
from uuid import uuid4
import httpx
import psycopg
from psycopg.rows import dict_row
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def dsn(service):
    return os.getenv(f'{service.upper()}_TEST_DB', f'postgresql://{service}:{service}@localhost:55432/{service}')


def query(service, sql, args=()):
    with psycopg.connect(dsn(service), row_factory=dict_row) as conn:
        return conn.execute(sql,args).fetchall()


@pytest.fixture(scope='session')
def client():
    with httpx.Client(base_url=os.getenv('ORDERS_TEST_URL','http://localhost:8000'), timeout=8, trust_env=False) as c:
        yield c


@pytest.fixture
def product():
    def make(stock=10, price=12345):
        pid = 1000 + uuid4().int % 1000000000
        query('inventory','INSERT INTO products VALUES (%s,%s,%s,%s) RETURNING id',
              (pid,f'Test product {pid}',price,stock))
        return pid
    return make


def submit(client, pid, outcome='approve', quantity=1, key=None, customer='student'):
    return client.post('/orders',json={'product_id':pid,'quantity':quantity,'payment_outcome':outcome},
                       headers={'Idempotency-Key':key or str(uuid4()),'X-Demo-Customer':customer})


def terminal(client, order_id, customer='student', timeout=35):
    end = time.monotonic()+timeout
    while time.monotonic()<end:
        r=client.get(f'/orders/{order_id}',headers={'X-Demo-Customer':customer})
        r.raise_for_status()
        order=r.json()
        if order['status'] in ('COMPLETED','CANCELLED'):
            return order
        time.sleep(.1)
    raise AssertionError(f'Order {order_id} did not finish: {order}')
