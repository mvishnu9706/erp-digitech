from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base


class SupplierPaymentInvoice(Base):
    __tablename__ = "supplier_payment_invoices"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    supplier_payment_id = Column(
        Integer,
        ForeignKey("supplier_payments.id"),
        nullable=False,
        index=True
    )

    purchase_invoice_id = Column(
        Integer,
        ForeignKey("purchase_invoices.id"),
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