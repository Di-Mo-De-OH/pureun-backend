from datetime import datetime

from pydantic import BaseModel, Field

from app.products.models import Category


class ProductOptionCreate(BaseModel):
    option_name: str
    price: int
    discount_price: int | None = None
    stock: int = 0


class ProductLabelCreate(BaseModel):
    item_name: str | None = None
    manufacturer: str | None = None
    origin: str | None = None
    expiration_info: str | None = None
    item_group_notice: str | None = None
    imported_food_notice: str | None = None
    composition: str | None = None
    storage_method: str | None = None
    safety_caution: str | None = None
    customer_service_phone: str | None = None


class ProductCreateRequest(BaseModel):
    category: Category
    name: str = Field(examples=["상품명"])
    description: str | None = Field(examples=["상품 상세설명"], default=None)
    supplier_code: str = Field(examples=["상품 코드"])
    options: list[ProductOptionCreate] = Field(min_length=1)
    label: ProductLabelCreate | None = None
    image_keys: list[str] = Field(min_length=1)


class ProductCreateResponse(BaseModel):
    id: str
    created_at: datetime
