class CartRedis:
    @classmethod
    def cart(cls, user_id: str) -> str:
        return f"cart:{user_id}"
