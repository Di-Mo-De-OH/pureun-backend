from pydantic import BaseModel, Field


class CartIncreaseResponse(BaseModel):
    quantity: int = Field(examples=[1])


class CartDecreaseResponse(BaseModel):
    quantity: int = Field(examples=[1])
