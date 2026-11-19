"""The payment service consumes commands; it has no business HTTP controller."""
from common.application import application
from services.payments.service import handle_event

app = application('payments', 'services/payments/schema.sql', handle_event)
