"""Create one successful and one declined order; print their state transitions."""
import json
import time
from uuid import uuid4
import httpx


def checkout(outcome):
    with httpx.Client(base_url='http://localhost:8000', timeout=5, trust_env=False) as client:
        key = str(uuid4())
        response = client.post('/orders',headers={'Idempotency-Key':key},
                               json={'product_id':1,'quantity':1,'payment_outcome':outcome})
        response.raise_for_status()
        order_id = response.json()['id']
        for _ in range(150):
            result = client.get(f'/orders/{order_id}')
            result.raise_for_status()
            order = result.json()
            if order['status'] in ('COMPLETED','CANCELLED'):
                print(json.dumps({'order_id':order_id,'outcome':outcome,'state':order['status'],
                                  'total_paise':order['total_paise'],'history':order['history']},indent=2))
                repeated = client.post('/orders',headers={'Idempotency-Key':key},
                                       json={'product_id':1,'quantity':1,'payment_outcome':outcome})
                repeated.raise_for_status()
                assert repeated.json()['id'] == order_id
                print('Same idempotency key returned the same order.\n')
                return
            time.sleep(0.2)
        raise RuntimeError('Checkout did not reach a final state')


if __name__ == '__main__':
    checkout('approve')
    checkout('decline')
