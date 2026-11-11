from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.services.trial_balance_service import (
    TrialBalanceService
)

from app.schemas.trial_balance import (
    TrialBalanceResponse
)

from app.core.dependencies import (
    get_current_user
)

router = APIRouter(

    prefix="/trial-balance",

    tags=["Trial Balance"]

)


@router.get(

    "/",

    response_model=TrialBalanceResponse

)

def trial_balance(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return TrialBalanceService.get_trial_balance(db)