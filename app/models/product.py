
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="ck_products_price_nonnegative",
        ),
        CheckConstraint(
            "stock >= 0",
            name="ck_products_stock_nonnegative",
        ),
        Index("ix_products_name", "name"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
