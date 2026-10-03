from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.cart.services.read import get_cart, get_cart_image, get_cart_options
from app.cart.utils.redis import CartRedis
from app.core.redis import redis_client
from app.order.models import Order, OrderItem
from app.order.schemas.cart_checkout import (
    OrderCartCheckoutItemResponse,
    OrderCartCheckoutRequest,
    OrderCartCheckoutResponse,
)
from app.products.models import Product, ProductOption


async def get_cart_products(db: AsyncSession, product_ids: list[str]) -> dict[str, str]:
    stmt = select(Product).where(Product.id.in_(product_ids))
    result = await db.execute(stmt)
    return {product.id: product.name for product in result.scalars().all()}


async def cart_checkout(db: AsyncSession, user_id: str, request: OrderCartCheckoutRequest) -> OrderCartCheckoutResponse:
    cart = await get_cart(user_id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="장바구니에 등록된 상품이 없습니다.")
    selected_option_ids = [oid for oid in request.option_ids if oid in cart]
    options = await get_cart_options(db, selected_option_ids)
    product_ids = [option.product_id for option in options.values()]
    images = await get_cart_image(db, product_ids)
    items: list[OrderCartCheckoutItemResponse] = []
    order_items_data: list[tuple[ProductOption, int]] = []
    amount = 0

    for option_id, option in options.items():
        quantity = int(cart[option_id])
        if quantity > option.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"{option.option_name}의 재고가 부족합니다."
            )
        unit_price = option.discount_price if option.discount_price is not None else option.price
        amount += quantity * unit_price
        items.append(
            OrderCartCheckoutItemResponse(
                option_name=option.option_name,
                thumbnail_image_key=images[option.product_id],
                quantity=quantity,
            )
        )
        order_items_data.append((option, quantity))
    if not order_items_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="선택한 상품이 장바구니에 존재하지 않습니다."
        )
    product_names = await get_cart_products(db, product_ids)
    representative_product_id = order_items_data[0][0].product_id
    representative_product_name = product_names[representative_product_id]

    if len(order_items_data) == 1:
        order_name = representative_product_name
    else:
        order_name = f"{representative_product_name} 외 {len(order_items_data) - 1}건"

    order = Order(
        user_id=user_id,
        amount=amount,
        order_name=order_name,
    )
    db.add(order)
    await db.flush()
    order_items = [
        OrderItem(
            order_id=order.id,
            option_id=option.id,
            option_name=option.option_name,
            price=option.price,
            discount_price=option.discount_price,
            quantity=quantity,
        )
        for option, quantity in order_items_data
    ]
    db.add_all(order_items)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="주문 생성에 실패했습니다.")
    await redis_client.hdel(CartRedis.cart(user_id), *selected_option_ids)
    return OrderCartCheckoutResponse(
        order_id=order.id,
        amount=amount,
        order_name=order_name,
        items=items,
    )
