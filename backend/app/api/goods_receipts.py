from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.goods_receipt import (
    GoodsReceiptCreate,
    GoodsReceiptResponse
)

from app.services.goods_receipt_service import (
    GoodsReceiptService
)

from app.repositories.goods_receipt_repository import (
    GoodsReceiptRepository
)

from app.core.dependencies import (
    get_current_user
)

router = APIRouter(
    prefix="/goods-receipts",
    tags=["Goods Receipts"]
)


# =====================================================
# Create Goods Receipt
# =====================================================

@router.post(
    "/",
    response_model=GoodsReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Goods Receipt"
)
def create_goods_receipt(

    goods_receipt: GoodsReceiptCreate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return GoodsReceiptService.create_goods_receipt(

        db=db,

        data=goods_receipt,

        current_user=current_user

    )


# =====================================================
# Get All Goods Receipts
# =====================================================

@router.get(
    "/",
    response_model=list[GoodsReceiptResponse],
    summary="Get Goods Receipts"
)
def get_goods_receipts(

    search: Optional[str] = Query(None),

    supplier_id: Optional[int] = Query(None),

    warehouse_id: Optional[int] = Query(None),

    page: int = Query(1, ge=1),

    page_size: int = Query(20, ge=1, le=100),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    skip = (page - 1) * page_size

    return GoodsReceiptRepository.get_all(

        db=db,

        search=search,

        supplier_id=supplier_id,

        warehouse_id=warehouse_id,

        skip=skip,

        limit=page_size

    )


# =====================================================
# Get Goods Receipt By ID
# =====================================================

@router.get(
    "/{goods_receipt_id}",
    response_model=GoodsReceiptResponse,
    summary="Get Goods Receipt"
)
def get_goods_receipt(

    goods_receipt_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    receipt = GoodsReceiptRepository.get_by_id(

        db,

        goods_receipt_id

    )

    return receipt


# =====================================================
# Delete Goods Receipt
# =====================================================

@router.delete(
    "/{goods_receipt_id}",
    summary="Delete Goods Receipt"
)
def delete_goods_receipt(

    goods_receipt_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return GoodsReceiptService.delete_goods_receipt(

        db,

        goods_receipt_id

    )


# =====================================================
# Dashboard
# =====================================================

@router.get(
    "/dashboard/summary",
    summary="Goods Receipt Dashboard"
)
def dashboard(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return GoodsReceiptRepository.dashboard(db)