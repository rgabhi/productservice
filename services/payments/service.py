"""Deterministic payment use case; owns inbox/effect/outbox transaction."""
from common.db import transaction
from common import repository as messages
from services.payments import repository


def handle_event(url, message):
    with transaction(url) as conn:
        if messages.receive_once(conn, message['event_id']):
            _charge(conn, message)


def _charge(conn, message):
    if message['type'] != 'payment.charge':
        raise ValueError('Unknown payment command')
    order_id, data = message['order_id'], message['data']
    if data['outcome'] not in ('approve','decline'):
        raise ValueError('Unknown simulated outcome')
    status = 'CHARGED' if data['outcome'] == 'approve' else 'DECLINED'
    payment = repository.insert_payment(conn, order_id, data['total_paise'], status)
    if not payment:
        payment = repository.find_payment(conn, order_id)
        if payment['total_paise'] != data['total_paise'] or payment['status'] != status:
            raise ValueError('Conflicting payment operation')
    messages.enqueue(conn, 'orders', 'payment.approved' if payment['status'] == 'CHARGED' else 'payment.declined', order_id)
