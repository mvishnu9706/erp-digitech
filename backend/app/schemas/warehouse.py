from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ======================================================
# Base Schema
# ======================================================

class WarehouseBase(BaseModel):

    warehouse_code: str = Field(
        ...,
        min_length=2,
        max_length=20
    )

    warehouse_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    contact_person: Optional[str] = Field(
        default=None,
        max_length=150
    )

    phone: Optional[str] = Field(
        default=None,
        max_length=20
    )

    email: Optional[EmailStr] = None

    address: Optional[str] = Field(
        default=None,
        max_length=300
    )

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

    is_default: bool = False

    is_active: bool = True


# ======================================================
# Create
# ======================================================

class WarehouseCreate(WarehouseBase):
    pass


# ======================================================
# Update
# ======================================================

class WarehouseUpdate(BaseModel):

    warehouse_code: Optional[str] = None

    warehouse_name: Optional[str] = None

    contact_person: Optional[str] = None

    phone: Optional[str] = None

    email: Optional[EmailStr] = None

    address: Optional[str] = None

    city: Optional[str] = None

    state: Optional[str] = None

    country: Optional[str] = None

    pincode: Optional[str] = None

    is_default: Optional[bool] = None

    is_active: Optional[bool] = None


# ======================================================
# Response
# ======================================================

class WarehouseResponse(WarehouseBase):

    id: int

    created_by: Optional[int]

    updated_by: Optional[int]

    created_at: datetime

    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )