from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.schemas.customer_outstanding import CustomerOutstandingEntry
from app.services.customer_outstanding_service import CustomerOutstandingService

router = APIRouter(prefix="/customer-outstanding", tags=["Customer Outstanding"])


@router.get("/", response_model=list[CustomerOutstandingEntry])
def customer_outstanding(
    customer_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return CustomerOutstandingService.get_outstanding(db, customer_id)
