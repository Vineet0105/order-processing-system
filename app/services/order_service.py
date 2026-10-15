
import hashlib
import json

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idempotency import IdempotencyRecord
from app.models.product import Product
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderResponse


class OrderService:

    def __init__(self):
        self.repository = OrderRepository()

    async def create_order(
        self,
        session: AsyncSession,
        data: OrderCreate,
        idempotency_key: str,
    ) -> dict:
        scope = "orders:create"

        # Generate a stable hash of the validated request body.
        canonical_request = json.dumps(
            data.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
        request_hash = hashlib.sha256(
            canonical_request.encode("utf-8")
        ).hexdigest()

        async with session.begin():

            # Atomically claim this idempotency key.
            claim_stmt = (
                pg_insert(IdempotencyRecord)
                .values(
                    scope=scope,
                    key=idempotency_key,
                    request_hash=request_hash,
                    status="processing",
                )
                .on_conflict_do_nothing(
                    index_elements=[
                        IdempotencyRecord.scope,
                        IdempotencyRecord.key,
                    ]
                )
                .returning(IdempotencyRecord.id)
            )

            claim_result = await session.execute(claim_stmt)
            claimed_id = claim_result.scalar_one_or_none()

            # Another request already owns this key.
            if claimed_id is None:
                existing = await session.scalar(
                    select(IdempotencyRecord).where(
                        IdempotencyRecord.scope == scope,
                        IdempotencyRecord.key == idempotency_key,
                    )
                )

                if existing is None:
                    raise HTTPException(
                        status_code=503,
                        detail="Could not resolve idempotency record",
                    )

                if existing.request_hash != request_hash:
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "Idempotency key was already used "
                            "with a different request"
                        ),
                    )

                if existing.status != "completed":
                    raise HTTPException(
                        status_code=409,
                        detail="Request is not yet completed",
                    )

                if existing.response_body is None:
                    raise HTTPException(
                        status_code=500,
                        detail="Stored response is unavailable",
                    )

                # Replay the original successful response.
                return existing.response_body

            record = await session.get(
                IdempotencyRecord,
                claimed_id,
            )

            # Atomically reserve inventory and obtain its price.
            stock_stmt = (
                update(Product)
                .where(
                    Product.id == data.product_id,
                    Product.stock >= data.quantity,
                )
                .values(
                    stock=Product.stock - data.quantity,
                )
                .returning(Product.price)
            )

            stock_result = await session.execute(stock_stmt)
            unit_price = stock_result.scalar_one_or_none()

            if unit_price is None:
                product_exists = await session.scalar(
                    select(Product.id).where(
                        Product.id == data.product_id
                    )
                )

                if product_exists is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Product not found",
                    )

                raise HTTPException(
                    status_code=409,
                    detail="Insufficient stock",
                )

            order = await self.repository.create(
                session=session,
                product_id=data.product_id,
                quantity=data.quantity,
                unit_price=unit_price,
            )

            # Convert the ORM object into JSON-compatible data.
            response_body = OrderResponse.model_validate(
                order
            ).model_dump(mode="json")

            # Store the result in the same transaction as the order.
            record.order_id = order.id
            record.status = "completed"
            record.response_status = 201
            record.response_body = response_body

            await session.flush()

        # The transaction has committed successfully.
        return response_body
