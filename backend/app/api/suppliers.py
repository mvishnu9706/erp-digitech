from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    SupplierDashboardResponse,
    SupplierListResponse
)

from app.services.supplier_service import SupplierService

from app.core.dependencies import (
    get_current_admin,
    get_current_user
)


router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


# =====================================================
# Create Supplier
# =====================================================

@router.post(
    "/",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Supplier"
)
def create_supplier(

    supplier: SupplierCreate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return SupplierService.create_supplier(

        db=db,

        data=supplier,

        current_user=current_user

    )


# =====================================================
# Get Suppliers
# =====================================================

@router.get(
    "/",
    response_model=SupplierListResponse,
    summary="Get Suppliers"
)
def get_suppliers(

    search: Optional[str] = Query(None),

    city: Optional[str] = Query(None),

    state: Optional[str] = Query(None),

    is_active: Optional[bool] = Query(None),

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

    return SupplierService.get_suppliers(

        db=db,

        search=search,

        city=city,

        state=state,

        is_active=is_active,

        page=page,

        page_size=page_size

    )


# =====================================================
# EXPORT SUPPLIERS
#
# No filters:
#     Export ALL suppliers
#
# Filters:
#     Export only matching suppliers
#
# Supported filters:
#     search
#     city
#     state
#     is_active
# =====================================================

@router.get(
    "/export",
    summary="Export Suppliers"
)
def export_suppliers(

    search: Optional[str] = Query(None),

    city: Optional[str] = Query(None),

    state: Optional[str] = Query(None),

    is_active: Optional[bool] = Query(None),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return SupplierService.export_suppliers(

        db=db,

        search=search,

        city=city,

        state=state,

        is_active=is_active

    )


# =====================================================
# Supplier Dashboard
# =====================================================

@router.get(
    "/dashboard",
    response_model=SupplierDashboardResponse,
    summary="Supplier Dashboard"
)
def supplier_dashboard(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return SupplierService.dashboard(db)


# =====================================================
# Get Supplier
# =====================================================

@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse,
    summary="Get Supplier"
)
def get_supplier(

    supplier_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return SupplierService.get_supplier(

        db=db,

        supplier_id=supplier_id

    )


# =====================================================
# Update Supplier
# =====================================================

@router.put(
    "/{supplier_id}",
    response_model=SupplierResponse,
    summary="Update Supplier"
)
def update_supplier(

    supplier_id: int,

    supplier: SupplierUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return SupplierService.update_supplier(

        db=db,

        supplier_id=supplier_id,

        data=supplier,

        current_user=current_user

    )


# =====================================================
# Delete Supplier
# =====================================================

@router.delete(
    "/{supplier_id}",
    summary="Deactivate Supplier"
)
def delete_supplier(

    supplier_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    SupplierService.delete_supplier(

        db=db,

        supplier_id=supplier_id

    )

    return {

        "success": True,

        "message":
            "Supplier deactivated successfully."

    }