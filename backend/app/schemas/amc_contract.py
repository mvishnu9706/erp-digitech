from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Base
# =====================================================

class AMCContractBase(BaseModel):

    customer_id: int

    machine_id: int

    contract_type: str = "AMC"

    start_date: date

    end_date: date

    amount: Decimal = Decimal("0.00")

    gst_percentage: Decimal = Decimal("18.00")

    free_black_copies: int = 0

    free_color_copies: int = 0

    black_cost_per_copy: Decimal = Decimal("0.0000")

    color_cost_per_copy: Decimal = Decimal("0.0000")

    included_service_visits: int = 12

    used_service_visits: int = 0

    auto_renew: bool = False

    renewal_reminder_days: int = 30

    status: str = "ACTIVE"

    remarks: Optional[str] = None


# =====================================================
# Create
# =====================================================

class AMCContractCreate(AMCContractBase):
    pass


# =====================================================
# Update
# =====================================================

class AMCContractUpdate(BaseModel):

    contract_type: Optional[str] = None

    start_date: Optional[date] = None

    end_date: Optional[date] = None

    amount: Optional[Decimal] = None

    gst_percentage: Optional[Decimal] = None

    free_black_copies: Optional[int] = None

    free_color_copies: Optional[int] = None

    black_cost_per_copy: Optional[Decimal] = None

    color_cost_per_copy: Optional[Decimal] = None

    included_service_visits: Optional[int] = None

    used_service_visits: Optional[int] = None

    auto_renew: Optional[bool] = None

    renewal_reminder_days: Optional[int] = None

    status: Optional[str] = None

    remarks: Optional[str] = None


# =====================================================
# Response
# =====================================================

class AMCContractResponse(AMCContractBase):

    id: int

    contract_number: str

    created_by: int

    updated_by: Optional[int]

    created_at: datetime

    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# List Response
# =====================================================

class AMCContractListResponse(BaseModel):

    total: int

    page: int

    page_size: int

    items: list[AMCContractResponse]


# =====================================================
# Dashboard
# =====================================================

class AMCContractDashboardResponse(BaseModel):

    total_contracts: int

    active_contracts: int

    expired_contracts: int

    expiring_this_month: int

    renewal_due: int


# =====================================================
# Filter
# =====================================================

class AMCContractFilter(BaseModel):

    customer_id: Optional[int] = None

    machine_id: Optional[int] = None

    contract_type: Optional[str] = None

    status: Optional[str] = None

    from_date: Optional[date] = None

    to_date: Optional[date] = None