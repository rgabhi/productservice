CREATE TABLE IF NOT EXISTS inbox (
    event_id UUID PRIMARY KEY,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS outbox (
    seq BIGSERIAL PRIMARY KEY,
    destination TEXT NOT NULL,
    event JSONB NOT NULL,
    sent BOOLEAN NOT NULL DEFAULT false
);
CREATE INDEX IF NOT EXISTS pending_outbox ON outbox(seq) WHERE NOT sent;
