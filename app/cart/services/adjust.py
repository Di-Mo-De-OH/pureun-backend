from fastapi import HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cart.schemas.adjust import CartDecreaseResponse, CartIncreaseResponse
from app.cart.utils.redis import CART_EXPIRE, CartRedis
from app.core.redis import redis_client
from app.products.models import ProductOption


async def cart_increase(db: AsyncSession, option_id: str,user_id: str, ) -> CartIncreaseResponse:
    stmt = select(ProductOption).where(ProductOption.id == option_id)
    result = await db.execute(stmt)
    option = result.scalar_one_or_none()
    if not option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 상품을 찾을 수 없습니다.")

    try:
        existing = await redis_client.hget(CartRedis.cart(user_id), option_id)
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )

    existing_quantity = int(existing) if existing is not None else 0
    if existing_quantity + 1 > option.stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="재고가 부족합니다.")
    try:
        async with redis_client.pipeline() as pipe:
            pipe.hincrby(CartRedis.cart(user_id), option_id)
            pipe.expire(CartRedis.cart(user_id), CART_EXPIRE)
            new_quantity, _ = await pipe.execute()
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )

    return CartIncreaseResponse(quantity=new_quantity)


async def cart_decrease(option_id: str,user_id: str, ) -> CartDecreaseResponse:
    try:
        existing = await redis_client.hget(CartRedis.cart(user_id), option_id)
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )

    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 상품을 찾을 수 없습니다.")
    if int(existing) < 2:
        return CartDecreaseResponse(quantity=1)

    try:
        async with redis_client.pipeline() as pipe:
            pipe.hincrby(CartRedis.cart(user_id), option_id, -1)
            pipe.expire(CartRedis.cart(user_id), CART_EXPIRE)
            new_quantity, _ = await pipe.execute()
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )
    return CartDecreaseResponse(quantity=new_quantity)
