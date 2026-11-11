from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field
)


# =====================================================
# Base Schema
# =====================================================

class SupplierBase(BaseModel):

    company_name: str = Field(
        ...,
        max_length=200
    )

    contact_person: Optional[str] = Field(
        default=None,
        max_length=150
    )

    phone: Optional[str] = Field(
        default=None,
        max_length=20
    )

    alternate_phone: Optional[str] = Field(
        default=None,
        max_length=25
    )

    contact_designation: Optional[str] = Field(
        default=None,
        max_length=100
    )

    email: Optional[EmailStr] = None

    website: Optional[str] = Field(
        default=None,
        max_length=255
    )

    gstin: Optional[str] = Field(
        default=None,
        max_length=20
    )

    pan: Optional[str] = Field(
        default=None,
        max_length=20
    )

    address: Optional[str] = None

    city: Optional[str] = Field(
        default=None,
        max_length=100
    )

    state: Optional[str] = Field(
        default=None,
        max_length=100
    )

    country: Optional[str] = Field(
        default=None,
        max_length=100
    )

    pincode: Optional[str] = Field(
        default=None,
        max_length=20
    )

    credit_limit: Decimal = Field(
        default=0,
        ge=0
    )

    credit_days: int = Field(
        default=0,
        ge=0
    )

    opening_balance: Decimal = Field(
        default=0
    )

    model_config = ConfigDict(
        from_attributes=True
    )

    remarks: Optional[str] = None

    is_active: bool = True


# =====================================================
# Create
# =====================================================

class SupplierCreate(SupplierBase):
    pass


# =====================================================
# Update
# =====================================================

class SupplierUpdate(BaseModel):

    company_name: Optional[str] = None

    contact_person: Optional[str] = None

    phone: Optional[str] = None

    alternate_phone: Optional[str] = None
    
    contact_designation: Optional[str] = None

    email: Optional[EmailStr] = None

    website: Optional[str] = None

    gstin: Optional[str] = None

    pan: Optional[str] = None

    address: Optional[str] = None

    city: Optional[str] = None

    state: Optional[str] = None

    country: Optional[str] = None

    pincode: Optional[str] = None

    credit_limit: Optional[Decimal] = Field(
        default=None,
        ge=0
    )

    credit_days: Optional[int] = Field(
        default=None,
        ge=0
    )

    opening_balance: Optional[Decimal] = None

    remarks: Optional[str] = None

    is_active: Optional[bool] = None


# =====================================================
# Response
# =====================================================

class SupplierResponse(SupplierBase):

    id: int

    supplier_code: str

    current_balance: Decimal

    created_by: Optional[int]

    updated_by: Optional[int]

    created_at: datetime

    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Dashboard Card
# =====================================================

class SupplierDashboardResponse(BaseModel):

    total_suppliers: int

    active_suppliers: int

    inactive_suppliers: int

    total_outstanding: Decimal

    total_credit_limit: Decimal


# =====================================================
# List Response
# =====================================================

class SupplierListResponse(BaseModel):

    total_records: int

    page: int

    page_size: int

    suppliers: list[SupplierResponse]