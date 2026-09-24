from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.pagination import CursorPage, CursorPageParams, paginate_by_cursor
from app.order.models import Order, OrderItem, Status
from app.order.schemas.read import OrderReadListItemResponse, OrderReadListResponse
from app.products.models import ProductImage, ProductOption


async def get_order_list(
    db: AsyncSession,
    user_id: str,
    params: CursorPageParams,
) -> CursorPage[OrderReadListResponse]:
    stmt = select(Order).where(Order.user_id == user_id, Order.status == Status.PAID)
    orders, next_cursor = await paginate_by_cursor(db, stmt, Order.id, params)
    if not orders:
        return CursorPage(items=[], next_cursor=None)

    order_ids = [order.id for order in orders]
    order_items_stmt = select(OrderItem).where(OrderItem.order_id.in_(order_ids))
    order_items_results = await db.execute(order_items_stmt)
    order_items = order_items_results.scalars().all()

    option_ids = [item.option_id for item in order_items]
    option_stmt = select(ProductOption).where(ProductOption.id.in_(option_ids))
    option_results = await db.execute(option_stmt)
    options = option_results.scalars().all()

    product_ids = [option.product_id for option in options]
    images_stmt = select(ProductImage).where(ProductImage.product_id.in_(product_ids), ProductImage.sort_order == 0)
    images_results = await db.execute(images_stmt)
    images = images_results.scalars().all()

    options_dict = {option.id: option for option in options}
    images_dict = {image.product_id: image.image_key for image in images}
    order_items_dict: defaultdict[str, list[OrderItem]] = defaultdict(list)
    for item in order_items:
        order_items_dict[item.order_id].append(item)
    result_items: list[OrderReadListResponse] = []

    for order in orders:
        items: list[OrderReadListItemResponse] = []
        for item in order_items_dict.get(order.id, []):
            option = options_dict.get(item.option_id)
            thumbnail = images_dict.get(option.product_id, "") if option else ""

            items.append(
                OrderReadListItemResponse(
                    option_name=item.option_name,
                    thumbnail_image_key=thumbnail,
                    quantity=item.quantity,
                )
            )
        result_items.append(
            OrderReadListResponse(
                order_id=order.id,
                order_name=order.order_name,
                amount=order.amount,
                created_at=order.created_at,
                items=items,
            )
        )
    return CursorPage(items=result_items, next_cursor=next_cursor)
