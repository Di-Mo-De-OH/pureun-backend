from pydantic import BaseModel, ConfigDict, field_serializer

from app.address.utils.formatters import format_phone_number


class AddressReadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    recipient_name: str
    phone_number: str
    post_code: str
    base_address: str
    detail_address: str | None
    is_default: bool

    @field_serializer("phone_number")
    def serialize_phone_number(self, value: str) -> str:
        return format_phone_number(value)
