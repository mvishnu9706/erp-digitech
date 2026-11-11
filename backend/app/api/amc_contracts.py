from datetime import date
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.amc_contract import (
    AMCContractCreate,
    AMCContractUpdate,
    AMCContractResponse,
    AMCContractListResponse,
    AMCContractDashboardResponse
)

from app.services.amc_contract_service import (
    AMCContractService
)

from app.core.dependencies import (
    get_current_admin,
    get_current_user
)

router = APIRouter(
    prefix="/amc-contracts",
    tags=["AMC Contracts"]
)


# =====================================================
# Create AMC Contract
# =====================================================

@router.post(
    "/",
    response_model=AMCContractResponse,
    status_code=status.HTTP_201_CREATED
)
def create_contract(
    data: AMCContractCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    return AMCContractService.create_contract(
        db,
        data,
        current_user
    )


# =====================================================
# Get AMC Contracts
# =====================================================

@router.get(
    "/",
    response_model=AMCContractListResponse
)
def get_contracts(

    search: Optional[str] = Query(None),

    customer_id: Optional[int] = Query(None),

    machine_id: Optional[int] = Query(None),

    contract_type: Optional[str] = Query(None),

    status: Optional[str] = Query(None),

    page: int = Query(1, ge=1),

    page_size: int = Query(10, ge=1, le=100),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return AMCContractService.get_contracts(

        db=db,

        search=search,

        customer_id=customer_id,

        machine_id=machine_id,

        contract_type=contract_type,

        status=status,

        page=page,

        page_size=page_size

    )


# =====================================================
# Dashboard
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=AMCContractDashboardResponse
)
def dashboard(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return AMCContractService.dashboard(db)


# =====================================================
# Get AMC Contract
# =====================================================

@router.get(
    "/{contract_id}",
    response_model=AMCContractResponse
)
def get_contract(

    contract_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return AMCContractService.get_contract(

        db,

        contract_id

    )


# =====================================================
# Update AMC Contract
# =====================================================

@router.put(
    "/{contract_id}",
    response_model=AMCContractResponse
)
def update_contract(

    contract_id: int,

    data: AMCContractUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return AMCContractService.update_contract(

        db,

        contract_id,

        data,

        current_user

    )


# =====================================================
# Delete AMC Contract
# =====================================================

@router.delete("/{contract_id}")
def delete_contract(

    contract_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return AMCContractService.delete_contract(

        db,

        contract_id

    )


# =====================================================
# Renew AMC Contract
# =====================================================

@router.put(
    "/{contract_id}/renew",
    response_model=AMCContractResponse
)
def renew_contract(

    contract_id: int,

    new_end_date: date,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return AMCContractService.renew_contract(

        db,

        contract_id,

        new_end_date,

        current_user

    )


# =====================================================
# Expire AMC Contract
# =====================================================

@router.put(
    "/{contract_id}/expire",
    response_model=AMCContractResponse
)
def expire_contract(

    contract_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return AMCContractService.expire_contract(

        db,

        contract_id,

        current_user

    )