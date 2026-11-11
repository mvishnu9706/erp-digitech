from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.supplier_payment import (
    SupplierPaymentCreate,
    SupplierPaymentUpdate,
    SupplierPaymentResponse,
    SupplierPaymentDashboardResponse
)

from app.services.supplier_payment_service import (
    SupplierPaymentService
)

from app.core.dependencies import (
    get_current_admin,
    get_current_user
)

router = APIRouter(
    prefix="/supplier-payments",
    tags=["Supplier Payments"]
)


# =====================================================
# Create Supplier Payment
# =====================================================

@router.post(
    "/",
    response_model=SupplierPaymentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_supplier_payment(

    data: SupplierPaymentCreate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return SupplierPaymentService.create_supplier_payment(

        db,

        data,

        current_user

    )


# =====================================================
# Get Supplier Payments
# =====================================================

@router.get(
    "/",
    response_model=list[SupplierPaymentResponse]
)
def get_supplier_payments(

    search: Optional[str] = Query(None),

    supplier_id: Optional[int] = Query(None),

    payment_mode: Optional[str] = Query(None),

    page: int = Query(1, ge=1),

    page_size: int = Query(10, ge=1, le=100),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return SupplierPaymentService.get_supplier_payments(

        db=db,

        search=search,

        supplier_id=supplier_id,

        payment_mode=payment_mode,

        page=page,

        page_size=page_size

    )


# =====================================================
# Get Supplier Payment
# =====================================================

@router.get(
    "/{payment_id}",
    response_model=SupplierPaymentResponse
)
def get_supplier_payment(

    payment_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return SupplierPaymentService.get_supplier_payment(

        db,

        payment_id

    )


# =====================================================
# Update Supplier Payment
# =====================================================

@router.put(
    "/{payment_id}",
    response_model=SupplierPaymentResponse
)
def update_supplier_payment(

    payment_id: int,

    data: SupplierPaymentUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return SupplierPaymentService.update_supplier_payment(

        db,

        payment_id,

        data,

        current_user

    )


# =====================================================
# Delete Supplier Payment
# =====================================================

@router.delete(
    "/{payment_id}"
)
def delete_supplier_payment(

    payment_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return SupplierPaymentService.delete_supplier_payment(

        db,

        payment_id

    )


# =====================================================
# Dashboard
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=SupplierPaymentDashboardResponse
)
def dashboard(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return SupplierPaymentService.dashboard(db)