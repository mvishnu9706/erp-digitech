from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.service_spare_part import (
    ServiceSparePartCreate,
    ServiceSparePartUpdate,
    ServiceSparePartResponse,
    ServiceSparePartListResponse,
    ServiceSparePartDashboardResponse
)

from app.services.service_spare_part_service import (
    ServiceSparePartService
)

from app.core.dependencies import (
    get_current_admin,
    get_current_user
)

router = APIRouter(
    prefix="/service-spare-parts",
    tags=["Service Spare Parts"]
)


# =====================================================
# Create Spare Part
# =====================================================

@router.post(
    "/",
    response_model=ServiceSparePartResponse,
    status_code=status.HTTP_201_CREATED
)
def create_spare_part(
    data: ServiceSparePartCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    return ServiceSparePartService.create_spare_part(
        db,
        data,
        current_user
    )


# =====================================================
# Get Spare Parts
# =====================================================

@router.get(
    "/",
    response_model=ServiceSparePartListResponse
)
def get_spare_parts(

    service_visit_id: int | None = Query(None),

    product_id: int | None = Query(None),

    warehouse_id: int | None = Query(None),

    is_billable: bool | None = Query(None),

    page: int = Query(1, ge=1),

    page_size: int = Query(10, ge=1, le=100),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return ServiceSparePartService.get_spare_parts(

        db=db,

        service_visit_id=service_visit_id,

        product_id=product_id,

        warehouse_id=warehouse_id,

        is_billable=is_billable,

        page=page,

        page_size=page_size

    )


# =====================================================
# Dashboard
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=ServiceSparePartDashboardResponse
)
def dashboard(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return ServiceSparePartService.dashboard(db)


# =====================================================
# Get Spare Part
# =====================================================

@router.get(
    "/{spare_part_id}",
    response_model=ServiceSparePartResponse
)
def get_spare_part(

    spare_part_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return ServiceSparePartService.get_spare_part(

        db,

        spare_part_id

    )


# =====================================================
# Update Spare Part
# =====================================================

@router.put(
    "/{spare_part_id}",
    response_model=ServiceSparePartResponse
)
def update_spare_part(

    spare_part_id: int,

    data: ServiceSparePartUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return ServiceSparePartService.update_spare_part(

        db,

        spare_part_id,

        data,

        current_user

    )


# =====================================================
# Delete Spare Part
# =====================================================

@router.delete("/{spare_part_id}")
def delete_spare_part(

    spare_part_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return ServiceSparePartService.delete_spare_part(

        db,

        spare_part_id

    )