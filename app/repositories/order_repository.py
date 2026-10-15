
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order


class OrderRepository:

    async def create(
        self,
        session: AsyncSession,
        product_id: int,
        quantity: int,
        unit_price: Decimal,
    ) -> Order:
        order = Order(
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=unit_price * quantity,
            status="pending",
        )

        session.add(order)
        await session.flush()
        await session.refresh(order)

        return order
