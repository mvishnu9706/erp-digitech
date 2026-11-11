from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.services.balance_sheet_service import (
    BalanceSheetService
)

from app.schemas.balance_sheet import (
    BalanceSheetResponse
)

from app.core.dependencies import (
    get_current_user
)

router = APIRouter(

    prefix="/balance-sheet",

    tags=["Balance Sheet"]

)


@router.get(

    "/",

    response_model=BalanceSheetResponse

)

def balance_sheet(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return BalanceSheetService.get_balance_sheet(db)