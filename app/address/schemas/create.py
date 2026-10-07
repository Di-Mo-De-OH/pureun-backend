from pydantic import BaseModel, Field

from app.core.utils.validators import PhoneField


class AddressCreateRequest(BaseModel):
    recipient_name: str = Field(examples=["수령자명"])
    phone_number: PhoneField = Field(examples=["010-0000-0000"])
    post_code: str = Field(examples=["우편번호"])
    base_address: str = Field(examples=["서울 마포구 ..."])
    detail_address: str | None = Field(examples=["101동 101호"], default=None)
    is_default: bool = Field(default=False)


class AddressCreateResponse(BaseModel):
    id: str
    is_default: bool
