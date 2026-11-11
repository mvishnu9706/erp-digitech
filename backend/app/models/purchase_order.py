from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    Date,
    DateTime,
    String,
    Text,
    Boolean
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # Purchase Order Number & References
    # =====================================================

    po_number = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    reference_number = Column(
        String(100),
        nullable=True
    )

    # =====================================================
    # Supplier
    # =====================================================

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Warehouse
    # =====================================================

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Dates
    # =====================================================

    po_date = Column(
        Date,
        nullable=False
    )

    # =====================================================
    # Status
    # =====================================================

    status = Column(
        String(30),
        nullable=False,
        default="PURCHASED",
        index=True
    )

    # Allowed values:
    # PURCHASED
    # CANCELLED

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    # =====================================================
    # Financials
    # =====================================================

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

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
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

    # =====================================================
    # Relationships
    # =====================================================

    supplier = relationship(
        "Supplier",
        lazy="joined"
    )
    
    warehouse = relationship(
        "Warehouse",
        lazy="joined"
    )

    items = relationship(
        "PurchaseOrderItem",
        back_populates="purchase_order",
        cascade="all, delete-orphan",
        lazy="selectin"
    )