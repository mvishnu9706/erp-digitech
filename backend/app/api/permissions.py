from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.role_permission import (
    RolePermissionCreate,
    RolePermissionUpdate,
    RolePermissionResponse,
)

from app.services.role_permission_service import (
    RolePermissionService,
)

from app.core.dependencies import (
    get_current_user,
    get_current_admin,
    get_current_super_admin,
)


# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


# =====================================================
# MANAGED ROLES
# =====================================================
#
# SUPER_ADMIN is NOT managed through the permission
# table.
#
# SUPER_ADMIN automatically has:
#
# ACCESS  = TRUE
# VIEW    = TRUE
# CREATE  = TRUE
# UPDATE  = TRUE
# DELETE  = TRUE
#
# =====================================================

MANAGED_ROLES = {
    "ADMIN",
    "CUSTOMER",
    "ENGINEER",
    "SALES_PERSON",
}


# =====================================================
# ALLOWED APPLICATION PAGES
# =====================================================

ALLOWED_PAGES = {
    "DASHBOARD",
    "PRODUCT_MASTER",
    "CUSTOMERS",
    "SUPPLIERS",
    "PURCHASE",
    "SALES",
    "INVENTORY",
    "SERVICE",
    "RENTAL_AMC",
    "REPORTS",
    "SETTINGS",
}


# =====================================================
# NORMALIZE ROLE
# =====================================================

def normalize_role(role: str) -> str:

    return (
        role
        .strip()
        .upper()
        .replace(" ", "_")
    )


# =====================================================
# NORMALIZE PAGE
# =====================================================

def normalize_page(page: str) -> str:

    return (
        page
        .strip()
        .upper()
        .replace(" ", "_")
    )


# =====================================================
# VALIDATE ROLE
# =====================================================

def validate_role(role: str) -> str:

    normalized_role = normalize_role(
        role
    )

    # -------------------------------------------------
    # SUPER ADMIN
    # -------------------------------------------------

    if normalized_role == "SUPER_ADMIN":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "SUPER_ADMIN has full access automatically "
                "and does not require permission records."
            ),
        )

    # -------------------------------------------------
    # NORMAL ROLES
    # -------------------------------------------------

    if normalized_role not in MANAGED_ROLES:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid role: {role}. "
                f"Allowed roles are: "
                f"{', '.join(sorted(MANAGED_ROLES))}"
            ),
        )

    return normalized_role


# =====================================================
# VALIDATE PAGE
# =====================================================

def validate_page(page: str) -> str:

    normalized_page = normalize_page(
        page
    )

    if normalized_page not in ALLOWED_PAGES:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid page: {page}. "
                f"Allowed pages are: "
                f"{', '.join(sorted(ALLOWED_PAGES))}"
            ),
        )

    return normalized_page


# =====================================================
# SERIALIZE PERMISSION
# =====================================================
#
# SQLAlchemy RolePermission objects must be converted
# to plain dictionaries before being returned inside
# a dictionary response.
#
# This also fixes:
#
# PydanticSerializationError
# Unable to serialize unknown type:
# RolePermission
#
# =====================================================

def serialize_permission(
    permission,
):

    # -------------------------------------------------
    # Already a dictionary
    # -------------------------------------------------

    if isinstance(
        permission,
        dict,
    ):

        return {
            "id": permission.get(
                "id",
                0,
            ),

            "role": permission.get(
                "role",
            ),

            "page": permission.get(
                "page",
            ),

            "can_access": bool(
                permission.get(
                    "can_access",
                    False,
                )
            ),

            "can_view": bool(
                permission.get(
                    "can_view",
                    False,
                )
            ),

            "can_create": bool(
                permission.get(
                    "can_create",
                    False,
                )
            ),

            "can_update": bool(
                permission.get(
                    "can_update",
                    False,
                )
            ),

            "can_delete": bool(
                permission.get(
                    "can_delete",
                    False,
                )
            ),
        }

    # -------------------------------------------------
    # SQLAlchemy RolePermission object
    # -------------------------------------------------

    return {
        "id": permission.id,

        "role": permission.role,

        "page": permission.page,

        "can_access": bool(
            permission.can_access
        ),

        "can_view": bool(
            permission.can_view
        ),

        "can_create": bool(
            permission.can_create
        ),

        "can_update": bool(
            permission.can_update
        ),

        "can_delete": bool(
            permission.can_delete
        ),
    }


# =====================================================
# GET CURRENT LOGGED-IN USER PERMISSIONS
# =====================================================
#
# GET /permissions/me
#
# THIS IS THE IMPORTANT NEW ENDPOINT.
#
# It is available to every authenticated user.
#
# The backend automatically determines the user's role:
#
# current_user.role
#
# and returns ONLY that role's permissions.
#
# =====================================================

@router.get(
    "/me",
    summary="Get My Permissions",
)
def get_my_permissions(

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    ),
):

    # =================================================
    # CHECK ACTIVE ACCOUNT
    # =================================================

    if not current_user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    # =================================================
    # GET CURRENT USER ROLE
    # =================================================

    normalized_role = normalize_role(
        current_user.role
    )

    # =================================================
    # SUPER ADMIN
    # =================================================
    #
    # Super Admin gets everything automatically.
    #
    # =================================================

    if normalized_role == "SUPER_ADMIN":

        permissions = []

        for page in sorted(
            ALLOWED_PAGES
        ):

            permissions.append({

                "id": 0,

                "role": "SUPER_ADMIN",

                "page": page,

                "can_access": True,

                "can_view": True,

                "can_create": True,

                "can_update": True,

                "can_delete": True,
            })

        return {
            "success": True,

            "role": "SUPER_ADMIN",

            "permissions": permissions,
        }

    # =================================================
    # VALIDATE NORMAL ROLE
    # =================================================

    if normalized_role not in MANAGED_ROLES:

        return {
            "success": True,

            "role": normalized_role,

            "permissions": [],
        }

    # =================================================
    # GET ROLE PERMISSIONS FROM DATABASE
    # =================================================

    permissions = (
        RolePermissionService.get_permissions(
            db=db,
            role=normalized_role,
        )
    )

    # =================================================
    # SERIALIZE
    # =================================================

    serialized_permissions = []

    for permission in permissions:

        serialized_permissions.append(
            serialize_permission(
                permission
            )
        )

    # =================================================
    # RETURN
    # =================================================

    return {
        "success": True,

        "role": normalized_role,

        "permissions": serialized_permissions,
    }


# =====================================================
# GET ALL PERMISSIONS
# =====================================================
#
# GET /permissions/
#
# ADMIN / SUPER_ADMIN ONLY
#
# =====================================================

@router.get(
    "/",
    response_model=List[
        RolePermissionResponse
    ],
    summary="Get All Role Permissions",
)
def get_all_permissions(

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    permissions = (
        RolePermissionService.get_all_permissions(
            db=db
        )
    )

    return permissions


# =====================================================
# GET PERMISSIONS FOR SELECTED ROLE
# =====================================================
#
# GET /permissions/{role}
#
# Used by Role Management.
#
# Examples:
#
# /permissions/ADMIN
# /permissions/CUSTOMER
# /permissions/ENGINEER
# /permissions/SALES_PERSON
#
# =====================================================

@router.get(
    "/{role}",
    response_model=dict,
    summary="Get Permissions For Role",
)
def get_role_permissions(

    role: str,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    normalized_role = normalize_role(
        role
    )

    # =================================================
    # SUPER ADMIN
    # =================================================

    if normalized_role == "SUPER_ADMIN":

        permissions = []

        for page in sorted(
            ALLOWED_PAGES
        ):

            permissions.append({

                "id": 0,

                "role": "SUPER_ADMIN",

                "page": page,

                "can_access": True,

                "can_view": True,

                "can_create": True,

                "can_update": True,

                "can_delete": True,
            })

        return {
            "role": "SUPER_ADMIN",

            "permissions": permissions,
        }

    # =================================================
    # VALIDATE ROLE
    # =================================================

    normalized_role = validate_role(
        normalized_role
    )

    # =================================================
    # GET DATABASE PERMISSIONS
    # =================================================

    permissions = (
        RolePermissionService.get_permissions(
            db=db,
            role=normalized_role,
        )
    )

    # =================================================
    # SERIALIZE
    # =================================================

    serialized_permissions = []

    for permission in permissions:

        serialized_permissions.append(
            serialize_permission(
                permission
            )
        )

    # =================================================
    # RETURN
    # =================================================

    return {
        "role": normalized_role,

        "permissions": serialized_permissions,
    }


# =====================================================
# CREATE PERMISSION
# =====================================================
#
# POST /permissions/
#
# ADMIN / SUPER_ADMIN
#
# =====================================================

@router.post(
    "/",
    response_model=RolePermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Role Permission",
)
def create_permission(

    permission: RolePermissionCreate,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    # -------------------------------------------------
    # SUPER ADMIN CANNOT BE STORED
    # -------------------------------------------------

    normalized_role = normalize_role(
        permission.role
    )

    if normalized_role == "SUPER_ADMIN":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "SUPER_ADMIN permissions are automatic "
                "and cannot be stored."
            ),
        )

    # -------------------------------------------------
    # CREATE
    # -------------------------------------------------

    created_permission = (
        RolePermissionService.create_permission(
            db=db,
            data=permission,
        )
    )

    return created_permission


# =====================================================
# UPDATE PERMISSION
# =====================================================
#
# PUT /permissions/{permission_id}
#
# =====================================================

@router.put(
    "/{permission_id}",
    response_model=RolePermissionResponse,
    summary="Update Role Permission",
)
def update_permission(

    permission_id: int,

    permission: RolePermissionUpdate,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    updated_permission = (
        RolePermissionService.update_permission(
            db=db,

            permission_id=permission_id,

            data=permission,
        )
    )

    return updated_permission


# =====================================================
# DELETE PERMISSION
# =====================================================
#
# DELETE /permissions/{permission_id}
#
# SUPER_ADMIN ONLY
#
# =====================================================

@router.delete(
    "/{permission_id}",
    summary="Delete Role Permission",
)
def delete_permission(

    permission_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_super_admin
    ),
):

    RolePermissionService.delete_permission(
        db=db,

        permission_id=permission_id,
    )

    return {
        "success": True,

        "message": (
            "Permission Deleted Successfully"
        ),

        "permission_id": permission_id,
    }


# =====================================================
# CHECK PAGE ACCESS
# =====================================================
#
# GET:
#
# /permissions/check-access/{role}/{page}
#
# This endpoint is for ADMIN / SUPER_ADMIN to check
# another role's permission.
#
# =====================================================

@router.get(
    "/check-access/{role}/{page}",
    summary="Check Page Access",
)
def check_page_access(

    role: str,

    page: str,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    normalized_role = normalize_role(
        role
    )

    normalized_page = validate_page(
        page
    )

    # =================================================
    # SUPER ADMIN
    # =================================================

    if normalized_role == "SUPER_ADMIN":

        return {

            "role": "SUPER_ADMIN",

            "page": normalized_page,

            "can_access": True,

            "can_view": True,

            "can_create": True,

            "can_update": True,

            "can_delete": True,
        }

    # =================================================
    # VALIDATE ROLE
    # =================================================

    normalized_role = validate_role(
        normalized_role
    )

    # =================================================
    # GET PERMISSION
    # =================================================

    permission = (
        RolePermissionService.get_permission(
            db=db,

            role=normalized_role,

            page=normalized_page,
        )
    )

    # =================================================
    # NO RECORD
    # =================================================

    if not permission:

        return {

            "role": normalized_role,

            "page": normalized_page,

            "can_access": False,

            "can_view": False,

            "can_create": False,

            "can_update": False,

            "can_delete": False,
        }

    # =================================================
    # RETURN
    # =================================================

    return {

        "role": normalized_role,

        "page": normalized_page,

        "can_access": bool(
            permission.can_access
        ),

        "can_view": bool(
            permission.can_view
        ),

        "can_create": bool(
            permission.can_create
        ),

        "can_update": bool(
            permission.can_update
        ),

        "can_delete": bool(
            permission.can_delete
        ),
    }