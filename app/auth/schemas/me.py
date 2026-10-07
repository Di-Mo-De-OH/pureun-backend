from pydantic import BaseModel, ConfigDict, Field

from app.core.utils.validators import NicknameField


class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(examples=["01JB3X8Z9Q0K4C7D2E5F6G7H8J"])
    email: str = Field(examples=["test@example.com"])
    name: str = Field(examples=["name"])
    nickname: str = Field(examples=["nickname"])


class MeUpdateRequest(BaseModel):

    name: str | None = Field(default=None, examples=["name"])
    nickname: NicknameField | None = Field(default=None, examples=["nickname"])
