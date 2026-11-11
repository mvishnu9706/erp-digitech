from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# =====================================================
# Base
# =====================================================

class InventoryTransactionBase(BaseModel):

    product_id: int

    # =================================================
    # Warehouse
    # =================================================
    #
    # For TRANSFER:
    #
    # warehouse_id = FROM warehouse
    #
    # =================================================

    warehouse_id: int

    # =================================================
    # To Warehouse
    # =================================================
    #
    # Used only for TRANSFER.
    #
    # =================================================

    to_warehouse_id: Optional[int] = None

    # =================================================
    # Transaction Type
    # =================================================

    transaction_type: str

    # =================================================
    # Reference
    # =================================================

    reference_type: Optional[str] = None

    reference_id: Optional[int] = None

    reference_by: Optional[str] = None

    # =================================================
    # Quantity
    # =================================================

    quantity: Decimal = Field(
        ...,
        gt=0,
    )

    # =================================================
    # Cost
    # =================================================

    unit_cost: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )

    total_cost: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )

    # =================================================
    # Remarks
    # =================================================

    remarks: Optional[str] = None


# =====================================================
# Create
# =====================================================

class InventoryTransactionCreate(
    InventoryTransactionBase
):
    pass


# =====================================================
# Update
# =====================================================

class InventoryTransactionUpdate(BaseModel):

    # -------------------------------------------------
    # Warehouse is NOT allowed to be changed after
    # transaction creation.
    # -------------------------------------------------

    warehouse_id: Optional[int] = None

    # -------------------------------------------------
    # Destination warehouse
    # -------------------------------------------------

    to_warehouse_id: Optional[int] = None

    # -------------------------------------------------
    # Quantity
    # -------------------------------------------------

    quantity: Optional[Decimal] = Field(
        default=None,
        gt=0,
    )

    # -------------------------------------------------
    # Cost
    # -------------------------------------------------

    unit_cost: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    total_cost: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    # -------------------------------------------------
    # Reference By
    # -------------------------------------------------

    reference_by: Optional[str] = None

    # -------------------------------------------------
    # Remarks
    # -------------------------------------------------

    remarks: Optional[str] = None


# =====================================================
# Normal Transaction Response
# =====================================================

class InventoryTransactionResponse(
    InventoryTransactionBase
):

    id: int

    transaction_number: str

    created_by: Optional[int] = None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Normal Transaction List Response
# =====================================================

class InventoryTransactionListResponse(
    BaseModel
):

    total: int

    page: int

    page_size: int

    items: list[
        InventoryTransactionResponse
    ]


# =====================================================
# Stock Transfer History Response
# =====================================================
#
# ONE database row = ONE stock transfer.
#
# Example:
#
#     transaction_type = TRANSFER
#
#     warehouse_id    = 1
#     to_warehouse_id = 2
#
#     quantity        = 10
#
# =====================================================

class StockTransferHistoryResponse(
    BaseModel
):

    id: int

    # =================================================
    # Transfer Number
    # =================================================

    transaction_number: str

    # =================================================
    # Product
    # =================================================

    product_id: int

    product_name: Optional[str] = None

    # =================================================
    # From Warehouse
    # =================================================

    from_warehouse_id: Optional[int] = None

    from_warehouse: Optional[str] = None

    # =================================================
    # To Warehouse
    # =================================================

    to_warehouse_id: Optional[int] = None

    to_warehouse: Optional[str] = None

    # =================================================
    # Transaction Type
    # =================================================

    transaction_type: str

    # =================================================
    # Reference
    # =================================================

    reference_type: Optional[str] = None

    reference_id: Optional[int] = None

    reference_by: Optional[str] = None

    # =================================================
    # Quantity
    # =================================================

    quantity: Decimal = Field(
        ...,
        gt=0,
    )

    # =================================================
    # Cost
    # =================================================

    unit_cost: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )

    total_cost: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )

    # =================================================
    # Remarks
    # =================================================

    remarks: Optional[str] = None

    # =================================================
    # Created By
    # =================================================

    created_by: Optional[int] = None

    # =================================================
    # Created At
    # =================================================

    created_at: datetime

    # =================================================
    # Activity
    # =================================================
    #
    # Currently every stored transfer is CREATED.
    #
    # We are NOT implementing separate:
    #     UPDATED
    #     DELETED
    #
    # history records.
    #
    # =================================================

    activity: str = "Created"

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Stock Transfer History List Response
# =====================================================

class StockTransferHistoryListResponse(
    BaseModel
):

    total: int

    page: int

    page_size: int

    items: list[
        StockTransferHistoryResponse
    ]


# =====================================================
# Dashboard
# =====================================================

class InventoryTransactionDashboardResponse(
    BaseModel
):

    total_transactions: int

    total_stock_in: Decimal

    total_stock_out: Decimal

    total_stock_value: Decimal


# =====================================================
# Filter
# =====================================================

class InventoryTransactionFilter(
    BaseModel
):

    product_id: Optional[int] = None

    warehouse_id: Optional[int] = None

    transaction_type: Optional[str] = None

    reference_type: Optional[str] = None

    reference_by: Optional[str] = None

    # =================================================
    # Transfer Warehouses
    # =================================================

    from_warehouse_id: Optional[int] = None

    to_warehouse_id: Optional[int] = None

    # =================================================
    # Dates
    # =================================================

    from_date: Optional[datetime] = None

    to_date: Optional[datetime] = None

    # =================================================
    # Activity
    # =================================================
    #
    # Kept for frontend filtering compatibility.
    #
    # Current supported value:
    #     CREATED
    #
    # =================================================

    activity: Optional[str] = None