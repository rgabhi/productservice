# Orders: controller → service → repository

- `app.py` wires application startup and the router.
- `controller.py` handles HTTP input/output and maps application errors to 404/409/503.
- `schemas.py` defines the Pydantic request contract.
- `service.py` implements idempotent order creation and saga transitions, and owns transaction boundaries.
- `repository.py` contains order SQL, with no independent commit.
- `inventory_client.py` reads the authoritative price over HTTP; it converts dependency failures to application errors.

The service writes the order, history and next command on the same connection. Its Kafka handler likewise owns inbox receipt, state change and outbox insertion as one transaction. A completed/cancelled order cannot move backwards on a duplicate response.

There are no generic base classes or ORM layers. Payment outcomes and demo customer headers remain teaching controls, not real payments/authentication.
