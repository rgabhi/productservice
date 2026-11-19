"""Wire dependencies and routes; no business rules or SQL."""
import os
import redis
from common.application import application
from services.inventory.controller import router
from services.inventory.service import handle_event

app = application('inventory', 'services/inventory/schema.sql', handle_event)
app.state.cache = redis.Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:16379/0'),
                                      socket_timeout=0.3, socket_connect_timeout=0.3,
                                      decode_responses=True)
app.include_router(router)
