from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.pm_schedule import (
    PMScheduleCreate,
    PMScheduleUpdate,
    PMScheduleResponse,
    PMScheduleListResponse,
    PMScheduleDashboardResponse
)

from app.services.pm_schedule_service import (
    PMScheduleService
)

from app.core.dependencies import (
    get_current_admin,
    get_current_user
)

router = APIRouter(
    prefix="/pm-schedules",
    tags=["Preventive Maintenance"]
)


# =====================================================
# Create PM
# =====================================================

@router.post(
    "/",
    response_model=PMScheduleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_pm(
    data: PMScheduleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    return PMScheduleService.create_pm(
        db,
        data,
        current_user
    )


# =====================================================
# Get PM List
# =====================================================

@router.get(
    "/",
    response_model=PMScheduleListResponse
)
def get_pms(

    search: Optional[str] = Query(None),

    customer_id: Optional[int] = Query(None),

    machine_id: Optional[int] = Query(None),

    engineer_id: Optional[int] = Query(None),

    status: Optional[str] = Query(None),

    page: int = Query(1, ge=1),

    page_size: int = Query(10, ge=1, le=100),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return PMScheduleService.get_pms(

        db=db,

        search=search,

        customer_id=customer_id,

        machine_id=machine_id,

        engineer_id=engineer_id,

        status=status,

        page=page,

        page_size=page_size

    )


# =====================================================
# Dashboard
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=PMScheduleDashboardResponse
)
def dashboard(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return PMScheduleService.dashboard(db)


# =====================================================
# Get PM
# =====================================================

@router.get(
    "/{pm_id}",
    response_model=PMScheduleResponse
)
def get_pm(

    pm_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return PMScheduleService.get_pm(

        db,

        pm_id

    )


# =====================================================
# Update PM
# =====================================================

@router.put(
    "/{pm_id}",
    response_model=PMScheduleResponse
)
def update_pm(

    pm_id: int,

    data: PMScheduleUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return PMScheduleService.update_pm(

        db,

        pm_id,

        data,

        current_user

    )


# =====================================================
# Delete PM
# =====================================================

@router.delete("/{pm_id}")
def delete_pm(

    pm_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return PMScheduleService.delete_pm(

        db,

        pm_id

    )


# =====================================================
# Complete PM
# =====================================================

@router.put(
    "/{pm_id}/complete",
    response_model=PMScheduleResponse
)
def complete_pm(

    pm_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return PMScheduleService.complete_pm(

        db,

        pm_id,

        current_user

    )