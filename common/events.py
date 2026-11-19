"""Version-one messages for the learning demo; order_id is the Kafka key."""
from uuid import uuid4


def event(kind, order_id, data):
    return {'event_id': str(uuid4()), 'version': 1, 'type': kind,
            'order_id': str(order_id), 'data': data}


def validate(message):
    from uuid import UUID
    UUID(message['event_id'])
    UUID(message['order_id'])
    if message['version'] != 1 or not isinstance(message['data'], dict):
        raise ValueError('Unsupported event contract')
    return message
