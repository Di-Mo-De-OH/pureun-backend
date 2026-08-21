from pydantic import BaseModel, ConfigDict, Field
from app.products.models import Category


class ProductSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"])
    name: str = Field(examples=["오징어"])
    price: int = Field(examples=[10000])
    discount_price: int | None = Field(examples=[5000], default=None)
    thumbnail_image_key: str

class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"])
    image_key:str = Field(examples=["products/01M07YY54WWGFSBDS9P8XQX2E5.jpeg"])
    sort_order:int = Field(examples= [1])

class ProductOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:str = Field(examples=["01M07YY54WWGFSBDS9P8XQX2E5"])
    option_name:str = Field(examples=["1kg,1박스"])
    price:int = Field(examples=[10000])
    discount_price:int|None = Field(examples=[5000],default=None)
    stock: int = Field(examples=[5])

class ProductLabelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:str = Field(examples=["01M07YY54WWGFSBDS9P8XQX2E5"])
    item_name:str = Field(examples=["상품명"])
    manufacturer:str = Field(examples=["제조업체"])
    origin:str = Field(examples=["원산지"])
    expiration_info:str = Field(examples=["유통기한"])
    item_group_notice:str = Field(examples=["상품군 공지"])
    imported_food_notice:str = Field(examples=["수입 식품 주의사항"])
    composition:str = Field(examples=["구성"])
    storage_method:str = Field(examples=["저장 방식"])
    safety_caution:str = Field(examples=["안전 주의"])
    customer_service_phone:str =Field(examples=["판매자 전화번호"])

class ProductDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:str = Field(examples=["01M07YY54WWGFSBDS9P8XQX2E5"])
    category:Category = Field(examples = ["육류"])
    name:str = Field(examples=["상품명"])
    description:str | None =Field(examples=["상품상세설명란"],default=None)
    supplier_code:str = Field(examples=["올바다수산"])
    options:list[ProductOptionResponse]
    images:list[ProductImageResponse]
    label:ProductLabelResponse
