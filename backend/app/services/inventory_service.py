from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

import math

from decimal import Decimal
from io import BytesIO

from app.models.inventory import Inventory

from app.models.inventory_transaction import (
    InventoryTransaction
)

from app.repositories.inventory_repository import (
    InventoryRepository,
)

from app.repositories.product_repository import (
    ProductRepository,
)

from app.repositories.warehouse_repository import (
    WarehouseRepository,
)

from app.schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    StockTransfer,
)

from app.utils.inventory_transaction_number import (
    InventoryTransactionNumberGenerator,
)


class InventoryService:

    # ==========================================================
    # LOW STOCK SETTINGS
    # ==========================================================

    LOW_STOCK_THRESHOLD = 10

    # ==========================================================
    # Stock Status Calculation
    # ==========================================================

    @staticmethod
    def calculate_stock_status(
        stock: int,
        minimum_stock: int = None,
    ):

        if stock <= 0:
            return "OUT_OF_STOCK"

        if minimum_stock is None:
            minimum_stock = (
                InventoryService.LOW_STOCK_THRESHOLD
            )

        if stock <= minimum_stock:
            return "LOW_STOCK"

        return "IN_STOCK"

    # ==========================================================
    # Refresh Inventory
    # ==========================================================

    @staticmethod
    def refresh_inventory(
        inventory: Inventory,
    ):
        """
        Recalculate only stock status.

        inventory.stock is the actual physical stock.

        There is no:
        - reserved_stock
        - available_stock
        """

        minimum_stock = getattr(
            inventory.product,
            "minimum_stock",
            None,
        )

        if minimum_stock is None:
            minimum_stock = (
                InventoryService.LOW_STOCK_THRESHOLD
            )

        inventory.stock_status = (
            InventoryService.calculate_stock_status(
                int(inventory.stock or 0),
                minimum_stock,
            )
        )

    # ==========================================================
    # Get All Inventory
    # ==========================================================

    @staticmethod
    def get_all(
        db: Session,
        page: int = 1,
        size: int = 10,
        search: str = None,
        warehouse_id: int = None,
        product_id: int = None,
        stock_status: str = None,
    ):

        skip = (page - 1) * size

        items = InventoryRepository.get_all(
            db=db,
            search=search,
            warehouse_id=warehouse_id,
            product_id=product_id,
            stock_status=stock_status,
            skip=skip,
            limit=size,
        )

        total = InventoryRepository.total_records(
            db=db,
            search=search,
            warehouse_id=warehouse_id,
            product_id=product_id,
            stock_status=stock_status,
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (
                math.ceil(total / size)
                if size
                else 1
            ),
        }

    # ==========================================================
    # Get Inventory By ID
    # ==========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        inventory_id: int,
    ):

        inventory = (
            InventoryRepository.get_by_id(
                db,
                inventory_id,
            )
        )

        if not inventory:

            raise HTTPException(
                status_code=404,
                detail="Inventory not found.",
            )

        return inventory

    # ==========================================================
    # Create Inventory
    # ==========================================================

    @staticmethod
    def create(
        db: Session,
        data: InventoryCreate,
        current_user,
    ):

        # ------------------------------------------------------
        # Validate Product
        # ------------------------------------------------------

        product = ProductRepository.get_by_id(
            db,
            data.product_id,
        )

        if not product:

            raise HTTPException(
                status_code=404,
                detail="Product not found.",
            )

        # ------------------------------------------------------
        # Validate Warehouse
        # ------------------------------------------------------

        warehouse = WarehouseRepository.get_by_id(
            db,
            data.warehouse_id,
        )

        if not warehouse:

            raise HTTPException(
                status_code=404,
                detail="Warehouse not found.",
            )

        # ------------------------------------------------------
        # Check Duplicate Inventory
        # ------------------------------------------------------

        existing = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db,
                data.product_id,
                data.warehouse_id,
            )
        )

        if existing:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Product already exists "
                    "in this warehouse."
                ),
            )

        # ------------------------------------------------------
        # Create Inventory
        # ------------------------------------------------------

        inventory = Inventory(
            product_id=data.product_id,
            warehouse_id=data.warehouse_id,
            rack_location=data.rack_location,
            stock=data.stock,
            stock_status="IN_STOCK",
            last_purchase_price=(
                data.last_purchase_price
            ),
            last_purchase_date=(
                data.last_purchase_date
            ),
            remarks=data.remarks,
            created_by=current_user.id,
            updated_by=current_user.id,
        )

        # ------------------------------------------------------
        # Calculate Status
        # ------------------------------------------------------

        InventoryService.refresh_inventory(
            inventory
        )

        # ------------------------------------------------------
        # Save
        # ------------------------------------------------------

        InventoryRepository.create(
            db,
            inventory,
        )

        db.commit()

        db.refresh(inventory)

        return inventory

    # ==========================================================
    # Update Inventory
    # ==========================================================

    @staticmethod
    def update(
        db: Session,
        inventory_id: int,
        data: InventoryUpdate,
        current_user,
    ):

        inventory = (
            InventoryRepository.get_by_id(
                db,
                inventory_id,
            )
        )

        if not inventory:

            raise HTTPException(
                status_code=404,
                detail="Inventory not found.",
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # ------------------------------------------------------
        # Apply Updates
        # ------------------------------------------------------

        for key, value in update_data.items():

            setattr(
                inventory,
                key,
                value,
            )

        inventory.updated_by = current_user.id

        # ------------------------------------------------------
        # Recalculate Stock Status
        # ------------------------------------------------------

        InventoryService.refresh_inventory(
            inventory
        )

        # ------------------------------------------------------
        # Save
        # ------------------------------------------------------

        InventoryRepository.update(
            db,
            inventory,
        )

        db.commit()

        db.refresh(inventory)

        return inventory

    # ==========================================================
    # Transfer Stock
    # ==========================================================
    #
    # SIMPLE TRANSFER SYSTEM
    #
    # One transfer:
    #
    #     Source stock  -> decreases
    #     Destination   -> increases
    #
    # One transaction record is created:
    #
    #     transaction_type = TRANSFER
    #
    # No:
    #     TRANSFER_OUT
    #     TRANSFER_IN
    #
    # warehouse_id     = FROM warehouse
    # to_warehouse_id  = TO warehouse
    #
    # ==========================================================

    @staticmethod
    def transfer_stock(
        db: Session,
        data: StockTransfer,
        current_user,
    ):

        try:

            # ==================================================
            # Validate Quantity
            # ==================================================

            requested_quantity = int(
                data.quantity or 0
            )

            if requested_quantity <= 0:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Transfer quantity must be "
                        "greater than zero."
                    ),
                )

            # ==================================================
            # Validate Source / Destination
            # ==================================================

            if (
                data.from_warehouse_id
                == data.to_warehouse_id
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "From and To Warehouse "
                        "cannot be the same."
                    ),
                )

            # ==================================================
            # Validate Product
            # ==================================================

            product = ProductRepository.get_by_id(
                db,
                data.product_id,
            )

            if not product:

                raise HTTPException(
                    status_code=404,
                    detail="Product not found.",
                )

            # ==================================================
            # Validate Source Warehouse
            # ==================================================

            source_warehouse = (
                WarehouseRepository.get_by_id(
                    db,
                    data.from_warehouse_id,
                )
            )

            if not source_warehouse:

                raise HTTPException(
                    status_code=404,
                    detail="Source warehouse not found.",
                )

            # ==================================================
            # Validate Destination Warehouse
            # ==================================================

            destination_warehouse = (
                WarehouseRepository.get_by_id(
                    db,
                    data.to_warehouse_id,
                )
            )

            if not destination_warehouse:

                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Destination warehouse not found."
                    ),
                )

            # ==================================================
            # Get Source Inventory
            # ==================================================

            source_inventory = (
                db.query(Inventory)
                .filter(
                    Inventory.product_id
                    == data.product_id,
                    Inventory.warehouse_id
                    == data.from_warehouse_id,
                )
                .first()
            )

            if not source_inventory:

                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Source inventory not found "
                        "for the selected product and "
                        "warehouse."
                    ),
                )

            # ==================================================
            # Get Actual Source Stock
            # ==================================================

            source_stock = int(
                source_inventory.stock or 0
            )

            # ==================================================
            # Check Available Physical Stock
            # ==================================================

            if source_stock < requested_quantity:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Insufficient stock. "
                        f"Available stock = {source_stock}, "
                        f"requested = {requested_quantity}."
                    ),
                )

            # ==================================================
            # Get Destination Inventory
            # ==================================================

            destination_inventory = (
                db.query(Inventory)
                .filter(
                    Inventory.product_id
                    == data.product_id,
                    Inventory.warehouse_id
                    == data.to_warehouse_id,
                )
                .first()
            )

            # ==================================================
            # Create Destination Inventory If Needed
            # ==================================================

            if not destination_inventory:

                destination_inventory = Inventory(
                    product_id=data.product_id,
                    warehouse_id=data.to_warehouse_id,
                    rack_location=None,
                    stock=0,
                    stock_status="OUT_OF_STOCK",
                    last_purchase_price=(
                        source_inventory.last_purchase_price
                    ),
                    last_purchase_date=(
                        source_inventory.last_purchase_date
                    ),
                    remarks=data.remarks,
                    created_by=current_user.id,
                    updated_by=current_user.id,
                )

                db.add(
                    destination_inventory
                )

                db.flush()

            # ==================================================
            # Reduce Source Stock
            # ==================================================

            source_inventory.stock = (
                source_stock
                - requested_quantity
            )

            source_inventory.updated_by = (
                current_user.id
            )

            InventoryService.refresh_inventory(
                source_inventory
            )

            # ==================================================
            # Increase Destination Stock
            # ==================================================

            destination_stock = int(
                destination_inventory.stock or 0
            )

            destination_inventory.stock = (
                destination_stock
                + requested_quantity
            )

            destination_inventory.updated_by = (
                current_user.id
            )

            InventoryService.refresh_inventory(
                destination_inventory
            )

            # ==================================================
            # Save Inventory Changes
            # ==================================================

            db.flush()

            # ==================================================
            # Transaction Cost
            # ==================================================

            unit_cost = Decimal(
                str(
                    source_inventory.last_purchase_price
                    or 0
                )
            )

            total_cost = (
                Decimal(requested_quantity)
                * unit_cost
            )

            # ==================================================
            # Get Next Transaction Number
            # ==================================================

            last_transaction = (
                db.query(InventoryTransaction)
                .order_by(
                    InventoryTransaction.id.desc()
                )
                .first()
            )

            next_id = (
                last_transaction.id + 1
                if last_transaction
                else 1
            )

            # ==================================================
            # Create ONE Transfer Transaction
            # ==================================================

            transfer_transaction = (
                InventoryTransaction(

                    transaction_number=(
                        InventoryTransactionNumberGenerator
                        .generate(next_id)
                    ),

                    product_id=data.product_id,

                    # FROM warehouse
                    warehouse_id=(
                        data.from_warehouse_id
                    ),

                    # TO warehouse
                    to_warehouse_id=(
                        data.to_warehouse_id
                    ),

                    transaction_type="TRANSFER",

                    reference_type="STOCK_TRANSFER",

                    reference_id=None,

                    reference_by=(
                        getattr(
                            data,
                            "reference_by",
                            None
                        )
                    ),

                    quantity=Decimal(
                        requested_quantity
                    ),

                    unit_cost=unit_cost,

                    total_cost=total_cost,

                    remarks=data.remarks,

                    created_by=current_user.id,
                )
            )

            db.add(
                transfer_transaction
            )

            db.flush()

            # ==================================================
            # Use Transaction ID As Reference
            # ==================================================

            transfer_transaction.reference_id = (
                transfer_transaction.id
            )

            # ==================================================
            # Commit Everything
            # ==================================================

            db.commit()

            # ==================================================
            # Refresh
            # ==================================================

            db.refresh(
                source_inventory
            )

            db.refresh(
                destination_inventory
            )

            db.refresh(
                transfer_transaction
            )

            # ==================================================
            # Return Result
            # ==================================================

            return {

                "success": True,

                "message": (
                    "Stock transferred successfully."
                ),

                "product_id": (
                    data.product_id
                ),

                "from_warehouse_id": (
                    data.from_warehouse_id
                ),

                "to_warehouse_id": (
                    data.to_warehouse_id
                ),

                "transferred_quantity": (
                    requested_quantity
                ),

                "reference_by": (
                    getattr(
                        data,
                        "reference_by",
                        None
                    )
                ),

                "reference_id": (
                    transfer_transaction.id
                ),

                "transaction_number": (
                    transfer_transaction
                    .transaction_number
                ),

                "source_stock": int(
                    source_inventory.stock or 0
                ),

                "destination_stock": int(
                    destination_inventory.stock or 0
                ),
            }

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=(
                    "Stock transfer failed: "
                    f"{str(e)}"
                ),
            )

    # ==========================================================
    # Check Inventory
    # ==========================================================

    @staticmethod
    def check_inventory(
        db: Session,
        product_id: int,
        warehouse_id: int,
    ):

        inventory = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db,
                product_id,
                warehouse_id,
            )
        )

        return {

            "exists": (
                inventory is not None
            ),

            "inventory_id": (
                inventory.id
                if inventory
                else None
            ),

            "message": (
                "Product already exists "
                "in this warehouse."
                if inventory
                else "Product can be added."
            ),
        }

    # ==========================================================
    # Delete Inventory
    # ==========================================================

    @staticmethod
    def delete(
        db: Session,
        inventory_id: int,
    ):

        inventory = (
            InventoryRepository.get_by_id(
                db,
                inventory_id,
            )
        )

        if not inventory:

            raise HTTPException(
                status_code=404,
                detail="Inventory not found.",
            )

        InventoryRepository.delete(
            db,
            inventory,
        )

        db.commit()

        return {

            "success": True,

            "message": (
                "Inventory deleted successfully."
            ),
        }

    # ==========================================================
    # Export Inventory To Excel
    # ==========================================================
    #
    # Exports all matching inventory records.
    #
    # Supported filters:
    #     search
    #     warehouse_id
    #     product_id
    #     stock_status
    #
    # Pagination is intentionally not used.
    #
    # ==========================================================

    @staticmethod
    def export_inventory(
        db: Session,
        search: str = None,
        warehouse_id: int = None,
        product_id: int = None,
        stock_status: str = None,
    ):

        try:

            # --------------------------------------------------
            # Get ALL matching inventory records.
            # No page/size is applied to export.
            # --------------------------------------------------

            total = InventoryRepository.total_records(
                db=db,
                search=search,
                warehouse_id=warehouse_id,
                product_id=product_id,
                stock_status=stock_status,
            )

            inventories = InventoryRepository.get_all(
                db=db,
                search=search,
                warehouse_id=warehouse_id,
                product_id=product_id,
                stock_status=stock_status,
                skip=0,
                limit=max(total, 1),
            )

            # --------------------------------------------------
            # Create Excel workbook
            # --------------------------------------------------

            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment
            from openpyxl.utils import get_column_letter

            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = "Inventory"

            headers = [
                "Inventory ID",
                "Product ID",
                "Product Name",
                "Warehouse ID",
                "Warehouse",
                "Rack Location",
                "Stock",
                "Stock Status",
                "Last Purchase Price",
                "Last Purchase Date",
                "Remarks",
            ]

            worksheet.append(headers)

            # --------------------------------------------------
            # Header formatting
            # --------------------------------------------------

            for cell in worksheet[1]:

                cell.font = Font(
                    bold=True
                )

                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center",
                )

            # --------------------------------------------------
            # Inventory rows
            # --------------------------------------------------

            for inventory in inventories:

                product_obj = getattr(
                    inventory,
                    "product",
                    None,
                )

                warehouse_obj = getattr(
                    inventory,
                    "warehouse",
                    None,
                )

                product_name = ""

                if product_obj:

                    product_name = (
                        getattr(
                            product_obj,
                            "name",
                            None,
                        )
                        or getattr(
                            product_obj,
                            "product_name",
                            None,
                        )
                        or ""
                    )

                warehouse_name = ""

                if warehouse_obj:

                    warehouse_name = (
                        getattr(
                            warehouse_obj,
                            "warehouse_name",
                            None,
                        )
                        or getattr(
                            warehouse_obj,
                            "name",
                            None,
                        )
                        or ""
                    )

                worksheet.append([
                    inventory.id,
                    inventory.product_id,
                    product_name,
                    inventory.warehouse_id,
                    warehouse_name,
                    getattr(
                        inventory,
                        "rack_location",
                        None,
                    ),
                    int(
                        inventory.stock or 0
                    ),
                    getattr(
                        inventory,
                        "stock_status",
                        None,
                    ),
                    getattr(
                        inventory,
                        "last_purchase_price",
                        None,
                    ),
                    getattr(
                        inventory,
                        "last_purchase_date",
                        None,
                    ),
                    getattr(
                        inventory,
                        "remarks",
                        None,
                    ),
                ])

            # --------------------------------------------------
            # Auto-size columns
            # --------------------------------------------------

            for column_cells in worksheet.columns:

                max_length = 0

                column_index = (
                    column_cells[0].column
                )

                for cell in column_cells:

                    value = cell.value

                    if value is not None:

                        max_length = max(
                            max_length,
                            len(str(value)),
                        )

                worksheet.column_dimensions[
                    get_column_letter(
                        column_index
                    )
                ].width = min(
                    max(max_length + 2, 12),
                    40,
                )

            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = (
                worksheet.dimensions
            )

            # --------------------------------------------------
            # Save workbook to memory
            # --------------------------------------------------

            output = BytesIO()

            workbook.save(output)

            output.seek(0)

            # --------------------------------------------------
            # Return Excel file
            # --------------------------------------------------

            return StreamingResponse(
                output,
                media_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                headers={
                    "Content-Disposition": (
                        'attachment; filename="Inventory.xlsx"'
                    )
                },
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to export inventory: "
                    f"{str(e)}"
                ),
            )


    # ==========================================================
    # Dashboard
    # ==========================================================

    @staticmethod
    def dashboard(
        db: Session,
        search: str = None,
        warehouse_id: int = None,
        product_id: int = None,
        stock_status: str = None,
    ):

        return InventoryRepository.dashboard(
            db=db,
            search=search,
            warehouse_id=warehouse_id,
            product_id=product_id,
            stock_status=stock_status,
        )

    # ==========================================================
    # Increase Stock After Purchase
    # ==========================================================

    @staticmethod
    def increase_stock(
        db: Session,
        product_id: int,
        warehouse_id: int,
        quantity: int,
        purchase_price,
        purchase_date,
        user_id: int,
    ):

        # ======================================================
        # Validate Quantity
        # ======================================================

        if quantity <= 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Purchase quantity must be "
                    "greater than zero."
                ),
            )

        # ======================================================
        # Get Inventory
        # ======================================================

        inventory = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db=db,
                product_id=product_id,
                warehouse_id=warehouse_id,
            )
        )

        # ======================================================
        # Inventory Already Exists
        # ======================================================

        if inventory:

            inventory.stock += quantity

            inventory.last_purchase_price = (
                purchase_price
            )

            inventory.last_purchase_date = (
                purchase_date
            )

            inventory.updated_by = user_id

            # --------------------------------------------------
            # Refresh Status
            # --------------------------------------------------

            InventoryService.refresh_inventory(
                inventory
            )

            db.flush()

            db.refresh(inventory)

            return inventory

        # ======================================================
        # Inventory Doesn't Exist
        # ======================================================

        inventory = Inventory(

            product_id=product_id,

            warehouse_id=warehouse_id,

            stock=quantity,

            last_purchase_price=purchase_price,

            last_purchase_date=purchase_date,

            stock_status="IN_STOCK",

            created_by=user_id,

            updated_by=user_id,
        )

        # ======================================================
        # Refresh Status
        # ======================================================

        InventoryService.refresh_inventory(
            inventory
        )

        # ======================================================
        # Add
        # ======================================================

        db.add(inventory)

        db.flush()

        db.refresh(inventory)

        return inventory

    # ==========================================================
    # Get Stock
    # ==========================================================

    @staticmethod
    def get_stock(
        db: Session,
        product_id,
        warehouse_id,
    ):

        inventory = (
            InventoryRepository.get_stock(
                db,
                product_id,
                warehouse_id,
            )
        )

        # ======================================================
        # Inventory Exists
        # ======================================================

        if inventory:

            return inventory.stock

        # ======================================================
        # Inventory Does Not Exist
        # ======================================================

        return 0


# ==========================================================
# Service Instance
# ==========================================================

inventory_service = InventoryService()