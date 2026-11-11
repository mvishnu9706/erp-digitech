from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.service_visit import (
    ServiceVisitCreate,
    ServiceVisitUpdate,
    ServiceVisitResponse,
    ServiceVisitListResponse,
    ServiceVisitDashboardResponse
)

from app.services.service_visit_service import (
    ServiceVisitService
)

from app.core.dependencies import (
    get_current_admin,
    get_current_user
)

router = APIRouter(
    prefix="/service-visits",
    tags=["Service Visits"]
)


# =====================================================
# Create Service Visit
# =====================================================

@router.post(
    "/",
    response_model=ServiceVisitResponse,
    status_code=status.HTTP_201_CREATED
)
def create_service_visit(
    data: ServiceVisitCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    return ServiceVisitService.create_service_visit(
        db,
        data,
        current_user
    )


# =====================================================
# Get Service Visits
# =====================================================

@router.get(
    "/",
    response_model=ServiceVisitListResponse
)
def get_service_visits(

    search: Optional[str] = Query(None),

    ticket_id: Optional[int] = Query(None),

    machine_id: Optional[int] = Query(None),

    customer_id: Optional[int] = Query(None),

    engineer_id: Optional[int] = Query(None),

    status: Optional[str] = Query(None),

    page: int = Query(1, ge=1),

    page_size: int = Query(10, ge=1, le=100),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return ServiceVisitService.get_service_visits(

        db=db,

        search=search,

        ticket_id=ticket_id,

        machine_id=machine_id,

        customer_id=customer_id,

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
    response_model=ServiceVisitDashboardResponse
)
def dashboard(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return ServiceVisitService.dashboard(db)


# =====================================================
# Get Service Visit
# =====================================================

@router.get(
    "/{visit_id}",
    response_model=ServiceVisitResponse
)
def get_service_visit(

    visit_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return ServiceVisitService.get_service_visit(

        db,

        visit_id

    )


# =====================================================
# Update Service Visit
# =====================================================

@router.put(
    "/{visit_id}",
    response_model=ServiceVisitResponse
)
def update_service_visit(

    visit_id: int,

    data: ServiceVisitUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return ServiceVisitService.update_service_visit(

        db,

        visit_id,

        data,

        current_user

    )


# =====================================================
# Delete Service Visit
# =====================================================

@router.delete("/{visit_id}")
def delete_service_visit(

    visit_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return ServiceVisitService.delete_service_visit(

        db,

        visit_id

    )


# =====================================================
# Start Visit
# =====================================================

@router.put(
    "/{visit_id}/start",
    response_model=ServiceVisitResponse
)
def start_visit(

    visit_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return ServiceVisitService.start_visit(

        db,

        visit_id,

        current_user

    )


# =====================================================
# Complete Visit
# =====================================================

@router.put(
    "/{visit_id}/complete",
    response_model=ServiceVisitResponse
)
def complete_visit(

    visit_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return ServiceVisitService.complete_visit(

        db,

        visit_id,

        current_user

    )