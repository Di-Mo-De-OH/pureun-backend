import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.utils.security import hash_password
from app.delivery.models import Delivery, DeliveryStatus
from app.order.models import Order, Status


@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    user = User(
        email="admin@example.com",
        hashed_password=hash_password("Password@1"),
        name="admin",
        nickname="admin",
        is_admin=True,
    )
    db.add(user)
    await db.commit()
    return user


@pytest.fixture
async def normal_user(db: AsyncSession) -> User:
    user = User(
        email="user@example.com",
        hashed_password=hash_password("Password@1"),
        name="user",
        nickname="user",
    )
    db.add(user)
    await db.commit()
    return user


@pytest.fixture
async def paid_delivery(db: AsyncSession, normal_user: User) -> Delivery:
    order = Order(
        user_id=normal_user.id,
        amount=16000,
        order_name="오징어 1kg 2개",
        status=Status.PAID,
    )
    db.add(order)
    await db.flush()

    delivery = Delivery(
        order_id=order.id,
        recipient_name="집",
        phone_number="01012341234",
        post_code="04044",
        base_address="서울특별시 마포구 ...",
        detail_address="2층",
    )
    db.add(delivery)
    await db.commit()
    return delivery


@pytest.fixture
async def pending_delivery(db: AsyncSession, normal_user: User) -> Delivery:
    order = Order(
        user_id=normal_user.id,
        amount=16000,
        order_name="오징어 1kg 2개",
    )
    db.add(order)
    await db.flush()

    delivery = Delivery(
        order_id=order.id,
        recipient_name="집",
        phone_number="01012341234",
        post_code="04044",
        base_address="서울특별시 마포구 ...",
        detail_address="2층",
    )
    db.add(delivery)
    await db.commit()
    return delivery


@pytest.fixture
async def shipping_delivery(db: AsyncSession, normal_user: User) -> Delivery:
    order = Order(
        user_id=normal_user.id,
        amount=16000,
        order_name="오징어 1kg 2개",
        status=Status.PAID,
    )
    db.add(order)
    await db.flush()

    delivery = Delivery(
        order_id=order.id,
        recipient_name="집",
        phone_number="01012341234",
        post_code="04044",
        base_address="서울특별시 마포구 ...",
        detail_address="2층",
        status=DeliveryStatus.SHIPPING,
    )
    db.add(delivery)
    await db.commit()
    return delivery
