from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    Text
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"

    # =====================================
    # Primary Key
    # =====================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================
    # GRN Number
    # =====================================

    grn_number = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    # =====================================
    # Purchase Order
    # =====================================

    purchase_order_id = Column(
        Integer,
        ForeignKey("purchase_orders.id"),
        nullable=False,
        index=True
    )

    # =====================================
    # Supplier
    # =====================================

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True
    )

    # =====================================
    # Warehouse
    # =====================================

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True
    )

    # =====================================
    # Received Date
    # =====================================

    received_date = Column(
        Date,
        nullable=False
    )

    # =====================================
    # Status
    # =====================================

    status = Column(
        String(20),
        nullable=False,
        default="RECEIVED"
    )

    # RECEIVED
    # PARTIAL
    # CANCELLED

    # =====================================
    # Remarks
    # =====================================

    remarks = Column(
        Text,
        nullable=True
    )

    # =====================================
    # Audit
    # =====================================

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

# =====================================
# Relationships
# =====================================

purchase_order = relationship("PurchaseOrder")

supplier = relationship("Supplier")

warehouse = relationship("Warehouse")

items = relationship(
    "GoodsReceiptItem",
    cascade="all, delete-orphan"
)