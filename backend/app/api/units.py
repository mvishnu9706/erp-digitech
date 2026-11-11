from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.unit import (
    UnitCreate,
    UnitUpdate,
    UnitResponse
)
from app.services.unit_service import UnitService
from app.core.dependencies import (
    get_current_admin,
    get_current_user
)

router = APIRouter(
    prefix="/units",
    tags=["Units"]
)


@router.post(
    "/",
    response_model=UnitResponse,
    status_code=status.HTTP_201_CREATED
)
def create_unit(
    unit: UnitCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    return UnitService.create_unit(
        db,
        unit,
        current_user
    )


@router.get(
    "/",
    response_model=list[UnitResponse]
)
def get_units(
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return UnitService.get_units(
        db,
        search,
        page,
        page_size
    )


@router.get(
    "/{unit_id}",
    response_model=UnitResponse
)
def get_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return UnitService.get_unit(
        db,
        unit_id
    )


@router.put(
    "/{unit_id}",
    response_model=UnitResponse
)
def update_unit(
    unit_id: int,
    unit: UnitUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    return UnitService.update_unit(
        db,
        unit_id,
        unit,
        current_user
    )


@router.delete(
    "/{unit_id}"
)
def delete_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    UnitService.delete_unit(
        db,
        unit_id
    )

    return {
        "success": True,
        "message": "Unit deleted successfully."
    }