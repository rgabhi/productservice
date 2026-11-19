"""Payment ledger SQL. No independent commits."""


def insert_payment(conn, order_id, total, status):
    return conn.execute('''INSERT INTO payments VALUES (%s,%s,%s)
        ON CONFLICT DO NOTHING RETURNING *''', (order_id, total, status)).fetchone()


def find_payment(conn, order_id):
    return conn.execute('SELECT * FROM payments WHERE order_id=%s', (order_id,)).fetchone()
