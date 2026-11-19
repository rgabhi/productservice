"""Inventory HTTP adapter; stock/cache decisions stay in service.py."""
from fastapi import APIRouter, HTTPException, Request, Response
from common.errors import NotFound
from services.inventory import service

router = APIRouter()


@router.get('/products')
def products(request: Request, response: Response):
    result, cache_status = service.catalog(request.app.state.database_url, request.app.state.cache)
    response.headers['X-Cache'] = cache_status
    return result


@router.get('/products/{product_id}')
def product(product_id: int, request: Request):
    try:
        return service.product(request.app.state.database_url, product_id)
    except NotFound as exc:
        raise HTTPException(404, str(exc)) from exc
