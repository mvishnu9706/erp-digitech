from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


# ============================================================
# CUSTOMER MACHINE RESPONSE
# ============================================================

class CustomerMachineResponse(BaseModel):
    """
    Machine information returned for a customer.

    One customer can have multiple machines.
    """

    id: int

    machine_number: Optional[str] = None

    machine_name: Optional[str] = None

    serial_number: Optional[str] = None

    product_id: Optional[int] = None

    # --------------------------------------------------------
    # RENTAL / BILLING
    # --------------------------------------------------------

    rental_rate: Decimal = Decimal("0")

    rental_advance: Decimal = Decimal("0")

    free_prints_per_month: int = 0

    # Individual monthly free-copy allowances.
    a4_bw_free_copies: int = 0
    a4_color_free_copies: int = 0
    a3_bw_free_copies: int = 0
    a3_color_free_copies: int = 0

    # --------------------------------------------------------
    # COPY RATES
    # --------------------------------------------------------

    a4_bw_rate: Decimal = Decimal("0")

    a4_color_rate: Decimal = Decimal("0")

    a3_bw_rate: Decimal = Decimal("0")

    a3_color_rate: Decimal = Decimal("0")

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# CUSTOMER MACHINE CREATE
# ============================================================

class CustomerMachineCreate(BaseModel):
    """
    Machine entered while creating a customer.

    One customer can have multiple machines.

    Product is optional because machines created through
    the Add Customer form do not select a Product Master
    product.
    """

    machine_name: str = Field(
        ...,
        max_length=200
    )

    machine_serial_number: str = Field(
        ...,
        max_length=100
    )

    # --------------------------------------------------------
    # RENTAL / BILLING
    # --------------------------------------------------------

    # Fixed monthly rental amount.
    rental_rate: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )

    # Advance amount received from customer.
    rental_advance: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )

    # Free prints allowed per month.
    free_prints_per_month: int = Field(
        default=0,
        ge=0
    )

    # Individual monthly free-copy allowances.
    a4_bw_free_copies: int = Field(default=0, ge=0)
    a4_color_free_copies: int = Field(default=0, ge=0)
    a3_bw_free_copies: int = Field(default=0, ge=0)
    a3_color_free_copies: int = Field(default=0, ge=0)

    # --------------------------------------------------------
    # COPY RATES
    # --------------------------------------------------------

    # A4 Black & White
    a4_bw_rate: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )

    # A4 Color
    a4_color_rate: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )

    # A3 Black & White
    a3_bw_rate: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )

    # A3 Color
    a3_color_rate: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )


# ============================================================
# CUSTOMER MACHINE UPDATE
# ============================================================

class CustomerMachineUpdate(BaseModel):
    """
    Machine entered while editing a customer.

    If id is provided:
        Update that existing machine.

    If id is None:
        Create a new machine for the customer.
    """

    id: Optional[int] = None

    machine_name: str = Field(
        ...,
        max_length=200
    )

    machine_serial_number: str = Field(
        ...,
        max_length=100
    )

    # --------------------------------------------------------
    # RENTAL / BILLING
    # --------------------------------------------------------

    rental_rate: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )

    rental_advance: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )

    free_prints_per_month: int = Field(
        default=0,
        ge=0
    )

    # Individual monthly free-copy allowances.
    a4_bw_free_copies: int = Field(default=0, ge=0)
    a4_color_free_copies: int = Field(default=0, ge=0)
    a3_bw_free_copies: int = Field(default=0, ge=0)
    a3_color_free_copies: int = Field(default=0, ge=0)

    # --------------------------------------------------------
    # COPY RATES
    # --------------------------------------------------------

    a4_bw_rate: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )

    a4_color_rate: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )

    a3_bw_rate: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )

    a3_color_rate: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )


# ============================================================
# CUSTOMER BASE
# ============================================================

class CustomerBase(BaseModel):

    customer_name: str = Field(
        ...,
        max_length=200
    )

    contact_person: Optional[str] = None

    phone: Optional[str] = None

    email: Optional[EmailStr] = None

    website: Optional[str] = None

    # --------------------------------------------------------
    # TAX DETAILS
    # --------------------------------------------------------

    gstin: Optional[str] = None

    pan: Optional[str] = None

    # --------------------------------------------------------
    # ADDRESS
    # --------------------------------------------------------

    billing_address: Optional[str] = None

    shipping_address: Optional[str] = None

    city: Optional[str] = None

    state: Optional[str] = None

    country: Optional[str] = None

    pincode: Optional[str] = None

    # --------------------------------------------------------
    # FINANCIAL INFORMATION
    # --------------------------------------------------------

    credit_limit: Decimal = Decimal("0")

    credit_days: int = 0

    opening_balance: Decimal = Decimal("0")

    # --------------------------------------------------------
    # SERVICE PORTAL
    # --------------------------------------------------------

    service_enabled: bool = False

    # --------------------------------------------------------
    # REMARKS
    # --------------------------------------------------------

    remarks: Optional[str] = None

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    is_active: bool = True


# ============================================================
# CUSTOMER CREATE
# ============================================================

class CustomerCreate(CustomerBase):
    """
    Customer creation request.

    A customer can have:

        zero machines
        one machine
        multiple machines
    """

    machines: list[CustomerMachineCreate] = Field(
        default_factory=list
    )


# ============================================================
# CUSTOMER UPDATE
# ============================================================

class CustomerUpdate(BaseModel):

    customer_name: Optional[str] = None

    contact_person: Optional[str] = None

    phone: Optional[str] = None

    email: Optional[EmailStr] = None

    website: Optional[str] = None

    # --------------------------------------------------------
    # TAX DETAILS
    # --------------------------------------------------------

    gstin: Optional[str] = None

    pan: Optional[str] = None

    # --------------------------------------------------------
    # ADDRESS
    # --------------------------------------------------------

    billing_address: Optional[str] = None

    shipping_address: Optional[str] = None

    city: Optional[str] = None

    state: Optional[str] = None

    country: Optional[str] = None

    pincode: Optional[str] = None

    # --------------------------------------------------------
    # FINANCIAL INFORMATION
    # --------------------------------------------------------

    credit_limit: Optional[Decimal] = None

    credit_days: Optional[int] = None

    opening_balance: Optional[Decimal] = None

    # --------------------------------------------------------
    # SERVICE PORTAL
    # --------------------------------------------------------

    service_enabled: Optional[bool] = None

    # --------------------------------------------------------
    # REMARKS
    # --------------------------------------------------------

    remarks: Optional[str] = None

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    is_active: Optional[bool] = None

    # --------------------------------------------------------
    # MULTIPLE MACHINE UPDATE
    # --------------------------------------------------------

    machines: Optional[list[CustomerMachineUpdate]] = None

    # --------------------------------------------------------
    # BACKWARD COMPATIBILITY
    # --------------------------------------------------------

    machine_id: Optional[int] = None

    machine_name: Optional[str] = Field(
        default=None,
        max_length=200
    )

    machine_serial_number: Optional[str] = Field(
        default=None,
        max_length=100
    )


# ============================================================
# CUSTOMER RESPONSE
# ============================================================

class CustomerResponse(CustomerBase):

    id: int

    customer_code: str

    current_balance: Decimal

    service_enabled: bool

    created_by: Optional[int]

    updated_by: Optional[int]

    created_at: datetime

    updated_at: Optional[datetime]

    # --------------------------------------------------------
    # ALL CUSTOMER MACHINES
    # --------------------------------------------------------

    machines: list[CustomerMachineResponse] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # BACKWARD COMPATIBILITY
    # --------------------------------------------------------

    machine_id: Optional[int] = None

    machine_name: Optional[str] = None

    machine_serial_number: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# CUSTOMER DASHBOARD RESPONSE
# ============================================================

class CustomerDashboardResponse(BaseModel):

    total_customers: int

    active_customers: int

    inactive_customers: int

    total_outstanding: Decimal

    total_credit_limit: Decimal

    service_enabled_customers: int

    service_disabled_customers: int