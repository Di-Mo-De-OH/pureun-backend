from typing import cast

from fastapi import HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cart.schemas.read import CartOptionsReadResponse, CartReadResponse
from app.cart.utils.redis import CartRedis
from app.core.redis import redis_client
from app.products.models import Product, ProductImage, ProductOption


async def get_cart(user_id: str) -> dict[str, str]:
    try:
        cart = await redis_client.hgetall(CartRedis.cart(user_id))
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="일시적으로 서비스를 사용할 수 없습니다."
        )
    return cast(dict[str, str], cart)


async def get_cart_options(db: AsyncSession, option_ids: list[str]) -> dict[str, ProductOption]:
    stmt = (
        select(ProductOption)
        .join(Product, Product.id == ProductOption.product_id)
        .where(ProductOption.id.in_(option_ids), Product.is_active.is_(True))
    )

    result = await db.execute(stmt)
    return {option.id: option for option in result.scalars().all()}


async def get_cart_image(db: AsyncSession, product_ids: list[str]) -> dict[str, str]:
    stmt = select(ProductImage).where(ProductImage.product_id.in_(product_ids), ProductImage.sort_order == 0)
    result = await db.execute(stmt)
    return {image.product_id: image.image_key for image in result.scalars().all()}


async def cart_read(db: AsyncSession, user_id: str) -> CartReadResponse:
    cart = await get_cart(user_id)
    if not cart:
        return CartReadResponse(items=[], total_price=0)

    option_ids = list(cart.keys())

    options = await get_cart_options(db, option_ids)

    product_ids = [option.product_id for option in options.values()]
    # ProductOption은 product_id만 알고 있어서, 이후 옵션 객체들이랑 이미지를 매핑하려면 product_id를 키로 둬야 한다
    images = await get_cart_image(db, product_ids)
    items: list[CartOptionsReadResponse] = []
    total_price = 0

    for option_id, quantity_str in cart.items():
        option = options.get(option_id)
        if not option:
            continue
            # Redis 카트에는 남아있지만 DB에서 상품이 이미 삭제된 "유령 항목"이라 조용히 건너뛴다
        quantity = int(quantity_str)
        unit_price = option.discount_price if option.discount_price is not None else option.price
        total_option_price = unit_price * quantity
        total_price += total_option_price
        items.append(
            CartOptionsReadResponse(
                option_id=option.id,
                option_name=option.option_name,
                price=option.price,
                discount_price=option.discount_price,
                quantity=quantity,
                total_option_price=total_option_price,
                thumbnail_image_key=images[option.product_id],
            )
        )
    return CartReadResponse(
        items=items,
        total_price=total_price,
    )
