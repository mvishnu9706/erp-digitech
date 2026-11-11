from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# =====================================================
# Base
# =====================================================

class PMScheduleBase(BaseModel):

    amc_contract_id: int

    customer_id: int

    machine_id: int

    engineer_id: Optional[int] = None

    scheduled_date: date

    completed_date: Optional[date] = None

    frequency_days: int = 90

    status: str = "PENDING"

    auto_generated: bool = True

    remarks: Optional[str] = None


# =====================================================
# Create
# =====================================================

class PMScheduleCreate(PMScheduleBase):
    pass


# =====================================================
# Update
# =====================================================

class PMScheduleUpdate(BaseModel):

    engineer_id: Optional[int] = None

    scheduled_date: Optional[date] = None

    completed_date: Optional[date] = None

    frequency_days: Optional[int] = None

    status: Optional[str] = None

    auto_generated: Optional[bool] = None

    remarks: Optional[str] = None


# =====================================================
# Response
# =====================================================

class PMScheduleResponse(PMScheduleBase):

    id: int

    pm_number: str

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

class PMScheduleListResponse(BaseModel):

    total: int

    page: int

    page_size: int

    items: list[PMScheduleResponse]


# =====================================================
# Dashboard
# =====================================================

class PMScheduleDashboardResponse(BaseModel):

    total_pm: int

    pending_pm: int

    completed_pm: int

    overdue_pm: int

    today_pm: int


# =====================================================
# Filter
# =====================================================

class PMScheduleFilter(BaseModel):

    customer_id: Optional[int] = None

    machine_id: Optional[int] = None

    engineer_id: Optional[int] = None

    status: Optional[str] = None

    scheduled_from: Optional[date] = None

    scheduled_to: Optional[date] = None