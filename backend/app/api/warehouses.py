from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseResponse
)

from app.services.warehouse_service import WarehouseService

from app.core.dependencies import (
    get_current_admin,
    get_current_user
)

router = APIRouter(
    prefix="/warehouses",
    tags=["Warehouses"]
)


# =====================================================
# Create Warehouse
# =====================================================

@router.post(
    "/",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Warehouse"
)
def create_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    return WarehouseService.create_warehouse(
        db=db,
        data=warehouse,
        current_user=current_user
    )


# =====================================================
# Get All Warehouses
# =====================================================

@router.get(
    "/",
    response_model=list[WarehouseResponse],
    summary="Get Warehouses"
)
def get_warehouses(

    search: Optional[str] = Query(None),

    is_active: Optional[bool] = Query(None),

    is_default: Optional[bool] = Query(None),

    page: int = Query(
        1,
        ge=1
    ),

    page_size: int = Query(
        10,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return WarehouseService.get_warehouses(

        db=db,

        search=search,

        is_active=is_active,

        is_default=is_default,

        page=page,

        page_size=page_size
    )


# =====================================================
# Get Warehouse By ID
# =====================================================

@router.get(
    "/{warehouse_id}",
    response_model=WarehouseResponse,
    summary="Get Warehouse"
)
def get_warehouse(

    warehouse_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return WarehouseService.get_warehouse(
        db,
        warehouse_id
    )


# =====================================================
# Update Warehouse
# =====================================================

@router.put(
    "/{warehouse_id}",
    response_model=WarehouseResponse,
    summary="Update Warehouse"
)
def update_warehouse(

    warehouse_id: int,

    warehouse: WarehouseUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return WarehouseService.update_warehouse(

        db=db,

        warehouse_id=warehouse_id,

        data=warehouse,

        current_user=current_user
    )


# =====================================================
# Delete Warehouse
# =====================================================

@router.delete(
    "/{warehouse_id}",
    summary="Delete Warehouse"
)
def delete_warehouse(

    warehouse_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    WarehouseService.delete_warehouse(
        db,
        warehouse_id
    )

    return {
        "success": True,
        "message": "Warehouse deleted successfully."
    }