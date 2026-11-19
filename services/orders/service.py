"""Order use cases and saga. This layer owns every business transaction."""
import hashlib
import json
from uuid import uuid4
from common.db import transaction
from common.errors import Conflict, NotFound
from common import repository as messages
from services.orders import inventory_client, repository


def check_request(existing, fingerprint):
    if existing['request_hash'] != fingerprint:
        raise Conflict('Idempotency key already used for another request')
    return existing


def create_order(url, data, key, customer):
    fingerprint = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    with transaction(url) as conn:
        existing = repository.find_by_key(conn, customer, key)
        if existing:
            return check_request(existing, fingerprint)
    # No DB transaction is held open during the other service's HTTP request.
    total = inventory_client.unit_price(data['product_id']) * data['quantity']
    with transaction(url) as conn:
        result = repository.insert_order(conn, uuid4(), customer, key, fingerprint, data, total)
        if result:
            # SAME connection => order, next command and history commit together.
            messages.enqueue(conn, 'inventory', 'inventory.reserve', result['id'],
                             {'product_id': data['product_id'], 'quantity': data['quantity']})
            repository.record(conn, result['id'], 'PENDING', 'order accepted')
        else:
            result = check_request(repository.find_by_key(conn, customer, key), fingerprint)
        return result


def get_order(url, order_id, customer):
    with transaction(url) as conn:
        order = repository.find_for_customer(conn, order_id, customer)
        if not order:
            raise NotFound('Order not found')
        order['history'] = repository.history(conn, order_id)
        return order


def handle_event(url, message):
    # Kafka transport does not own this business transaction.
    with transaction(url) as conn:
        if messages.receive_once(conn, message['event_id']):
            _advance(conn, message)


def _advance(conn, message):
    order_id, kind = message['order_id'], message['type']
    order = repository.lock_order(conn, order_id)
    if not order:
        raise ValueError('Event refers to an unknown order')
    status = order['status']
    if kind == 'inventory.reserved' and status == 'PENDING':
        new = 'RESERVED'
        messages.enqueue(conn, 'payments', 'payment.charge', order_id,
                         {'total_paise': order['total_paise'], 'outcome': order['payment_outcome']})
    elif kind == 'inventory.rejected' and status == 'PENDING':
        new = 'CANCELLED'
    elif kind == 'payment.approved' and status == 'RESERVED':
        new = 'PAID'
        messages.enqueue(conn, 'inventory', 'inventory.confirm', order_id)
    elif kind == 'inventory.confirmed' and status == 'PAID':
        new = 'COMPLETED'
    elif kind == 'payment.declined' and status == 'RESERVED':
        new = 'COMPENSATING'
        messages.enqueue(conn, 'inventory', 'inventory.release', order_id)
    elif kind == 'inventory.released' and status == 'COMPENSATING':
        new = 'CANCELLED'
    elif kind in {'inventory.reserved','inventory.rejected','payment.approved',
                  'inventory.confirmed','payment.declined','inventory.released'}:
        return  # Duplicate/stale responses cannot move completed state backwards.
    else:
        raise ValueError(f'Unknown order event: {kind}')
    reason = 'out_of_stock' if kind == 'inventory.rejected' else 'payment_declined' if kind == 'payment.declined' else order['reason']
    repository.set_state(conn, order_id, new, reason)
    repository.record(conn, order_id, new, kind)
