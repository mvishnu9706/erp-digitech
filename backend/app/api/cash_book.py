from typing import Optional

from fastapi import APIRouter, Depends, Query

from sqlalchemy.orm import Session

from datetime import date

from app.core.dependencies import get_current_user
from app.database import get_db
from app.schemas.cash_book import CashBookResponse
from app.services.cash_book_service import CashBookService

router = APIRouter(prefix="/cash-book", tags=["Cash Book"])


@router.get("/", response_model=CashBookResponse)
def cash_book(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return CashBookService.get_cash_book(db, from_date, to_date)
