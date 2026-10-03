from pydantic import BaseModel, Field


class CartOptionsReadResponse(BaseModel):
    option_id: str
    option_name: str
    price: int
    discount_price: int | None = Field(default=None)
    quantity: int
    total_option_price: int
    thumbnail_image_key: str


class CartReadResponse(BaseModel):
    items: list[CartOptionsReadResponse]
    total_price: int
