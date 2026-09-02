from fastapi import HTTPException, status
from redis.exceptions import RedisError

from app.cart.utils.redis import CartRedis
from app.core.redis import redis_client


async def cart_delete(option_id: str, user_id: str) -> None:
    try:
        await redis_client.hdel(CartRedis.cart(user_id), option_id)
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )
