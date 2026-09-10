from pydantic import BaseModel, Field


class OrderBuyNowRequest(BaseModel):
    option_id: str
    quantity: int = Field(gt=0)


class OrderBuyNowResponse(BaseModel):
    order_id: str
    thumbnail_image_key: str
    amount: int
    order_name: str
