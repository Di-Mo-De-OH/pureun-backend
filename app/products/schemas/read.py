from pydantic import BaseModel, ConfigDict, Field


class ProductSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    name: str = Field(examples=["오징어"])
    price: int = Field(examples=[10000])
    discount_price: int | None = Field(examples=[5000], default=None)
    thumbnail_image_key: str
