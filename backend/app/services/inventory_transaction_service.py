from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventory_transaction import (
    InventoryTransaction,
)

from app.repositories.inventory_transaction_repository import (
    InventoryTransactionRepository,
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

from app.schemas.inventory_transaction import (
    InventoryTransactionCreate,
    InventoryTransactionUpdate,
)

from app.utils.inventory_transaction_number import (
    InventoryTransactionNumberGenerator,
)


class InventoryTransactionService:

    # =====================================================
    # Create Transaction
    # =====================================================

    @staticmethod
    def create_transaction(
        db: Session,
        data: InventoryTransactionCreate,
        current_user,
    ):

        try:

            # =================================================
            # Normalize Transaction Type
            # =================================================

            transaction_type = (
                data.transaction_type
                .strip()
                .upper()
            )

            # =================================================
            # Product Validation
            # =================================================

            product = ProductRepository.get_by_id(
                db,
                data.product_id,
            )

            if not product:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found.",
                )

            # =================================================
            # Source Warehouse Validation
            # =================================================

            warehouse = WarehouseRepository.get_by_id(
                db,
                data.warehouse_id,
            )

            if not warehouse:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Warehouse not found.",
                )

            # =================================================
            # Quantity Validation
            # =================================================

            quantity = Decimal(
                str(data.quantity)
            )

            if quantity <= 0:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Quantity must be greater than zero.",
                )

            # =================================================
            # Unit Cost
            # =================================================

            unit_cost = Decimal(
                str(data.unit_cost or 0)
            )

            if unit_cost < 0:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unit cost cannot be negative.",
                )

            # =================================================
            # Total Cost
            # =================================================

            total_cost = (
                quantity *
                unit_cost
            )

            # =================================================
            # Transaction Number
            # =================================================

            last_transaction = (
                db.query(
                    InventoryTransaction
                )
                .order_by(
                    InventoryTransaction.id.desc()
                )
                .first()
            )

            if last_transaction:

                next_number = (
                    last_transaction.id + 1
                )

            else:

                next_number = 1

            transaction_number = (
                InventoryTransactionNumberGenerator.generate(
                    next_number
                )
            )

            # =================================================
            # Stock Transaction Types
            # =================================================

            stock_in_types = {

                "PURCHASE",

                "GOODS_RECEIPT",

                "OPENING_STOCK",

                "SALES_RETURN",

                "STOCK_ADJUSTMENT_IN",

            }

            stock_out_types = {

                "SALE",

                "SALES_OUT",

                "PURCHASE_RETURN",

                "SERVICE_PART",

                "ADJUSTMENT",

                "STOCK_ADJUSTMENT_OUT",

            }

            # =================================================
            # TRANSFER
            # =================================================
            #
            # ONE TRANSFER RECORD ONLY
            #
            # warehouse_id      = FROM
            # to_warehouse_id   = TO
            #
            # Stock:
            #
            # FROM warehouse -> decrease
            # TO warehouse   -> increase
            #
            # =================================================

            if transaction_type == "TRANSFER":

                # ---------------------------------------------
                # Destination Warehouse Required
                # ---------------------------------------------

                to_warehouse_id = getattr(
                    data,
                    "to_warehouse_id",
                    None,
                )

                if not to_warehouse_id:

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Destination warehouse "
                            "is required for a transfer."
                        ),
                    )

                # ---------------------------------------------
                # Same Warehouse Check
                # ---------------------------------------------

                if (
                    int(to_warehouse_id)
                    ==
                    int(data.warehouse_id)
                ):

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Source and destination "
                            "warehouses cannot be the same."
                        ),
                    )

                # ---------------------------------------------
                # Destination Warehouse
                # ---------------------------------------------

                to_warehouse = (
                    WarehouseRepository.get_by_id(
                        db,
                        to_warehouse_id,
                    )
                )

                if not to_warehouse:

                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=(
                            "Destination warehouse "
                            "not found."
                        ),
                    )

                # ---------------------------------------------
                # Source Inventory
                # ---------------------------------------------

                source_inventory = (
                    InventoryRepository
                    .get_by_product_and_warehouse(
                        db,
                        data.product_id,
                        data.warehouse_id,
                    )
                )

                if not source_inventory:

                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=(
                            "Source inventory record "
                            "not found."
                        ),
                    )

                # ---------------------------------------------
                # Destination Inventory
                # ---------------------------------------------

                destination_inventory = (
                    InventoryRepository
                    .get_by_product_and_warehouse(
                        db,
                        data.product_id,
                        to_warehouse_id,
                    )
                )

                # ---------------------------------------------
                # Create Destination Inventory
                # if it does not exist
                # ---------------------------------------------

                if not destination_inventory:

                    destination_inventory = (
                        InventoryRepository.create(
                            db,
                            {
                                "product_id":
                                    data.product_id,

                                "warehouse_id":
                                    to_warehouse_id,

                                "stock":
                                    0,
                            },
                        )
                    )

                # ---------------------------------------------
                # Source Stock Validation
                # ---------------------------------------------

                source_stock = int(
                    source_inventory.stock or 0
                )

                transfer_quantity = int(
                    quantity
                )

                if source_stock < transfer_quantity:

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Insufficient stock in source "
                            "warehouse. "
                            f"Available stock: "
                            f"{source_stock}"
                        ),
                    )

                # ---------------------------------------------
                # Decrease Source Stock
                # ---------------------------------------------

                source_inventory.stock = (
                    source_stock
                    -
                    transfer_quantity
                )

                # ---------------------------------------------
                # Increase Destination Stock
                # ---------------------------------------------

                destination_inventory.stock = (
                    int(
                        destination_inventory.stock or 0
                    )
                    +
                    transfer_quantity
                )

                # ---------------------------------------------
                # Update Source Stock Status
                # ---------------------------------------------

                if source_inventory.stock <= 0:

                    source_inventory.stock_status = (
                        "OUT_OF_STOCK"
                    )

                elif source_inventory.stock <= 5:

                    source_inventory.stock_status = (
                        "LOW_STOCK"
                    )

                else:

                    source_inventory.stock_status = (
                        "IN_STOCK"
                    )

                # ---------------------------------------------
                # Update Destination Stock Status
                # ---------------------------------------------

                if destination_inventory.stock <= 0:

                    destination_inventory.stock_status = (
                        "OUT_OF_STOCK"
                    )

                elif destination_inventory.stock <= 5:

                    destination_inventory.stock_status = (
                        "LOW_STOCK"
                    )

                else:

                    destination_inventory.stock_status = (
                        "IN_STOCK"
                    )

                # ---------------------------------------------
                # Updated By
                # ---------------------------------------------

                source_inventory.updated_by = (
                    current_user.id
                )

                destination_inventory.updated_by = (
                    current_user.id
                )

                # ---------------------------------------------
                # Create ONE Transfer Transaction
                # ---------------------------------------------

                transaction = InventoryTransaction(

                    transaction_number=(
                        transaction_number
                    ),

                    product_id=(
                        data.product_id
                    ),

                    warehouse_id=(
                        data.warehouse_id
                    ),

                    to_warehouse_id=(
                        to_warehouse_id
                    ),

                    transaction_type="TRANSFER",

                    reference_type=(
                        data.reference_type
                    ),

                    reference_id=(
                        data.reference_id
                    ),

                    reference_by=(
                        getattr(
                            data,
                            "reference_by",
                            None,
                        )
                    ),

                    quantity=(
                        quantity
                    ),

                    unit_cost=(
                        unit_cost
                    ),

                    total_cost=(
                        total_cost
                    ),

                    remarks=(
                        data.remarks
                    ),

                    created_by=(
                        current_user.id
                    ),

                )

                InventoryTransactionRepository.create(
                    db,
                    transaction,
                )

                db.commit()

                db.refresh(
                    transaction
                )

                return transaction

            # =================================================
            # NORMAL STOCK-IN
            # =================================================

            if transaction_type in stock_in_types:

                inventory = (
                    InventoryRepository
                    .get_by_product_and_warehouse(
                        db,
                        data.product_id,
                        data.warehouse_id,
                    )
                )

                if not inventory:

                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=(
                            "Inventory record "
                            "not found."
                        ),
                    )

                inventory.stock = (
                    int(
                        inventory.stock or 0
                    )
                    +
                    int(quantity)
                )

                # ---------------------------------------------
                # Stock Status
                # ---------------------------------------------

                if inventory.stock <= 0:

                    inventory.stock_status = (
                        "OUT_OF_STOCK"
                    )

                elif inventory.stock <= 5:

                    inventory.stock_status = (
                        "LOW_STOCK"
                    )

                else:

                    inventory.stock_status = (
                        "IN_STOCK"
                    )

                inventory.updated_by = (
                    current_user.id
                )

            # =================================================
            # NORMAL STOCK-OUT
            # =================================================

            elif transaction_type in stock_out_types:

                inventory = (
                    InventoryRepository
                    .get_by_product_and_warehouse(
                        db,
                        data.product_id,
                        data.warehouse_id,
                    )
                )

                if not inventory:

                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=(
                            "Inventory record "
                            "not found."
                        ),
                    )

                current_stock = int(
                    inventory.stock or 0
                )

                requested_quantity = int(
                    quantity
                )

                if current_stock < requested_quantity:

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Insufficient stock. "
                            f"Available stock: "
                            f"{current_stock}"
                        ),
                    )

                inventory.stock = (
                    current_stock
                    -
                    requested_quantity
                )

                # ---------------------------------------------
                # Stock Status
                # ---------------------------------------------

                if inventory.stock <= 0:

                    inventory.stock_status = (
                        "OUT_OF_STOCK"
                    )

                elif inventory.stock <= 5:

                    inventory.stock_status = (
                        "LOW_STOCK"
                    )

                else:

                    inventory.stock_status = (
                        "IN_STOCK"
                    )

                inventory.updated_by = (
                    current_user.id
                )

            # =================================================
            # Invalid Transaction
            # =================================================

            else:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Invalid transaction type: "
                        f"{data.transaction_type}"
                    ),
                )

            # =================================================
            # Create Normal Transaction
            # =================================================

            transaction = InventoryTransaction(

                transaction_number=(
                    transaction_number
                ),

                product_id=(
                    data.product_id
                ),

                warehouse_id=(
                    data.warehouse_id
                ),

                # Normal transactions do not
                # have destination warehouse.
                to_warehouse_id=None,

                transaction_type=(
                    transaction_type
                ),

                reference_type=(
                    data.reference_type
                ),

                reference_id=(
                    data.reference_id
                ),

                reference_by=(
                    getattr(
                        data,
                        "reference_by",
                        None,
                    )
                ),

                quantity=(
                    quantity
                ),

                unit_cost=(
                    unit_cost
                ),

                total_cost=(
                    total_cost
                ),

                remarks=(
                    data.remarks
                ),

                created_by=(
                    current_user.id
                ),

            )

            # =================================================
            # Save
            # =================================================

            InventoryTransactionRepository.create(
                db,
                transaction,
            )

            db.commit()

            db.refresh(
                transaction
            )

            return transaction

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Inventory transaction failed: "
                    f"{str(e)}"
                ),
            )

    # =====================================================
    # Get All Transactions
    # =====================================================

    @staticmethod
    def get_transactions(
        db: Session,
        product_id: Optional[int] = None,
        warehouse_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        reference_type: Optional[str] = None,
        reference_by: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ):

        if page < 1:
            page = 1

        if page_size < 1:
            page_size = 10

        skip = (
            (page - 1)
            *
            page_size
        )

        transactions = (
            InventoryTransactionRepository.get_all(
                db=db,
                product_id=product_id,
                warehouse_id=warehouse_id,
                transaction_type=transaction_type,
                reference_type=reference_type,
                reference_by=reference_by,
                search=search,
                skip=skip,
                limit=page_size,
            )
        )

        total = (
            InventoryTransactionRepository.count(
                db=db,
                product_id=product_id,
                warehouse_id=warehouse_id,
                transaction_type=transaction_type,
                reference_type=reference_type,
                reference_by=reference_by,
                search=search,
            )
        )

        return {

            "total": total,

            "page": page,

            "page_size": page_size,

            "items": transactions,

        }

    # =====================================================
    # Stock Transfer History
    # =====================================================

    @staticmethod
    def get_stock_transfers(
        db: Session,
        product_id: Optional[int] = None,
        warehouse_id: Optional[int] = None,
        from_warehouse_id: Optional[int] = None,
        to_warehouse_id: Optional[int] = None,
        reference_by: Optional[str] = None,
        search: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        activity: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ):

        # =================================================
        # Pagination Validation
        # =================================================

        if page < 1:
            page = 1

        if page_size < 1:
            page_size = 10

        # =================================================
        # Activity
        # =================================================

        normalized_activity = None

        if activity:

            normalized_activity = (
                activity
                .strip()
                .upper()
            )

            allowed_activities = {

                "CREATED",

                "UPDATED",

                "DELETED",

            }

            if (
                normalized_activity
                not in
                allowed_activities
            ):

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Invalid activity. "
                        "Allowed values are "
                        "CREATED, UPDATED and DELETED."
                    ),
                )

            # ---------------------------------------------
            # Only actual creation history currently exists.
            # ---------------------------------------------

            if normalized_activity in {
                "UPDATED",
                "DELETED",
            }:

                return {

                    "total": 0,

                    "page": page,

                    "page_size": page_size,

                    "items": [],

                }

        # =================================================
        # Date Handling
        # =================================================

        normalized_from_date = (
            from_date
        )

        normalized_to_date = (
            to_date
        )

        # ---------------------------------------------
        # From Date
        # ---------------------------------------------

        if normalized_from_date:

            if (
                isinstance(
                    normalized_from_date,
                    date,
                )
                and
                not isinstance(
                    normalized_from_date,
                    datetime,
                )
            ):

                normalized_from_date = (
                    datetime.combine(
                        normalized_from_date,
                        time.min,
                    )
                )

        # ---------------------------------------------
        # To Date
        # ---------------------------------------------

        if normalized_to_date:

            if (
                isinstance(
                    normalized_to_date,
                    date,
                )
                and
                not isinstance(
                    normalized_to_date,
                    datetime,
                )
            ):

                normalized_to_date = (
                    datetime.combine(
                        normalized_to_date,
                        time.max,
                    )
                )

        # =================================================
        # Pagination Offset
        # =================================================

        skip = (
            (page - 1)
            *
            page_size
        )

        # =================================================
        # Get Transfers
        # =================================================

        rows = (
            InventoryTransactionRepository
            .get_stock_transfer_rows(

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
                    normalized_from_date
                ),

                to_date=(
                    normalized_to_date
                ),

                skip=skip,

                limit=page_size,

            )
        )

        # =================================================
        # Count
        # =================================================

        total = (
            InventoryTransactionRepository
            .count_stock_transfer_rows(

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
                    normalized_from_date
                ),

                to_date=(
                    normalized_to_date
                ),

            )
        )

        # =================================================
        # Build Response
        # =================================================

        items = []

        for transaction in rows:

            # ---------------------------------------------
            # Product
            # ---------------------------------------------

            product = (
                ProductRepository.get_by_id(
                    db,
                    transaction.product_id,
                )
            )

            product_name = None

            if product:

                product_name = getattr(
                    product,
                    "product_name",
                    None,
                )

            # ---------------------------------------------
            # From Warehouse
            # ---------------------------------------------

            from_warehouse = (
                WarehouseRepository.get_by_id(
                    db,
                    transaction.warehouse_id,
                )
            )

            from_warehouse_name = None

            if from_warehouse:

                from_warehouse_name = getattr(
                    from_warehouse,
                    "warehouse_name",
                    None,
                )

            # ---------------------------------------------
            # To Warehouse
            # ---------------------------------------------

            to_warehouse_name = None

            if transaction.to_warehouse_id:

                to_warehouse = (
                    WarehouseRepository.get_by_id(
                        db,
                        transaction.to_warehouse_id,
                    )
                )

                if to_warehouse:

                    to_warehouse_name = getattr(
                        to_warehouse,
                        "warehouse_name",
                        None,
                    )

            # ---------------------------------------------
            # Quantity
            # ---------------------------------------------

            quantity = (
                transaction.quantity
                or
                Decimal("0.00")
            )

            # ---------------------------------------------
            # Activity
            # ---------------------------------------------

            activity_value = "Created"

            # ---------------------------------------------
            # Response Item
            # ---------------------------------------------

            items.append({

                "id": (
                    transaction.id
                ),

                "transaction_number": (
                    transaction.transaction_number
                ),

                "product_id": (
                    transaction.product_id
                ),

                "product_name": (
                    product_name
                ),

                "from_warehouse_id": (
                    transaction.warehouse_id
                ),

                "from_warehouse": (
                    from_warehouse_name
                ),

                "to_warehouse_id": (
                    transaction.to_warehouse_id
                ),

                "to_warehouse": (
                    to_warehouse_name
                ),

                "transaction_type": (
                    "STOCK_TRANSFER"
                ),

                "reference_type": (
                    transaction.reference_type
                ),

                "reference_id": (
                    transaction.reference_id
                ),

                "reference_by": (
                    transaction.reference_by
                ),

                "quantity": (
                    quantity
                ),

                "unit_cost": (
                    transaction.unit_cost
                    or
                    Decimal("0.00")
                ),

                "total_cost": (
                    transaction.total_cost
                    or
                    Decimal("0.00")
                ),

                "remarks": (
                    transaction.remarks
                ),

                "created_by": (
                    transaction.created_by
                ),

                "created_at": (
                    transaction.created_at
                ),

                "activity": (
                    activity_value
                ),

            })

        # =================================================
        # Final Response
        # =================================================

        return {

            "total": total,

            "page": page,

            "page_size": page_size,

            "items": items,

        }

    # =====================================================
    # Get Transaction By ID
    # =====================================================

    @staticmethod
    def get_transaction(
        db: Session,
        transaction_id: int,
    ):

        transaction = (
            InventoryTransactionRepository
            .get_by_id(
                db,
                transaction_id,
            )
        )

        if not transaction:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Inventory Transaction "
                    "not found."
                ),
            )

        return transaction

    # =====================================================
    # Update Transaction
    # =====================================================

    @staticmethod
    def update_transaction(
        db: Session,
        transaction_id: int,
        data: InventoryTransactionUpdate,
        current_user,
    ):

        try:

            transaction = (
                InventoryTransactionRepository
                .get_by_id(
                    db,
                    transaction_id,
                )
            )

            if not transaction:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        "Inventory Transaction "
                        "not found."
                    ),
                )

            # =================================================
            # Do not allow changing transfer warehouse
            # structure through generic update.
            #
            # Stock movement has already happened.
            # =================================================

            update_data = (
                data.model_dump(
                    exclude_unset=True
                )
            )

            if (
                "warehouse_id"
                in update_data
                or
                "to_warehouse_id"
                in update_data
                or
                "product_id"
                in update_data
                or
                "transaction_type"
                in update_data
                or
                "quantity"
                in update_data
            ):

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Product, warehouse, "
                        "destination warehouse, "
                        "transaction type and quantity "
                        "cannot be changed after "
                        "the transaction is created."
                    ),
                )

            # =================================================
            # Update Allowed Fields
            # =================================================

            for key, value in update_data.items():

                setattr(
                    transaction,
                    key,
                    value,
                )

            # =================================================
            # Recalculate Total Cost
            # =================================================

            if (
                data.unit_cost is not None
            ):

                transaction.unit_cost = (
                    Decimal(
                        str(
                            data.unit_cost
                        )
                    )
                )

            quantity = (
                transaction.quantity
                or
                Decimal("0")
            )

            unit_cost = (
                transaction.unit_cost
                or
                Decimal("0")
            )

            transaction.total_cost = (
                Decimal(str(quantity))
                *
                Decimal(str(unit_cost))
            )

            # =================================================
            # Save
            # =================================================

            InventoryTransactionRepository.update(
                db,
                transaction,
            )

            return transaction

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Failed to update inventory "
                    f"transaction: {str(e)}"
                ),
            )

    # =====================================================
    # Delete Transaction
    # =====================================================

    @staticmethod
    def delete_transaction(
        db: Session,
        transaction_id: int,
    ):

        transaction = (
            InventoryTransactionRepository
            .get_by_id(
                db,
                transaction_id,
            )
        )

        if not transaction:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Inventory Transaction "
                    "not found."
                ),
            )

        InventoryTransactionRepository.delete(
            db,
            transaction,
        )

        return {

            "success": True,

            "message": (
                "Inventory Transaction "
                "deleted successfully."
            ),

        }

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session,
    ):

        return (
            InventoryTransactionRepository
            .dashboard(
                db
            )
        )


# =========================================================
# Service Instance
# =========================================================

inventory_transaction_service = (
    InventoryTransactionService()
)