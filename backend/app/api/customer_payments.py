from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.customer_payment import (
    CustomerPaymentCreate,
    CustomerPaymentUpdate,
    CustomerPaymentResponse,
    CustomerPaymentDashboardResponse
)

from app.services.customer_payment_service import (
    CustomerPaymentService
)

from app.core.dependencies import (
    get_current_admin,
    get_current_user
)

router = APIRouter(
    prefix="/customer-payments",
    tags=["Customer Payments"]
)


# =====================================================
# Create Customer Payment
# =====================================================

@router.post(
    "/",
    response_model=CustomerPaymentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_customer_payment(

    data: CustomerPaymentCreate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return CustomerPaymentService.create_customer_payment(

        db,

        data,

        current_user

    )


# =====================================================
# Get Customer Payments
# =====================================================

@router.get(
    "/",
    response_model=list[CustomerPaymentResponse]
)
def get_customer_payments(

    search: Optional[str] = Query(None),

    customer_id: Optional[int] = Query(None),

    payment_mode: Optional[str] = Query(None),

    page: int = Query(1, ge=1),

    page_size: int = Query(10, ge=1, le=100),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return CustomerPaymentService.get_customer_payments(

        db=db,

        search=search,

        customer_id=customer_id,

        payment_mode=payment_mode,

        page=page,

        page_size=page_size

    )


# =====================================================
# Get Customer Payment
# =====================================================

@router.get(
    "/{payment_id}",
    response_model=CustomerPaymentResponse
)
def get_customer_payment(

    payment_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return CustomerPaymentService.get_customer_payment(

        db,

        payment_id

    )


# =====================================================
# Update Customer Payment
# =====================================================

@router.put(
    "/{payment_id}",
    response_model=CustomerPaymentResponse
)
def update_customer_payment(

    payment_id: int,

    data: CustomerPaymentUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return CustomerPaymentService.update_customer_payment(

        db,

        payment_id,

        data,

        current_user

    )


# =====================================================
# Delete Customer Payment
# =====================================================

@router.delete(
    "/{payment_id}"
)
def delete_customer_payment(

    payment_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return CustomerPaymentService.delete_customer_payment(

        db,

        payment_id

    )


# =====================================================
# Dashboard
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=CustomerPaymentDashboardResponse
)
def dashboard(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return CustomerPaymentService.dashboard(db)