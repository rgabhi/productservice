"""Application composition only; endpoints and business logic live in their layers."""
from common.application import application
from services.orders.controller import router
from services.orders.service import handle_event

app = application('orders', 'services/orders/schema.sql', handle_event)
app.include_router(router)
