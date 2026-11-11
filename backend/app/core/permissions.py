from enum import Enum
from typing import List

from fastapi import Depends, HTTPException, status

from app.core.dependencies import get_current_user


# =====================================================
# Permission Constants
# =====================================================

class Permission(str, Enum):

    # Dashboard
    DASHBOARD_VIEW = "dashboard.view"

    # Users
    USER_VIEW = "user.view"
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"

    # Roles
    ROLE_VIEW = "role.view"
    ROLE_CREATE = "role.create"
    ROLE_UPDATE = "role.update"
    ROLE_DELETE = "role.delete"

    # Customers
    CUSTOMER_VIEW = "customer.view"
    CUSTOMER_CREATE = "customer.create"
    CUSTOMER_UPDATE = "customer.update"
    CUSTOMER_DELETE = "customer.delete"

    # Suppliers
    SUPPLIER_VIEW = "supplier.view"
    SUPPLIER_CREATE = "supplier.create"
    SUPPLIER_UPDATE = "supplier.update"
    SUPPLIER_DELETE = "supplier.delete"

    # Products
    PRODUCT_VIEW = "product.view"
    PRODUCT_CREATE = "product.create"
    PRODUCT_UPDATE = "product.update"
    PRODUCT_DELETE = "product.delete"

    # Categories
    CATEGORY_VIEW = "category.view"
    CATEGORY_CREATE = "category.create"
    CATEGORY_UPDATE = "category.update"
    CATEGORY_DELETE = "category.delete"

    # Brands
    BRAND_VIEW = "brand.view"
    BRAND_CREATE = "brand.create"
    BRAND_UPDATE = "brand.update"
    BRAND_DELETE = "brand.delete"

    # Units
    UNIT_VIEW = "unit.view"
    UNIT_CREATE = "unit.create"
    UNIT_UPDATE = "unit.update"
    UNIT_DELETE = "unit.delete"

    # Warehouses
    WAREHOUSE_VIEW = "warehouse.view"
    WAREHOUSE_CREATE = "warehouse.create"
    WAREHOUSE_UPDATE = "warehouse.update"
    WAREHOUSE_DELETE = "warehouse.delete"

    # Inventory
    INVENTORY_VIEW = "inventory.view"
    INVENTORY_UPDATE = "inventory.update"
    INVENTORY_TRANSFER = "inventory.transfer"

    # Purchase
    PURCHASE_VIEW = "purchase.view"
    PURCHASE_CREATE = "purchase.create"
    PURCHASE_UPDATE = "purchase.update"
    PURCHASE_DELETE = "purchase.delete"

    # Sales
    SALES_VIEW = "sales.view"
    SALES_CREATE = "sales.create"
    SALES_UPDATE = "sales.update"
    SALES_DELETE = "sales.delete"

    # Machines
    MACHINE_VIEW = "machine.view"
    MACHINE_CREATE = "machine.create"
    MACHINE_UPDATE = "machine.update"
    MACHINE_DELETE = "machine.delete"

    # Service
    SERVICE_VIEW = "service.view"
    SERVICE_CREATE = "service.create"
    SERVICE_UPDATE = "service.update"
    SERVICE_DELETE = "service.delete"

    # AMC
    AMC_VIEW = "amc.view"
    AMC_CREATE = "amc.create"
    AMC_UPDATE = "amc.update"
    AMC_DELETE = "amc.delete"

    # PM
    PM_VIEW = "pm.view"
    PM_CREATE = "pm.create"
    PM_UPDATE = "pm.update"
    PM_DELETE = "pm.delete"

    # Rental
    RENTAL_VIEW = "rental.view"
    RENTAL_CREATE = "rental.create"
    RENTAL_UPDATE = "rental.update"
    RENTAL_DELETE = "rental.delete"

    # Finance
    FINANCE_VIEW = "finance.view"

    # Reports
    REPORT_VIEW = "report.view"

    # Settings
    SETTINGS_VIEW = "settings.view"
    # =====================================================
# Role Permission Mapping
# =====================================================

ROLE_PERMISSIONS = {

    "ADMIN": list(Permission),

    "ACCOUNTANT": [

        Permission.DASHBOARD_VIEW,

        Permission.FINANCE_VIEW,

        Permission.REPORT_VIEW,

    ],

    "SALES": [

        Permission.DASHBOARD_VIEW,

        Permission.CUSTOMER_VIEW,

        Permission.CUSTOMER_CREATE,

        Permission.PRODUCT_VIEW,

        Permission.SALES_VIEW,

        Permission.SALES_CREATE,

        Permission.REPORT_VIEW,

    ],

    "WAREHOUSE": [

        Permission.DASHBOARD_VIEW,

        Permission.PRODUCT_VIEW,

        Permission.WAREHOUSE_VIEW,

        Permission.INVENTORY_VIEW,

        Permission.INVENTORY_UPDATE,

        Permission.INVENTORY_TRANSFER,

    ],

    "SERVICE": [

        Permission.DASHBOARD_VIEW,

        Permission.MACHINE_VIEW,

        Permission.SERVICE_VIEW,

        Permission.SERVICE_CREATE,

        Permission.AMC_VIEW,

        Permission.PM_VIEW,

    ],

}
# =====================================================
# Permission Dependency
# =====================================================

def require_permission(permission: Permission):

    def checker(

        current_user=Depends(get_current_user)

    ):

        role = current_user.role.upper()

        allowed_permissions = ROLE_PERMISSIONS.get(

            role,

            []

        )

        if permission not in allowed_permissions:

            raise HTTPException(

                status_code=status.HTTP_403_FORBIDDEN,

                detail="Permission denied."

            )

        return current_user

    return checker
# =====================================================
# Multiple Permission Check
# =====================================================

def require_any_permission(

    permissions: List[Permission]

):

    def checker(

        current_user=Depends(get_current_user)

    ):

        role = current_user.role.upper()

        allowed_permissions = ROLE_PERMISSIONS.get(

            role,

            []

        )

        for permission in permissions:

            if permission in allowed_permissions:

                return current_user

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="Permission denied."

        )

    return checker
# =====================================================
# Role Dependency
# =====================================================

def require_role(

    roles: List[str]

):

    def checker(

        current_user=Depends(get_current_user)

    ):

        if current_user.role.upper() not in [

            role.upper()

            for role in roles

        ]:

            raise HTTPException(

                status_code=status.HTTP_403_FORBIDDEN,

                detail="Role not allowed."

            )

        return current_user

    return checker