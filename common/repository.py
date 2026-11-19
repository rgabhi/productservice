"""SQL for shared messaging tables. Never open or commit a transaction here."""
from psycopg.types.json import Jsonb
from common.events import event


def enqueue(conn, destination, kind, order_id, data=None):
    message = event(kind, str(order_id), data or {})
    conn.execute('INSERT INTO outbox(destination,event) VALUES (%s,%s)',
                 (destination, Jsonb(message)))


def receive_once(conn, event_id):
    return conn.execute('INSERT INTO inbox(event_id) VALUES (%s) ON CONFLICT DO NOTHING RETURNING event_id',
                        (event_id,)).fetchone() is not None


def next_pending(conn):
    return conn.execute('SELECT * FROM outbox WHERE NOT sent ORDER BY seq LIMIT 1 FOR UPDATE SKIP LOCKED').fetchone()


def mark_sent(conn, sequence):
    conn.execute('UPDATE outbox SET sent=true WHERE seq=%s', (sequence,))


def ping(conn):
    conn.execute('SELECT 1')
