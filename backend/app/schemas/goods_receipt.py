from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Goods Receipt Item
# =====================================================

class GoodsReceiptItemBase(BaseModel):

    purchase_order_item_id: int

    product_id: int

    received_quantity: int = Field(..., gt=0)

    purchase_price: Decimal = Field(..., ge=0)

    remarks: Optional[str] = None


class GoodsReceiptItemCreate(GoodsReceiptItemBase):
    pass


class GoodsReceiptItemResponse(GoodsReceiptItemBase):

    id: int

    goods_receipt_id: int

    created_at: datetime

    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Goods Receipt Header
# =====================================================

class GoodsReceiptBase(BaseModel):

    purchase_order_id: int

    supplier_id: int

    warehouse_id: int

    received_date: date

    remarks: Optional[str] = None


# =====================================================
# Create
# =====================================================

class GoodsReceiptCreate(GoodsReceiptBase):

    items: List[GoodsReceiptItemCreate]


# =====================================================
# Update
# =====================================================

class GoodsReceiptUpdate(BaseModel):

    remarks: Optional[str] = None

    status: Optional[str] = None


# =====================================================
# Response
# =====================================================

class GoodsReceiptResponse(GoodsReceiptBase):

    id: int

    grn_number: str

    status: str

    created_by: Optional[int]

    updated_by: Optional[int]

    created_at: datetime

    updated_at: Optional[datetime]

    items: List[GoodsReceiptItemResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Dashboard
# =====================================================

class GoodsReceiptDashboardResponse(BaseModel):

    total_goods_receipts: int

    received_today: int

    total_received_quantity: int