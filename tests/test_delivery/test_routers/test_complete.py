from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.delivery.models import Delivery, DeliveryStatus
from tests.utils import login


async def test_complete_delivery(
    client: AsyncClient,
    db: AsyncSession,
    admin_user: User,
    shipping_delivery: Delivery,
) -> None:
    header = await login(client, admin_user)
    response = await client.post(
        f"/api/v1/deliveries/{shipping_delivery.id}/complete",
        headers=header,
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["status"] == DeliveryStatus.DELIVERED


async def test_complete_delivery_already_delivered(
    client: AsyncClient,
    db: AsyncSession,
    admin_user: User,
    shipping_delivery: Delivery,
) -> None:
    header = await login(client, admin_user)
    first_response = await client.post(
        f"/api/v1/deliveries/{shipping_delivery.id}/complete",
        headers=header,
    )
    assert first_response.status_code == status.HTTP_200_OK

    second_response = await client.post(
        f"/api/v1/deliveries/{shipping_delivery.id}/complete",
        headers=header,
    )
    assert second_response.status_code == status.HTTP_200_OK

    first_response_body = first_response.json()
    second_response_body = second_response.json()
    assert first_response_body["delivered_at"] == second_response_body["delivered_at"]


async def test_complete_delivery_not_shipping(
    client: AsyncClient,
    db: AsyncSession,
    admin_user: User,
    paid_delivery: Delivery,
) -> None:
    header = await login(client, admin_user)
    response = await client.post(
        f"/api/v1/deliveries/{paid_delivery.id}/complete",
        headers=header,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    await db.refresh(paid_delivery)
    assert paid_delivery.status == DeliveryStatus.PREPARING


async def test_complete_delivery_not_admin(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    shipping_delivery: Delivery,
) -> None:
    header = await login(client, normal_user)
    response = await client.post(
        f"/api/v1/deliveries/{shipping_delivery.id}/complete",
        headers=header,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_complete_delivery_not_found(
    client: AsyncClient,
    db: AsyncSession,
    admin_user: User,
) -> None:
    header = await login(client, admin_user)
    response = await client.post(
        "/api/v1/deliveries/invalid-id/complete",
        headers=header,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
