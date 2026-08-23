from pydantic import BaseModel, Field
from app.products.models import Category

class ProductOptionUpdate(BaseModel):
    id: str | None = Field(default=None, examples=["01M07YY54WWGFSBDS9P8XQX2E5"])
    option_name: str = Field(examples=["1kg"])
    price: int = Field(examples=[10000])
    discount_price: int | None = Field(default=None, examples=[8000])
    stock: int = Field(examples=[10])

class ProductImageUpdate(BaseModel):
    id: str | None = Field(default=None, examples=["01M07YY54WWGFSBDS9P8XQX2E5"])
    image_key: str = Field(examples=["products/01M07YY54WWGFSBDS9P8XQX2E5.jpeg"])
    sort_order: int = Field(examples=[0])

class ProductLabelUpdate(BaseModel):
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

class ProductUpdateRequest(BaseModel):
    category: Category = Field(examples=["수산물"])
    name: str = Field(examples=["산지직송 코코넛"])
    description: str | None = Field(default=None, examples=["상품 상세설명"])
    is_active: bool = Field(examples=[True])
    supplier_code: str = Field(examples=["SUP001"])
    options: list[ProductOptionUpdate] = Field(min_length=1)
    images: list[ProductImageUpdate] = Field(min_length=1)
    label: ProductLabelUpdate
