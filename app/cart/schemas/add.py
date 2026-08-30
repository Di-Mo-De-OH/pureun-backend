from pydantic import BaseModel, Field


class CartAddRequest(BaseModel):
    option_id: str
    quantity: int = Field(gt=0)


class CartAddResponse(BaseModel):
    option_name: str = Field(examples=["상품명"])
    quantity: int = Field(examples=[3])
