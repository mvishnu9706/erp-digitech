from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.schemas.supplier_ledger import SupplierLedgerResponse
from app.services.supplier_ledger_service import SupplierLedgerService

router = APIRouter(prefix="/supplier-ledger", tags=["Supplier Ledger"])


@router.get("/{supplier_id}", response_model=SupplierLedgerResponse)
def supplier_ledger(
    supplier_id: int,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return SupplierLedgerService.get_ledger(db, supplier_id, from_date, to_date)
