from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
    StockTransfer,
)

from app.services.inventory_service import inventory_service

from app.core.dependencies import (
    get_current_user,
    get_current_admin,
)


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


# =====================================================
# Get All Inventory
# =====================================================

@router.get("")
def get_inventory(

    page: int = Query(
        1,
        ge=1,
    ),

    size: int = Query(
        10,
        ge=1,
    ),

    search: Optional[str] = None,

    warehouse_id: Optional[int] = None,

    product_id: Optional[int] = None,

    stock_status: Optional[str] = None,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user),

):

    return inventory_service.get_all(

        db=db,

        page=page,

        size=size,

        search=search,

        warehouse_id=warehouse_id,

        product_id=product_id,

        stock_status=stock_status,

    )


# =====================================================
# EXPORT INVENTORY TO EXCEL
#
# No filters:
#     Export ALL inventory
#
# Filters:
#     Export matching inventory only
#
# Supported:
#     search
#     warehouse_id
#     product_id
#     stock_status
#
# IMPORTANT:
# This endpoint is BEFORE /{inventory_id}
# =====================================================

@router.get(
    "/export",
    summary="Export Inventory to Excel",
)
def export_inventory(

    search: Optional[str] = Query(None),

    warehouse_id: Optional[int] = Query(None),

    product_id: Optional[int] = Query(None),

    stock_status: Optional[str] = Query(None),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user),

):

    return inventory_service.export_inventory(

        db=db,

        search=search,

        warehouse_id=warehouse_id,

        product_id=product_id,

        stock_status=stock_status,

    )


# =====================================================
# Dashboard
# =====================================================

@router.get("/dashboard")
def dashboard(

    search: Optional[str] = Query(None),

    warehouse_id: Optional[int] = Query(None),

    product_id: Optional[int] = Query(None),

    stock_status: Optional[str] = Query(None),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user),

):

    return inventory_service.dashboard(

        db=db,

        search=search,

        warehouse_id=warehouse_id,

        product_id=product_id,

        stock_status=stock_status,

    )


# =====================================================
# Check Inventory
#
# IMPORTANT:
# This must stay BEFORE /{inventory_id}
# =====================================================

@router.get("/check")
def check_inventory(

    product_id: int = Query(...),

    warehouse_id: int = Query(...),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user),

):

    return inventory_service.check_inventory(

        db,

        product_id,

        warehouse_id,

    )


# =====================================================
# Get Stock
#
# IMPORTANT:
# This must stay BEFORE /{inventory_id}
#
# Returns ONLY actual stock.
#
# Example:
#
# {
#     "stock": 25
# }
#
# =====================================================

@router.get("/stock")
def get_stock(

    product_id: int = Query(...),

    warehouse_id: int = Query(...),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user),

):

    inventory = inventory_service.get_stock(

        db,

        product_id,

        warehouse_id,

    )


    # -------------------------------------------------
    # Inventory does not exist
    # -------------------------------------------------

    if inventory is None:

        return {
            "stock": 0,
        }


    # -------------------------------------------------
    # Return actual database stock
    # -------------------------------------------------

    return {

        "stock": int(inventory),

    }


# =====================================================
# Get Inventory By ID
# =====================================================

@router.get(
    "/{inventory_id}",
    response_model=InventoryResponse,
)
def get_inventory_by_id(

    inventory_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user),

):

    return inventory_service.get_by_id(

        db,

        inventory_id,

    )


# =====================================================
# Create Inventory
# =====================================================

@router.post(
    "",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inventory(

    data: InventoryCreate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin),

):

    return inventory_service.create(

        db,

        data,

        current_user,

    )


# =====================================================
# Update Inventory
# =====================================================

@router.put(
    "/{inventory_id}",
    response_model=InventoryResponse,
)
def update_inventory(

    inventory_id: int,

    data: InventoryUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin),

):

    return inventory_service.update(

        db,

        inventory_id,

        data,

        current_user,

    )


# =====================================================
# Delete Inventory
# =====================================================

@router.delete("/{inventory_id}")
def delete_inventory(

    inventory_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin),

):

    return inventory_service.delete(

        db,

        inventory_id,

    )


# =====================================================
# Transfer Stock
# =====================================================

@router.post("/transfer")
def transfer_stock(

    data: StockTransfer,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin),

):

    return inventory_service.transfer_stock(

        db,

        data,

        current_user,

    )