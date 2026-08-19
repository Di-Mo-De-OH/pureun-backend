import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.utils.security import hash_password
from app.products.models import Category, Product, ProductImage, ProductOption


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

    await db.commit()
    return product


@pytest.fixture
async def product_2(db: AsyncSession) -> Product:
    product = Product(
        category=Category.FRUIT,
        name="제주 감귤",
        supplier_code="SUP002",
    )
    db.add(product)
    await db.flush()

    db.add(
        ProductOption(
            product_id=product.id,
            option_name="3kg",
            price=15000,
            discount_price=None,
            stock=20,
        )
    )
    db.add(
        ProductImage(
            product_id=product.id,
            image_key="products/test-thumbnail-2.jpg",
            sort_order=0,
        )
    )

    await db.commit()
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

    await db.commit()
    return product
