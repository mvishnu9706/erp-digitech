from typing import Optional

from pydantic import BaseModel, Field


# =====================================================
# ROLE PERMISSION BASE
# =====================================================

class RolePermissionBase(BaseModel):

    role: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )

    page: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    # -------------------------------------------------
    # Page Access
    # -------------------------------------------------

    can_access: bool = False

    # -------------------------------------------------
    # View Permission
    # -------------------------------------------------

    can_view: bool = False

    # -------------------------------------------------
    # Create Permission
    # -------------------------------------------------

    can_create: bool = False

    # -------------------------------------------------
    # Update Permission
    # -------------------------------------------------

    can_update: bool = False

    # -------------------------------------------------
    # Delete Permission
    # -------------------------------------------------

    can_delete: bool = False


# =====================================================
# CREATE ROLE PERMISSION
# =====================================================

class RolePermissionCreate(RolePermissionBase):
    pass


# =====================================================
# UPDATE ROLE PERMISSION
# =====================================================
#
# All fields are optional because we may update only
# one permission at a time.
#
# Example:
#
# {
#     "can_access": true
# }
#
# or:
#
# {
#     "can_create": true
# }
#
# =====================================================

class RolePermissionUpdate(BaseModel):

    role: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    page: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    can_access: Optional[bool] = None

    can_view: Optional[bool] = None

    can_create: Optional[bool] = None

    can_update: Optional[bool] = None

    can_delete: Optional[bool] = None


# =====================================================
# ROLE PERMISSION RESPONSE
# =====================================================

class RolePermissionResponse(BaseModel):

    id: int

    role: str

    page: str

    can_access: bool

    can_view: bool

    can_create: bool

    can_update: bool

    can_delete: bool

    class Config:
        from_attributes = True