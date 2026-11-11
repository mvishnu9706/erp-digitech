from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)

from pydantic import (
    BaseModel,
    Field,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.core.dependencies import (
    get_current_customer,
    get_current_service_customer,
)

from app.models import (
    Customer,
    Machine,
    ServiceTicket,
)

from app.services.customer_service import (
    CustomerService,
)

from app.services.customer_portal_service import (
    CustomerPortalService,
)


# =====================================================
# Router
# =====================================================

router = APIRouter(
    prefix="/customer",
    tags=["Customer Portal"],
)


# =====================================================
# CUSTOMER SERVICE REQUEST SCHEMA
# =====================================================


class CustomerServiceRequestCreate(BaseModel):

    machine_id: int

    complaint: str = Field(
        ...,
        min_length=5,
        max_length=1000,
    )

    priority: str = Field(
        default="MEDIUM",
        max_length=20,
    )

    # Customer's current machine reading.
    # Accept both names used by the frontend for compatibility.
    meter_reading: int | None = Field(
        default=None,
        ge=0,
    )

    current_meter_reading: int | None = Field(
        default=None,
        ge=0,
    )


# =====================================================
# CUSTOMER PROFILE
# =====================================================
#
# GET /customer/me
#
# Returns the customer connected to the logged-in
# CUSTOMER user.
#
# =====================================================


@router.get(
    "/me",
    summary="Get My Customer Profile",
)
def get_my_customer(

    current_user=Depends(
        get_current_customer
    ),

    db: Session = Depends(
        get_db
    ),

):

    customer = CustomerService.get_my_customer(
        db=db,
        current_user=current_user,
    )

    return {

        "success": True,

        "customer": {

            "id":
                customer.id,

            "customer_code":
                customer.customer_code,

            "customer_name":
                customer.customer_name,

            "contact_person":
                customer.contact_person,

            "phone":
                customer.phone,

            "email":
                customer.email,

            "website":
                customer.website,

            "billing_address":
                customer.billing_address,

            "shipping_address":
                customer.shipping_address,

            "city":
                customer.city,

            "state":
                customer.state,

            "country":
                customer.country,

            "pincode":
                customer.pincode,

            "service_enabled":
                customer.service_enabled,

        },

        "user": {

            "id":
                current_user.id,

            "full_name":
                current_user.full_name,

            "email":
                current_user.email,

            "phone":
                current_user.phone,

            "role":
                current_user.role,

            "service_access":
                bool(
                    getattr(
                        current_user,
                        "service_access",
                        False,
                    )
                ),

            "rental_access":
                bool(
                    getattr(
                        current_user,
                        "rental_access",
                        False,
                    )
                ),

        },

    }


# =====================================================
# CUSTOMER DASHBOARD
# =====================================================
#
# GET /customer/dashboard
#
# Only the logged-in customer's information.
#
# =====================================================


@router.get(
    "/dashboard",
    summary="Customer Dashboard",
)
def customer_dashboard(

    current_user=Depends(
        get_current_service_customer
    ),

    db: Session = Depends(
        get_db
    ),

):

    return CustomerService.customer_portal_dashboard(

        db=db,

        current_user=current_user,

    )


# =====================================================
# MY MACHINES
# =====================================================
#
# GET /customer/machines
#
# Optional:
#
# ?search=HP
# ?page=1
# ?page_size=100
#
# customer_id is NEVER accepted from frontend.
#
# =====================================================


@router.get(
    "/machines",
    summary="Get My Machines",
)
def get_my_machines(

    search: str | None = None,

    page: int = 1,

    page_size: int = 100,

    current_user=Depends(
        get_current_service_customer
    ),

    db: Session = Depends(
        get_db
    ),

):

    if page < 1:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be greater than 0.",
        )

    if page_size < 1 or page_size > 100:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Page size must be between "
                "1 and 100."
            ),
        )

    machine_data = CustomerService.get_my_machines(

        db=db,

        current_user=current_user,

        search=search,

        page=page,

        page_size=page_size,

    )

    return {

        "success": True,

        "customer_id":
            current_user.customer_id,

        **machine_data,

    }


# =====================================================
# MY MACHINE
# =====================================================
#
# GET /customer/machines/{machine_id}
#
# Security:
#
# Machine must belong to the logged-in customer.
#
# =====================================================


@router.get(
    "/machines/{machine_id}",
    summary="Get My Machine",
)
def get_my_machine(

    machine_id: int,

    current_user=Depends(
        get_current_service_customer
    ),

    db: Session = Depends(
        get_db
    ),

):

    machine = CustomerService.get_my_machine(

        db=db,

        machine_id=machine_id,

        current_user=current_user,

    )

    return {

        "success": True,

        "machine": {

            "id":
                machine.id,

            "machine_number":
                machine.machine_number,

            "serial_number":
                machine.serial_number,

            "asset_tag":
                machine.asset_tag,

            "product_id":
                machine.product_id,

            "installation_date":
                machine.installation_date,

            "installation_address":
                machine.installation_address,

            "warranty_start":
                machine.warranty_start,

            "warranty_end":
                machine.warranty_end,

            "amc_start":
                machine.amc_start,

            "amc_end":
                machine.amc_end,

            "current_meter":
                machine.current_meter,

            "status":
                machine.status,

            "remarks":
                machine.remarks,

        },

    }


# =====================================================
# MY SERVICE REQUESTS
# =====================================================
#
# GET /customer/service-requests
#
# Only tickets belonging to this customer.
#
# =====================================================


@router.get(
    "/service-requests",
    summary="Get My Service Requests",
)
def get_my_service_requests(

    current_user=Depends(
        get_current_service_customer
    ),

    db: Session = Depends(
        get_db
    ),

):

    tickets = (
        db.query(ServiceTicket)
        .filter(
            ServiceTicket.customer_id
            == current_user.customer_id
        )
        .order_by(
            ServiceTicket.id.desc()
        )
        .all()
    )

    result = []

    for ticket in tickets:

        result.append({

            "id":
                ticket.id,

            "ticket_number":
                ticket.ticket_number,

            "machine_id":
                ticket.machine_id,

            "serial_number":
                ticket.serial_number,

            "meter_reading":
                ticket.meter_reading,

            "complaint":
                ticket.complaint,

            "priority":
                ticket.priority,

            "status":
                ticket.status,

            "reported_date":
                ticket.reported_date,

            "expected_visit_date":
                ticket.expected_visit_date,

            "completed_date":
                ticket.completed_date,

            "resolution":
                ticket.resolution,

            "assigned_engineer_id":
                ticket.assigned_engineer_id,

        })

    return {

        "success": True,

        "customer_id":
            current_user.customer_id,

        "total":
            len(result),

        "service_requests":
            result,

    }


# =====================================================
# GET SINGLE SERVICE REQUEST
# =====================================================
#
# GET /customer/service-requests/{ticket_id}
#
# Customer can only see their own ticket.
#
# =====================================================


@router.get(
    "/service-requests/{ticket_id}",
    summary="Get My Service Request",
)
def get_my_service_request(

    ticket_id: int,

    current_user=Depends(
        get_current_service_customer
    ),

    db: Session = Depends(
        get_db
    ),

):

    ticket = (
        db.query(ServiceTicket)
        .filter(

            ServiceTicket.id
            == ticket_id,

            ServiceTicket.customer_id
            == current_user.customer_id,

        )
        .first()
    )

    if not ticket:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found",
        )

    return {

        "success": True,

        "service_request": {

            "id":
                ticket.id,

            "ticket_number":
                ticket.ticket_number,

            "machine_id":
                ticket.machine_id,

            "serial_number":
                ticket.serial_number,

            "meter_reading":
                ticket.meter_reading,

            "complaint":
                ticket.complaint,

            "priority":
                ticket.priority,

            "status":
                ticket.status,

            "reported_date":
                ticket.reported_date,

            "expected_visit_date":
                ticket.expected_visit_date,

            "completed_date":
                ticket.completed_date,

            "resolution":
                ticket.resolution,

            "assigned_engineer_id":
                ticket.assigned_engineer_id,

        },

    }


# =====================================================
# RAISE SERVICE REQUEST
# =====================================================
#
# POST /customer/service-requests
#
# Customer sends:
#
# {
#     "machine_id": 12,
#     "complaint": "Printer showing paper jam",
#     "priority": "HIGH"
# }
#
# customer_id is NEVER accepted from frontend.
#
# =====================================================


@router.post(
    "/service-requests",
    status_code=status.HTTP_201_CREATED,
    summary="Raise Service Request",
)
def create_service_request(

    data: CustomerServiceRequestCreate,

    background_tasks: BackgroundTasks,

    current_user=Depends(
        get_current_service_customer
    ),

    db: Session = Depends(
        get_db
    ),

):

    return CustomerPortalService.create_service_request(

        db=db,

        current_user=current_user,

        machine_id=data.machine_id,

        complaint=data.complaint,

        priority=data.priority,

        meter_reading=(
            data.meter_reading
            if data.meter_reading is not None
            else data.current_meter_reading
        ),

        background_tasks=background_tasks,

    )