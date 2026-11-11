from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BrandBase(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Brand Name"
    )

    code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Unique Brand Code"
    )

    logo: Optional[str] = None

    website: Optional[str] = None

    email: Optional[EmailStr] = None

    phone: Optional[str] = Field(
        default=None,
        max_length=20
    )

    description: Optional[str] = None

    is_active: bool = True


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    code: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50
    )

    logo: Optional[str] = None

    website: Optional[str] = None

    email: Optional[EmailStr] = None

    phone: Optional[str] = None

    description: Optional[str] = None

    is_active: Optional[bool] = None


class BrandResponse(BrandBase):

    id: int

    created_by: Optional[int]

    updated_by: Optional[int]

    created_at: datetime

    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )