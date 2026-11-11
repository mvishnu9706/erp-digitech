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


class SalesInvoice(Base):
    __tablename__ = "sales_invoices"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # Invoice Number
    # =====================================================

    invoice_number = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    # =====================================================
    # References
    # =====================================================

    sales_order_id = Column(
        Integer,
        ForeignKey("sales_orders.id"),
        nullable=False,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Dates
    # =====================================================

    invoice_date = Column(
        Date,
        nullable=False
    )

    due_date = Column(
        Date,
        nullable=True
    )

    # =====================================================
    # Status
    # =====================================================

    status = Column(
        String(30),
        nullable=False,
        default="DRAFT",
        index=True
    )

    # UNPAID
    # PARTIALLY_PAID
    # PAID
    # CANCELLED

    # =====================================================
    # Amounts
    # =====================================================

    # =====================================================
    # Payment Status
    # =====================================================

    payment_status = Column(
        String(30),
        nullable=False,
        default="UNPAID",
        index=True
    )

    subtotal = Column(
        Numeric(12, 2),
        default=0
    )

    discount_amount = Column(
        Numeric(12, 2),
        default=0
    )

    gst_amount = Column(
        Numeric(12, 2),
        default=0
    )

    other_charges = Column(
        Numeric(12, 2),
        default=0
    )

    grand_total = Column(
        Numeric(12, 2),
        default=0
    )

    paid_amount = Column(
        Numeric(12, 2),
        default=0
    )

    balance_amount = Column(
        Numeric(12, 2),
        default=0
    )

    remarks = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # Audit
    # =====================================================

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