"""One publisher and one consumer thread per service: deliberately easy to trace.

The database commit and Kafka acknowledgement are separate. A crash between them
can repeat delivery; inbox receipt + business effect commit in one DB transaction.
"""
import json
import logging
import os
import threading
import time
from confluent_kafka import Consumer, Producer
from common.db import transaction
from common import repository as messages
from common.events import validate

log = logging.getLogger('checkout.events')


class Worker:
    def __init__(self, name, url, handler):
        self.name, self.url, self.handler = name, url, handler
        self.bootstrap = os.getenv('KAFKA_BOOTSTRAP', 'localhost:19092')
        self.prefix = os.getenv('TOPIC_PREFIX', 'student-checkout')
        self.stop = threading.Event()
        self.threads = []
        self.last_error = None

    def start(self):
        for target in (self.publish, self.consume):
            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            self.threads.append(thread)

    def close(self):
        self.stop.set()
        for thread in self.threads:
            thread.join(timeout=6)

    def publish(self):
        producer = Producer({'bootstrap.servers': self.bootstrap,
                             'enable.idempotence': True, 'message.timeout.ms': 5000})
        while not self.stop.is_set():
            try:
                with transaction(self.url) as conn:
                    row = messages.next_pending(conn)
                    if row:
                        delivered = []
                        producer.produce(f'{self.prefix}.{row["destination"]}',
                                         key=row['event']['order_id'], value=json.dumps(row['event']),
                                         on_delivery=lambda error, message, result=delivered: result.append(error))
                        deadline = time.monotonic() + 6
                        while not delivered and time.monotonic() < deadline and not self.stop.is_set():
                            producer.poll(0.1)
                        if not delivered or delivered[0] is not None:
                            raise RuntimeError(f'Kafka delivery not acknowledged: {delivered}')
                        # Crash here => replay after restart; the consumer must deduplicate.
                        messages.mark_sent(conn, row['seq'])
                        log.info('%s published %s order=%s', self.name, row['event']['type'], row['event']['order_id'])
                self.stop.wait(0.05 if row else 0.2)
            except Exception as exc:
                self.last_error = str(exc)
                log.warning('%s publisher retry: %s', self.name, exc)
                self.stop.wait(1)
        producer.flush(1)

    def consume(self):
        while not self.stop.is_set():
            consumer = Consumer({'bootstrap.servers': self.bootstrap,
                                 'group.id': f'{self.prefix}.{self.name}',
                                 'auto.offset.reset': 'earliest', 'enable.auto.commit': False,
                                 'socket.timeout.ms': 3000, 'session.timeout.ms': 6000})
            try:
                consumer.subscribe([f'{self.prefix}.{self.name}'])
                while not self.stop.is_set():
                    message = consumer.poll(0.3)
                    if message is None:
                        continue
                    if message.error():
                        log.warning('%s broker: %s', self.name, message.error())
                        continue
                    value = validate(json.loads(message.value()))
                    # The service owns inbox + business effect + outgoing events as one unit.
                    self.handler(self.url, value)
                    # Crash here => replay, but the committed inbox entry skips the effect.
                    consumer.commit(message=message, asynchronous=False)
                    log.info('%s received %s order=%s', self.name, value['type'], value['order_id'])
            except Exception as exc:
                self.last_error = str(exc)
                log.warning('%s consumer restart/retry: %s', self.name, exc)
                self.stop.wait(1)
            finally:
                consumer.close()
