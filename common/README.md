# Shared mechanics

`db.py`: connection/transaction context and schema startup. Application services use the context to own business commits/rollbacks.

`repository.py`: SQL for inbox/outbox delivery records. It uses the service's connection when participating in business work; it never opens or commits a connection itself.

`bus.py`: one polling publisher/consumer per service. The consumer validates the event and calls service.handle_event(database_url, message). The service returns after its transaction commits; only then is the Kafka offset committed. The publisher owns only the separate transport-delivery bookkeeping transaction.

`application.py`: infrastructure startup, shared health route and worker wiring. `events.py`: small versioned message envelope. `errors.py`: HTTP-independent application errors translated by controllers.

Business rules belong in each service module. The lab retains one consumer/publisher per service, simple retry logs and order-ID Kafka keys.
