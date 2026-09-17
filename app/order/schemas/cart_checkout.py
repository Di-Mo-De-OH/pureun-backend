from pydantic import BaseModel


class OrderCartCheckoutItemResponse(BaseModel):
    option_name: str
    thumbnail_image_key: str
    quantity: int


class OrderCartCheckoutResponse(BaseModel):
    order_id: str
    amount: int
    order_name: str
    items: list[OrderCartCheckoutItemResponse]
