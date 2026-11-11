from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# =====================================================
# Product Response
# =====================================================

class InventoryProductResponse(BaseModel):

    id: int

    product_name: str

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Warehouse Response
# =====================================================

class InventoryWarehouseResponse(BaseModel):

    id: int

    warehouse_name: str

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Base Schema
# =====================================================

class InventoryBase(BaseModel):

    product_id: int

    warehouse_id: int

    rack_location: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    # =================================================
    # Actual Physical Stock
    # =================================================
    #
    # Only actual stock is maintained.
    #
    # There is NO:
    #
    # - current_stock
    # - reserved_stock
    # - available_stock
    #
    # Stock changes only after a completed movement.
    # =================================================

    stock: int = Field(
        default=0,
        ge=0,
    )

    stock_status: str = Field(
        default="IN_STOCK",
    )

    last_purchase_price: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )

    last_purchase_date: Optional[date] = None

    remarks: Optional[str] = None


# =====================================================
# Create Inventory
# =====================================================

class InventoryCreate(
    InventoryBase
):
    pass


# =====================================================
# Update Inventory
# =====================================================

class InventoryUpdate(BaseModel):

    rack_location: Optional[str] = None

    stock: Optional[int] = Field(
        default=None,
        ge=0,
    )

    stock_status: Optional[str] = None

    last_purchase_price: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    last_purchase_date: Optional[date] = None

    remarks: Optional[str] = None


# =====================================================
# Stock Transfer
# =====================================================
#
# ONE transfer request.
#
# From warehouse stock decreases.
# To warehouse stock increases.
#
# ONE TRANSFER transaction is stored in
# inventory_transactions.
#
# =====================================================

class StockTransfer(BaseModel):

    # =================================================
    # Product
    # =================================================

    product_id: int

    # =================================================
    # From Warehouse
    # =================================================

    from_warehouse_id: int

    # =================================================
    # To Warehouse
    # =================================================

    to_warehouse_id: int

    # =================================================
    # Quantity
    # =================================================

    quantity: int = Field(
        ...,
        gt=0,
    )

    # =================================================
    # Reference By
    # =================================================

    reference_by: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    # =================================================
    # Remarks
    # =================================================

    remarks: Optional[str] = Field(
        default=None,
    )


# =====================================================
# Inventory Response
# =====================================================

class InventoryResponse(BaseModel):

    id: int

    product: InventoryProductResponse

    warehouse: InventoryWarehouseResponse

    rack_location: Optional[str]

    # =================================================
    # Actual Stock
    # =================================================

    stock: int

    stock_status: str

    last_purchase_price: Decimal

    last_purchase_date: Optional[date]

    remarks: Optional[str]

    # =================================================
    # Audit User
    # =================================================

    created_by: Optional[int]

    updated_by: Optional[int]

    # =================================================
    # Dates
    # =================================================

    created_at: datetime

    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )