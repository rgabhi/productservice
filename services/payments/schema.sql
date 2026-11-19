CREATE TABLE IF NOT EXISTS payments (
    order_id UUID PRIMARY KEY,
    total_paise BIGINT NOT NULL CHECK(total_paise>0),
    status TEXT NOT NULL CHECK(status IN ('CHARGED','DECLINED'))
);
