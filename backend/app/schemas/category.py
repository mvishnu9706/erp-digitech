from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    code: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    description: Optional[str] = None

    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):

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

    description: Optional[str] = None

    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):

    id: int

    created_by: Optional[int]

    updated_by: Optional[int]

    created_at: datetime

    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )