from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Text,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class InventoryTransaction(Base):

    __tablename__ = "inventory_transactions"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # =====================================================
    # Transaction Number
    # =====================================================

    transaction_number = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    # =====================================================
    # Product
    # =====================================================

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    # =====================================================
    # From Warehouse
    # =====================================================
    #
    # For normal inventory transactions:
    #     warehouse_id = affected warehouse
    #
    # For TRANSFER:
    #     warehouse_id = FROM warehouse
    #
    # =====================================================

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True,
    )

    # =====================================================
    # To Warehouse
    # =====================================================
    #
    # Used only for TRANSFER.
    #
    # Example:
    #
    # warehouse_id      = 1  -> Office
    # to_warehouse_id   = 2  -> Main Warehouse
    #
    # =====================================================

    to_warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=True,
        index=True,
    )

    # =====================================================
    # Transaction Type
    # =====================================================
    #
    # Examples:
    #
    # SALE
    # PURCHASE
    # SALES_RETURN
    # PURCHASE_RETURN
    # STOCK_ADJUSTMENT_IN
    # STOCK_ADJUSTMENT_OUT
    # TRANSFER
    #
    # =====================================================

    transaction_type = Column(
        String(30),
        nullable=False,
        index=True,
    )

    # =====================================================
    # Reference Type
    # ===================================================== 

    reference_type = Column(
        String(50),
        nullable=True,
    )

    # =====================================================
    # Reference ID
    # =====================================================

    reference_id = Column(
        Integer, 
        nullable=True,
    )

    # =====================================================
    # Reference By
    # =====================================================
    #
    # Example:
    #
    # Manager
    # Admin
    # Vishnu
    # Purchase Department
    #
    # =====================================================

    reference_by = Column(
        String(255),
        nullable=True,
    )

    # =====================================================
    # Quantity
    # =====================================================

    quantity = Column(
        Numeric(12, 2),
        nullable=False,
    )

    # =====================================================
    # Unit Cost
    # =====================================================

    unit_cost = Column(
        Numeric(12, 2),
        default=0,
    )

    # =====================================================
    # Total Cost
    # =====================================================

    total_cost = Column(
        Numeric(12, 2),
        default=0,
    )

    # =====================================================
    # Remarks
    # =====================================================

    remarks = Column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Created By
    # =====================================================

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    # =====================================================
    # Created At
    # =====================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # =====================================================
    # Relationships
    # =====================================================

    product = relationship(
        "Product",
    )

    # -----------------------------------------------------
    # From Warehouse
    # -----------------------------------------------------

    warehouse = relationship(
        "Warehouse",
        foreign_keys=[warehouse_id],
    )

    # -----------------------------------------------------
    # To Warehouse
    # -----------------------------------------------------

    to_warehouse = relationship(
        "Warehouse",
        foreign_keys=[to_warehouse_id],
    )