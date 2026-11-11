from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.role_permission import RolePermission

from app.schemas.role_permission import (
    RolePermissionCreate,
    RolePermissionUpdate,
)


# =====================================================
# MANAGED ROLES
# =====================================================
#
# SUPER_ADMIN is NOT stored in role_permissions.
#
# SUPER_ADMIN automatically has:
#
# Access  = TRUE
# View    = TRUE
# Create  = TRUE
# Update  = TRUE
# Delete  = TRUE
#
# =====================================================

MANAGED_ROLES = {
    "ADMIN",
    "CUSTOMER",
    "ENGINEER",
    "SALES_PERSON",
}


# =====================================================
# VALID PAGES
# =====================================================

VALID_PAGES = {
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
# ROLE PERMISSION SERVICE
# =====================================================

class RolePermissionService:

    # =================================================
    # NORMALIZE ROLE
    # =================================================

    @staticmethod
    def normalize_role(role: str) -> str:

        return (
            role
            .strip()
            .upper()
            .replace(" ", "_")
        )

    # =================================================
    # NORMALIZE PAGE
    # =================================================

    @staticmethod
    def normalize_page(page: str) -> str:

        return (
            page
            .strip()
            .upper()
            .replace(" ", "_")
        )

    # =================================================
    # VALIDATE ROLE
    # =================================================

    @staticmethod
    def validate_role(role: str) -> str:

        role = RolePermissionService.normalize_role(
            role
        )

        # -------------------------------------------------
        # SUPER ADMIN
        # -------------------------------------------------

        if role == "SUPER_ADMIN":

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

        if role not in MANAGED_ROLES:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid permission role: {role}. "
                    f"Allowed roles: "
                    f"{', '.join(sorted(MANAGED_ROLES))}"
                ),
            )

        return role

    # =================================================
    # VALIDATE PAGE
    # =================================================

    @staticmethod
    def validate_page(page: str) -> str:

        page = RolePermissionService.normalize_page(
            page
        )

        if page not in VALID_PAGES:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid page: {page}. "
                    f"Allowed pages: "
                    f"{', '.join(sorted(VALID_PAGES))}"
                ),
            )

        return page

    # =================================================
    # GET ALL PERMISSIONS
    # =================================================
    #
    # Returns all database permission records.
    #
    # SUPER_ADMIN is intentionally NOT included because
    # SUPER_ADMIN has automatic full access.
    #
    # =================================================

    @staticmethod
    def get_all_permissions(
        db: Session,
    ):

        return (
            db.query(RolePermission)
            .filter(
                RolePermission.role.in_(
                    MANAGED_ROLES
                )
            )
            .order_by(
                RolePermission.role.asc(),
                RolePermission.page.asc(),
            )
            .all()
        )

    # =================================================
    # GET PERMISSIONS FOR ROLE
    # =================================================
    #
    # Returns all permissions for a particular role.
    #
    # SUPER_ADMIN gets virtual full-access permissions.
    #
    # =================================================

    @staticmethod
    def get_permissions(
        db: Session,
        role: str,
    ):

        role = RolePermissionService.normalize_role(
            role
        )

        # -------------------------------------------------
        # SUPER ADMIN
        # -------------------------------------------------

        if role == "SUPER_ADMIN":

            return [
                {
                    "id": 0,
                    "role": "SUPER_ADMIN",
                    "page": page,
                    "can_access": True,
                    "can_view": True,
                    "can_create": True,
                    "can_update": True,
                    "can_delete": True,
                }
                for page in sorted(
                    VALID_PAGES
                )
            ]

        # -------------------------------------------------
        # Validate normal role
        # -------------------------------------------------

        role = RolePermissionService.validate_role(
            role
        )

        # -------------------------------------------------
        # Database permissions
        # -------------------------------------------------

        permissions = (
            db.query(RolePermission)
            .filter(
                RolePermission.role == role
            )
            .order_by(
                RolePermission.page.asc()
            )
            .all()
        )

        return permissions

    # =================================================
    # GET SINGLE PERMISSION
    # =================================================

    @staticmethod
    def get_permission(
        db: Session,
        role: str,
        page: str,
    ):

        role = RolePermissionService.normalize_role(
            role
        )

        page = RolePermissionService.normalize_page(
            page
        )

        # -------------------------------------------------
        # SUPER ADMIN
        # -------------------------------------------------

        if role == "SUPER_ADMIN":

            return {
                "id": 0,
                "role": "SUPER_ADMIN",
                "page": page,
                "can_access": True,
                "can_view": True,
                "can_create": True,
                "can_update": True,
                "can_delete": True,
            }

        # -------------------------------------------------
        # Validate
        # -------------------------------------------------

        role = RolePermissionService.validate_role(
            role
        )

        page = RolePermissionService.validate_page(
            page
        )

        # -------------------------------------------------
        # Database
        # -------------------------------------------------

        return (
            db.query(RolePermission)
            .filter(
                RolePermission.role == role,
                RolePermission.page == page,
            )
            .first()
        )

    # =================================================
    # CREATE PERMISSION
    # =================================================

    @staticmethod
    def create_permission(
        db: Session,
        data: RolePermissionCreate,
    ):

        # -------------------------------------------------
        # Validate
        # -------------------------------------------------

        role = RolePermissionService.validate_role(
            data.role
        )

        page = RolePermissionService.validate_page(
            data.page
        )

        # -------------------------------------------------
        # Check duplicate
        # -------------------------------------------------

        existing = (
            db.query(RolePermission)
            .filter(
                RolePermission.role == role,
                RolePermission.page == page,
            )
            .first()
        )

        if existing:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Permission already exists for "
                    f"{role} / {page}"
                ),
            )

        # -------------------------------------------------
        # Create permission
        # -------------------------------------------------

        permission = RolePermission(

            role=role,

            page=page,

            can_access=bool(
                data.can_access
            ),

            can_view=bool(
                data.can_view
            ),

            can_create=bool(
                data.can_create
            ),

            can_update=bool(
                data.can_update
            ),

            can_delete=bool(
                data.can_delete
            ),
        )

        db.add(
            permission
        )

        db.commit()

        db.refresh(
            permission
        )

        return permission

    # =================================================
    # UPDATE PERMISSION
    # =================================================

    @staticmethod
    def update_permission(
        db: Session,
        permission_id: int,
        data: RolePermissionUpdate,
    ):

        # -------------------------------------------------
        # Find permission
        # -------------------------------------------------

        permission = (
            db.query(RolePermission)
            .filter(
                RolePermission.id == permission_id
            )
            .first()
        )

        if not permission:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found.",
            )

        # -------------------------------------------------
        # Current values
        # -------------------------------------------------

        current_role = (
            RolePermissionService.normalize_role(
                permission.role
            )
        )

        current_page = (
            RolePermissionService.normalize_page(
                permission.page
            )
        )

        # -------------------------------------------------
        # SUPER_ADMIN protection
        # -------------------------------------------------

        if current_role == "SUPER_ADMIN":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "SUPER_ADMIN permissions cannot "
                    "be modified."
                ),
            )

        # -------------------------------------------------
        # New role
        # -------------------------------------------------

        new_role = current_role

        if data.role is not None:

            new_role = (
                RolePermissionService.validate_role(
                    data.role
                )
            )

        # -------------------------------------------------
        # New page
        # -------------------------------------------------

        new_page = current_page

        if data.page is not None:

            new_page = (
                RolePermissionService.validate_page(
                    data.page
                )
            )

        # -------------------------------------------------
        # Check duplicate role + page
        # -------------------------------------------------
        #
        # Only check if role/page is actually changing.
        #
        # -------------------------------------------------

        if (
            new_role != current_role
            or new_page != current_page
        ):

            duplicate = (
                db.query(RolePermission)
                .filter(
                    RolePermission.role == new_role,
                    RolePermission.page == new_page,
                    RolePermission.id != permission_id,
                )
                .first()
            )

            if duplicate:

                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Permission already exists for "
                        f"{new_role} / {new_page}"
                    ),
                )

        # -------------------------------------------------
        # Apply role
        # -------------------------------------------------

        permission.role = new_role

        # -------------------------------------------------
        # Apply page
        # -------------------------------------------------

        permission.page = new_page

        # -------------------------------------------------
        # ACCESS
        # -------------------------------------------------

        if data.can_access is not None:

            permission.can_access = (
                data.can_access
            )

        # -------------------------------------------------
        # VIEW
        # -------------------------------------------------

        if data.can_view is not None:

            permission.can_view = (
                data.can_view
            )

        # -------------------------------------------------
        # CREATE
        # -------------------------------------------------

        if data.can_create is not None:

            permission.can_create = (
                data.can_create
            )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        if data.can_update is not None:

            permission.can_update = (
                data.can_update
            )

        # -------------------------------------------------
        # DELETE
        # -------------------------------------------------

        if data.can_delete is not None:

            permission.can_delete = (
                data.can_delete
            )

        # -------------------------------------------------
        # Save
        # -------------------------------------------------

        try:

            db.commit()

            db.refresh(
                permission
            )

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Unable to update permission. "
                    "The role and page combination "
                    "may already exist."
                ),
            )

        return permission

    # =================================================
    # DELETE PERMISSION
    # =================================================

    @staticmethod
    def delete_permission(
        db: Session,
        permission_id: int,
    ):

        permission = (
            db.query(RolePermission)
            .filter(
                RolePermission.id == permission_id
            )
            .first()
        )

        if not permission:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found.",
            )

        # -------------------------------------------------
        # Never delete SUPER_ADMIN
        # -------------------------------------------------

        if (
            RolePermissionService.normalize_role(
                permission.role
            )
            == "SUPER_ADMIN"
        ):

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "SUPER_ADMIN permissions cannot "
                    "be deleted."
                ),
            )

        db.delete(
            permission
        )

        db.commit()

        return True

    # =================================================
    # CHECK PAGE ACCESS
    # =================================================

    @staticmethod
    def has_access(
        db: Session,
        role: str,
        page: str,
    ) -> bool:

        role = RolePermissionService.normalize_role(
            role
        )

        page = RolePermissionService.normalize_page(
            page
        )

        # -------------------------------------------------
        # SUPER ADMIN
        # -------------------------------------------------

        if role == "SUPER_ADMIN":

            return True

        # -------------------------------------------------
        # Permission
        # -------------------------------------------------

        permission = (
            RolePermissionService.get_permission(
                db=db,
                role=role,
                page=page,
            )
        )

        if not permission:

            return False

        return bool(
            permission.can_access
        )

    # =================================================
    # CHECK VIEW
    # =================================================

    @staticmethod
    def can_view(
        db: Session,
        role: str,
        page: str,
    ) -> bool:

        role = RolePermissionService.normalize_role(
            role
        )

        page = RolePermissionService.normalize_page(
            page
        )

        # -------------------------------------------------
        # SUPER ADMIN
        # -------------------------------------------------

        if role == "SUPER_ADMIN":

            return True

        # -------------------------------------------------
        # Permission
        # -------------------------------------------------

        permission = (
            RolePermissionService.get_permission(
                db=db,
                role=role,
                page=page,
            )
        )

        if not permission:

            return False

        return bool(
            permission.can_view
        )

    # =================================================
    # CHECK CREATE
    # =================================================

    @staticmethod
    def can_create(
        db: Session,
        role: str,
        page: str,
    ) -> bool:

        role = RolePermissionService.normalize_role(
            role
        )

        page = RolePermissionService.normalize_page(
            page
        )

        # -------------------------------------------------
        # SUPER ADMIN
        # -------------------------------------------------

        if role == "SUPER_ADMIN":

            return True

        # -------------------------------------------------
        # Permission
        # -------------------------------------------------

        permission = (
            RolePermissionService.get_permission(
                db=db,
                role=role,
                page=page,
            )
        )

        if not permission:

            return False

        return bool(
            permission.can_create
        )

    # =================================================
    # CHECK UPDATE
    # =================================================

    @staticmethod
    def can_update(
        db: Session,
        role: str,
        page: str,
    ) -> bool:

        role = RolePermissionService.normalize_role(
            role
        )

        page = RolePermissionService.normalize_page(
            page
        )

        # -------------------------------------------------
        # SUPER ADMIN
        # -------------------------------------------------

        if role == "SUPER_ADMIN":

            return True

        # -------------------------------------------------
        # Permission
        # -------------------------------------------------

        permission = (
            RolePermissionService.get_permission(
                db=db,
                role=role,
                page=page,
            )
        )

        if not permission:

            return False

        return bool(
            permission.can_update
        )

    # =================================================
    # CHECK DELETE
    # =================================================

    @staticmethod
    def can_delete(
        db: Session,
        role: str,
        page: str,
    ) -> bool:

        role = RolePermissionService.normalize_role(
            role
        )

        page = RolePermissionService.normalize_page(
            page
        )

        # -------------------------------------------------
        # SUPER ADMIN
        # -------------------------------------------------

        if role == "SUPER_ADMIN":

            return True

        # -------------------------------------------------
        # Permission
        # -------------------------------------------------

        permission = (
            RolePermissionService.get_permission(
                db=db,
                role=role,
                page=page,
            )
        )

        if not permission:

            return False

        return bool(
            permission.can_delete
        )