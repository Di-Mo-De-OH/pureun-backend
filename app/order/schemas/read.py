from datetime import datetime

from pydantic import BaseModel


class OrderReadListItemResponse(BaseModel):
    option_name: str
    thumbnail_image_key: str
    quantity: int


class OrderReadListResponse(BaseModel):
    order_id: str
    order_name: str
    amount: int
    created_at: datetime
    items: list[OrderReadListItemResponse]
