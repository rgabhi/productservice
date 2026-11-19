# Why this small design?

The purpose is student learning and interview discussion. The three service boundaries create a reason to discuss distributed consistency, while one-item orders and deterministic payments keep the code small.

## Boundaries

Orders owns the API, request keys, price snapshots and saga state. Inventory owns products/stock and reservations. Payments owns a durable simulated payment result. Each has its own PostgreSQL database/role; using one local server is a development convenience, not shared data ownership.

Controllers handle HTTP and application-error translation; services contain business use cases and own transactions; repositories execute SQL using the supplied connection. The common helpers contain transport, transaction mechanics and messaging-table SQL. Business transitions stay inside the relevant service. The original Java source is retained separately; the new Python system is a dated rebuild.

## What a transaction solves

A reservation executes `UPDATE products SET stock=stock-quantity WHERE ... AND stock>=quantity`. PostgreSQL serialises competing updates; the condition is re-evaluated against the current row. The same transaction records its reservation and next event. If any operation fails, all those changes roll back. A separate Python read-then-write check would permit a race.

Request idempotency is scoped by `(customer, idempotency_key)` and includes a canonical body fingerprint. The unique constraint, not a precheck alone, settles concurrent requests. Prices are looked up server-side and saved as integer-paise snapshots. Catalog prices are seeded and not edited through this demo; price-change/quote-expiry policy is a later extension.

## What a transaction does not solve

PostgreSQL cannot atomically commit a row and acknowledge a Kafka publication using an ordinary local transaction. An outbox stores the next event with the business update. A publisher retries unsent rows. A crash after Kafka acknowledgement but before marking the row sent can repeat the event.

A consumer passes the message to the service. That service inserts the event ID into its inbox and changes business state in one transaction using repositories. After the service commits, the consumer acknowledges the Kafka offset. Replaying the same event ID skips its effect. The reservation/payment order ID constraints additionally protect against the same logical command delivered with a different event ID. This is at-least-once delivery with idempotent business effects, not a general exactly-once guarantee.

One publisher per service sends rows in local outbox order. Kafka uses order ID as the message key. This lab does not support arbitrary parallel publishers or claim ordering across topics. One consumer handles each service's topic; adding concurrency requires revisiting partition ordering and offset commits.

## Saga

A successful reservation triggers payment. A successful payment triggers reservation confirmation, then order completion. A definitive decline triggers release; only its acknowledgement closes the order as cancelled. Release increments stock once because the reservation is locked and changes from RESERVED to RELEASED in that same transaction.

The deterministic provider cannot have an ambiguous result: approval/decline is stored locally. Real providers introduce a crucial extra case: timeout after a successful charge. A production design needs a stable provider operation key, reconciliation and refund policy. Those are deliberately not implemented in this learning version.

## Cache and failure behaviour

Redis caches only catalog metadata. The price/stock detail endpoint goes directly to inventory's DB, and stock is changed only by reservation transactions. Redis failure produces a DB fallback and X-Cache: BYPASS. A 30-second TTL bounds metadata staleness; catalog mutation/invalidation is an optional exercise.

Kafka failure leaves committed unsent outbox rows and pending orders. Publisher/consumer retries resume after recovery. Unexpected handler errors are visible in logs/health and retry from the last committed offset; poison-message quarantine is a later lesson. Worker processes must not silently acknowledge a failed database transaction.

## Intentionally simple

A connection per SQL transaction, one polling publisher and one consumer thread per service, a row lock during send, and a local Compose stack are adequate for this lab. Pooling, relay leases, multiple API replicas, full telemetry, retry queues, dead-letter tooling and HA clusters would add learning topics and code, not make this particular lesson more complete.

Future exercises: multi-item atomic reservations; consumer scaling; avoid a long outbox lock; provider timeout/reconciliation; cache invalidation; event schema evolution. Add one exercise at a time and state its new invariant before implementing it.

## Primary references

- [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [Kafka delivery semantics](https://kafka.apache.org/41/design/design/)
- [Psycopg transaction contexts](https://www.psycopg.org/psycopg3/docs/basic/transactions.html)

## Layered refactor · 19 November 2026

Each business transaction is opened in service.py. Repositories receive the connection; they neither commit individual steps nor know HTTP status codes. Controllers use application errors from common/errors.py and preserve the public HTTP contract. Price lookup is an outbound adapter in orders/inventory_client.py. Payments enters the service layer through Kafka and has no unnecessary business controller. Plain functions keep this separation small. All table definitions, routes, status codes and event formats are preserved.

The rollback test now injects failure during outbox insertion through the service entry point, rather than letting the test own the business transaction. It checks that the service rolls back inbox receipt, stock, reservation and outgoing event together.
