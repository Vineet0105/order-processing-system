from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    __table_args__ = (
        UniqueConstraint(
            "scope",
            "key",
            name="uq_idempotency_scope_key",
        ),
        CheckConstraint(
            "status IN ('processing', 'completed', 'failed')",
            name="ck_idempotency_status",
        ),
        Index("ix_idempotency_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    scope: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    request_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="processing",
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id"),
        nullable=True,
    )
    response_status: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    response_body: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
