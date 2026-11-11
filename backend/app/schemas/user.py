from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
)


# =====================================================
# Base User
# =====================================================

class UserBase(BaseModel):

    # -------------------------------------------------
    # Full Name
    # -------------------------------------------------

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    # -------------------------------------------------
    # Email
    # -------------------------------------------------

    email: EmailStr

    # -------------------------------------------------
    # Phone / Mobile
    # -------------------------------------------------

    phone: Optional[str] = Field(
        default=None,
        max_length=20,
    )


# =====================================================
# Create User
# =====================================================

class UserCreate(UserBase):

    # -------------------------------------------------
    # Password
    # -------------------------------------------------

    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
    )

    # -------------------------------------------------
    # PORTAL PASSWORD
    # -------------------------------------------------

    portal_password: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=128,
    )

    # -------------------------------------------------
    # Customer Assignment
    #
    # Used only when the user is a CUSTOMER.
    #
    # Other roles can leave this NULL.
    # -------------------------------------------------

    customer_id: Optional[int] = None


# =====================================================
# Create User With Role
# =====================================================

class AdminUserCreate(BaseModel):

    # -------------------------------------------------
    # Company Name
    # -------------------------------------------------

    company_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    # -------------------------------------------------
    # Contact Person Name
    # -------------------------------------------------

    contact_person_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    # -------------------------------------------------
    # Email
    # -------------------------------------------------

    email: EmailStr

    # -------------------------------------------------
    # Mobile Number
    # -------------------------------------------------

    phone: Optional[str] = Field(
        default=None,
        max_length=20,
    )

    # -------------------------------------------------
    # Password
    # -------------------------------------------------

    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
    )

    # -------------------------------------------------
    # PORTAL PASSWORD
    # -------------------------------------------------
    #
    # This is the password entered by the admin for the
    # Customer Portal account.
    #
    # It is separate from the hashed "password" field.
    #
    # -------------------------------------------------

    portal_password: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=128,
    )

    # -------------------------------------------------
    # Role
    # -------------------------------------------------

    role: str

    # -------------------------------------------------
    # Customer Assignment
    #
    # When creating a CUSTOMER login, select which
    # customer this login belongs to.
    # -------------------------------------------------

    customer_id: Optional[int] = None

    # -------------------------------------------------
    # CUSTOMER PORTAL MODULE ACCESS
    # -------------------------------------------------
    #
    # Default:
    #     Service = enabled
    #     Rental  = disabled
    #
    # This preserves the current frontend behavior for
    # existing Service portal functionality.
    # -------------------------------------------------

    service_access: bool = True

    rental_access: bool = False


# =====================================================
# Update User
# =====================================================

class UserUpdate(BaseModel):

    # -------------------------------------------------
    # Company Name
    # -------------------------------------------------

    company_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    # -------------------------------------------------
    # Contact Person Name
    # -------------------------------------------------

    contact_person_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    # -------------------------------------------------
    # Full Name
    # -------------------------------------------------

    full_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    # -------------------------------------------------
    # Email
    # -------------------------------------------------

    email: Optional[EmailStr] = None

    # -------------------------------------------------
    # Phone / Mobile
    # -------------------------------------------------

    phone: Optional[str] = Field(
        default=None,
        max_length=20,
    )

    # -------------------------------------------------
    # Role
    # -------------------------------------------------

    role: Optional[str] = None

    # -------------------------------------------------
    # Customer Assignment
    #
    # Allows ADMIN to change which customer a CUSTOMER
    # login belongs to.
    # -------------------------------------------------

    customer_id: Optional[int] = None

    # -------------------------------------------------
    # PORTAL PASSWORD
    # -------------------------------------------------

    portal_password: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=128,
    )

    # -------------------------------------------------
    # Active / Inactive
    # -------------------------------------------------

    is_active: Optional[bool] = None

    # =================================================
    # CUSTOMER PORTAL MODULE ACCESS
    # =================================================
    #
    # These are Optional because UserUpdate is a partial
    # update schema.
    #
    # Example:
    #
    # {
    #     "rental_access": true
    # }
    #
    # changes only Rental access.
    #
    # Example:
    #
    # {
    #     "service_access": false,
    #     "rental_access": true
    # }
    #
    # changes both.
    # =================================================

    service_access: Optional[bool] = None

    rental_access: Optional[bool] = None


# =====================================================
# Change Password
# =====================================================

class PasswordChangeRequest(BaseModel):

    new_password: str = Field(
        ...,
        min_length=6,
        max_length=128,
    )

    confirm_password: str = Field(
        ...,
        min_length=6,
        max_length=128,
    )


# =====================================================
# User Response
# =====================================================

class UserResponse(BaseModel):

    # -------------------------------------------------
    # ID
    # -------------------------------------------------

    id: int

    # -------------------------------------------------
    # Company
    # -------------------------------------------------

    company_name: Optional[str] = None

    # -------------------------------------------------
    # Contact Person
    # -------------------------------------------------

    contact_person_name: Optional[str] = None

    # -------------------------------------------------
    # Full Name
    # -------------------------------------------------

    full_name: str

    # -------------------------------------------------
    # Email
    # -------------------------------------------------

    email: EmailStr

    # -------------------------------------------------
    # Phone
    # -------------------------------------------------

    phone: Optional[str] = None

    # -------------------------------------------------
    # Role
    # -------------------------------------------------

    role: str

    # -------------------------------------------------
    # Customer ID
    #
    # This tells the frontend which customer this
    # CUSTOMER login belongs to.
    # -------------------------------------------------

    customer_id: Optional[int] = None

    # =================================================
    # CUSTOMER PORTAL MODULE ACCESS
    # =================================================
    #
    # These values are returned to the frontend so the
    # Customer Portal can determine which modules the
    # customer has access to.
    # =================================================

    service_access: bool = True

    rental_access: bool = False

    # -------------------------------------------------
    # Account Status
    # -------------------------------------------------

    is_active: bool

    # -------------------------------------------------
    # Pydantic ORM Support
    # -------------------------------------------------

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# ROLE PERMISSION SCHEMAS
# =====================================================


# =====================================================
# Permission Page Names
# =====================================================

class PermissionPage:

    DASHBOARD = "DASHBOARD"

    PRODUCT_MASTER = "PRODUCT_MASTER"

    CUSTOMERS = "CUSTOMERS"

    SUPPLIERS = "SUPPLIERS"

    PURCHASE = "PURCHASE"

    SALES = "SALES"

    INVENTORY = "INVENTORY"

    SERVICE = "SERVICE"

    RENTAL_AMC = "RENTAL_AMC"

    REPORTS = "REPORTS"

    SETTINGS = "SETTINGS"


# =====================================================
# Role Permission Base
# =====================================================

class RolePermissionBase(BaseModel):

    # -------------------------------------------------
    # Role
    # -------------------------------------------------

    role: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )

    # -------------------------------------------------
    # Page
    # -------------------------------------------------

    page: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    # -------------------------------------------------
    # View
    # -------------------------------------------------

    can_view: bool = False

    # -------------------------------------------------
    # Create
    # -------------------------------------------------

    can_create: bool = False

    # -------------------------------------------------
    # Update
    # -------------------------------------------------

    can_update: bool = False

    # -------------------------------------------------
    # Delete
    # -------------------------------------------------

    can_delete: bool = False


# =====================================================
# Create / Update Permission
# =====================================================

class RolePermissionCreate(RolePermissionBase):
    pass


class RolePermissionUpdate(BaseModel):

    # -------------------------------------------------
    # Role
    # -------------------------------------------------

    role: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    # -------------------------------------------------
    # Page
    # -------------------------------------------------

    page: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    # -------------------------------------------------
    # Permissions
    # -------------------------------------------------

    can_view: Optional[bool] = None

    can_create: Optional[bool] = None

    can_update: Optional[bool] = None

    can_delete: Optional[bool] = None


# =====================================================
# Permission Response
# =====================================================

class RolePermissionResponse(RolePermissionBase):

    id: int

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Permission List Response
# =====================================================

class RolePermissionListResponse(BaseModel):

    role: str

    permissions: list[RolePermissionResponse]