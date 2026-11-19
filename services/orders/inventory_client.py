"""Small HTTP adapter. Convert dependency failures into application errors."""
import os
import httpx
from common.errors import NotFound, Unavailable

INVENTORY_URL = os.getenv('INVENTORY_URL', 'http://localhost:8001')


def unit_price(product_id):
    try:
        product = httpx.get(f'{INVENTORY_URL}/products/{product_id}', timeout=3)
        if product.status_code == 404:
            raise NotFound('Unknown product')
        product.raise_for_status()
        return product.json()['price_paise']
    except httpx.HTTPError as exc:
        raise Unavailable('Inventory service unavailable') from exc
