# Layered checkout validation · 19 November 2026

The controller–service–repository refactor preserves all public routes, request/response schemas, statuses and complete OpenAPI documents.

| Check | Result |
|---|---|
| Existing real infrastructure integration cases | **15 passed** |
| Isolated controller HTTP contracts | **3 passed**: application errors map to 404/409/503 |
| Kafka recovery / Redis fallback | **2 passed** |
| Total | **20 checks passed** |
| External API compatibility | All three OpenAPI documents exactly equal before/after |
| Service-owned rollback | Failure at outbox insertion rolled back inbox, stock, reservation and event |
| Concurrency/idempotency | Buyer requests, direct SQL contention and event/business replays passed |
| Demo | Approved COMPLETED; declined compensated CANCELLED; repeated keys reuse orders |
| Dependency/import checks | No broken requirements; Python code compiles/imports |

Source fingerprint: `ebfe9303b23a737ee9e960944e290ae5919e7ade0a8b52b7b1bfe47cc91b69f4`. PostgreSQL, Kafka and Redis are real local Linux containers. The three controller-only checks replace the business function with an application error; they do not claim database coverage.

Reproduce: `python3 tools/dev.py up`, then `test`, `failure-demo` and `demo`. Failure demonstrations restore the broker/cache. Raw evidence and before/after OpenAPI documents are stored locally outside the publication tree.

Business services own transactions. Repositories receive the connection and do not commit. Consumers acknowledge only after the service commits. Publisher delivery bookkeeping and startup/health operations are infrastructure transactions, not business-use-case commits.

GitHub CI is prepared, not remotely run. No production-readiness, real-payment/authentication, refund/reconciliation or throughput claim. Java history is preserved; personal learning materials remain local.
