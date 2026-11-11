from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base


class CustomerPaymentInvoice(Base):
    __tablename__ = "customer_payment_invoices"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_payment_id = Column(
        Integer,
        ForeignKey("customer_payments.id"),
        nullable=False,
        index=True
    )

    sales_invoice_id = Column(
        Integer,
        ForeignKey("sales_invoices.id"),
        nullable=False,
        index=True
    )

    paid_amount = Column(
        Numeric(12,2),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )