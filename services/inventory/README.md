# Inventory: controller → service → repository

`app.py` wires the router, cache and event handler. `controller.py` handles HTTP and X-Cache headers. `service.py` implements reservation/confirmation/release and catalog-cache decisions; `repository.py` holds the SQL.

The service owns inbox + stock/reservation + outgoing result in one transaction. The repository's conditional stock UPDATE is atomic. Confirmation does not deduct stock twice. Release locks the reservation and restores stock only once.

Catalog metadata is cached for 30 seconds. Stock and the detail/price endpoint remain authoritative. Redis failure falls back to PostgreSQL. No separate schemas module is needed for the existing read-only HTTP endpoints, which have no request-body models.
