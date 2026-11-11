from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.machine import (
    MachineCreate,
    MachineUpdate,
    MachineResponse,
    MachineListResponse,
    MachineDashboardResponse
)

from app.services.machine_service import MachineService

from app.core.dependencies import (
    get_current_admin,
    get_current_user
)

router = APIRouter(
    prefix="/machines",
    tags=["Machines"]
)


# =====================================================
# Create Machine
# =====================================================

@router.post(
    "/",
    response_model=MachineResponse,
    status_code=status.HTTP_201_CREATED
)
def create_machine(
    data: MachineCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    return MachineService.create_machine(
        db,
        data,
        current_user
    )


# =====================================================
# Get Machines
# =====================================================

@router.get(
    "/",
    response_model=MachineListResponse
)
def get_machines(

    search: str | None = Query(None),

    customer_id: int | None = Query(None),

    product_id: int | None = Query(None),

    status: str | None = Query(None),

    page: int = 1,

    page_size: int = 10,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return MachineService.get_machines(

        db,

        search,

        customer_id,

        product_id,

        status,

        page,

        page_size

    )


# =====================================================
# Dashboard
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=MachineDashboardResponse
)
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return MachineService.dashboard(db)


# =====================================================
# Get Machine
# =====================================================

@router.get(
    "/{machine_id}",
    response_model=MachineResponse
)
def get_machine(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return MachineService.get_machine(
        db,
        machine_id
    )


# =====================================================
# Update Machine
# =====================================================

@router.put(
    "/{machine_id}",
    response_model=MachineResponse
)
def update_machine(

    machine_id: int,

    data: MachineUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return MachineService.update_machine(

        db,

        machine_id,

        data,

        current_user

    )


# =====================================================
# Delete Machine
# =====================================================

@router.delete("/{machine_id}")
def delete_machine(

    machine_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return MachineService.delete_machine(

        db,

        machine_id

    )