from httpx import AsyncClient

from app.auth.models import User


async def login(client: AsyncClient, user: User) -> dict[str, str]:
    response = await client.post("/api/v1/auth/login", json={"email": user.email, "password": "Password@1"})
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


async def add_cart(client: AsyncClient, headers: dict[str, str], option_id: str, quantity: int) -> None:
    await client.post("/api/v1/cart", headers=headers, json={"option_id": option_id, "quantity": quantity})
