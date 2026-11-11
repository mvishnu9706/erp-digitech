from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Delivery Challan Item
# =====================================================

class DeliveryChallanItemBase(BaseModel):

    sales_order_item_id: int

    product_id: int

    delivered_quantity: int = Field(..., gt=0)

    selling_price: Decimal = Field(..., ge=0)

    remarks: Optional[str] = None


class DeliveryChallanItemCreate(DeliveryChallanItemBase):
    pass


class DeliveryChallanItemResponse(DeliveryChallanItemBase):

    id: int

    delivery_challan_id: int

    product_name: str

    sku: Optional[str]

    model_no: Optional[str]

    created_at: datetime

    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Delivery Challan Header
# =====================================================

class DeliveryChallanBase(BaseModel):

    sales_order_id: int

    customer_id: int

    warehouse_id: int

    delivery_date: date

    remarks: Optional[str] = None


# =====================================================
# Create
# =====================================================

class DeliveryChallanCreate(DeliveryChallanBase):

    items: List[DeliveryChallanItemCreate]


# =====================================================
# Update
# =====================================================

class DeliveryChallanUpdate(BaseModel):

    remarks: Optional[str] = None

    status: Optional[str] = None


# =====================================================
# Response
# =====================================================

class DeliveryChallanResponse(DeliveryChallanBase):

    id: int

    dc_number: str

    status: str

    created_by: Optional[int]

    updated_by: Optional[int]

    created_at: datetime

    updated_at: Optional[datetime]

    items: List[DeliveryChallanItemResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Dashboard
# =====================================================

class DeliveryDashboardResponse(BaseModel):

    total_delivery_challans: int

    delivered: int

    cancelled: int