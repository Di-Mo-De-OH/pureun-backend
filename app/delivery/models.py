from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import BaseModel


class Courier(str, Enum):
    CJ = "CJ대한통운"
    HANJIN = "한진택배"
    LOTTE = "롯데택배"
    EPOST = "우체국택배"
    LOGEN = "로젠택배"


class DeliveryStatus(str, Enum):
    PREPARING = "준비중"
    SHIPPING = "배송중"
    DELIVERED = "배송완료"


class Delivery(BaseModel):
    __tablename__ = "deliveries"
    order_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("orders.id"),
        index=True,
        unique=True,
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
    courier: Mapped[Courier | None] = mapped_column(
        String(20),
        default=None,
    )
    tracking_number: Mapped[str | None] = mapped_column(
        String(20),
        default=None,
    )
    status: Mapped[DeliveryStatus] = mapped_column(
        String(10),
        default=DeliveryStatus.PREPARING,
    )
    shipped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
    )
