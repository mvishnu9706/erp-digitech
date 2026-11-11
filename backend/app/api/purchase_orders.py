from datetime import date
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

from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderResponse,
    PurchaseDashboardResponse,
    PurchaseOrderListResponse
)

from app.services.purchase_order_service import (
    PurchaseOrderService
)

from app.core.dependencies import (
    get_current_user,
    get_current_admin
)

router = APIRouter(
    prefix="/purchase-orders",
    tags=["Purchase Orders"]
)


# =====================================================
# Dashboard (Must be before /{purchase_order_id})
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=PurchaseDashboardResponse
)
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return PurchaseOrderService.dashboard(
        db
    )


# =====================================================
# Export Purchase Orders (Must be before /{purchase_order_id})
# =====================================================

@router.get("/export")
def export_purchase_orders(
    search: Optional[str] = Query(None),
    supplier_id: Optional[int] = Query(None),
    warehouse_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PurchaseOrderService.export_purchase_orders(
        db=db,
        search=search,
        supplier_id=supplier_id,
        warehouse_id=warehouse_id,
        date_from=date_from,
        date_to=date_to,
    )


# =====================================================
# Create Purchase Order
# =====================================================

@router.post(
    "",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_purchase_order(
    purchase_order: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return PurchaseOrderService.create_purchase_order(
        db=db,
        data=purchase_order,
        current_user=current_user
    )


# =====================================================
# Get Purchase Orders
# =====================================================

@router.get(
    "",
    response_model=PurchaseOrderListResponse
)
def get_purchase_orders(
    search: Optional[str] = Query(None),
    supplier_id: Optional[int] = Query(None),
    warehouse_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    print("=" * 50)
    print("SEARCH      :", search)
    print("SUPPLIER ID :", supplier_id)
    print("WAREHOUSE ID:", warehouse_id)
    print("DATE FROM   :", date_from)
    print("DATE TO     :", date_to)
    print("PAGE        :", page)
    print("PAGE SIZE   :", page_size)
    print("=" * 50)

    return PurchaseOrderService.get_purchase_orders(
        db=db,
        search=search,
        supplier_id=supplier_id,
        warehouse_id=warehouse_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )


# =====================================================
# Get Purchase Order
# =====================================================

@router.get(
    "/{purchase_order_id}",
    response_model=PurchaseOrderResponse
)
def get_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return PurchaseOrderService.get_purchase_order(
        db,
        purchase_order_id
    )


# =====================================================
# Update Purchase Order
# =====================================================

@router.put(
    "/{purchase_order_id}",
    response_model=PurchaseOrderResponse
)
def update_purchase_order(
    purchase_order_id: int,
    purchase_order: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return PurchaseOrderService.update_purchase_order(
        db=db,
        purchase_order_id=purchase_order_id,
        data=purchase_order,
        current_user=current_user
    )


# =====================================================
# Delete Purchase Order
# =====================================================

@router.delete(
    "/{purchase_order_id}"
)
def delete_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return PurchaseOrderService.delete_purchase_order(
        db,
        purchase_order_id
    )