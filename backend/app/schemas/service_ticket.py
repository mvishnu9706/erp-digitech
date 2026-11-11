from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# =====================================================
# ENUMS
# =====================================================


class TicketStatus(str, Enum):
    REQUESTED = "REQUESTED"
    ASSIGNED = "ASSIGNED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    ON_HOLD = "ON_HOLD"
    PARTS_PENDING = "PARTS_PENDING"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class TicketPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TicketType(str, Enum):
    BREAKDOWN = "BREAKDOWN"
    INSTALLATION = "INSTALLATION"
    AMC = "AMC"
    PREVENTIVE_MAINTENANCE = "PREVENTIVE_MAINTENANCE"
    RENTAL = "RENTAL"
    DEMO = "DEMO"
    SHIFTING = "SHIFTING"
    REINSTALLATION = "REINSTALLATION"


# =====================================================
# CUSTOMER PORTAL
# CREATE SERVICE REQUEST
# =====================================================


class CustomerServiceRequestCreate(BaseModel):

    # -------------------------------------------------
    # Machine
    # -------------------------------------------------

    machine_id: int = Field(
        ...,
        gt=0,
    )

    # -------------------------------------------------
    # Service Type
    # -------------------------------------------------

    ticket_type: TicketType = (
        TicketType.BREAKDOWN
    )

    # -------------------------------------------------
    # Priority
    # -------------------------------------------------

    priority: TicketPriority = (
        TicketPriority.MEDIUM
    )

    # -------------------------------------------------
    # Subject
    # -------------------------------------------------

    subject: str = Field(
        ...,
        min_length=3,
        max_length=200,
    )

    # -------------------------------------------------
    # Complaint
    # -------------------------------------------------

    complaint: str = Field(
        ...,
        min_length=5,
        max_length=1000,
    )

    # -------------------------------------------------
    # Detailed Problem
    # -------------------------------------------------

    problem_description: Optional[str] = Field(
        default=None,
        max_length=3000,
    )

    # -------------------------------------------------
    # Meter Reading
    # -------------------------------------------------

    meter_reading: Optional[int] = Field(
        default=None,
        ge=0,
    )

    # Compatibility with the customer portal frontend payload.
    current_meter_reading: Optional[int] = Field(
        default=None,
        ge=0,
    )

    # -------------------------------------------------
    # Preferred Visit Date
    # -------------------------------------------------

    expected_visit_date: Optional[date] = None

    # -------------------------------------------------
    # Remarks
    # -------------------------------------------------

    remarks: Optional[str] = Field(
        default=None,
        max_length=2000,
    )


# =====================================================
# CUSTOMER SERVICE REQUEST RESPONSE
# =====================================================


class CustomerServiceRequestResponse(BaseModel):

    id: int

    ticket_number: str

    subject: str

    complaint: str

    priority: str

    status: str

    request_source: str

    customer_id: int

    requested_by_user_id: int

    machine_id: int

    meter_reading: Optional[int] = None

    serial_number: Optional[str] = None

    assigned_engineer_id: Optional[int] = None

    reported_date: date

    expected_visit_date: Optional[date] = None

    completed_date: Optional[date] = None

    assigned_at: Optional[datetime] = None

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    closed_at: Optional[datetime] = None

    resolution: Optional[str] = None

    is_warranty: Optional[str] = None

    is_amc: Optional[str] = None

    customer_status: Optional[str] = None

    created_by: int

    updated_by: Optional[int] = None

    created_at: datetime

    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# CUSTOMER SERVICE REQUEST LIST
# =====================================================


class CustomerServiceRequestListResponse(BaseModel):

    success: bool = True

    customer_id: int

    total: int

    page: int

    page_size: int

    items: list[
        CustomerServiceRequestResponse
    ]


# =====================================================
# EXISTING SERVICE TICKET BASE
# =====================================================


class ServiceTicketBase(BaseModel):

    customer_id: int

    machine_id: int

    engineer_id: Optional[int] = None

    ticket_type: TicketType = (
        TicketType.BREAKDOWN
    )

    priority: TicketPriority = (
        TicketPriority.MEDIUM
    )

    subject: str = Field(
        ...,
        min_length=3,
        max_length=200,
    )

    complaint: str = Field(
        ...,
        min_length=5,
        max_length=1000,
    )

    problem_description: Optional[str] = None

    reported_date: date

    expected_visit_date: Optional[date] = None

    visit_date: Optional[date] = None

    completion_date: Optional[date] = None

    status: TicketStatus = (
        TicketStatus.REQUESTED
    )

    meter_reading: Optional[int] = 0

    remarks: Optional[str] = None


# =====================================================
# ADMIN CREATE
# =====================================================


class ServiceTicketCreate(ServiceTicketBase):
    """
    Admin/internal service creation.

    Unlike the customer portal request schema, Admin can create a
    service directly in any valid workflow status. This supports
    manually entering historical/already-completed services.
    """

    # -------------------------------------------------
    # Completion / manual-entry details
    # -------------------------------------------------

    material_used: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    service_cost: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    payment_status: Optional[str] = Field(
        default="PENDING",
        max_length=20,
    )


# =====================================================
# ADMIN / ENGINEER UPDATE
# =====================================================


class ServiceTicketUpdate(BaseModel):

    # -------------------------------------------------
    # General fields
    # -------------------------------------------------

    customer_id: Optional[int] = None

    machine_id: Optional[int] = None

    engineer_id: Optional[int] = None

    ticket_type: Optional[TicketType] = None

    priority: Optional[TicketPriority] = None

    subject: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=200,
    )

    complaint: Optional[str] = None

    problem_description: Optional[str] = None

    reported_date: Optional[date] = None

    expected_visit_date: Optional[date] = None

    visit_date: Optional[date] = None

    completion_date: Optional[date] = None

    status: Optional[TicketStatus] = None

    meter_reading: Optional[int] = None

    remarks: Optional[str] = None

    resolution: Optional[str] = None

    # =================================================
    # COMPLETION DETAILS
    # =================================================

    material_used: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    service_cost: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    # =================================================
    # PAYMENT STATUS
    #
    # Values used by the engineer portal:
    #
    # PENDING
    # RECEIVED
    #
    # This value is persisted to:
    # service_tickets.payment_status
    # =================================================

    payment_status: Optional[str] = Field(
        default=None,
        max_length=20,
    )


# =====================================================
# GENERAL SERVICE TICKET RESPONSE
# =====================================================


class ServiceTicketResponse(BaseModel):

    # =================================================
    # BASIC TICKET INFORMATION
    # =================================================

    id: int

    ticket_number: str

    subject: str

    complaint: str

    priority: str

    status: str

    request_source: str

    # =================================================
    # CUSTOMER IDs
    # =================================================

    customer_id: int

    requested_by_user_id: int

    # =================================================
    # MACHINE
    # =================================================

    machine_id: int

    serial_number: Optional[str] = None

    # =================================================
    # ENGINEER
    # =================================================

    assigned_engineer_id: Optional[int] = None

    engineer_id: Optional[int] = None

    # =================================================
    # DATES
    # =================================================

    reported_date: date

    expected_visit_date: Optional[date] = None

    visit_date: Optional[date] = None

    completed_date: Optional[date] = None

    completion_date: Optional[date] = None

    # =================================================
    # TIMESTAMPS
    # =================================================

    assigned_at: Optional[datetime] = None

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    closed_at: Optional[datetime] = None

    # =================================================
    # SERVICE DETAILS
    # =================================================

    resolution: Optional[str] = None

    # =================================================
    # COMPLETION DETAILS
    # =================================================

    material_used: Optional[str] = None

    service_cost: Optional[Decimal] = None

    # =================================================
    # PAYMENT STATUS
    # =================================================

    payment_status: Optional[str] = None

    problem_description: Optional[str] = None

    remarks: Optional[str] = None

    meter_reading: Optional[int] = None

    # =================================================
    # WARRANTY / AMC
    # =================================================

    is_warranty: Optional[str] = None

    is_amc: Optional[str] = None

    # =================================================
    # CUSTOMER STATUS
    # =================================================

    customer_status: Optional[str] = None

    # =================================================
    # AUDIT
    # =================================================

    created_by: int

    updated_by: Optional[int] = None

    created_at: datetime

    updated_at: Optional[datetime] = None

    # =================================================
    # CUSTOMER INFORMATION
    #
    # These fields are populated by
    # service_ticket_service.py
    # =================================================

    customer_name: Optional[str] = None

    phone: Optional[str] = None

    mobile: Optional[str] = None

    mobile_number: Optional[str] = None

    email: Optional[str] = None

    address: Optional[str] = None

    billing_address: Optional[str] = None

    shipping_address: Optional[str] = None

    city: Optional[str] = None

    state: Optional[str] = None

    country: Optional[str] = None

    pincode: Optional[str] = None

    # =================================================
    # CUSTOMER OBJECT
    # =================================================

    customer: Optional[dict[str, Any]] = None

    customer_details: Optional[dict[str, Any]] = None

    # =================================================
    # MACHINE INFORMATION
    # =================================================

    machine_number: Optional[str] = None

    machine_name: Optional[str] = None

    machine: Optional[dict[str, Any]] = None

    machine_details: Optional[dict[str, Any]] = None

    # =================================================
    # PRODUCT INFORMATION
    # =================================================

    product_id: Optional[int] = None

    product_name: Optional[str] = None

    product: Optional[dict[str, Any]] = None

    product_details: Optional[dict[str, Any]] = None

    # =================================================
    # ENGINEER INFORMATION
    # =================================================

    engineer_name: Optional[str] = None

    technician: Optional[str] = None

    engineer: Optional[dict[str, Any]] = None

    assigned_engineer: Optional[dict[str, Any]] = None

    engineer_details: Optional[dict[str, Any]] = None

    # =================================================
    # PYDANTIC CONFIG
    # =================================================

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# GENERAL LIST RESPONSE
# =====================================================


class ServiceTicketListResponse(BaseModel):

    total: int

    page: int

    page_size: int

    items: list[
        ServiceTicketResponse
    ]


# =====================================================
# DASHBOARD
# =====================================================


class ServiceTicketDashboardResponse(BaseModel):

    total_tickets: int

    requested_tickets: int

    assigned_tickets: int

    in_progress_tickets: int

    completed_tickets: int

    closed_tickets: int

    cancelled_tickets: int

    overdue_tickets: int


# =====================================================
# FILTER
# =====================================================


class ServiceTicketFilter(BaseModel):

    customer_id: Optional[int] = None

    machine_id: Optional[int] = None

    engineer_id: Optional[int] = None

    status: Optional[TicketStatus] = None

    priority: Optional[TicketPriority] = None

    ticket_type: Optional[TicketType] = None

    from_date: Optional[date] = None

    to_date: Optional[date] = None

    ticket_number: Optional[str] = None