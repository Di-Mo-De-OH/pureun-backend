import pytest
from fastapi import status
from httpx import AsyncClient, HTTPError, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.order.models import Order
from app.products.models import Product
from tests.utils import login


async def test_order_confirm(
    client: AsyncClient,
    db: AsyncSession,
    order_1: Order,
    normal_user: User,
    product_1: Product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_call_toss_confirm(payment_key: str, order_id: str, amount: int) -> Response:
        return Response(200, json={"status": "DONE"})

    monkeypatch.setattr("app.order.services.confirm.call_toss_confirm", fake_call_toss_confirm)

    headers = await login(client, normal_user)
    response = await client.post(
        f"/api/v1/orders/{order_1.id}/confirm",
        headers=headers,
        json={
            "payment_key": "test-payment-key",
            "amount": order_1.amount,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "결제완료"


async def test_order_confirm_invalid_order_id(
    client: AsyncClient,
    db: AsyncSession,
    order_1: Order,
    normal_user: User,
    product_1: Product,
) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "/api/v1/orders/invalid-order_id/confirm",
        headers=headers,
        json={
            "payment_key": "test-payment-key",
            "amount": order_1.amount,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_order_confirm_forbidden_user(
    client: AsyncClient,
    db: AsyncSession,
    order_1: Order,
    normal_user2: User,
    product_1: Product,
) -> None:
    headers = await login(client, normal_user2)
    response = await client.post(
        f"/api/v1/orders/{order_1.id}/confirm",
        headers=headers,
        json={
            "payment_key": "test-payment-key",
            "amount": order_1.amount,
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_order_confirm_wrong_amount(
    client: AsyncClient,
    db: AsyncSession,
    order_1: Order,
    normal_user: User,
    product_1: Product,
) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        f"/api/v1/orders/{order_1.id}/confirm",
        headers=headers,
        json={
            "payment_key": "test-payment-key",
            "amount": 10000,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_order_confirm_toss_fail(
    client: AsyncClient,
    db: AsyncSession,
    order_1: Order,
    normal_user: User,
    product_1: Product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_call_toss_confirm(payment_key: str, order_id: str, amount: int) -> Response:
        return Response(400, json={"status": "FAILED"})

    monkeypatch.setattr("app.order.services.confirm.call_toss_confirm", fake_call_toss_confirm)
    headers = await login(client, normal_user)
    response = await client.post(
        f"/api/v1/orders/{order_1.id}/confirm",
        headers=headers,
        json={
            "payment_key": "test-payment-key",
            "amount": order_1.amount,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "결제실패"


async def test_order_confirm_duplicate(
    client: AsyncClient,
    db: AsyncSession,
    order_1: Order,
    normal_user: User,
    product_1: Product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    call_count = 0

    async def fake_call_toss_confirm(payment_key: str, order_id: str, amount: int) -> Response:
        nonlocal call_count
        call_count += 1
        return Response(200, json={"status": "DONE"})

    monkeypatch.setattr("app.order.services.confirm.call_toss_confirm", fake_call_toss_confirm)

    headers = await login(client, normal_user)
    response1 = await client.post(
        f"/api/v1/orders/{order_1.id}/confirm",
        headers=headers,
        json={
            "payment_key": "test-payment-key",
            "amount": order_1.amount,
        },
    )

    response2 = await client.post(
        f"/api/v1/orders/{order_1.id}/confirm",
        headers=headers,
        json={
            "payment_key": "test-payment-key",
            "amount": order_1.amount,
        },
    )
    assert response1.status_code == status.HTTP_200_OK
    assert response1.json()["status"] == "결제완료"
    assert response2.status_code == status.HTTP_200_OK
    assert response2.json()["status"] == "결제완료"
    assert call_count == 1


async def test_order_confirm_unauthorized(
    client: AsyncClient,
    db: AsyncSession,
    order_1: Order,
    product_1: Product,
) -> None:
    response = await client.post(
        f"/api/v1/orders/{order_1.id}/confirm",
        json={
            "payment_key": "test-payment-key",
            "amount": order_1.amount,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_order_confirm_network_error(
    client: AsyncClient,
    db: AsyncSession,
    order_1: Order,
    normal_user: User,
    product_1: Product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_call_toss_confirm(payment_key: str, order_id: str, amount: int) -> Response:
        raise HTTPError("network error")

    monkeypatch.setattr("app.order.services.confirm.call_toss_confirm", fake_call_toss_confirm)
    headers = await login(client, normal_user)
    response = await client.post(
        f"/api/v1/orders/{order_1.id}/confirm",
        headers=headers,
        json={
            "payment_key": "test-payment-key",
            "amount": order_1.amount,
        },
    )
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
