"""One product per order keeps the distributed-systems lesson small."""
from typing import Literal
from pydantic import BaseModel, Field


class NewOrder(BaseModel):
    product_id: int = Field(gt=0, strict=True)
    quantity: int = Field(ge=1, le=10, strict=True)
    # Teaching switch only: no real payment provider or card information.
    payment_outcome: Literal['approve', 'decline'] = 'approve'
