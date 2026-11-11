from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.sales_invoice import (
    SalesInvoiceCreate,
    SalesInvoiceUpdate,
    SalesInvoiceResponse,
    SalesInvoiceDashboardResponse
)

from app.services.sales_invoice_service import (
    SalesInvoiceService
)

from app.core.dependencies import (
    get_current_admin,
    get_current_user
)

router = APIRouter(
    prefix="/sales-invoices",
    tags=["Sales Invoices"]
)


# =====================================================
# Create Sales Invoice
# =====================================================

@router.post(
    "/",
    response_model=SalesInvoiceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_sales_invoice(

    data: SalesInvoiceCreate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return SalesInvoiceService.create_sales_invoice(

        db,

        data,

        current_user

    )


# =====================================================
# Get Sales Invoices
# =====================================================

@router.get(
    "/",
    response_model=list[SalesInvoiceResponse]
)
def get_sales_invoices(

    search: Optional[str] = Query(None),

    customer_id: Optional[int] = Query(None),

    warehouse_id: Optional[int] = Query(None),

    status: Optional[str] = Query(None),

    page: int = Query(1, ge=1),

    page_size: int = Query(10, ge=1, le=100),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return SalesInvoiceService.get_sales_invoices(

        db=db,

        search=search,

        customer_id=customer_id,

        warehouse_id=warehouse_id,

        status=status,

        page=page,

        page_size=page_size

    )


# =====================================================
# Get Sales Invoice
# =====================================================

@router.get(
    "/{sales_invoice_id}",
    response_model=SalesInvoiceResponse
)
def get_sales_invoice(

    sales_invoice_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return SalesInvoiceService.get_sales_invoice(

        db,

        sales_invoice_id

    )


# =====================================================
# Update Sales Invoice
# =====================================================

@router.put(
    "/{sales_invoice_id}",
    response_model=SalesInvoiceResponse
)
def update_sales_invoice(

    sales_invoice_id: int,

    data: SalesInvoiceUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return SalesInvoiceService.update_sales_invoice(

        db,

        sales_invoice_id,

        data,

        current_user

    )


# =====================================================
# Delete Sales Invoice
# =====================================================

@router.delete(
    "/{sales_invoice_id}"
)
def delete_sales_invoice(

    sales_invoice_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return SalesInvoiceService.delete_sales_invoice(

        db,

        sales_invoice_id

    )


# =====================================================
# Dashboard
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=SalesInvoiceDashboardResponse
)
def dashboard(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return SalesInvoiceService.dashboard(db)