from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.schemas.supplier_outstanding import SupplierOutstandingEntry
from app.services.supplier_outstanding_service import SupplierOutstandingService

router = APIRouter(prefix="/supplier-outstanding", tags=["Supplier Outstanding"])


@router.get("/", response_model=list[SupplierOutstandingEntry])
def supplier_outstanding(
    supplier_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return SupplierOutstandingService.get_outstanding(db, supplier_id)
