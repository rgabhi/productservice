"""Inventory SQL; transaction/commit decisions belong to the service."""


def catalog(conn):
    return conn.execute('SELECT id,name,price_paise FROM products ORDER BY id').fetchall()


def product(conn, product_id):
    return conn.execute('SELECT * FROM products WHERE id=%s', (product_id,)).fetchone()


def lock_reservation(conn, order_id):
    return conn.execute('SELECT * FROM reservations WHERE order_id=%s FOR UPDATE', (order_id,)).fetchone()


def take_stock(conn, product_id, quantity):
    # One conditional SQL statement keeps the check-and-decrement atomic.
    return conn.execute('UPDATE products SET stock=stock-%s WHERE id=%s AND stock>=%s RETURNING id',
                        (quantity, product_id, quantity)).fetchone()


def add_reservation(conn, order_id, product_id, quantity, status):
    conn.execute('INSERT INTO reservations VALUES (%s,%s,%s,%s)',
                 (order_id, product_id, quantity, status))


def set_reservation_status(conn, order_id, status):
    conn.execute('UPDATE reservations SET status=%s WHERE order_id=%s', (status, order_id))


def return_stock(conn, product_id, quantity):
    conn.execute('UPDATE products SET stock=stock+%s WHERE id=%s', (quantity, product_id))
