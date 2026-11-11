from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.goods_receipt import GoodsReceipt
from app.models.goods_receipt_item import GoodsReceiptItem
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.inventory_transaction import InventoryTransaction
from app.models.inventory import Inventory

from app.repositories.goods_receipt_repository import (
    GoodsReceiptRepository
)

from app.repositories.purchase_order_repository import (
    PurchaseOrderRepository
)

from app.repositories.inventory_repository import (
    InventoryRepository
)

from app.utils.grn_number import (
    GRNNumberGenerator
)

from app.utils.transaction_number import (
    TransactionNumberGenerator
)

from app.repositories.inventory_transaction_repository import (
    InventoryTransactionRepository
)


class GoodsReceiptService:

    # =====================================================
    # Create Goods Receipt
    # =====================================================

    @staticmethod
    def create_goods_receipt(
        db: Session,
        data,
        current_user
    ):

        try:

            # =================================================
            # Validate Purchase Order
            # =================================================

            purchase_order = (
                PurchaseOrderRepository.get_by_id(
                    db,
                    data.purchase_order_id
                )
            )

            if not purchase_order:

                raise HTTPException(
                    status_code=404,
                    detail="Purchase Order not found."
                )

            if purchase_order.status in [
                "COMPLETED",
                "CANCELLED"
            ]:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Cannot receive goods for a "
                        f"{purchase_order.status} "
                        f"Purchase Order."
                    )
                )

            # =================================================
            # Validate Supplier
            # =================================================

            if (
                purchase_order.supplier_id
                != data.supplier_id
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Supplier mismatch."
                )

            # =================================================
            # Validate Warehouse
            # =================================================

            if (
                purchase_order.warehouse_id
                != data.warehouse_id
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Warehouse mismatch."
                )

            # =================================================
            # Generate GRN Number
            # =================================================

            last_grn = (
                GoodsReceiptRepository.last_goods_receipt(
                    db
                )
            )

            if last_grn:

                grn_number = (
                    GRNNumberGenerator.generate(
                        last_grn.id + 1
                    )
                )

            else:

                grn_number = (
                    GRNNumberGenerator.generate(1)
                )

            # =================================================
            # Create Goods Receipt Header
            # =================================================

            goods_receipt = GoodsReceipt(

                grn_number=grn_number,

                purchase_order_id=(
                    data.purchase_order_id
                ),

                supplier_id=data.supplier_id,

                warehouse_id=data.warehouse_id,

                received_date=data.received_date,

                remarks=data.remarks,

                status="RECEIVED",

                created_by=current_user.id,

                updated_by=current_user.id
            )

            receipt_items = []

            # =================================================
            # Validate Duplicate Products
            # =================================================

            product_ids = [
                item.product_id
                for item in data.items
            ]

            if len(product_ids) != len(
                set(product_ids)
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Duplicate products are not "
                        "allowed in Goods Receipt."
                    )
                )

            # =================================================
            # Process Items
            # =================================================

            for item in data.items:

                # =============================================
                # Get Purchase Order Item
                # =============================================

                purchase_item = (
                    db.query(PurchaseOrderItem)
                    .filter(
                        PurchaseOrderItem.id
                        == item.purchase_order_item_id
                    )
                    .first()
                )

                if not purchase_item:

                    raise HTTPException(
                        status_code=404,
                        detail=(
                            "Purchase Order Item "
                            "not found."
                        )
                    )

                # =============================================
                # Validate Purchase Order
                # =============================================

                if (
                    purchase_item.purchase_order_id
                    != purchase_order.id
                ):

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Purchase Order Item does "
                            "not belong to this "
                            "Purchase Order."
                        )
                    )

                # =============================================
                # Validate Product
                # =============================================

                if (
                    purchase_item.product_id
                    != item.product_id
                ):

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Product does not belong "
                            "to the Purchase Order."
                        )
                    )

                # =============================================
                # Validate Quantity
                # =============================================

                if item.received_quantity <= 0:

                    raise HTTPException(
                        status_code=400,
                        detail="Invalid quantity."
                    )

                if (
                    item.received_quantity
                    > purchase_item.pending_quantity
                ):

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Received quantity exceeds "
                            "pending quantity."
                        )
                    )

                # =============================================
                # Validate Purchase Price
                # =============================================

                if item.purchase_price <= 0:

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Purchase price must be "
                            "greater than zero."
                        )
                    )

                # =============================================
                # Get Inventory
                # =============================================

                inventory = (
                    InventoryRepository
                    .get_product_inventory(
                        db,
                        item.product_id,
                        data.warehouse_id
                    )
                )

                # =============================================
                # Create Inventory If Missing
                # =============================================

                if inventory is None:

                    inventory = Inventory(

                        product_id=item.product_id,

                        warehouse_id=data.warehouse_id,

                        rack_location="DEFAULT",

                        stock=0,

                        stock_status="OUT_OF_STOCK",

                        created_by=current_user.id
                    )

                    db.add(inventory)

                    db.flush()

                # =============================================
                # UPDATE INVENTORY STOCK
                #
                # IMPORTANT:
                #
                # Goods Receipt means purchased goods have
                # physically been received.
                #
                # Therefore stock increases here.
                #
                # Only one stock field exists:
                #
                #     inventory.stock
                #
                # No:
                #
                # current_stock
                # reserved_stock
                # available_stock
                # =============================================

                inventory.stock += (
                    item.received_quantity
                )

                # =============================================
                # Update Stock Status
                # =============================================

                if inventory.stock <= 0:

                    inventory.stock_status = (
                        "OUT_OF_STOCK"
                    )

                elif inventory.stock <= 10:

                    inventory.stock_status = (
                        "LOW_STOCK"
                    )

                else:

                    inventory.stock_status = (
                        "IN_STOCK"
                    )

                # =============================================
                # Update Purchase Information
                # =============================================

                inventory.last_purchase_price = (
                    item.purchase_price
                )

                inventory.last_purchase_date = (
                    data.received_date
                )

                inventory.updated_by = (
                    current_user.id
                )

                # =============================================
                # Update Purchase Order Item
                # =============================================

                purchase_item.received_quantity += (
                    item.received_quantity
                )

                purchase_item.pending_quantity -= (
                    item.received_quantity
                )

                # =============================================
                # Create Goods Receipt Item
                # =============================================

                receipt_item = GoodsReceiptItem(

                    purchase_order_item_id=(
                        item.purchase_order_item_id
                    ),

                    product_id=item.product_id,

                    received_quantity=(
                        item.received_quantity
                    ),

                    purchase_price=item.purchase_price,

                    remarks=item.remarks
                )

                receipt_items.append(
                    receipt_item
                )

            # =================================================
            # Update Purchase Order Status
            # =================================================

            pending = (
                db.query(PurchaseOrderItem)
                .filter(
                    PurchaseOrderItem.purchase_order_id
                    == purchase_order.id,

                    PurchaseOrderItem.pending_quantity > 0
                )
                .count()
            )

            if pending == 0:

                purchase_order.status = "COMPLETED"

            else:

                purchase_order.status = (
                    "PARTIALLY_RECEIVED"
                )

            purchase_order.updated_by = (
                current_user.id
            )

            # =================================================
            # Save Goods Receipt
            # =================================================

            goods_receipt = (
                GoodsReceiptRepository.create(
                    db,
                    goods_receipt,
                    receipt_items
                )
            )

            # =================================================
            # Create Inventory Transactions
            #
            # This records the stock IN movement.
            # =================================================

            for item in data.items:

                transaction = InventoryTransaction(

                    transaction_number=(
                        TransactionNumberGenerator.generate()
                    ),

                    product_id=item.product_id,

                    warehouse_id=data.warehouse_id,

                    transaction_type="GOODS_RECEIPT",

                    reference_type="GOODS_RECEIPT",

                    reference_id=goods_receipt.id,

                    quantity=item.received_quantity,

                    unit_cost=item.purchase_price,

                    total_cost=(
                        item.received_quantity
                        * item.purchase_price
                    ),

                    remarks=item.remarks,

                    created_by=current_user.id
                )

                InventoryTransactionRepository.create(
                    db,
                    transaction
                )

            # =================================================
            # Commit
            # =================================================

            db.commit()

            db.refresh(
                goods_receipt
            )

            return goods_receipt

        # =====================================================
        # HTTP Exception
        # =====================================================

        except HTTPException:

            db.rollback()

            raise

        # =====================================================
        # Unexpected Exception
        # =====================================================

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=str(e)
            )