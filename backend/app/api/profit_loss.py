from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.services.profit_loss_service import (
    ProfitLossService
)

from app.schemas.profit_loss import (
    ProfitLossResponse
)

from app.core.dependencies import (
    get_current_user
)

router = APIRouter(

    prefix="/profit-loss",

    tags=["Profit & Loss"]

)


@router.get(

    "/",

    response_model=ProfitLossResponse

)

def profit_loss(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return ProfitLossService.get_profit_loss(db)