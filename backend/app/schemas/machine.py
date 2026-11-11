from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class MachineBase(BaseModel):
    customer_id: int
    product_id: Optional[int] = None
    machine_name: Optional[str] = Field(default=None, max_length=200)
    serial_number: str = Field(..., min_length=3, max_length=100)
    asset_tag: Optional[str] = None

    installation_date: Optional[date] = None
    installation_address: Optional[str] = None
    installed_by: Optional[int] = None

    warranty_start: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "warranty_start", "warranty_start_date"
        ),
    )
    warranty_end: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "warranty_end", "warranty_end_date"
        ),
    )
    amc_start: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices("amc_start", "amc_start_date"),
    )
    amc_end: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices("amc_end", "amc_end_date"),
    )

    # Legacy overall meter fields — retained for compatibility.
    opening_meter: int = Field(default=0, ge=0)
    current_meter: int = Field(default=0, ge=0)

    # Rental billing settings.
    rental_rate: Decimal = Field(default=Decimal("0.00"), ge=0)
    cost_per_copy: Decimal = Field(default=Decimal("0.00"), ge=0)

    # Legacy common free-copy allowance.
    # Retained for existing ERP functionality.
    free_prints_per_month: int = Field(default=0, ge=0)

    # Individual monthly free-copy allowances.
    a4_bw_free_copies: int = Field(default=0, ge=0)
    a4_color_free_copies: int = Field(default=0, ge=0)
    a3_bw_free_copies: int = Field(default=0, ge=0)
    a3_color_free_copies: int = Field(default=0, ge=0)

    # Separate rates for each print type.
    a4_bw_rate: Decimal = Field(default=Decimal("0.0000"), ge=0)
    a4_color_rate: Decimal = Field(default=Decimal("0.0000"), ge=0)
    a3_bw_rate: Decimal = Field(default=Decimal("0.0000"), ge=0)
    a3_color_rate: Decimal = Field(default=Decimal("0.0000"), ge=0)

    # Latest meter readings for each print type.
    a4_bw_current_meter: int = Field(default=0, ge=0)
    a4_color_current_meter: int = Field(default=0, ge=0)
    a3_bw_current_meter: int = Field(default=0, ge=0)
    a3_color_current_meter: int = Field(default=0, ge=0)

    status: str = "ACTIVE"
    is_active: bool = True
    remarks: Optional[str] = None


class MachineCreate(MachineBase):
    pass


class MachineUpdate(BaseModel):
    customer_id: Optional[int] = None
    product_id: Optional[int] = None
    machine_name: Optional[str] = Field(default=None, max_length=200)
    serial_number: Optional[str] = Field(
        default=None, min_length=3, max_length=100
    )
    asset_tag: Optional[str] = None

    installation_date: Optional[date] = None
    installation_address: Optional[str] = None
    installed_by: Optional[int] = None

    warranty_start: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "warranty_start", "warranty_start_date"
        ),
    )
    warranty_end: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "warranty_end", "warranty_end_date"
        ),
    )
    amc_start: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices("amc_start", "amc_start_date"),
    )
    amc_end: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices("amc_end", "amc_end_date"),
    )

    # Legacy overall meter fields.
    opening_meter: Optional[int] = Field(default=None, ge=0)
    current_meter: Optional[int] = Field(default=None, ge=0)

    # Rental billing settings.
    rental_rate: Optional[Decimal] = Field(default=None, ge=0)
    cost_per_copy: Optional[Decimal] = Field(default=None, ge=0)

    # Legacy common free-copy allowance.
    free_prints_per_month: Optional[int] = Field(default=None, ge=0)

    # Individual monthly free-copy allowances.
    # Optional so partial updates preserve unchanged values.
    a4_bw_free_copies: Optional[int] = Field(default=None, ge=0)
    a4_color_free_copies: Optional[int] = Field(default=None, ge=0)
    a3_bw_free_copies: Optional[int] = Field(default=None, ge=0)
    a3_color_free_copies: Optional[int] = Field(default=None, ge=0)

    # Separate print rates.
    a4_bw_rate: Optional[Decimal] = Field(default=None, ge=0)
    a4_color_rate: Optional[Decimal] = Field(default=None, ge=0)
    a3_bw_rate: Optional[Decimal] = Field(default=None, ge=0)
    a3_color_rate: Optional[Decimal] = Field(default=None, ge=0)

    # Separate current meter readings.
    a4_bw_current_meter: Optional[int] = Field(default=None, ge=0)
    a4_color_current_meter: Optional[int] = Field(default=None, ge=0)
    a3_bw_current_meter: Optional[int] = Field(default=None, ge=0)
    a3_color_current_meter: Optional[int] = Field(default=None, ge=0)

    status: Optional[str] = None
    is_active: Optional[bool] = None
    remarks: Optional[str] = None


class MachineResponse(MachineBase):
    id: int
    machine_number: str
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MachineListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[MachineResponse]


class MachineDashboardResponse(BaseModel):
    total_machines: int
    active_machines: int
    warranty_expiring: int
    amc_expiring: int
    rental_machines: int


class MachineFilter(BaseModel):
    customer_id: Optional[int] = None
    product_id: Optional[int] = None
    status: Optional[str] = None
    serial_number: Optional[str] = None
    machine_number: Optional[str] = None
    machine_name: Optional[str] = None
