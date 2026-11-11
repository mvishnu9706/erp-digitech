from typing import Optional

from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.sales_order import SalesOrder

from app.schemas.sales_order import (
    SalesOrderCreate,
    SalesOrderUpdate,
    SalesOrderResponse,
    SalesDashboardResponse,
)

from app.services.sales_order_service import (
    SalesOrderService,
)

from app.core.dependencies import (
    get_current_admin,
    get_current_user,
)

from app.utils.sales_order_pdf import (
    SalesOrderPDFGenerator,
)


router = APIRouter(
    prefix="/sales-orders",
    tags=["Sales Orders"],
)


# =====================================================
# Create Sales Order
# =====================================================

@router.post(
    "/",
    response_model=SalesOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Sales Order",
)
def create_sales_order(
    sales_order: SalesOrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return SalesOrderService.create_sales_order(
        db=db,
        data=sales_order,
        current_user=current_user,
    )


# =====================================================
# Get Sales Orders
# =====================================================

@router.get(
    "/",
    response_model=list[SalesOrderResponse],
    summary="Get Sales Orders",
)
def get_sales_orders(
    search: Optional[str] = Query(
        None
    ),

    customer_id: Optional[int] = Query(
        None
    ),

    product_id: Optional[int] = Query(
        None
    ),

    warehouse_id: Optional[int] = Query(
        None
    ),

    status: Optional[str] = Query(
        None
    ),

    payment_status: Optional[str] = Query(
        None
    ),

    date_from: Optional[str] = Query(
        None
    ),

    date_to: Optional[str] = Query(
        None
    ),

    page: int = Query(
        1,
        ge=1,
    ),

    page_size: int = Query(
        10,
        ge=1,
        le=100,
    ),

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    ),
):

    return SalesOrderService.get_sales_orders(
        db=db,
        search=search,
        customer_id=customer_id,
        product_id=product_id,
        warehouse_id=warehouse_id,
        status=status,
        payment_status=payment_status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )


# =====================================================
# Sales Dashboard
# =====================================================
#
# IMPORTANT:
# Keep this BEFORE /{sales_order_id}
#
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=SalesDashboardResponse,
    summary="Sales Dashboard",
)
def dashboard(
    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    ),
):

    return SalesOrderService.dashboard(
        db
    )


# =====================================================
# Export Sales Orders
# =====================================================

@router.get(
    "/export",
    summary="Export Sales Orders to Excel",
)
def export_sales_orders(
    search: Optional[str] = Query(
        None
    ),

    customer_id: Optional[int] = Query(
        None
    ),

    product_id: Optional[int] = Query(
        None
    ),

    warehouse_id: Optional[int] = Query(
        None
    ),

    status: Optional[str] = Query(
        None
    ),

    payment_status: Optional[str] = Query(
        None
    ),

    date_from: Optional[str] = Query(
        None
    ),

    date_to: Optional[str] = Query(
        None
    ),

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    ),
):

    excel_file = (
        SalesOrderService.export_sales_orders(
            db=db,
            search=search,
            customer_id=customer_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            status=status,
            payment_status=payment_status,
            date_from=date_from,
            date_to=date_to,
        )
    )

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; "
                "filename=sales_orders.xlsx"
        },
    )


# =====================================================
# Generate + Store Sales Order PDF
# =====================================================
#
# IMPORTANT:
# Keep this BEFORE /{sales_order_id}
#
# This endpoint does BOTH:
#
# 1. Generates the PDF
# 2. Stores the PDF in PostgreSQL
# 3. Returns the PDF to frontend
#
# =====================================================

@router.get(
    "/{sales_order_id}/pdf",
    summary="Generate and Store Sales Order PDF",
)
def generate_sales_order_pdf(
    sales_order_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    ),
):

    # =================================================
    # Get Sales Order
    # =================================================

    sales_order = (
        db.query(
            SalesOrder
        )
        .filter(
            SalesOrder.id ==
            sales_order_id
        )
        .first()
    )

    # =================================================
    # Check Sales Order
    # =================================================

    if not sales_order:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "Sales order not found.",
        )

    # =================================================
    # Generate PDF
    # =================================================

    try:

        pdf_buffer = (
            SalesOrderPDFGenerator.generate(
                sales_order
            )
        )

    except Exception as error:

        print(
            "SALES ORDER PDF GENERATION ERROR:"
        )

        print(error)

        raise HTTPException(
            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=
                "Failed to generate sales order PDF.",
        )

    # =================================================
    # Convert PDF Buffer To Bytes
    # =================================================

    try:

        pdf_bytes = (
            pdf_buffer.getvalue()
        )

    except Exception as error:

        print(
            "SALES ORDER PDF BUFFER ERROR:"
        )

        print(error)

        raise HTTPException(
            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=
                "Failed to read generated PDF.",
        )

    # =================================================
    # Check PDF
    # =================================================

    if not pdf_bytes:

        raise HTTPException(
            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=
                "Generated PDF is empty.",
        )

    # =================================================
    # File Name
    # =================================================

    filename = (
        f"{sales_order.so_number}.pdf"
    )

    # =================================================
    # Store PDF In PostgreSQL
    # =================================================

    try:

        sales_order.pdf_file = (
            pdf_bytes
        )

        sales_order.pdf_file_name = (
            filename
        )

        sales_order.pdf_content_type = (
            "application/pdf"
        )

        sales_order.pdf_generated_at = (
            datetime.now(
                timezone.utc
            )
        )

        # ---------------------------------------------
        # Save PDF to database
        # ---------------------------------------------

        db.commit()

        # ---------------------------------------------
        # Refresh SQLAlchemy object
        # ---------------------------------------------

        db.refresh(
            sales_order
        )

    except Exception as error:

        # ---------------------------------------------
        # Rollback if database storage fails
        # ---------------------------------------------

        db.rollback()

        print(
            "SALES ORDER PDF DATABASE STORAGE ERROR:"
        )

        print(error)

        raise HTTPException(
            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=
                "Failed to save sales order PDF to database.",
        )

    # =================================================
    # Return PDF
    # =================================================

    return StreamingResponse(
        iter(
            [
                pdf_bytes
            ]
        ),
        media_type=
            "application/pdf",

        headers={

            "Content-Disposition":
                f'attachment; filename="{filename}"',

            "Content-Length":
                str(
                    len(pdf_bytes)
                ),
        },
    )


# =====================================================
# Get Sales Order
# =====================================================

@router.get(
    "/{sales_order_id}",
    response_model=SalesOrderResponse,
    summary="Get Sales Order",
)
def get_sales_order(
    sales_order_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    ),
):

    return SalesOrderService.get_sales_order(
        db,
        sales_order_id,
    )


# =====================================================
# Update Sales Order
# =====================================================
#
# Used mainly for:
#
# - Payment status
# - Payment method
# - Payment reference
# - Paid amount
# - Due date
# - Remarks
# - Sales order items
#
# IMPORTANT:
#
# Inventory stock is controlled by the service.
# A PENDING sale does not change stock.
# A COMPLETED sale has already deducted stock.
#
# =====================================================

@router.put(
    "/{sales_order_id}",
    response_model=SalesOrderResponse,
    summary="Update Sales Order",
)
def update_sales_order(
    sales_order_id: int,

    sales_order: SalesOrderUpdate,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    return SalesOrderService.update_sales_order(
        db=db,

        sales_order_id=
            sales_order_id,

        data=sales_order,

        current_user=
            current_user,
    )


# =====================================================
# Complete Sales Order
# =====================================================
#
# PENDING
#    ↓
# COMPLETED
#    ↓
# Check actual stock
#    ↓
# Deduct stock
#    ↓
# Create SALE transaction
#    ↓
# COMMIT
#
# IMPORTANT:
#
# Creating a PENDING sale does NOT change inventory.
#
# Stock is deducted only when this endpoint is called.
#
# =====================================================

@router.post(
    "/{sales_order_id}/complete",
    response_model=SalesOrderResponse,
    summary="Complete Sales Order",
)
def complete_sales_order(
    sales_order_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    return SalesOrderService.complete_sales_order(
        db=db,

        sales_order_id=
            sales_order_id,

        current_user=
            current_user,
    )


# =====================================================
# Cancel Sales Order
# =====================================================
#
# PENDING
#    ↓
# CANCELLED
#    ↓
# No inventory change
#
#
# COMPLETED
#    ↓
# CANCELLED
#    ↓
# Restore stock
#    ↓
# Create SALE_RETURN transaction
#
# =====================================================

@router.post(
    "/{sales_order_id}/cancel",
    response_model=SalesOrderResponse,
    summary="Cancel Sales Order",
)
def cancel_sales_order(
    sales_order_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    return SalesOrderService.cancel_sales_order(
        db=db,

        sales_order_id=
            sales_order_id,

        current_user=
            current_user,
    )


# =====================================================
# Delete Sales Order
# =====================================================
#
# This actually deletes the Sales Order.
#
# PENDING:
#    - No inventory change.
#
# COMPLETED:
#    - Stock is restored.
#    - SALE_RETURN transaction is created.
#
# =====================================================

@router.delete(
    "/{sales_order_id}",
    summary="Delete Sales Order",
)
def delete_sales_order(
    sales_order_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_admin
    ),
):

    return SalesOrderService.delete_sales_order(
        db=db,

        sales_order_id=
            sales_order_id,

        current_user=
            current_user,
    )