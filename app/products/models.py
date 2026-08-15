from enum import Enum

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import BaseModel


class Category(str, Enum):
    SEAFOOD = "수산물"
    FRUIT = "과일"
    VEGETABLE = "채소"
    MEAT = "육류"
    GRAIN = "쌀/잡곡"
    PROCESSED = "가공식품"


class Product(BaseModel):
    __tablename__ = "products"
    category: Mapped[Category] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    supplier_code: Mapped[str] = mapped_column(String(50), index=True)


class ProductImage(BaseModel):
    __tablename__ = "product_images"
    product_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
    )
    image_key: Mapped[str] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class ProductOption(BaseModel):
    __tablename__ = "product_options"
    product_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
    )
    option_name: Mapped[str] = mapped_column(String(40))
    price: Mapped[int] = mapped_column(Integer)
    discount_price: Mapped[int | None] = mapped_column(Integer, nullable=True)

    stock: Mapped[int] = mapped_column(Integer, default=0)


class ProductLabel(BaseModel):
    __tablename__ = "product_labels"
    product_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
    )
    item_name: Mapped[str] = mapped_column(String(255))
    manufacturer: Mapped[str] = mapped_column(String(255))
    origin: Mapped[str] = mapped_column(Text)
    expiration_info: Mapped[str] = mapped_column(Text)
    item_group_notice: Mapped[str] = mapped_column(Text)
    imported_food_notice: Mapped[str] = mapped_column(Text)
    composition: Mapped[str] = mapped_column(Text)
    storage_method: Mapped[str] = mapped_column(Text)
    safety_caution: Mapped[str] = mapped_column(Text)
    customer_service_phone: Mapped[str] = mapped_column(String(50))
