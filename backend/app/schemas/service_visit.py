from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Base
# =====================================================

class ServiceVisitBase(BaseModel):

    ticket_id: int

    machine_id: int

    customer_id: int

    engineer_id: int

    visit_date: date

    start_time: Optional[datetime] = None

    end_time: Optional[datetime] = None

    previous_meter: int = 0

    current_meter: int = 0

    work_done: Optional[str] = Field(
        None,
        max_length=5000
    )

    problem_found: Optional[str] = Field(
        None,
        max_length=5000
    )

    solution: Optional[str] = Field(
        None,
        max_length=5000
    )

    recommendations: Optional[str] = Field(
        None,
        max_length=5000
    )

    customer_name: Optional[str] = Field(
        None,
        max_length=100
    )

    signature_path: Optional[str] = None

    status: str = "OPEN"

    remarks: Optional[str] = None

    is_active: bool = True


# =====================================================
# Create
# =====================================================

class ServiceVisitCreate(ServiceVisitBase):
    pass


# =====================================================
# Update
# =====================================================

class ServiceVisitUpdate(BaseModel):

    engineer_id: Optional[int] = None

    visit_date: Optional[date] = None

    start_time: Optional[datetime] = None

    end_time: Optional[datetime] = None

    previous_meter: Optional[int] = None

    current_meter: Optional[int] = None

    work_done: Optional[str] = None

    problem_found: Optional[str] = None

    solution: Optional[str] = None

    recommendations: Optional[str] = None

    customer_name: Optional[str] = None

    signature_path: Optional[str] = None

    status: Optional[str] = None

    remarks: Optional[str] = None

    is_active: Optional[bool] = None
    # =====================================================
# Response
# =====================================================

class ServiceVisitResponse(ServiceVisitBase):

    id: int

    visit_number: str

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

class ServiceVisitListResponse(BaseModel):

    total: int

    page: int

    page_size: int

    items: list[ServiceVisitResponse]


# =====================================================
# Dashboard Response
# =====================================================

class ServiceVisitDashboardResponse(BaseModel):

    total_visits: int

    open_visits: int

    completed_visits: int

    cancelled_visits: int

    today_visits: int

    pending_visits: int


# =====================================================
# Filter
# =====================================================

class ServiceVisitFilter(BaseModel):

    ticket_id: Optional[int] = None

    machine_id: Optional[int] = None

    customer_id: Optional[int] = None

    engineer_id: Optional[int] = None

    status: Optional[str] = None

    visit_number: Optional[str] = None

    from_date: Optional[date] = None

    to_date: Optional[date] = None