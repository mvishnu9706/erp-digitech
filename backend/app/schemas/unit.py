from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UnitBase(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    short_name: str = Field(
        ...,
        min_length=1,
        max_length=20
    )

    is_active: bool = True


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):

    name: Optional[str] = None

    short_name: Optional[str] = None

    is_active: Optional[bool] = None


class UnitResponse(UnitBase):

    id: int

    created_by: Optional[int]

    updated_by: Optional[int]

    created_at: datetime

    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )