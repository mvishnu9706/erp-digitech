from datetime import datetime
from io import BytesIO
from typing import Optional

import openpyxl

from openpyxl.styles import (
    Alignment,
    Font,
)

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.inventory_transaction import (
    InventoryTransactionCreate,
    InventoryTransactionUpdate,
    InventoryTransactionResponse,
    InventoryTransactionListResponse,
    InventoryTransactionDashboardResponse,
    StockTransferHistoryListResponse,
)

from app.services.inventory_transaction_service import (
    InventoryTransactionService,
)

from app.core.dependencies import (
    get_current_admin,
    get_current_user,
)


router = APIRouter(
    prefix="/inventory-transactions",
    tags=["Inventory Transactions"],
)


# =====================================================
# CREATE INVENTORY TRANSACTION
# =====================================================

@router.post(
    "/",
    response_model=InventoryTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(

    data: InventoryTransactionCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_admin
    ),

):

    return (
        InventoryTransactionService
        .create_transaction(

            db,

            data,

            current_user,

        )
    )


# =====================================================
# GET INVENTORY TRANSACTIONS
# =====================================================

@router.get(
    "/",
    response_model=InventoryTransactionListResponse,
)
def get_transactions(

    product_id: Optional[int] = Query(
        None,
    ),

    warehouse_id: Optional[int] = Query(
        None,
    ),

    transaction_type: Optional[str] = Query(
        None,
    ),

    reference_type: Optional[str] = Query(
        None,
    ),

    reference_by: Optional[str] = Query(
        None,
    ),

    search: Optional[str] = Query(
        None,
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

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),

):

    return (
        InventoryTransactionService
        .get_transactions(

            db=db,

            product_id=product_id,

            warehouse_id=warehouse_id,

            transaction_type=transaction_type,

            reference_type=reference_type,

            reference_by=reference_by,

            search=search,

            page=page,

            page_size=page_size,

        )
    )


# =====================================================
# STOCK TRANSFER HISTORY
# =====================================================
#
# ONE database row = ONE stock transfer.
#
# Example:
#
#     transaction_type = TRANSFER
#
#     warehouse_id    = FROM warehouse
#     to_warehouse_id = TO warehouse
#
# Filters:
#
#     Search
#     From Date
#     To Date
#     Product
#     Warehouse
#     From Warehouse
#     To Warehouse
#     Reference By
#     Activity
#     Page
#     Page Size
#
# =====================================================

@router.get(
    "/transfers/history",
    response_model=StockTransferHistoryListResponse,
)
def get_stock_transfer_history(

    product_id: Optional[int] = Query(
        None,
    ),

    warehouse_id: Optional[int] = Query(
        None,
    ),

    from_warehouse_id: Optional[int] = Query(
        None,
    ),

    to_warehouse_id: Optional[int] = Query(
        None,
    ),

    reference_by: Optional[str] = Query(
        None,
    ),

    search: Optional[str] = Query(
        None,
    ),

    from_date: Optional[datetime] = Query(
        None,
    ),

    to_date: Optional[datetime] = Query(
        None,
    ),

    activity: Optional[str] = Query(
        None,
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

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),

):

    return (
        InventoryTransactionService
        .get_stock_transfers(

            db=db,

            product_id=product_id,

            warehouse_id=warehouse_id,

            from_warehouse_id=(
                from_warehouse_id
            ),

            to_warehouse_id=(
                to_warehouse_id
            ),

            reference_by=(
                reference_by
            ),

            search=search,

            from_date=(
                from_date
            ),

            to_date=(
                to_date
            ),

            activity=(
                activity
            ),

            page=page,

            page_size=page_size,

        )
    )


# =====================================================
# EXPORT STOCK TRANSFER HISTORY
# =====================================================
#
# Exports the same filtered transfer history
# as an Excel (.xlsx) file.
#
# =====================================================

@router.get(
    "/transfers/history/export",
)
def export_stock_transfer_history(

    product_id: Optional[int] = Query(
        None,
    ),

    warehouse_id: Optional[int] = Query(
        None,
    ),

    from_warehouse_id: Optional[int] = Query(
        None,
    ),

    to_warehouse_id: Optional[int] = Query(
        None,
    ),

    reference_by: Optional[str] = Query(
        None,
    ),

    search: Optional[str] = Query(
        None,
    ),

    from_date: Optional[datetime] = Query(
        None,
    ),

    to_date: Optional[datetime] = Query(
        None,
    ),

    activity: Optional[str] = Query(
        None,
    ),

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),

):

    # =================================================
    # Get All Filtered Transfers
    # =================================================

    result = (
        InventoryTransactionService
        .get_stock_transfers(

            db=db,

            product_id=product_id,

            warehouse_id=warehouse_id,

            from_warehouse_id=(
                from_warehouse_id
            ),

            to_warehouse_id=(
                to_warehouse_id
            ),

            reference_by=(
                reference_by
            ),

            search=search,

            from_date=(
                from_date
            ),

            to_date=(
                to_date
            ),

            activity=(
                activity
            ),

            page=1,

            page_size=100000,

        )
    )

    items = result.get(
        "items",
        [],
    )

    # =================================================
    # Create Excel Workbook
    # =================================================

    workbook = openpyxl.Workbook()

    worksheet = (
        workbook.active
    )

    worksheet.title = (
        "Stock Transfer History"
    )

    # =================================================
    # Headers
    # =================================================

    headers = [

        "S.No",

        "Date & Time",

        "Transfer No.",

        "Item",

        "From Warehouse",

        "To Warehouse",

        "Quantity",

        "Reference By",

        "Activity",

        "Created By",

        "Remarks",

    ]

    worksheet.append(
        headers
    )

    # =================================================
    # Header Formatting
    # =================================================

    for cell in worksheet[1]:

        cell.font = Font(
            bold=True,
        )

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

    # =================================================
    # Data
    # =================================================

    for index, item in enumerate(
        items,
        start=1,
    ):

        created_at = item.get(
            "created_at"
        )

        if created_at:

            created_at = str(
                created_at
            )

        worksheet.append([

            index,

            created_at or "",

            item.get(
                "transaction_number",
                "",
            ),

            item.get(
                "product_name",
                "",
            ),

            item.get(
                "from_warehouse",
                "",
            ),

            item.get(
                "to_warehouse",
                "",
            ),

            item.get(
                "quantity",
                "",
            ),

            item.get(
                "reference_by",
                "",
            ),

            item.get(
                "activity",
                "Created",
            ),

            item.get(
                "created_by_name",
                item.get(
                    "created_by",
                    "",
                ),
            ),

            item.get(
                "remarks",
                "",
            ),

        ])

    # =================================================
    # Column Widths
    # =================================================

    column_widths = {

        "A": 8,

        "B": 22,

        "C": 25,

        "D": 30,

        "E": 25,

        "F": 25,

        "G": 12,

        "H": 22,

        "I": 15,

        "J": 20,

        "K": 40,

    }

    for column, width in (
        column_widths.items()
    ):

        worksheet.column_dimensions[
            column
        ].width = width

    # =================================================
    # Freeze Header
    # =================================================

    worksheet.freeze_panes = "A2"

    # =================================================
    # Excel Filter
    # =================================================

    if items:

        last_row = (
            len(items) + 1
        )

        worksheet.auto_filter.ref = (
            f"A1:K{last_row}"
        )

    # =================================================
    # Alignment
    # =================================================

    for row in (
        worksheet.iter_rows()
    ):

        for cell in row:

            cell.alignment = Alignment(
                vertical="center",
            )

    # =================================================
    # Save Workbook
    # =================================================

    output = BytesIO()

    workbook.save(
        output
    )

    output.seek(0)

    # =================================================
    # File Name
    # =================================================

    filename = (
        "Stock_Transfer_History.xlsx"
    )

    # =================================================
    # Return Excel File
    # =================================================

    return StreamingResponse(

        output,

        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),

        headers={

            "Content-Disposition": (
                "attachment; "
                f'filename="{filename}"'
            ),

        },

    )


# =====================================================
# DASHBOARD
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=(
        InventoryTransactionDashboardResponse
    ),
)
def dashboard(

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),

):

    return (
        InventoryTransactionService
        .dashboard(
            db
        )
    )


# =====================================================
# GET TRANSACTION BY ID
# =====================================================

@router.get(
    "/{transaction_id}",
    response_model=InventoryTransactionResponse,
)
def get_transaction(

    transaction_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),

):

    return (
        InventoryTransactionService
        .get_transaction(

            db,

            transaction_id,

        )
    )


# =====================================================
# UPDATE TRANSACTION
# =====================================================

@router.put(
    "/{transaction_id}",
    response_model=InventoryTransactionResponse,
)
def update_transaction(

    transaction_id: int,

    data: InventoryTransactionUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_admin
    ),

):

    return (
        InventoryTransactionService
        .update_transaction(

            db,

            transaction_id,

            data,

            current_user,

        )
    )


# =====================================================
# DELETE TRANSACTION
# =====================================================

@router.delete(
    "/{transaction_id}"
)
def delete_transaction(

    transaction_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_admin
    ),

):

    return (
        InventoryTransactionService
        .delete_transaction(

            db,

            transaction_id,

        )
    )