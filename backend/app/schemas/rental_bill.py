
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RentalBillBase(BaseModel):
    billing_month: str = Field(
        ...,
        min_length=7,
        max_length=7,
        pattern=r"^\d{4}-\d{2}$",
    )
    billing_date: date

    # Retained for legacy single-meter billing.
    current_meter: Optional[int] = Field(default=None, ge=0)
    remarks: Optional[str] = None


class RentalBillCreate(RentalBillBase):
    machine_id: int = Field(..., gt=0)

    # Legacy billing fields.
    cost_per_copy: Optional[Decimal] = Field(default=None, ge=0)
    previous_meter: Optional[int] = Field(default=None, ge=0)
    payment_status: Optional[str] = Field(
        default="PENDING",
        max_length=20,
    )

    # New four-type billing readings.
    # When supplied, the backend can use four-type billing.
    # Missing readings should default to the machine's last saved
    # readings in the billing service.
    a4_bw_current_meter: Optional[int] = Field(default=None, ge=0)
    a4_color_current_meter: Optional[int] = Field(default=None, ge=0)
    a3_bw_current_meter: Optional[int] = Field(default=None, ge=0)
    a3_color_current_meter: Optional[int] = Field(default=None, ge=0)


class RentalBillUpdate(BaseModel):
    # Legacy billing fields.
    current_meter: Optional[int] = Field(default=None, ge=0)
    cost_per_copy: Optional[Decimal] = Field(default=None, ge=0)

    # Payment fields.
    payment_status: Optional[str] = Field(
        default=None,
        max_length=20,
    )
    paid_amount: Optional[Decimal] = Field(default=None, ge=0)
    remarks: Optional[str] = None

    # Four-type meter readings.
    a4_bw_current_meter: Optional[int] = Field(default=None, ge=0)
    a4_color_current_meter: Optional[int] = Field(default=None, ge=0)
    a3_bw_current_meter: Optional[int] = Field(default=None, ge=0)
    a3_color_current_meter: Optional[int] = Field(default=None, ge=0)


class RentalBillPaymentUpdate(BaseModel):
    payment_status: str = Field(..., max_length=20)
    paid_amount: Decimal = Field(..., ge=0)
    remarks: Optional[str] = None


class RentalBillResponse(RentalBillBase):
    id: int
    bill_number: str
    customer_id: int
    machine_id: int

    # Legacy aggregate billing fields.
    current_meter: int
    previous_meter: int
    copies_used: int
    cost_per_copy: Decimal
    total_amount: Decimal

    # Payment tracking.
    payment_status: str
    paid_amount: Decimal
    outstanding_amount: Decimal

    created_by: int
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # Billing mode.
    billing_mode: str

    # A4 Black and White.
    a4_bw_previous_meter: int
    a4_bw_current_meter: int
    a4_bw_copies_used: int
    a4_bw_free_copies: int
    a4_bw_rate: Decimal
    a4_bw_amount: Decimal

    # A4 Color.
    a4_color_previous_meter: int
    a4_color_current_meter: int
    a4_color_copies_used: int
    a4_color_free_copies: int
    a4_color_rate: Decimal
    a4_color_amount: Decimal

    # A3 Black and White.
    a3_bw_previous_meter: int
    a3_bw_current_meter: int
    a3_bw_copies_used: int
    a3_bw_free_copies: int
    a3_bw_rate: Decimal
    a3_bw_amount: Decimal

    # A3 Color.
    a3_color_previous_meter: int
    a3_color_current_meter: int
    a3_color_copies_used: int
    a3_color_free_copies: int
    a3_color_rate: Decimal
    a3_color_amount: Decimal

    # Rental, free-copy allowance, and tax breakdown.
    rental_amount: Decimal
    free_copy_allowance: int
    free_copies_applied: int
    copy_charges_amount: Decimal
    subtotal_amount: Decimal
    gst_rate: Decimal
    gst_amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class RentalBillListResponse(BaseModel):
    items: list[RentalBillResponse]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)
