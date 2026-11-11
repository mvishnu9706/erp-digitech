from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Base
# =====================================================

class ServiceSparePartBase(BaseModel):

    service_visit_id: int

    product_id: int

    warehouse_id: int

    quantity: Decimal = Field(..., gt=0)

    unit_price: Decimal = Decimal("0.00")

    total_price: Decimal = Decimal("0.00")

    is_billable: bool = True

    remarks: Optional[str] = None


# =====================================================
# Create
# =====================================================

class ServiceSparePartCreate(ServiceSparePartBase):
    pass


# =====================================================
# Update
# =====================================================

class ServiceSparePartUpdate(BaseModel):

    product_id: Optional[int] = None

    warehouse_id: Optional[int] = None

    quantity: Optional[Decimal] = None

    unit_price: Optional[Decimal] = None

    total_price: Optional[Decimal] = None

    is_billable: Optional[bool] = None

    remarks: Optional[str] = None


# =====================================================
# Response
# =====================================================

class ServiceSparePartResponse(ServiceSparePartBase):

    id: int

    created_by: int

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# List Response
# =====================================================

class ServiceSparePartListResponse(BaseModel):

    total: int

    page: int

    page_size: int

    items: list[ServiceSparePartResponse]


# =====================================================
# Dashboard
# =====================================================

class ServiceSparePartDashboardResponse(BaseModel):

    total_parts_used: int

    total_quantity: Decimal

    total_cost: Decimal

    billable_parts: int

    warranty_parts: int


# =====================================================
# Filter
# =====================================================

class ServiceSparePartFilter(BaseModel):

    service_visit_id: Optional[int] = None

    product_id: Optional[int] = None

    warehouse_id: Optional[int] = None

    is_billable: Optional[bool] = None