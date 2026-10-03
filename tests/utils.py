import pytest
from fastapi import status
from httpx import AsyncClient, Response

from app.auth.models import User
from app.order.models import Order


async def login(client: AsyncClient, user: User) -> dict[str, str]:
    response = await client.post("/api/v1/auth/login", json={"email": user.email, "password": "Password@1"})
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


async def add_cart(client: AsyncClient, headers: dict[str, str], option_id: str, quantity: int) -> None:
    await client.post("/api/v1/cart", headers=headers, json={"option_id": option_id, "quantity": quantity})


async def confirm_order(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch, headers: dict[str, str], order: Order
) -> int:
    async def fake_call_toss_confirm(payment_key: str, order_id: str, amount: int) -> Response:
        return Response(status.HTTP_200_OK, json={"status": "DONE"})

    monkeypatch.setattr("app.order.services.confirm.call_toss_confirm", fake_call_toss_confirm)

    response = await client.post(
        f"/api/v1/orders/{order.id}/confirm",
        headers=headers,
        json={
            "payment_key": "test-payment-key",
            "amount": order.amount,
        },
    )
    return response.status_code
