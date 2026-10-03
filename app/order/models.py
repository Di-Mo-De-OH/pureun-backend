from enum import Enum

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import BaseModel


class Status(str, Enum):
    PENDING = "결제대기"
    PAID = "결제완료"
    FAILED = "결제실패"


class Order(BaseModel):
    __tablename__ = "orders"
    user_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("users.id"),
        index=True,
    )
    amount: Mapped[int] = mapped_column(
        Integer,
    )
    order_name: Mapped[str] = mapped_column(
        String(100),
    )
    payment_key: Mapped[str | None] = mapped_column(String(200), unique=True, nullable=True)
    status: Mapped[Status] = mapped_column(String(10), default=Status.PENDING)


class OrderItem(BaseModel):
    __tablename__ = "order_items"
    order_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("orders.id"),
        index=True,
    )
    option_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("product_options.id"),
        index=True,
    )
    option_name: Mapped[str] = mapped_column(
        String(40),
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
    )
    price: Mapped[int] = mapped_column(
        Integer,
    )
    discount_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
