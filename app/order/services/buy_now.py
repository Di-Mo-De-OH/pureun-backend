from fastapi import HTTPException, status
from sqlalchemy import Row, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.order.models import Order, OrderItem
from app.order.schemas.buy_now import OrderBuyNowResponse
from app.products.models import Product, ProductImage, ProductOption


async def get_option(db: AsyncSession, option_id: str) -> Row[tuple[ProductOption, str]] | None:
    stmt = (
        select(ProductOption, Product.name)
        .join(Product, Product.id == ProductOption.product_id)
        .where(ProductOption.id == option_id, Product.is_active.is_(True))
    )
    result = await db.execute(stmt)
    return result.one_or_none()


async def get_thumbnail_image(db: AsyncSession, product_id: str) -> ProductImage | None:
    stmt = (
        select(ProductImage)
        .join(Product, Product.id == ProductImage.product_id)
        .where(ProductImage.product_id == product_id, ProductImage.sort_order == 0)
    )
    result = await db.execute(stmt)
    return result.scalars().one_or_none()


async def order_buy_now(db: AsyncSession, user_id: str, option_id: str, quantity: int) -> OrderBuyNowResponse:
    result = await get_option(db, option_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 상품을 찾을 수 없습니다.")
    option, product_name = result
    product_id = option.product_id
    product_image = await get_thumbnail_image(db, product_id)
    if not product_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="상품 이미지를 찾을 수 없습니다.")
    thumbnail_image = product_image.image_key
    if quantity > option.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="현재 재고보다 더 많은 구매를 할 수 없습니다."
        )
    amount = quantity * option.price if option.discount_price is None else quantity * option.discount_price
    order_name = f"{product_name} {option.option_name} {quantity}개"

    order = Order(
        user_id=user_id,
        amount=amount,
        order_name=order_name,
    )
    db.add(order)

    try:
        await db.flush()
        db.add(
            OrderItem(
                order_id=order.id,
                option_id=option.id,
                option_name=option.option_name,
                price=option.price,
                quantity=quantity,
                discount_price=option.discount_price,
            )
        )
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="주문 생성에 실패했습니다.")
    return OrderBuyNowResponse(
        order_id=order.id,
        amount=order.amount,
        order_name=order.order_name,
        thumbnail_image_key=thumbnail_image,
    )
