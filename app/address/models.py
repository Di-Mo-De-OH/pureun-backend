from sqlalchemy import Boolean, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import BaseModel


class Address(BaseModel):
    __tablename__ = "addresses"
    user_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    recipient_name: Mapped[str] = mapped_column(
        String(30),
    )
    phone_number: Mapped[str] = mapped_column(
        String(20),
    )
    post_code: Mapped[str] = mapped_column(
        String(10),
    )
    base_address: Mapped[str] = mapped_column(
        String(255),
    )
    detail_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
    )
