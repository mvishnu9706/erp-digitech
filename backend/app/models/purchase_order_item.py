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
from sqlalchemy.orm import relationship

from app.database import Base


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # Purchase Order
    # =====================================================

    purchase_order_id = Column(
        Integer,
        ForeignKey("purchase_orders.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Product & Snapshot Details
    # =====================================================

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    product_name = Column(
        String(200),
        nullable=False
    )
    
    sku = Column(
        String(100),
        nullable=True
    )

    # =====================================================
    # Warehouse & Snapshot Details
    # =====================================================

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True
    )

    warehouse_name = Column(
        String(200),
        nullable=True
    )

    # =====================================================
    # Unit & Snapshot Details
    # =====================================================

    unit_id = Column(
        Integer,
        ForeignKey("units.id"),
        nullable=False,
        index=True
    )

    unit_name = Column(
        String(100),
        nullable=True
    )

    # =====================================================
    # Ordered Quantity
    # =====================================================

    quantity = Column(
        Integer,
        nullable=False
    )

    # =====================================================
    # Goods Received
    # =====================================================

    received_quantity = Column(
        Integer,
        nullable=False,
        default=0
    )

    pending_quantity = Column(
        Integer,
        nullable=False
    )

    # =====================================================
    # Pricing
    # =====================================================

    purchase_price = Column(
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
    
    purchase_order = relationship(
        "PurchaseOrder",
        back_populates="items",
        lazy="joined"
    )
    
    product = relationship(
        "Product",
        lazy="joined"
    )
    
    warehouse = relationship(
        "Warehouse",
        lazy="joined"
    )
    
    unit = relationship(
        "Unit",
        lazy="joined"
    )