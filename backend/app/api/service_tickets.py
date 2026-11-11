from decimal import Decimal
from typing import Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    status,
)

from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.service_ticket import (
    ServiceTicketCreate,
    ServiceTicketUpdate,
    ServiceTicketResponse,
    ServiceTicketListResponse,
    ServiceTicketDashboardResponse,
)

from app.services.service_ticket_service import (
    ServiceTicketService,
)

from app.core.dependencies import (
    get_current_admin,
    get_current_user,
    get_current_engineer,
)


# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/service-tickets",
    tags=["Service Tickets"],
)


# =====================================================
# ENGINEER - COMPLETE SERVICE REQUEST SCHEMA
# =====================================================
#
# Engineer sends completion information.
#
# payment_status:
#     PENDING
#     RECEIVED
#
# =====================================================

class ServiceCompletionRequest(BaseModel):

    material_used: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    service_cost: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    resolution: Optional[str] = Field(
        default=None,
        max_length=10000,
    )

    # -------------------------------------------------
    # PAYMENT STATUS
    # -------------------------------------------------
    #
    # This value is persisted to:
    #
    # service_tickets.payment_status
    #
    # Default is PENDING.
    #
    # -------------------------------------------------

    payment_status: Optional[str] = Field(
        default="PENDING",
        max_length=20,
    )


# =====================================================
# CREATE SERVICE TICKET
# =====================================================

@router.post(
    "/",
    response_model=ServiceTicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service_ticket(
    data: ServiceTicketCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):

    return ServiceTicketService.create_service_ticket(
        db=db,
        data=data,
        current_user=current_user,
        background_tasks=background_tasks,
    )


# =====================================================
# GET SERVICE TICKETS
# =====================================================

@router.get(
    "/",
    response_model=ServiceTicketListResponse,
)
def get_service_tickets(
    search: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    machine_id: Optional[int] = Query(None),
    engineer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    ticket_type: Optional[str] = Query(None),

    page: int = Query(
        1,
        ge=1,
    ),

    page_size: int = Query(
        10,
        ge=1,
        le=100,
    ),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return ServiceTicketService.get_service_tickets(
        db=db,
        search=search,
        customer_id=customer_id,
        machine_id=machine_id,
        engineer_id=engineer_id,
        status=status,
        priority=priority,
        ticket_type=ticket_type,
        page=page,
        page_size=page_size,
    )


# =====================================================
# DASHBOARD
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=ServiceTicketDashboardResponse,
)
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return ServiceTicketService.dashboard(
        db
    )


# =====================================================
# ENGINEER - MY SERVICE TICKETS
# =====================================================

@router.get(
    "/engineer/my-services",
    response_model=ServiceTicketListResponse,
)
def get_my_engineer_services(
    page: int = Query(
        1,
        ge=1,
    ),

    page_size: int = Query(
        100,
        ge=1,
        le=100,
    ),

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_engineer
    ),
):

    return ServiceTicketService.get_service_tickets(
        db=db,
        search=None,
        customer_id=None,
        machine_id=None,

        # Engineer sees only his/her services.
        engineer_id=current_user.id,

        status=None,
        priority=None,
        ticket_type=None,

        page=page,
        page_size=page_size,
    )


# =====================================================
# ENGINEER - ACCEPT SERVICE
# =====================================================
#
# ASSIGNED -> IN_PROGRESS
#
# Only assigned engineer can accept.
#
# =====================================================

@router.put(
    "/{ticket_id}/accept",
    response_model=ServiceTicketResponse,
)
def accept_service(
    ticket_id: int,
    background_tasks: BackgroundTasks,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_engineer
    ),
):

    return ServiceTicketService.accept_service(
        db=db,
        ticket_id=ticket_id,
        current_user=current_user,
        background_tasks=background_tasks,
    )


# =====================================================
# ENGINEER - REJECT SERVICE
# =====================================================
#
# ASSIGNED -> CANCELLED
#
# Only assigned engineer can reject.
#
# =====================================================

@router.put(
    "/{ticket_id}/reject",
    response_model=ServiceTicketResponse,
)
def reject_service(
    ticket_id: int,
    background_tasks: BackgroundTasks,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_engineer
    ),
):

    return ServiceTicketService.reject_service(
        db=db,
        ticket_id=ticket_id,
        current_user=current_user,
        background_tasks=background_tasks,
    )


# =====================================================
# ENGINEER - COMPLETE SERVICE
# =====================================================
#
# IN_PROGRESS -> COMPLETED
#
# Only assigned engineer can complete.
#
# Completion data:
#
#     material_used
#     service_cost
#     resolution
#     payment_status
#
# =====================================================

@router.put(
    "/{ticket_id}/complete",
    response_model=ServiceTicketResponse,
)
def complete_service(
    ticket_id: int,

    data: ServiceCompletionRequest,

    background_tasks: BackgroundTasks,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_engineer
    ),
):

    # -------------------------------------------------
    # NORMALIZE PAYMENT STATUS
    # -------------------------------------------------

    payment_status = (
        str(
            data.payment_status
            or "PENDING"
        )
        .strip()
        .upper()
    )

    # -------------------------------------------------
    # ONLY ACCEPT SUPPORTED VALUES
    # -------------------------------------------------

    if payment_status not in {
        "PENDING",
        "RECEIVED",
    }:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Payment status must be "
                "PENDING or RECEIVED."
            ),
        )

    # -------------------------------------------------
    # SEND EVERYTHING TO SERVICE LAYER
    # -------------------------------------------------

    return ServiceTicketService.complete_service(
        db=db,
        ticket_id=ticket_id,
        current_user=current_user,

        material_used=data.material_used,

        service_cost=data.service_cost,

        resolution=data.resolution,

        payment_status=payment_status,

        background_tasks=background_tasks,
    )


# =====================================================
# GET SERVICE TICKET
# =====================================================

@router.get(
    "/{ticket_id}",
    response_model=ServiceTicketResponse,
)
def get_service_ticket(
    ticket_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),
):

    return ServiceTicketService.get_service_ticket(
        db,
        ticket_id,
    )


# =====================================================
# UPDATE SERVICE TICKET
# =====================================================

@router.put(
    "/{ticket_id}",
    response_model=ServiceTicketResponse,
)
def update_service_ticket(
    ticket_id: int,

    data: ServiceTicketUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),
):

    """
    Update service ticket.

    ADMIN / SUPER_ADMIN:
        Can update any service ticket.

    ENGINEER:
        Can update only a service ticket assigned
        to that engineer.

        Engineer-editable fields:

            - completion_date
            - material_used
            - service_cost
            - resolution
            - payment_status

    CUSTOMER / other users:
        Cannot update service tickets.
    """

    # =================================================
    # NORMALIZE ROLE
    # =================================================

    role = (
        str(
            getattr(
                current_user,
                "role",
                "",
            )
            or ""
        )
        .strip()
        .upper()
        .replace(
            " ",
            "_",
        )
    )

    # =================================================
    # ADMIN / SUPER ADMIN
    # =================================================

    if role in {
        "ADMIN",
        "SUPER_ADMIN",
        "SUPERADMIN",
    }:

        return ServiceTicketService.update_service_ticket(
            db=db,
            ticket_id=ticket_id,
            data=data,
            current_user=current_user,
        )

    # =================================================
    # ENGINEER
    # =================================================

    if role == "ENGINEER":

        # -------------------------------------------------
        # GET TICKET
        # -------------------------------------------------

        ticket = ServiceTicketService.get_service_ticket(
            db=db,
            ticket_id=ticket_id,
        )

        if not ticket:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service Ticket not found.",
            )

        # -------------------------------------------------
        # GET ASSIGNED ENGINEER
        # -------------------------------------------------

        assigned_engineer_id = getattr(
            ticket,
            "assigned_engineer_id",
            None,
        )

        if assigned_engineer_id is None:

            assigned_engineer_id = getattr(
                ticket,
                "engineer_id",
                None,
            )

        # -------------------------------------------------
        # ENGINEER MUST OWN THE TICKET
        # -------------------------------------------------

        if assigned_engineer_id != current_user.id:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can update only service tickets "
                    "assigned to you."
                ),
            )

        # -------------------------------------------------
        # ENGINEER CAN ONLY UPDATE COMPLETION DATA
        # -------------------------------------------------
        #
        # We deliberately create a clean ServiceTicketUpdate
        # object so the engineer cannot change:
        #
        #     customer
        #     machine
        #     assignment
        #     priority
        #     status
        #     ticket number
        #     etc.
        #
        # -------------------------------------------------

        payment_status = data.payment_status

        if payment_status is not None:

            payment_status = (
                str(payment_status)
                .strip()
                .upper()
            )

            if payment_status not in {
                "PENDING",
                "RECEIVED",
            }:

                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        "Payment status must be "
                        "PENDING or RECEIVED."
                    ),
                )

        engineer_data = ServiceTicketUpdate(
            completion_date=data.completion_date,

            material_used=data.material_used,

            service_cost=data.service_cost,

            resolution=data.resolution,

            payment_status=payment_status,
        )

        return ServiceTicketService.update_service_ticket(
            db=db,
            ticket_id=ticket_id,
            data=engineer_data,
            current_user=current_user,
        )

    # =================================================
    # EVERY OTHER ROLE
    # =================================================

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "You do not have permission to update "
            "service tickets."
        ),
    )


# =====================================================
# CANCEL SERVICE TICKET - SOFT CANCEL ONLY
# =====================================================
#
# IMPORTANT:
#
# This endpoint DOES NOT physically delete the row.
#
# It changes:
#
#     status = CANCELLED
#
# The database record remains.
#
# POST /service-tickets/{ticket_id}/cancel
#
# =====================================================

@router.post(
    "/{ticket_id}/cancel",
    response_model=ServiceTicketResponse,
)
def cancel_service_ticket(
    ticket_id: int,

    background_tasks: BackgroundTasks,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_admin
    ),
):

    return ServiceTicketService.change_status(
        db=db,

        ticket_id=ticket_id,

        status_value="CANCELLED",

        current_user=current_user,

        background_tasks=background_tasks,
    )


# =====================================================
# DELETE SERVICE TICKET
# =====================================================
#
# This remains the actual DELETE endpoint.
#
# DO NOT use this endpoint from the Admin clear/cancel
# button. The Admin cancel button should use:
#
#     POST /service-tickets/{ticket_id}/cancel
#
# =====================================================

@router.delete(
    "/{ticket_id}",
)
def delete_service_ticket(
    ticket_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_admin
    ),
):

    return ServiceTicketService.delete_service_ticket(
        db,
        ticket_id,
    )


# =====================================================
# ASSIGN ENGINEER
# =====================================================

@router.put(
    "/{ticket_id}/assign/{engineer_id}",
    response_model=ServiceTicketResponse,
)
def assign_engineer(
    ticket_id: int,

    engineer_id: int,

    background_tasks: BackgroundTasks,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_admin
    ),
):

    return ServiceTicketService.assign_engineer(
        db=db,

        ticket_id=ticket_id,

        engineer_id=engineer_id,

        current_user=current_user,

        background_tasks=background_tasks,
    )


# =====================================================
# CHANGE STATUS
# =====================================================

@router.put(
    "/{ticket_id}/status/{status_value}",
    response_model=ServiceTicketResponse,
)
def change_status(
    ticket_id: int,

    status_value: str,

    background_tasks: BackgroundTasks,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_admin
    ),
):

    return ServiceTicketService.change_status(
        db=db,

        ticket_id=ticket_id,

        status_value=status_value,

        current_user=current_user,

        background_tasks=background_tasks,
    )