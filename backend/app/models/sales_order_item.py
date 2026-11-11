from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    DateTime,
    String,
    Text,
    text,
)

from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class SalesOrderItem(Base):

    __tablename__ = "sales_order_items"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # Sales Order
    # =====================================================

    sales_order_id = Column(
        Integer,
        ForeignKey("sales_orders.id"),
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

    # =====================================================
    # Quantity
    # =====================================================
    #
    # quantity
    #   = Total quantity sold in this sales order.
    #
    # delivered_quantity
    #   = Quantity already delivered.
    #
    # pending_quantity
    #   = Quantity still pending for delivery.
    #
    # There is NO reserved quantity anymore.
    # Inventory reservation is not used.
    #
    # Inventory stock is deducted when the sale is
    # successfully committed.
    # =====================================================

    quantity = Column(
        Integer,
        nullable=False
    )

    delivered_quantity = Column(
        Integer,
        nullable=False,
        default=0
    )

    pending_quantity = Column(
        Integer,
        nullable=False,
        default=0
    )

    # =====================================================
    # Pricing
    # =====================================================

    selling_price = Column(
        Numeric(12, 2),
        nullable=False
    )

    discount_percentage = Column(
        Numeric(5, 2),
        default=0
    )

    discount_amount = Column(
        Numeric(12, 2),
        default=0
    )

    gst_percentage = Column(
        Numeric(5, 2),
        default=18
    )

    gst_amount = Column(
        Numeric(12, 2),
        default=0
    )

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

    # =====================================================
    # Serial Numbers
    #
    # PostgreSQL JSONB array
    #
    # Example:
    # ["SN001", "SN002", "SN003"]
    # =====================================================

    serial_numbers = Column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb")
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

    # =====================================================
    # Relationships
    # =====================================================

    sales_order = relationship(
        "SalesOrder",
        back_populates="items"
    )

    product = relationship(
        "Product",
        foreign_keys=[product_id]
    )