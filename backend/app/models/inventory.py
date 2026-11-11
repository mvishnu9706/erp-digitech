from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    Date,
    DateTime,
    String,
    Text,
    UniqueConstraint
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Inventory(Base):

    __tablename__ = "inventory"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "warehouse_id",
            name="uq_inventory_product_warehouse",
        ),
    )

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
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
    # Warehouse
    # =====================================================

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Rack / Bin
    # =====================================================

    rack_location = Column(
        String(100),
        nullable=True
    )

    # =====================================================
    # Stock
    # =====================================================
    # Only one stock quantity is maintained.
    #
    # Stock changes only when:
    # - Purchase is completed/received
    # - Sale is completed
    # - Stock is transferred
    # - Manual stock adjustment is made
    #
    # There is NO reserved stock and NO available stock.
    # =====================================================

    stock = Column(
        Integer,
        nullable=False,
        default=0
    )

    stock_status = Column(
        String(20),
        nullable=False,
        default="IN_STOCK",
        index=True
    )

    # =====================================================
    # Purchase
    # =====================================================

    last_purchase_price = Column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    last_purchase_date = Column(
        Date,
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

    product = relationship(
        "Product",
        back_populates="inventory",
        lazy="joined"
    )

    warehouse = relationship(
        "Warehouse",
        back_populates="inventory",
        lazy="joined"
    )