# Payments: service → repository, entered through Kafka

There is no business HTTP API here; the shared application provides health only. `app.py` wires the Kafka handler. `service.py` owns inbox receipt, the deterministic payment decision, ledger write and outgoing result in one transaction. `repository.py` executes ledger SQL on its supplied connection and never commits independently.

A unique order ID protects the simulated operation even if another event ID repeats it. This is an approve/decline simulator, not a real payment integration. No empty controller, ORM, provider reconciliation or refunds are added for architectural symmetry.
