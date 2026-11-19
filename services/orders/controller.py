"""HTTP input/output only: use cases do not know HTTP status codes."""
from uuid import UUID
from fastapi import APIRouter, Header, HTTPException, Request, Response
from common.errors import Conflict, NotFound, Unavailable
from services.orders import service
from services.orders.schemas import NewOrder

router = APIRouter()


@router.post('/orders', status_code=202)
def create_order(body: NewOrder, response: Response, request: Request,
                 idempotency_key: str = Header(min_length=1, max_length=80),
                 x_demo_customer: str = Header(default='student', min_length=1, max_length=80)):
    """Commit order + reserve command; the asynchronous saga finishes afterwards."""
    try:
        result = service.create_order(request.app.state.database_url, body.model_dump(),
                                      idempotency_key, x_demo_customer)
    except NotFound as exc:
        raise HTTPException(404, str(exc)) from exc
    except Conflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except Unavailable as exc:
        raise HTTPException(503, str(exc)) from exc
    response.headers['Location'] = f'/orders/{result["id"]}'
    return result


@router.get('/orders/{order_id}')
def get_order(order_id: UUID, request: Request, x_demo_customer: str = Header(default='student')):
    try:
        return service.get_order(request.app.state.database_url, order_id, x_demo_customer)
    except NotFound as exc:
        raise HTTPException(404, str(exc)) from exc
