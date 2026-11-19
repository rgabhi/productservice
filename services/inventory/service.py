"""Inventory decisions and transaction boundaries, independent of HTTP/Kafka."""
import json
import redis
from common.db import transaction
from common.errors import NotFound
from common import repository as messages
from services.inventory import repository

CACHE_KEY = 'student-checkout:catalog:v1'


def catalog(url, cache):
    try:
        value = cache.get(CACHE_KEY)
        if value:
            return json.loads(value), 'HIT'
    except redis.RedisError:
        pass
    with transaction(url) as conn:
        result = repository.catalog(conn)
    try:
        cache.setex(CACHE_KEY, 30, json.dumps(result))
        return result, 'MISS'
    except redis.RedisError:
        return result, 'BYPASS'


def product(url, product_id):
    with transaction(url) as conn:
        result = repository.product(conn, product_id)
        if not result:
            raise NotFound('Unknown product')
        return result


def handle_event(url, message):
    with transaction(url) as conn:
        if messages.receive_once(conn, message['event_id']):
            _apply(conn, message)


def _apply(conn, message):
    order_id, kind, data = message['order_id'], message['type'], message['data']
    reservation = repository.lock_reservation(conn, order_id)
    if kind == 'inventory.reserve':
        if not reservation:
            row = repository.take_stock(conn, data['product_id'], data['quantity'])
            status = 'RESERVED' if row else 'REJECTED'
            repository.add_reservation(conn, order_id, data['product_id'], data['quantity'], status)
        else:
            if (reservation['product_id'],reservation['quantity']) != (data['product_id'],data['quantity']):
                raise ValueError('Conflicting reserve operation')
            status = reservation['status']
        if status in ('RESERVED','CONFIRMED'):
            messages.enqueue(conn, 'orders', 'inventory.reserved', order_id)
        elif status == 'REJECTED':
            messages.enqueue(conn, 'orders', 'inventory.rejected', order_id)
    elif kind == 'inventory.confirm':
        if not reservation:
            raise ValueError('No reservation to confirm')
        if reservation['status'] == 'RESERVED':
            repository.set_reservation_status(conn, order_id, 'CONFIRMED')
        if reservation['status'] in ('RESERVED','CONFIRMED'):
            messages.enqueue(conn, 'orders', 'inventory.confirmed', order_id)
    elif kind == 'inventory.release':
        if not reservation:
            raise ValueError('No reservation to release')
        if reservation['status'] == 'RESERVED':
            repository.return_stock(conn, reservation['product_id'], reservation['quantity'])
            repository.set_reservation_status(conn, order_id, 'RELEASED')
        if reservation['status'] in ('RESERVED','RELEASED'):
            messages.enqueue(conn, 'orders', 'inventory.released', order_id)
    else:
        raise ValueError(f'Unknown inventory command: {kind}')
