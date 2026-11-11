from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.purchase_invoice import (
    PurchaseInvoiceCreate,
    PurchaseInvoiceUpdate,
    PurchaseInvoiceResponse,
    PurchaseInvoiceDashboardResponse
)

from app.services.purchase_invoice_service import (
    PurchaseInvoiceService
)

from app.core.dependencies import (
    get_current_admin,
    get_current_user
)

router = APIRouter(
    prefix="/purchase-invoices",
    tags=["Purchase Invoices"]
)


# =====================================================
# Create Purchase Invoice
# =====================================================

@router.post(
    "/",
    response_model=PurchaseInvoiceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_purchase_invoice(

    data: PurchaseInvoiceCreate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return PurchaseInvoiceService.create_purchase_invoice(

        db,

        data,

        current_user

    )


# =====================================================
# Get Purchase Invoices
# =====================================================

@router.get(
    "/",
    response_model=list[PurchaseInvoiceResponse]
)
def get_purchase_invoices(

    search: Optional[str] = Query(None),

    supplier_id: Optional[int] = Query(None),

    warehouse_id: Optional[int] = Query(None),

    status: Optional[str] = Query(None),

    page: int = Query(1, ge=1),

    page_size: int = Query(10, ge=1, le=100),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return PurchaseInvoiceService.get_purchase_invoices(

        db=db,

        search=search,

        supplier_id=supplier_id,

        warehouse_id=warehouse_id,

        status=status,

        page=page,

        page_size=page_size

    )


# =====================================================
# Get Purchase Invoice
# =====================================================

@router.get(
    "/{purchase_invoice_id}",
    response_model=PurchaseInvoiceResponse
)
def get_purchase_invoice(

    purchase_invoice_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return PurchaseInvoiceService.get_purchase_invoice(

        db,

        purchase_invoice_id

    )


# =====================================================
# Update Purchase Invoice
# =====================================================

@router.put(
    "/{purchase_invoice_id}",
    response_model=PurchaseInvoiceResponse
)
def update_purchase_invoice(

    purchase_invoice_id: int,

    data: PurchaseInvoiceUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return PurchaseInvoiceService.update_purchase_invoice(

        db,

        purchase_invoice_id,

        data,

        current_user

    )


# =====================================================
# Delete Purchase Invoice
# =====================================================

@router.delete(
    "/{purchase_invoice_id}"
)
def delete_purchase_invoice(

    purchase_invoice_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return PurchaseInvoiceService.delete_purchase_invoice(

        db,

        purchase_invoice_id

    )


# =====================================================
# Dashboard
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=PurchaseInvoiceDashboardResponse
)
def dashboard(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return PurchaseInvoiceService.dashboard(db)