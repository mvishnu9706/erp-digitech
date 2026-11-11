from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerDashboardResponse,
)

from app.services.customer_service import (
    CustomerService,
)

from app.core.dependencies import (
    get_current_admin,
)


# =====================================================
# Router
# =====================================================

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


# =====================================================
# CREATE CUSTOMER
# =====================================================
#
# POST /customers/
#
# ADMIN
# SUPER_ADMIN
#
# Can create customers.
#
# New customers can optionally include:
#
# machine_name
# machine_serial_number
#
# When both machine fields are provided,
# CustomerService creates the machine and links it
# to the newly created customer.
#
# product_id is NOT required for this customer
# creation flow.
#
# =====================================================

@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Customer",
)
def create_customer(

    customer: CustomerCreate,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),

):

    return CustomerService.create_customer(

        db=db,

        data=customer,

        current_user=current_user,

    )


# =====================================================
# GET CUSTOMERS
# =====================================================
#
# GET /customers/
#
# This is the ADMIN customer-management API.
#
# CUSTOMER and ENGINEER should NOT use this endpoint.
#
# They will have separate portal APIs later.
#
# =====================================================

@router.get(
    "/",
    response_model=list[CustomerResponse],
    summary="Get Customers",
)
def get_customers(

    search: Optional[str] = Query(
        None
    ),

    city: Optional[str] = Query(
        None
    ),

    state: Optional[str] = Query(
        None
    ),

    is_active: Optional[bool] = Query(
        None
    ),

    page: int = Query(
        1,
        ge=1,
    ),

    page_size: int = Query(
        10,
        ge=1,
        le=100,
    ),

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),

):

    return CustomerService.get_customers(

        db=db,

        search=search,

        city=city,

        state=state,

        is_active=is_active,

        page=page,

        page_size=page_size,

    )


# =====================================================
# EXPORT CUSTOMERS
# =====================================================
#
# GET /customers/export
#
# ADMIN / SUPER_ADMIN only.
#
# =====================================================

@router.get(
    "/export",
    summary="Export Customers",
)
def export_customers(

    search: Optional[str] = Query(
        None
    ),

    city: Optional[str] = Query(
        None
    ),

    state: Optional[str] = Query(
        None
    ),

    is_active: Optional[bool] = Query(
        None
    ),

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),

):

    return CustomerService.export_customers(

        db=db,

        search=search,

        city=city,

        state=state,

        is_active=is_active,

    )


# =====================================================
# CUSTOMER DASHBOARD
# =====================================================
#
# GET /customers/dashboard/summary
#
# This is the ADMIN customer-management dashboard.
#
# It is NOT the customer portal dashboard.
#
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=CustomerDashboardResponse,
    summary="Customer Dashboard Summary",
)
def dashboard(

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),

):

    return CustomerService.dashboard(
        db
    )


# =====================================================
# GET CUSTOMER BY ID
# =====================================================
#
# GET /customers/{customer_id}
#
# ADMIN / SUPER_ADMIN only.
#
# =====================================================

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get Customer",
)
def get_customer(

    customer_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),

):

    return CustomerService.get_customer(

        db,

        customer_id,

    )


# =====================================================
# UPDATE CUSTOMER
# =====================================================
#
# PUT /customers/{customer_id}
#
# ADMIN / SUPER_ADMIN only.
#
# This also controls:
#
# service_enabled
#
# Machine fields can also be supplied through
# CustomerUpdate:
#
# machine_id
# machine_name
# machine_serial_number
#
# Example:
#
# {
#     "machine_name": "Canon ImageRunner",
#     "machine_serial_number": "SN-10025"
# }
#
# =====================================================

@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update Customer",
)
def update_customer(

    customer_id: int,

    customer: CustomerUpdate,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),

):

    return CustomerService.update_customer(

        db=db,

        customer_id=customer_id,

        data=customer,

        current_user=current_user,

    )


# =====================================================
# DELETE CUSTOMER
# =====================================================
#
# DELETE /customers/{customer_id}
#
# ADMIN / SUPER_ADMIN only.
#
# =====================================================

@router.delete(
    "/{customer_id}",
    summary="Delete Customer",
)
def delete_customer(

    customer_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),

):

    return CustomerService.delete_customer(

        db=db,

        customer_id=customer_id,

    )