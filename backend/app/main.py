from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.exceptions.handlers import register_exception_handlers
from app.database import engine


# =====================================================
# DATABASE MODELS
# =====================================================

from app.models.role_permission import RolePermission
from app.models.rental_billing_cycle import RentalBillingCycle


# =====================================================
# API ROUTERS
# =====================================================

# -----------------------------------------------------
# Master Data
# -----------------------------------------------------

from app.api.categories import router as category_router
from app.api.brands import router as brand_router
from app.api.units import router as unit_router
from app.api.products import router as product_router
from app.api.warehouses import router as warehouse_router


# -----------------------------------------------------
# Inventory
# -----------------------------------------------------

from app.api.inventory_router import router as inventory_router

from app.api.inventory_transactions import (
    router as inventory_transaction_router
)


# -----------------------------------------------------
# Suppliers / Purchasing
# -----------------------------------------------------

from app.api.suppliers import router as supplier_router

from app.api.purchase_orders import (
    router as purchase_order_router
)

from app.api.goods_receipts import (
    router as goods_receipt_router
)

from app.api.purchase_invoices import (
    router as purchase_invoice_router
)

from app.api.supplier_payments import (
    router as supplier_payment_router
)

from app.api.supplier_ledger import (
    router as supplier_ledger_router
)

from app.api.supplier_outstanding import (
    router as supplier_outstanding_router
)


# -----------------------------------------------------
# Customers / Sales
# -----------------------------------------------------

from app.api.customers import (
    router as customer_router
)

from app.api.sales_orders import (
    router as sales_order_router
)

from app.api.sales_invoices import (
    router as sales_invoice_router
)

from app.api.customer_payments import (
    router as customer_payment_router
)

from app.api.customer_outstanding import (
    router as customer_outstanding_router
)


# -----------------------------------------------------
# Users / Authentication
# -----------------------------------------------------

from app.api.users import (
    router as user_router
)

from app.api.auth import (
    router as auth_router
)


# -----------------------------------------------------
# Permissions
# -----------------------------------------------------

from app.api.permissions import (
    router as permission_router
)


# -----------------------------------------------------
# Notifications
# -----------------------------------------------------

from app.api.notifications import (
    router as notification_router
)


# -----------------------------------------------------
# WhatsApp
# -----------------------------------------------------

from app.api.whatsapp import (
    router as whatsapp_router
)


# -----------------------------------------------------
# Service / Engineer
# -----------------------------------------------------

from app.api.machines import (
    router as machine_router
)

from app.api.service_tickets import (
    router as service_ticket_router
)

from app.api.service_visits import (
    router as service_visit_router
)

from app.api.service_spare_parts import (
    router as service_spare_part_router
)

from app.api.pm_schedules import (
    router as pm_schedule_router
)


# -----------------------------------------------------
# Rental / AMC
# -----------------------------------------------------

from app.api.rental_bills import (
    router as rental_bill_router
)

from app.api.rental_billing_cycle import (
    router as rental_billing_cycle_router
)

from app.api.amc_contracts import (
    router as amc_contract_router
)


# -----------------------------------------------------
# Customer Portal
# -----------------------------------------------------

from app.api.customer_portal import (
    router as customer_portal_router
)


# =====================================================
# MIDDLEWARE
# =====================================================

from app.middleware.logging import (
    log_requests
)


# =====================================================
# AUTHENTICATION / AUTHORIZATION
# =====================================================

from app.core.dependencies import (
    get_current_admin
)


# =====================================================
# FASTAPI APPLICATION
# =====================================================

app = FastAPI(
    title="Digitech ERP API",
    description=(
        "Production ERP Backend built with "
        "FastAPI + PostgreSQL"
    ),
    version="1.0.0"
)


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =====================================================
# EXCEPTION HANDLERS
# =====================================================

register_exception_handlers(app)


# =====================================================
# REQUEST LOGGING MIDDLEWARE
# =====================================================

app.middleware("http")(log_requests)


# =====================================================
# REGISTER API ROUTERS
# =====================================================


# -----------------------------------------------------
# Authentication / Users
# -----------------------------------------------------

app.include_router(
    user_router
)

app.include_router(
    auth_router
)


# -----------------------------------------------------
# Permissions
# -----------------------------------------------------

app.include_router(
    permission_router
)


# -----------------------------------------------------
# Notifications
# -----------------------------------------------------

app.include_router(
    notification_router
)


# -----------------------------------------------------
# WhatsApp
# -----------------------------------------------------

app.include_router(
    whatsapp_router
)


# -----------------------------------------------------
# Master Data
# -----------------------------------------------------

app.include_router(
    brand_router
)

app.include_router(
    category_router
)

app.include_router(
    unit_router
)

app.include_router(
    product_router
)

app.include_router(
    warehouse_router
)


# -----------------------------------------------------
# Suppliers / Purchasing
# -----------------------------------------------------

app.include_router(
    supplier_router
)

app.include_router(
    purchase_order_router
)

app.include_router(
    goods_receipt_router
)

app.include_router(
    purchase_invoice_router
)

app.include_router(
    supplier_payment_router
)


# -----------------------------------------------------
# Customers / Sales
# -----------------------------------------------------

app.include_router(
    customer_router
)

app.include_router(
    sales_order_router
)

app.include_router(
    sales_invoice_router
)

app.include_router(
    customer_payment_router
)


# -----------------------------------------------------
# Supplier / Customer Accounts
# -----------------------------------------------------

app.include_router(
    supplier_ledger_router
)

app.include_router(
    customer_outstanding_router
)

app.include_router(
    supplier_outstanding_router
)


# -----------------------------------------------------
# Service / Engineer
# -----------------------------------------------------

app.include_router(
    machine_router
)

app.include_router(
    service_ticket_router
)

app.include_router(
    service_visit_router
)

app.include_router(
    service_spare_part_router
)

app.include_router(
    pm_schedule_router
)


# -----------------------------------------------------
# Rental / AMC
# -----------------------------------------------------

app.include_router(
    amc_contract_router
)

app.include_router(
    rental_bill_router
)

app.include_router(
    rental_billing_cycle_router
)


# -----------------------------------------------------
# Inventory
# -----------------------------------------------------

app.include_router(
    inventory_transaction_router
)

app.include_router(
    inventory_router
)


# =====================================================
# CUSTOMER PORTAL
# =====================================================

# Separate customer-facing API.
#
# These APIs use:
#
#     current_user.customer_id
#
# instead of accepting customer_id from the frontend.
#
# =====================================================

app.include_router(
    customer_portal_router
)


# =====================================================
# HOME
# =====================================================

@app.get(
    "/",
    tags=["Home"],
    summary="Home API"
)
def home():

    return {
        "application": "Digitech ERP",
        "version": "1.0.0",
        "status": "Running",
        "environment": "Development"
    }


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get(
    "/health",
    tags=["System"],
    summary="Health Check"
)
def health():

    return {
        "status": "Healthy",
        "database": "Connected",
        "application": "Digitech ERP"
    }


# =====================================================
# DATABASE TEST
# =====================================================

@app.get(
    "/db-test",
    tags=["Database"],
    summary="Database Connection Test"
)
def database_test():

    try:

        with engine.connect() as conn:

            database = conn.execute(
                text(
                    "SELECT current_database();"
                )
            ).scalar()

            version = conn.execute(
                text(
                    "SELECT version();"
                )
            ).scalar()

            return {
                "success": True,

                "database": database,

                "postgres_version": version,

                "message": (
                    "Database Connected Successfully"
                )
            }

    except Exception as e:

        return {
            "success": False,

            "message": (
                "Database Connection Failed"
            ),

            "error": str(e)
        }


# =====================================================
# AUTHORIZATION TEST
# =====================================================

@app.get(
    "/admin-test",
    tags=["Authorization"],
    summary="Admin Protected API"
)
def admin_test(
    current_user=Depends(
        get_current_admin
    )
):

    return {
        "success": True,

        "message": "Welcome Admin",

        "user": {
            "id": current_user.id,

            "full_name": current_user.full_name,

            "email": current_user.email,

            "role": current_user.role
        }
    }