"""Startup wiring shared by the three apps; business rules stay in each service."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from common.bus import Worker
from common.db import database_url, initialize, transaction
from common.repository import ping


def application(name, schema, handler):
    url = database_url(name)
    worker = Worker(name, url, handler)

    @asynccontextmanager
    async def lifespan(app):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(message)s')
        initialize(url, schema)
        worker.start()
        yield
        worker.close()

    app = FastAPI(title=f'Student Checkout — {name}', lifespan=lifespan)
    app.state.database_url = url

    @app.get('/health')
    def health():
        with transaction(url) as conn:
            ping(conn)
        return {'service': name, 'database': 'ok', 'workers_alive': all(t.is_alive() for t in worker.threads),
                'last_worker_error': worker.last_error}

    return app
