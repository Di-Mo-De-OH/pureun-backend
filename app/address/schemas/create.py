from pydantic import BaseModel, ConfigDict, Field

from app.core.utils.validators import PhoneField, PostCodeField


class AddressCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    recipient_name: str = Field(examples=["수령자명"], min_length=1, max_length=30)
    phone_number: PhoneField = Field(examples=["010-0000-0000"])
    post_code: PostCodeField = Field(examples=["04048"])
    base_address: str = Field(examples=["서울 마포구 ..."], min_length=1, max_length=255)
    detail_address: str | None = Field(examples=["101동 101호"], default=None, max_length=255)
    is_default: bool = Field(default=False)


class AddressCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    is_default: bool
