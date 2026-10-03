from datetime import datetime

from pydantic import BaseModel, Field

from app.products.models import Category


class ProductOptionCreate(BaseModel):
    option_name: str
    price: int
    discount_price: int | None = None
    stock: int = 0


class ProductLabelCreate(BaseModel):
    item_name: str = Field(examples=["상품명"])
    manufacturer: str = Field(examples=["제조업체"])
    origin: str = Field(examples=["원산지"])
    expiration_info: str = Field(examples=["유통기한"])
    item_group_notice: str = Field(examples=["상품군 공지"])
    imported_food_notice: str = Field(examples=["수입 식품 주의사항"])
    composition: str = Field(examples=["구성"])
    storage_method: str = Field(examples=["저장 방식"])
    safety_caution: str = Field(examples=["안전 주의"])
    customer_service_phone: str = Field(examples=["판매자 전화번호"])


class ProductCreateRequest(BaseModel):
    category: Category
    name: str = Field(examples=["상품명"])
    description: str | None = Field(examples=["상품 상세설명"], default=None)
    supplier_code: str = Field(examples=["상품 코드"])
    options: list[ProductOptionCreate] = Field(min_length=1)
    label: ProductLabelCreate
    image_keys: list[str] = Field(min_length=1)


class ProductCreateResponse(BaseModel):
    id: str
    created_at: datetime
