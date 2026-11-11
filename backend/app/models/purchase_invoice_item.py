from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    DateTime,
    String,
    Text
)

from sqlalchemy.sql import func

from app.database import Base


class PurchaseInvoiceItem(Base):
    __tablename__ = "purchase_invoice_items"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # Purchase Invoice
    # =====================================================

    purchase_invoice_id = Column(
        Integer,
        ForeignKey("purchase_invoices.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Product
    # =====================================================

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True
    )

    unit_id = Column(
        Integer,
        ForeignKey("units.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Quantity
    # =====================================================

    quantity = Column(
        Integer,
        nullable=False
    )

    # =====================================================
    # Purchase Price
    # =====================================================

    purchase_price = Column(
        Numeric(12, 2),
        nullable=False
    )

    # =====================================================
    # Discount
    # =====================================================

    discount_percentage = Column(
        Numeric(5, 2),
        default=0
    )

    discount_amount = Column(
        Numeric(12, 2),
        default=0
    )

    # =====================================================
    # GST
    # =====================================================

    gst_percentage = Column(
        Numeric(5, 2),
        default=18
    )

    gst_amount = Column(
        Numeric(12, 2),
        default=0
    )

    # =====================================================
    # Line Total
    # =====================================================

    line_total = Column(
        Numeric(12, 2),
        nullable=False
    )

    # =====================================================
    # Product Snapshot
    # =====================================================

    product_name = Column(
        String(200),
        nullable=False
    )

    sku = Column(
        String(100),
        nullable=True
    )

    model_no = Column(
        String(100),
        nullable=True
    )

    hsn_code = Column(
        String(30),
        nullable=True
    )

    serial_number = Column(
        String(200),
        nullable=True
    )

    # =====================================================
    # Remarks
    # =====================================================

    remarks = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # Audit
    # =====================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )