from pydantic import BaseModel, Field


class CartAddRequest(BaseModel):
    option_id: str
    quantity: int = Field(gt=0)
