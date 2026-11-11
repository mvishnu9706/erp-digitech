from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Purchase Order Item
# =====================================================

class PurchaseOrderItemBase(BaseModel):
    product_id: int
    warehouse_id: int
    unit_id: int
    quantity: int = Field(..., gt=0)
    purchase_price: Decimal = Field(..., ge=0)
    discount_percentage: Decimal = Field(
        default=0,
        ge=0,
        le=100
    )
    gst_percentage: Decimal = Field(
        default=18,
        ge=0,
        le=100
    )
    # NEW
    hsn_code: Optional[str] = Field(
        default=None,
        max_length=30
    )
    # NEW
    serial_number: Optional[str] = Field(
        default=None,
        max_length=200
    )
    remarks: Optional[str] = None


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass


class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    id: int
    purchase_order_id: int
    received_quantity: int
    pending_quantity: int
    discount_amount: Decimal
    gst_amount: Decimal
    line_total: Decimal
    product_name: Optional[str] = None
    sku: Optional[str] = None
    model_no: Optional[str] = None
    # NEW
    hsn_code: Optional[str] = None
    # NEW
    serial_number: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Purchase Order Header
# =====================================================

class PurchaseOrderBase(BaseModel):
    supplier_id: int
    warehouse_id: int
    po_date: date
    reference_number: Optional[str] = Field(
        default=None,
        max_length=100
    )
    remarks: Optional[str] = None


# =====================================================
# Create
# =====================================================

class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[PurchaseOrderItemCreate]


# =====================================================
# Update
# =====================================================

class PurchaseOrderUpdate(BaseModel):
    supplier_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    po_date: Optional[date] = None
    reference_number: Optional[str] = None
    remarks: Optional[str] = None


# =====================================================
# Response
# =====================================================

class PurchaseOrderResponse(PurchaseOrderBase):
    id: int
    po_number: str
    supplier_name: Optional[str] = None
    warehouse_name: Optional[str] = None
    subtotal: Decimal
    discount_amount: Decimal
    gst_amount: Decimal
    other_charges: Decimal
    grand_total: Decimal
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[PurchaseOrderItemResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Dashboard
# =====================================================

class PurchaseDashboardResponse(BaseModel):
    total_purchases: int
    today_entries: int
    today_purchases: int
    month_entries: int
    month_purchases: int
    total_purchase_value: Decimal
    today_entry_value: Decimal
    today_purchase_value: Decimal


# =====================================================
# Purchase Order List Response
# =====================================================

class PurchaseOrderListResponse(BaseModel):
    total_records: int
    page: int
    page_size: int
    purchase_orders: List[PurchaseOrderResponse]