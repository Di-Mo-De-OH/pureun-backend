import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.utils.security import hash_password
from app.order.models import Order, OrderItem
from app.products.models import Category, Product, ProductImage, ProductLabel, ProductOption


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
async def normal_user2(db: AsyncSession) -> User:
    user = User(
        email="user2@example.com",
        hashed_password=hash_password("Password@1"),
        name="user2",
        nickname="user2",
    )
    db.add(user)
    await db.commit()
    return user


@pytest.fixture
async def product_1(db: AsyncSession) -> Product:
    product = Product(
        category=Category.SEAFOOD,
        name="오징어",
        supplier_code="SUP001",
    )
    db.add(product)
    await db.flush()

    db.add(
        ProductOption(
            product_id=product.id,
            option_name="1kg",
            price=10000,
            discount_price=8000,
            stock=10,
        )
    )
    db.add(
        ProductImage(
            product_id=product.id,
            image_key="products/test-thumbnail.jpg",
            sort_order=0,
        )
    )
    db.add(
        ProductLabel(
            product_id=product.id,
            item_name="냉동 오징어",
            manufacturer="올바다수산",
            origin="국내산",
            expiration_info="제조일로부터 12개월",
            item_group_notice="수산물 가공식품",
            imported_food_notice="해당사항없음",
            composition="오징어 100%",
            storage_method="냉동보관(-18℃ 이하)",
            safety_caution="해동 후 재냉동 금지",
            customer_service_phone="1577-0000",
        )
    )

    await db.commit()
    await db.refresh(product, attribute_names=["options", "images", "label"])
    return product


@pytest.fixture
async def product_3(db: AsyncSession) -> Product:
    product = Product(
        category=Category.VEGETABLE,
        name="유기농 상추",
        supplier_code="SUP003",
        is_active=False,
    )
    db.add(product)
    await db.flush()

    db.add(
        ProductOption(
            product_id=product.id,
            option_name="1봉지",
            price=3000,
            discount_price=None,
            stock=5,
        )
    )
    db.add(
        ProductImage(
            product_id=product.id,
            image_key="products/test-thumbnail-3.jpg",
            sort_order=0,
        )
    )
    db.add(
        ProductLabel(
            product_id=product.id,
            item_name="냉동 오징어",
            manufacturer="올바다수산",
            origin="국내산",
            expiration_info="제조일로부터 12개월",
            item_group_notice="수산물 가공식품",
            imported_food_notice="해당사항없음",
            composition="오징어 100%",
            storage_method="냉동보관(-18℃ 이하)",
            safety_caution="해동 후 재냉동 금지",
            customer_service_phone="1577-0000",
        )
    )

    await db.commit()
    await db.refresh(product, attribute_names=["options", "images", "label"])
    return product


@pytest.fixture
async def order_1(db: AsyncSession, normal_user: User, product_1: Product) -> Order:
    option = product_1.options[0]
    assert option.discount_price is not None
    order = Order(
        user_id=normal_user.id,
        amount=option.discount_price * 2,
        order_name=f"{product_1.name} {option.option_name} 2개",
    )
    db.add(order)
    await db.flush()

    db.add(
        OrderItem(
            order_id=order.id,
            option_id=option.id,
            option_name=option.option_name,
            price=option.price,
            discount_price=option.discount_price,
            quantity=2,
        )
    )

    await db.commit()
    return order
