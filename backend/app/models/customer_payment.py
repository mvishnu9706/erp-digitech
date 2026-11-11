from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    Date,
    DateTime,
    String,
    Text
)

from sqlalchemy.sql import func

from app.database import Base


class CustomerPayment(Base):
    __tablename__ = "customer_payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    payment_number = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    payment_date = Column(
        Date,
        nullable=False
    )

    payment_mode = Column(
        String(30),
        nullable=False
    )

    reference_number = Column(
        String(100),
        nullable=True
    )

    amount = Column(
        Numeric(12,2),
        nullable=False
    )

    remarks = Column(
        Text,
        nullable=True
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id")
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id")
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )