"""Public HTTP error contracts remain stable when business errors move into services."""
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from common.errors import Conflict, NotFound, Unavailable
from services.orders.controller import router
from services.orders import service


@pytest.mark.parametrize('error,code',[(NotFound,404),(Conflict,409),(Unavailable,503)])
def test_controller_translates_application_errors(monkeypatch, error, code):
    app = FastAPI()
    app.state.database_url = 'unused-by-fake-use-case'
    app.include_router(router)

    def fail_use_case(*args):
        raise error('learning example')

    monkeypatch.setattr(service, 'create_order', fail_use_case)
    with TestClient(app) as client:
        result = client.post('/orders', headers={'Idempotency-Key':'controller-example'},
                             json={'product_id':1,'quantity':1})
    assert result.status_code == code
    assert result.json() == {'detail':'learning example'}
