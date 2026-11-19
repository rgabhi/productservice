CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price_paise BIGINT NOT NULL CHECK(price_paise>0),
    stock INTEGER NOT NULL CHECK(stock>=0)
);
CREATE TABLE IF NOT EXISTS reservations (
    order_id UUID PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK(quantity BETWEEN 1 AND 10),
    status TEXT NOT NULL CHECK(status IN ('RESERVED','CONFIRMED','RELEASED','REJECTED'))
);
INSERT INTO products VALUES (1,'Notebook',19900,100),(2,'Headphones',149900,50),(3,'Last lab kit',99900,1)
ON CONFLICT DO NOTHING;
