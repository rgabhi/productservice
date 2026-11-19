"""Order SQL only. The caller supplies the service-owned transaction."""


def find_by_key(conn, customer, key):
    return conn.execute('SELECT * FROM orders WHERE customer=%s AND idempotency_key=%s',
                        (customer, key)).fetchone()


def insert_order(conn, order_id, customer, key, fingerprint, data, total):
    return conn.execute('''INSERT INTO orders(id,customer,idempotency_key,request_hash,product_id,
        quantity,total_paise,payment_outcome,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'PENDING')
        ON CONFLICT(customer,idempotency_key) DO NOTHING RETURNING *''',
        (order_id, customer, key, fingerprint, data['product_id'],
         data['quantity'], total, data['payment_outcome'])).fetchone()


def find_for_customer(conn, order_id, customer):
    return conn.execute('SELECT * FROM orders WHERE id=%s AND customer=%s',
                        (order_id, customer)).fetchone()


def history(conn, order_id):
    return conn.execute('SELECT status,note FROM order_history WHERE order_id=%s ORDER BY seq',
                        (order_id,)).fetchall()


def lock_order(conn, order_id):
    return conn.execute('SELECT * FROM orders WHERE id=%s FOR UPDATE', (order_id,)).fetchone()


def set_state(conn, order_id, state, reason):
    conn.execute('UPDATE orders SET status=%s,reason=%s WHERE id=%s', (state, reason, order_id))


def record(conn, order_id, state, note):
    conn.execute('INSERT INTO order_history(order_id,status,note) VALUES (%s,%s,%s)',
                 (order_id, state, note))
