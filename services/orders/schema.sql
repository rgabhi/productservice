CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY,
    customer TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity BETWEEN 1 AND 10),
    total_paise BIGINT NOT NULL CHECK(total_paise > 0),
    payment_outcome TEXT NOT NULL CHECK(payment_outcome IN ('approve','decline')),
    status TEXT NOT NULL CHECK(status IN ('PENDING','RESERVED','PAID','COMPLETED','COMPENSATING','CANCELLED')),
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(customer,idempotency_key)
);
CREATE TABLE IF NOT EXISTS order_history (
    seq BIGSERIAL PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id),
    status TEXT NOT NULL,
    note TEXT NOT NULL
);
