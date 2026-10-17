from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.delivery.models import Courier, Delivery, DeliveryStatus
from tests.utils import login

data = {
    "courier": Courier.CJ,
    "tracking_number": "1234-1432-1578-12",
}


async def test_ship(
    client: AsyncClient,
    db: AsyncSession,
    admin_user: User,
    paid_delivery: Delivery,
) -> None:
    headers = await login(client, admin_user)
    response = await client.post(f"/api/v1/deliveries/{paid_delivery.id}/ship", headers=headers, json=data)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["status"] == DeliveryStatus.SHIPPING
    await db.refresh(paid_delivery)
    assert paid_delivery.status == DeliveryStatus.SHIPPING
    assert paid_delivery.courier == data["courier"]
    assert paid_delivery.tracking_number == "12341432157812"
    assert paid_delivery.shipped_at is not None


async def test_ship_delivery_not_found(client: AsyncClient, db: AsyncSession, admin_user: User) -> None:
    headers = await login(client, admin_user)
    response = await client.post("/api/v1/deliveries/invalid-id/ship", headers=headers, json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_ship_delivery_not_admin(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    paid_delivery: Delivery,
) -> None:
    headers = await login(client, normal_user)
    response = await client.post(f"/api/v1/deliveries/{paid_delivery.id}/ship", headers=headers, json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    await db.refresh(paid_delivery)
    assert paid_delivery.status == DeliveryStatus.PREPARING
    assert paid_delivery.courier is None
    assert paid_delivery.tracking_number is None
    assert paid_delivery.shipped_at is None


async def test_ship_delivery_unpaid_order(
    client: AsyncClient,
    db: AsyncSession,
    admin_user: User,
    pending_delivery: Delivery,
) -> None:
    headers = await login(client, admin_user)
    response = await client.post(f"/api/v1/deliveries/{pending_delivery.id}/ship", headers=headers, json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    await db.refresh(pending_delivery)
    assert pending_delivery.status == DeliveryStatus.PREPARING
    assert pending_delivery.courier is None
    assert pending_delivery.tracking_number is None
    assert pending_delivery.shipped_at is None


async def test_ship_delivery_already_shipped(
    client: AsyncClient,
    db: AsyncSession,
    admin_user: User,
    paid_delivery: Delivery,
) -> None:
    headers = await login(client, admin_user)
    response = await client.post(f"/api/v1/deliveries/{paid_delivery.id}/ship", headers=headers, json=data)
    assert response.status_code == status.HTTP_200_OK
    second_response = await client.post(
        f"/api/v1/deliveries/{paid_delivery.id}/ship",
        headers=headers,
        json={
            "courier": Courier.HANJIN,
            "tracking_number": "1111-11111-1111-11",
        },
    )
    assert second_response.status_code == status.HTTP_400_BAD_REQUEST
    await db.refresh(paid_delivery)
    assert paid_delivery.courier == data["courier"]
    assert paid_delivery.tracking_number == "12341432157812"
    assert paid_delivery.status == DeliveryStatus.SHIPPING


async def test_ship_delivery_invalid_courier(
    client: AsyncClient,
    db: AsyncSession,
    admin_user: User,
    paid_delivery: Delivery,
) -> None:
    headers = await login(client, admin_user)
    response = await client.post(
        f"/api/v1/deliveries/{paid_delivery.id}/ship",
        headers=headers,
        json={
            "courier": "이상한 택배사",
            "tracking_number": "1234-1432-1578-12",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    await db.refresh(paid_delivery)
    assert paid_delivery.courier is None
    assert paid_delivery.tracking_number is None
    assert paid_delivery.shipped_at is None


async def test_ship_delivery_invalid_tracking_number(
    client: AsyncClient,
    db: AsyncSession,
    admin_user: User,
    paid_delivery: Delivery,
) -> None:
    headers = await login(client, admin_user)
    response = await client.post(
        f"/api/v1/deliveries/{paid_delivery.id}/ship",
        headers=headers,
        json={
            "courier": Courier.HANJIN,
            "tracking_number": "1234-1432-1578-as12",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    await db.refresh(paid_delivery)
    assert paid_delivery.courier is None
    assert paid_delivery.tracking_number is None
    assert paid_delivery.shipped_at is None
