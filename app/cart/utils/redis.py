from datetime import timedelta

CART_EXPIRE = timedelta(weeks=2)


class CartRedis:
    @classmethod
    def cart(cls, user_id: str) -> str:
        return f"cart:{user_id}"
