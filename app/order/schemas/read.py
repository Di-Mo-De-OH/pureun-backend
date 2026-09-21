from pydantic import BaseModel
from datetime import datetime

class OrderReadListItemResponse(BaseModel):
    option_name:str
    thumbnail_image_key: str
    quantity: int

class OrderReadListResponse(BaseModel):
    order_id: str
    amount: int
    created_at: datetime
    items: list[OrderReadListItemResponse]



