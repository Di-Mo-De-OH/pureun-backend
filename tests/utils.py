from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.delivery.models import Delivery
from app.order.models import Order


async def login(client: AsyncClient, user: User) -> dict[str, str]:
    response = await client.post("/api/v1/auth/login", json={"email": user.email, "password": "Password@1"})
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


async def add_cart(client: AsyncClient, headers: dict[str, str], option_id: str, quantity: int) -> None:
    await client.post("/api/v1/cart", headers=headers, json={"option_id": option_id, "quantity": quantity})


async def create_address(client: AsyncClient, headers: dict[str, str], is_default: bool = False) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/addresses",
        headers=headers,
        json={
            "recipient_name": "집",
            "phone_number": "010-1234-1234",
            "post_code": "04044",
            "base_address": "서울특별시 마포구 ...",
            "detail_address": "2층 ",
            "is_default": is_default,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


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


async def assert_delivery_snapshot(
    db: AsyncSession,
    order_id: str,
) -> None:
    stmt = select(Delivery).where(Delivery.order_id == order_id)
    result = await db.execute(stmt)
    delivery = result.scalar_one()
    assert delivery.recipient_name == "집"
    assert delivery.phone_number == "01012341234"
    assert delivery.post_code == "04044"
    assert delivery.base_address == "서울특별시 마포구 ..."
    assert delivery.detail_address == "2층"
    assert delivery.status == "준비중"
