from datetime import datetime
from decimal import Decimal
from io import BytesIO

from fastapi import HTTPException, status

from openpyxl import Workbook

from sqlalchemy.orm import Session

from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.inventory_transaction import InventoryTransaction
from app.models.customer import Customer
from app.models.warehouse import Warehouse

from app.repositories.customer_repository import CustomerRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sales_order_repository import SalesOrderRepository
from app.repositories.warehouse_repository import WarehouseRepository

from app.schemas.sales_order import SalesOrderCreate

from app.utils.sales_order_number import SalesOrderNumberGenerator
from app.utils.transaction_number import TransactionNumberGenerator


class SalesOrderService:

    # =====================================================
    # Helper - Stock Status
    # =====================================================

    @staticmethod
    def _update_stock_status(
        inventory,
        product
    ):
        minimum_stock = getattr(
            product,
            "minimum_stock",
            5
        )

        if inventory.stock <= 0:
            inventory.stock_status = "OUT_OF_STOCK"

        elif inventory.stock <= minimum_stock:
            inventory.stock_status = "LOW_STOCK"

        else:
            inventory.stock_status = "IN_STOCK"

    # =====================================================
    # Helper - Deduct Stock
    # =====================================================

    @staticmethod
    def _deduct_stock(
        db: Session,
        product,
        inventory,
        quantity: int,
        selling_price,
        sales_order_id: int,
        current_user
    ):
        """
        Deduct actual inventory stock.

        There is NO reservation system.

        Stock is reduced only inside the same database
        transaction as the sales order.
        """

        quantity = int(quantity)

        if quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than zero."
            )

        if inventory.stock < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock for "
                    f"{product.product_name}. "
                    f"Stock = {inventory.stock}, "
                    f"requested = {quantity}."
                )
            )

        # ---------------------------------------------
        # Deduct Actual Stock
        # ---------------------------------------------

        inventory.stock -= quantity

        inventory.updated_by = current_user.id

        # ---------------------------------------------
        # Update Status
        # ---------------------------------------------

        SalesOrderService._update_stock_status(
            inventory,
            product
        )

        InventoryRepository.update(
            db,
            inventory
        )

        # ---------------------------------------------
        # Inventory Transaction
        # ---------------------------------------------

        transaction = InventoryTransaction(
            transaction_number=(
                TransactionNumberGenerator.generate()
            ),
            product_id=product.id,
            warehouse_id=inventory.warehouse_id,
            transaction_type="SALE",
            reference_type="SALES_ORDER",
            reference_id=sales_order_id,
            quantity=quantity,
            unit_cost=(
                selling_price
                or Decimal("0.00")
            ),
            total_cost=(
                Decimal(quantity)
                * Decimal(
                    str(
                        selling_price
                        or 0
                    )
                )
            ),
            remarks="Stock deducted for completed sale.",
            created_by=current_user.id
        )

        db.add(transaction)

        return transaction

    # =====================================================
    # Helper - Restore Stock
    # =====================================================

    @staticmethod
    def _restore_stock(
        db: Session,
        product,
        warehouse_id: int,
        quantity: int,
        selling_price,
        sales_order_id: int,
        current_user,
        transaction_type="SALE_RETURN",
        remarks="Stock restored after sales order cancellation."
    ):
        """
        Return stock to inventory.

        Used when:
        - An active sale is deleted/cancelled
        - An existing sale quantity is reduced
        - A sale is moved to another warehouse
        - An updated sale removes a product
        """

        quantity = int(quantity)

        if quantity <= 0:
            return None

        inventory = (
            InventoryRepository
            .get_product_inventory(
                db,
                product.id,
                warehouse_id
            )
        )

        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Inventory not found for "
                    f"{product.product_name}."
                )
            )

        inventory.stock += quantity

        inventory.updated_by = current_user.id

        SalesOrderService._update_stock_status(
            inventory,
            product
        )

        InventoryRepository.update(
            db,
            inventory
        )

        transaction = InventoryTransaction(
            transaction_number=(
                TransactionNumberGenerator.generate()
            ),
            product_id=product.id,
            warehouse_id=warehouse_id,
            transaction_type=transaction_type,
            reference_type="SALES_ORDER",
            reference_id=sales_order_id,
            quantity=quantity,
            unit_cost=(
                selling_price
                or Decimal("0.00")
            ),
            total_cost=(
                Decimal(quantity)
                * Decimal(
                    str(
                        selling_price
                        or 0
                    )
                )
            ),
            remarks=remarks,
            created_by=current_user.id
        )

        db.add(transaction)

        return transaction

    # =====================================================
    # Create Sales Order
    # =====================================================

    @staticmethod
    def create_sales_order(
        db: Session,
        data: SalesOrderCreate,
        current_user
    ):

        try:

            # =================================================
            # Validate Customer
            # =================================================

            customer = CustomerRepository.get_by_id(
                db,
                data.customer_id
            )

            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found."
                )

            if not customer.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Customer is inactive."
                )

            # =================================================
            # Validate Warehouse
            # =================================================

            warehouse = WarehouseRepository.get_by_id(
                db,
                data.warehouse_id
            )

            if not warehouse:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Warehouse not found."
                )

            if not getattr(
                warehouse,
                "is_active",
                False
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Warehouse is inactive."
                )

            # =================================================
            # Validate Items
            # =================================================

            if not data.items:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one product is required."
                )

            product_ids = [
                item.product_id
                for item in data.items
            ]

            if (
                len(product_ids)
                != len(set(product_ids))
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Duplicate products are not allowed "
                        "in Sales Order."
                    )
                )

            # =================================================
            # Generate Sales Order Number
            # =================================================

            last_order = (
                SalesOrderRepository.last_sales_order(
                    db
                )
            )

            last_so_number = (
                last_order.so_number
                if last_order
                else None
            )

            so_number = (
                SalesOrderNumberGenerator.generate(
                    last_so_number
                )
            )

            # =================================================
            # Totals
            # =================================================

            subtotal = Decimal("0.00")
            discount_total = Decimal("0.00")
            gst_total = Decimal("0.00")
            grand_total = Decimal("0.00")

            # =================================================
            # Payment Status
            # =================================================

            payment_status = (
                data.payment_status
                or "PENDING"
            )

            payment_status = str(
                payment_status
            ).strip().upper()

            if payment_status == "RECEIVED BY HAND":
                payment_status = "RECEIVED_BY_HAND"

            if payment_status == "PARTIALLY RECEIVED BY HAND":
                payment_status = "PARTIALLY_RECEIVED_BY_HAND"

            if payment_status == "RECEIVED TO ACCOUNT":
                payment_status = "RECEIVED_TO_ACCOUNT"

            if payment_status == "PARTIALLY RECEIVED TO ACCOUNT":
                payment_status = "PARTIALLY_RECEIVED_TO_ACCOUNT"

            allowed_payment_statuses = {
                "PENDING",
                "RECEIVED_BY_HAND",
                "PARTIALLY_RECEIVED_BY_HAND",
                "RECEIVED_TO_ACCOUNT",
                "PARTIALLY_RECEIVED_TO_ACCOUNT"
            }

            if payment_status not in allowed_payment_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Invalid payment status. "
                        "Allowed values are PENDING, "
                        "RECEIVED_BY_HAND, "
                        "PARTIALLY_RECEIVED_BY_HAND, "
                        "RECEIVED_TO_ACCOUNT and "
                        "PARTIALLY_RECEIVED_TO_ACCOUNT."
                    )
                )

            # =================================================
            # Paid Amount
            # =================================================

            paid_amount = (
                data.paid_amount
                if data.paid_amount is not None
                else Decimal("0.00")
            )

            paid_amount = Decimal(
                str(paid_amount)
            )

            if paid_amount < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Paid amount cannot be negative."
                )

            # =================================================
            # Sales Order Header
            # =================================================

            sales_order = SalesOrder(
                so_number=so_number,

                # =================================================
                # Sales Reference
                # =================================================
                #
                # Store the reference entered on the sales form.
                # This is displayed in the Sales table as
                # "Reference By".
                #
                reference=(
                    data.reference.strip()
                    if data.reference
                    and data.reference.strip()
                    else None
                ),

                customer_id=data.customer_id,
                warehouse_id=data.warehouse_id,
                order_date=data.order_date,
                due_date=data.due_date,
                expected_delivery_date=(
                    data.expected_delivery_date
                ),

                status="PENDING",

                payment_status=payment_status,
                payment_method=data.payment_method,
                payment_reference=data.payment_reference,
                paid_amount=paid_amount,

                subtotal=Decimal("0.00"),
                discount_amount=Decimal("0.00"),
                gst_amount=Decimal("0.00"),
                other_charges=Decimal("0.00"),
                grand_total=Decimal("0.00"),

                remarks=data.remarks,

                created_by=current_user.id,
                updated_by=current_user.id
            )

            items = []

            # =================================================
            # Process Items
            # =================================================

            for item in data.items:

                # ---------------------------------------------
                # Product
                # ---------------------------------------------

                product = ProductRepository.get_by_id(
                    db,
                    item.product_id
                )

                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=(
                            f"Product {item.product_id} "
                            f"not found."
                        )
                    )

                # ---------------------------------------------
                # Product Active Check
                # ---------------------------------------------

                prod_status = getattr(
                    product,
                    "status",
                    None
                )

                if (
                    not prod_status
                    or str(prod_status).lower()
                    != "active"
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"{product.product_name} "
                            f"is inactive."
                        )
                    )

                # ---------------------------------------------
                # Quantity
                # ---------------------------------------------

                quantity = int(
                    item.quantity
                )

                if quantity <= 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Quantity must be "
                            "greater than zero."
                        )
                    )

                # ---------------------------------------------
                # Selling Price
                # ---------------------------------------------

                selling_price = Decimal(
                    str(
                        product.retail_price
                        or 0
                    )
                )

                if selling_price <= 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Sale price for "
                            f"{product.product_name} "
                            f"must be greater than zero "
                            f"in Product Master."
                        )
                    )

                # ---------------------------------------------
                # Inventory
                # ---------------------------------------------

                inventory = (
                    InventoryRepository
                    .get_product_inventory(
                        db,
                        item.product_id,
                        data.warehouse_id
                    )
                )

                if not inventory:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=(
                            f"No inventory found for "
                            f"{product.product_name} "
                            f"in the selected warehouse."
                        )
                    )

                # ---------------------------------------------
                # Check Actual Stock
                # ---------------------------------------------

                if inventory.stock < quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Insufficient stock for "
                            f"{product.product_name}. "
                            f"Stock = {inventory.stock}, "
                            f"requested = {quantity}."
                        )
                    )

                # ---------------------------------------------
                # Calculate Line Amounts
                # ---------------------------------------------

                line_subtotal = (
                    Decimal(quantity)
                    * selling_price
                )

                discount_percentage = Decimal(
                    str(
                        item.discount_percentage
                        or 0
                    )
                )

                gst_percentage = Decimal(
                    str(
                        product.gst_percentage
                        if product.gst_percentage
                        is not None
                        else 18
                    )
                )

                discount_amount = (
                    line_subtotal
                    * discount_percentage
                    / Decimal("100")
                )

                taxable_amount = (
                    line_subtotal
                    - discount_amount
                )

                gst_amount = (
                    taxable_amount
                    * gst_percentage
                    / Decimal("100")
                )

                line_total = (
                    taxable_amount
                    + gst_amount
                )

                subtotal += line_subtotal
                discount_total += discount_amount
                gst_total += gst_amount
                grand_total += line_total

                # ---------------------------------------------
                # Serial Numbers
                # ---------------------------------------------

                serial_numbers = getattr(
                    item,
                    "serial_numbers",
                    []
                )

                if serial_numbers is None:
                    serial_numbers = []

                if isinstance(
                    serial_numbers,
                    tuple
                ):
                    serial_numbers = list(
                        serial_numbers
                    )

                if serial_numbers:

                    if len(serial_numbers) != quantity:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Product "
                                f"{product.product_name}: "
                                f"quantity is "
                                f"{quantity}, "
                                f"but "
                                f"{len(serial_numbers)} "
                                f"serial number(s) "
                                f"were provided."
                            )
                        )

                # ---------------------------------------------
                # Sales Order Item
                # ---------------------------------------------

                order_item = SalesOrderItem(
                    product_id=product.id,

                    quantity=quantity,

                    delivered_quantity=0,

                    pending_quantity=quantity,

                    selling_price=selling_price,

                    discount_percentage=(
                        discount_percentage
                    ),

                    discount_amount=(
                        discount_amount
                    ),

                    gst_percentage=(
                        gst_percentage
                    ),

                    gst_amount=(
                        gst_amount
                    ),

                    line_total=line_total,

                    product_name=(
                        product.product_name
                    ),

                    sku=product.sku,

                    model_no=product.model_no,

                    serial_numbers=(
                        serial_numbers
                    ),

                    remarks=item.remarks
                )

                items.append(order_item)

            # =================================================
            # Update Sales Order Totals
            # =================================================

            sales_order.subtotal = subtotal

            sales_order.discount_amount = (
                discount_total
            )

            sales_order.gst_amount = (
                gst_total
            )

            sales_order.grand_total = (
                grand_total
            )

            # =================================================
            # Payment Validation
            # =================================================

            if paid_amount > grand_total:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Paid amount cannot be "
                        "greater than the grand total."
                    )
                )

            if payment_status == "PENDING":

                if paid_amount != Decimal("0.00"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Paid amount must be 0 "
                            "when payment status is PENDING."
                        )
                    )

            elif payment_status in {
                "PARTIALLY_RECEIVED_BY_HAND",
                "PARTIALLY_RECEIVED_TO_ACCOUNT"
            }:

                if paid_amount <= Decimal("0.00"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Partially received payment "
                            "amount must be greater than 0."
                        )
                    )

                if paid_amount >= grand_total:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Partially received payment "
                            "amount must be less than the grand total."
                        )
                    )

            elif payment_status in {
                "RECEIVED_BY_HAND",
                "RECEIVED_TO_ACCOUNT"
            }:

                if paid_amount != grand_total:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Paid amount must equal the grand total "
                            "for a fully received payment."
                        )
                    )

            # =================================================
            # Save Sales Order
            #
            # At this point all validation has passed.
            # =================================================

            sales_order = (
                SalesOrderRepository.create(
                    db,
                    sales_order,
                    items
                )
            )

            db.flush()

            # =================================================
            # DEDUCT STOCK ON SALE CREATION
            #
            # Stock is deducted exactly once when the sale is
            # successfully created. The deduction is inside the
            # same database transaction as the sales order.
            # =================================================

            for item in items:

                inventory = (
                    InventoryRepository
                    .get_product_inventory(
                        db,
                        item.product_id,
                        sales_order.warehouse_id
                    )
                )

                if not inventory:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=(
                            f"Inventory not found for "
                            f"{item.product_name}."
                        )
                    )

                product = ProductRepository.get_by_id(
                    db,
                    item.product_id
                )

                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=(
                            f"Product {item.product_id} not found."
                        )
                    )

                SalesOrderService._deduct_stock(
                    db=db,
                    product=product,
                    inventory=inventory,
                    quantity=int(item.quantity),
                    selling_price=item.selling_price,
                    sales_order_id=sales_order.id,
                    current_user=current_user
                )

            # =================================================
            # Commit Everything
            # =================================================

            db.commit()

            db.refresh(
                sales_order
            )

            return sales_order

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

            import traceback

            db.rollback()

            traceback.print_exc()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Sales Order Creation Failed : "
                    f"{str(e)}"
                )
            )

    # =====================================================
    # Complete Sales Order
    # =====================================================

    @staticmethod
    def complete_sales_order(
        db: Session,
        sales_order_id: int,
        current_user
    ):
        """
        Mark an existing sale as COMPLETED.

        IMPORTANT:
        Inventory is already deducted when the sale is created, so
        this endpoint MUST NOT deduct stock again.
        """
        try:

            sales_order = (
                SalesOrderRepository.get_by_id(
                    db,
                    sales_order_id
                )
            )

            if not sales_order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sales Order not found."
                )

            if sales_order.status == "COMPLETED":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sales Order is already completed."
                )

            if sales_order.status == "CANCELLED":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cancelled Sales Order cannot be completed."
                )

            if sales_order.status != "PENDING":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Sales Order with status "
                        f"{sales_order.status} cannot be completed."
                    )
                )

            # Stock was deducted at creation. Do NOT call _deduct_stock here.
            sales_order.status = "COMPLETED"
            sales_order.updated_by = current_user.id

            SalesOrderRepository.update(
                db,
                sales_order
            )

            db.commit()
            db.refresh(sales_order)

            return sales_order

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            import traceback

            db.rollback()
            traceback.print_exc()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Sales Order Completion Failed : "
                    f"{str(e)}"
                )
            )

    # =====================================================
    # Cancel Sales Order
    # =====================================================

    @staticmethod
    def cancel_sales_order(
        db: Session,
        sales_order_id: int,
        current_user
    ):
        try:

            sales_order = (
                SalesOrderRepository.get_by_id(
                    db,
                    sales_order_id
                )
            )

            if not sales_order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sales Order not found."
                )

            if sales_order.status == "CANCELLED":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sales Order is already cancelled."
                )

            # =================================================
            # PENDING / COMPLETED -> CANCELLED
            #
            # Both states already have stock deducted because stock
            # is deducted when the sale is created. Restore the exact
            # quantities once when cancelling.
            # =================================================

            if sales_order.status in {"PENDING", "COMPLETED"}:

                items = list(
                    getattr(
                        sales_order,
                        "items",
                        []
                    )
                    or []
                )

                for item in items:

                    quantity = int(
                        item.quantity or 0
                    )

                    if quantity <= 0:
                        continue

                    product = (
                        ProductRepository.get_by_id(
                            db,
                            item.product_id
                        )
                    )

                    if not product:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=(
                                f"Product "
                                f"{item.product_id} "
                                f"not found."
                            )
                        )

                    SalesOrderService._restore_stock(
                        db=db,
                        product=product,
                        warehouse_id=sales_order.warehouse_id,
                        quantity=quantity,
                        selling_price=item.selling_price,
                        sales_order_id=sales_order.id,
                        current_user=current_user,
                        transaction_type="SALE_RETURN",
                        remarks=(
                            "Stock restored after "
                            "sales order cancellation."
                        )
                    )

                sales_order.status = "CANCELLED"

                sales_order.updated_by = (
                    current_user.id
                )

                SalesOrderRepository.update(
                    db,
                    sales_order
                )

                db.commit()

                db.refresh(
                    sales_order
                )

                return sales_order

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Sales Order with status "
                    f"{sales_order.status} cannot be cancelled."
                )
            )

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:

            import traceback

            db.rollback()
            traceback.print_exc()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Sales Order Cancellation Failed : "
                    f"{str(e)}"
                )
            )

    # =====================================================
    # Get Sales Orders
    # =====================================================

    @staticmethod
    def get_sales_orders(
        db: Session,
        search=None,
        customer_id=None,
        warehouse_id=None,
        product_id=None,
        status=None,
        payment_status=None,
        date_from=None,
        date_to=None,
        page=1,
        page_size=10
    ):

        skip = (
            page - 1
        ) * page_size

        return SalesOrderRepository.get_all(
            db=db,
            search=search,
            customer_id=customer_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
            status=status,
            payment_status=payment_status,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=page_size
        )

    # =====================================================
    # Get Sales Order
    # =====================================================

    @staticmethod
    def get_sales_order(
        db: Session,
        sales_order_id: int
    ):

        sales_order = (
            SalesOrderRepository.get_by_id(
                db,
                sales_order_id
            )
        )

        if not sales_order:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales Order not found."
            )

        return sales_order

    # =====================================================
    # Update Sales Order
    # =====================================================

    @staticmethod
    def update_sales_order(
        db: Session,
        sales_order_id: int,
        data,
        current_user
    ):

        try:

            # =================================================
            # Existing Order
            # =================================================

            sales_order = (
                SalesOrderRepository.get_by_id(
                    db,
                    sales_order_id
                )
            )

            if not sales_order:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sales Order not found."
                )

            # =================================================
            # Update payload
            # =================================================
            # Item quantities are allowed to change. Inventory is
            # reconciled using ONLY the quantity difference:
            #
            #   old 2 -> new 3  => deduct 1
            #   old 3 -> new 2  => restore 1
            #   old 2 -> new 2  => no stock movement
            #
            # Product/warehouse changes restore the old allocation
            # and deduct the new allocation.
            # =================================================

            update_data = data.model_dump(
                exclude_unset=True
            )

            # =================================================
            # Don't Allow Workflow Status Change
            # =================================================

            update_data.pop(
                "status",
                None
            )

            # =================================================
            # Detect Item Update
            # =================================================

            items_were_supplied = (
                "items" in update_data
            )

            new_items = (
                list(data.items)
                if items_were_supplied
                else None
            )

            update_data.pop(
                "items",
                None
            )

            # =================================================
            # Payment Status
            # =================================================

            if "payment_status" in update_data:

                payment_status = (
                    update_data[
                        "payment_status"
                    ]
                )

                if payment_status is not None:

                    payment_status = str(
                        payment_status
                    ).strip().upper()

                    if payment_status == "RECEIVED BY HAND":
                        payment_status = (
                            "RECEIVED_BY_HAND"
                        )

                    if payment_status == "PARTIALLY RECEIVED BY HAND":
                        payment_status = (
                            "PARTIALLY_RECEIVED_BY_HAND"
                        )

                    if payment_status == "RECEIVED TO ACCOUNT":
                        payment_status = (
                            "RECEIVED_TO_ACCOUNT"
                        )

                    if payment_status == "PARTIALLY RECEIVED TO ACCOUNT":
                        payment_status = (
                            "PARTIALLY_RECEIVED_TO_ACCOUNT"
                        )

                    allowed_payment_statuses = {
                        "PENDING",
                        "RECEIVED_BY_HAND",
                        "PARTIALLY_RECEIVED_BY_HAND",
                        "RECEIVED_TO_ACCOUNT",
                        "PARTIALLY_RECEIVED_TO_ACCOUNT"
                    }

                    if payment_status not in (
                        allowed_payment_statuses
                    ):

                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                "Invalid payment status. "
                                "Allowed values are PENDING, "
                                "RECEIVED_BY_HAND, "
                                "PARTIALLY_RECEIVED_BY_HAND, "
                                "RECEIVED_TO_ACCOUNT and "
                                "PARTIALLY_RECEIVED_TO_ACCOUNT."
                            )
                        )

                    update_data[
                        "payment_status"
                    ] = payment_status

            # =================================================
            # Paid Amount
            # =================================================

            if "paid_amount" in update_data:

                paid_amount = (
                    update_data[
                        "paid_amount"
                    ]
                )

                if paid_amount is not None:

                    paid_amount = Decimal(
                        str(paid_amount)
                    )

                    if paid_amount < 0:

                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                "Paid amount cannot "
                                "be negative."
                            )
                        )

                    update_data[
                        "paid_amount"
                    ] = paid_amount

            # =================================================
            # Current Warehouse
            # =================================================

            old_warehouse_id = (
                sales_order.warehouse_id
            )

            new_warehouse_id = (
                update_data.get(
                    "warehouse_id",
                    old_warehouse_id
                )
            )

            # =================================================
            # Full Item Update
            # =================================================

            if items_were_supplied:

                if not new_items:

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "At least one product is required "
                            "when updating a sales order."
                        )
                    )

                # ---------------------------------------------
                # Duplicate Products
                # ---------------------------------------------

                product_ids = [
                    item.product_id
                    for item in new_items
                ]

                if (
                    len(product_ids)
                    != len(set(product_ids))
                ):

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Duplicate products are not "
                            "allowed in Sales Order."
                        )
                    )

                # ---------------------------------------------
                # Don't edit delivered order items
                # ---------------------------------------------

                existing_items = list(
                    getattr(
                        sales_order,
                        "items",
                        []
                    )
                    or []
                )

                for old_item in existing_items:

                    delivered_quantity = int(
                        old_item.delivered_quantity
                        or 0
                    )

                    if delivered_quantity > 0:

                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                "This sales order contains "
                                "delivered quantity and its "
                                "products cannot be edited."
                            )
                        )

                # ---------------------------------------------
                # Validate New Warehouse
                # ---------------------------------------------

                warehouse = (
                    WarehouseRepository.get_by_id(
                        db,
                        new_warehouse_id
                    )
                )

                if not warehouse:

                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Warehouse not found."
                    )

                if not getattr(
                    warehouse,
                    "is_active",
                    False
                ):

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Warehouse is inactive."
                    )

                # ---------------------------------------------
                # Prepare New Items
                # ---------------------------------------------

                prepared_items = []

                subtotal = Decimal("0.00")
                discount_total = Decimal("0.00")
                gst_total = Decimal("0.00")
                grand_total = Decimal("0.00")

                for item in new_items:

                    quantity = int(
                        item.quantity
                    )

                    if quantity <= 0:

                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                "Quantity must be "
                                "greater than zero."
                            )
                        )

                    product = (
                        ProductRepository.get_by_id(
                            db,
                            item.product_id
                        )
                    )

                    if not product:

                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=(
                                f"Product "
                                f"{item.product_id} "
                                f"not found."
                            )
                        )

                    prod_status = getattr(
                        product,
                        "status",
                        None
                    )

                    if (
                        not prod_status
                        or str(prod_status).lower()
                        != "active"
                    ):

                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"{product.product_name} "
                                f"is inactive."
                            )
                        )

                    selling_price = Decimal(
                        str(
                            product.retail_price
                            or 0
                        )
                    )

                    if selling_price <= 0:

                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Sale price for "
                                f"{product.product_name} "
                                f"must be greater than zero "
                                f"in Product Master."
                            )
                        )

                    inventory = (
                        InventoryRepository
                        .get_product_inventory(
                            db,
                            item.product_id,
                            new_warehouse_id
                        )
                    )

                    if not inventory:

                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=(
                                f"No inventory found for "
                                f"{product.product_name} "
                                f"in the selected warehouse."
                            )
                        )

                    # -----------------------------------------
                    # Serial Numbers
                    # -----------------------------------------

                    serial_numbers = getattr(
                        item,
                        "serial_numbers",
                        []
                    )

                    if serial_numbers is None:
                        serial_numbers = []

                    if isinstance(
                        serial_numbers,
                        tuple
                    ):
                        serial_numbers = list(
                            serial_numbers
                        )

                    if serial_numbers:

                        if (
                            len(serial_numbers)
                            != quantity
                        ):

                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=(
                                    f"Product "
                                    f"{product.product_name}: "
                                    f"quantity is "
                                    f"{quantity}, "
                                    f"but "
                                    f"{len(serial_numbers)} "
                                    f"serial number(s) "
                                    f"were provided."
                                )
                            )

                    # -----------------------------------------
                    # Pricing
                    # -----------------------------------------

                    line_subtotal = (
                        Decimal(quantity)
                        * selling_price
                    )

                    discount_percentage = Decimal(
                        str(
                            item.discount_percentage
                            or 0
                        )
                    )

                    gst_percentage = Decimal(
                        str(
                            product.gst_percentage
                            if product.gst_percentage
                            is not None
                            else 18
                        )
                    )

                    discount_amount = (
                        line_subtotal
                        * discount_percentage
                        / Decimal("100")
                    )

                    taxable_amount = (
                        line_subtotal
                        - discount_amount
                    )

                    gst_amount = (
                        taxable_amount
                        * gst_percentage
                        / Decimal("100")
                    )

                    line_total = (
                        taxable_amount
                        + gst_amount
                    )

                    subtotal += line_subtotal
                    discount_total += discount_amount
                    gst_total += gst_amount
                    grand_total += line_total

                    prepared_items.append(
                        {
                            "item": item,
                            "product": product,
                            "inventory": inventory,
                            "selling_price": selling_price,
                            "discount_percentage":
                                discount_percentage,
                            "discount_amount":
                                discount_amount,
                            "gst_percentage":
                                gst_percentage,
                            "gst_amount":
                                gst_amount,
                            "line_total":
                                line_total,
                            "serial_numbers":
                                serial_numbers,
                        }
                    )

                # =================================================
                # INVENTORY RECONCILIATION
                # =================================================
                # The existing sale has already deducted its old
                # quantities. Therefore an update must move only the
                # DIFFERENCE in quantity.
                #
                # Example:
                #   old = 2, new = 3 -> deduct 1
                #   old = 3, new = 2 -> restore 1
                #   old = 2, new = 2 -> do nothing
                #
                # If product or warehouse changes, the old allocation
                # is fully returned and the new allocation is deducted.
                # =================================================

                old_allocations = {}
                for old_item in existing_items:
                    key = (
                        int(old_item.product_id),
                        int(old_warehouse_id)
                    )
                    old_allocations[key] = (
                        old_allocations.get(key, 0)
                        + int(old_item.quantity or 0)
                    )

                new_allocations = {}
                for prepared in prepared_items:
                    item = prepared["item"]
                    key = (
                        int(item.product_id),
                        int(new_warehouse_id)
                    )
                    new_allocations[key] = (
                        new_allocations.get(key, 0)
                        + int(item.quantity or 0)
                    )

                # Validate every positive delta before changing stock.
                # This keeps the operation atomic if any product does
                # not have enough stock.
                for key, new_quantity in new_allocations.items():
                    old_quantity = old_allocations.get(key, 0)
                    delta = new_quantity - old_quantity

                    if delta <= 0:
                        continue

                    product_id, warehouse_id = key
                    product = ProductRepository.get_by_id(
                        db,
                        product_id
                    )
                    if not product:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=(
                                f"Product {product_id} not found."
                            )
                        )

                    inventory = (
                        InventoryRepository
                        .get_product_inventory(
                            db,
                            product_id,
                            warehouse_id
                        )
                    )
                    if not inventory:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=(
                                f"Inventory not found for "
                                f"{product.product_name}."
                            )
                        )

                    if inventory.stock < delta:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Insufficient stock for "
                                f"{product.product_name}. "
                                f"Available stock = {inventory.stock}, "
                                f"additional quantity required = {delta}."
                            )
                        )

                # Apply only the differences.
                all_keys = set(old_allocations) | set(new_allocations)

                for key in all_keys:
                    old_quantity = old_allocations.get(key, 0)
                    new_quantity = new_allocations.get(key, 0)
                    delta = new_quantity - old_quantity

                    if delta == 0:
                        continue

                    product_id, warehouse_id = key
                    product = ProductRepository.get_by_id(
                        db,
                        product_id
                    )
                    if not product:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=(
                                f"Product {product_id} not found."
                            )
                        )

                    if delta > 0:
                        inventory = (
                            InventoryRepository
                            .get_product_inventory(
                                db,
                                product_id,
                                warehouse_id
                            )
                        )
                        if not inventory:
                            raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND,
                                detail=(
                                    f"Inventory not found for "
                                    f"{product.product_name}."
                                )
                            )

                        # Find the new item's price for the inventory
                        # transaction.
                        selling_price = Decimal("0.00")
                        for prepared in prepared_items:
                            item = prepared["item"]
                            if (
                                int(item.product_id) == product_id
                                and int(new_warehouse_id) == warehouse_id
                            ):
                                selling_price = prepared["selling_price"]
                                break

                        SalesOrderService._deduct_stock(
                            db=db,
                            product=product,
                            inventory=inventory,
                            quantity=delta,
                            selling_price=selling_price,
                            sales_order_id=sales_order.id,
                            current_user=current_user
                        )

                    else:
                        # Negative delta means the sale quantity was
                        # reduced or the old allocation was removed.
                        restore_quantity = abs(delta)
                        selling_price = Decimal("0.00")

                        for old_item in existing_items:
                            if (
                                int(old_item.product_id) == product_id
                                and int(old_warehouse_id) == warehouse_id
                            ):
                                selling_price = (
                                    old_item.selling_price
                                    or Decimal("0.00")
                                )
                                break

                        SalesOrderService._restore_stock(
                            db=db,
                            product=product,
                            warehouse_id=warehouse_id,
                            quantity=restore_quantity,
                            selling_price=selling_price,
                            sales_order_id=sales_order.id,
                            current_user=current_user,
                            transaction_type="SALE_UPDATE_RETURN",
                            remarks=(
                                "Stock restored for the reduced "
                                "sales order quantity."
                            )
                        )

                # =================================================
                # Remove Existing Items
                # =================================================

                for old_item in existing_items:

                    db.delete(
                        old_item
                    )

                db.flush()

                # =================================================
                # Create New Sales Items
                # =================================================

                new_order_items = []

                for prepared in prepared_items:

                    item = prepared["item"]
                    product = prepared["product"]

                    quantity = int(
                        item.quantity
                    )

                    # ---------------------------------------------
                    # New Sales Item
                    # ---------------------------------------------


                    # -----------------------------------------

                    order_item = SalesOrderItem(
                        product_id=product.id,

                        quantity=quantity,

                        delivered_quantity=0,

                        pending_quantity=quantity,

                        selling_price=(
                            prepared[
                                "selling_price"
                            ]
                        ),

                        discount_percentage=(
                            prepared[
                                "discount_percentage"
                            ]
                        ),

                        discount_amount=(
                            prepared[
                                "discount_amount"
                            ]
                        ),

                        gst_percentage=(
                            prepared[
                                "gst_percentage"
                            ]
                        ),

                        gst_amount=(
                            prepared[
                                "gst_amount"
                            ]
                        ),

                        line_total=(
                            prepared[
                                "line_total"
                            ]
                        ),

                        product_name=(
                            product.product_name
                        ),

                        sku=product.sku,

                        model_no=product.model_no,

                        serial_numbers=(
                            prepared[
                                "serial_numbers"
                            ]
                        ),

                        remarks=item.remarks
                    )

                    new_order_items.append(
                        order_item
                    )

                # ---------------------------------------------
                # Attach Items
                # ---------------------------------------------

                sales_order.items = (
                    new_order_items
                )

                # ---------------------------------------------
                # Update Warehouse
                # ---------------------------------------------

                sales_order.warehouse_id = (
                    new_warehouse_id
                )

                # ---------------------------------------------
                # Financial Totals
                # ---------------------------------------------

                sales_order.subtotal = (
                    subtotal
                )

                sales_order.discount_amount = (
                    discount_total
                )

                sales_order.gst_amount = (
                    gst_total
                )

                other_charges = Decimal(
                    str(
                        sales_order.other_charges
                        or 0
                    )
                )

                sales_order.grand_total = (
                    grand_total
                    + other_charges
                )

                # ---------------------------------------------
                # Final Payment Validation
                # ---------------------------------------------

                final_paid_amount = Decimal(
                    str(
                        update_data.get(
                            "paid_amount",
                            sales_order.paid_amount
                        )
                        or 0
                    )
                )

                if final_paid_amount > (
                    sales_order.grand_total
                ):

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Paid amount cannot be "
                            "greater than the grand total."
                        )
                    )

            # =================================================
            # Warehouse-only update
            # =================================================
            # If the caller changes only the warehouse and does not
            # send items, move the existing sale allocation from the
            # old warehouse to the new warehouse.
            # =====================================================
            if (
                not items_were_supplied
                and new_warehouse_id != old_warehouse_id
            ):
                existing_items_for_move = list(
                    getattr(sales_order, "items", []) or []
                )

                # Check destination stock first.
                for old_item in existing_items_for_move:
                    quantity = int(old_item.quantity or 0)
                    if quantity <= 0:
                        continue

                    product = ProductRepository.get_by_id(
                        db,
                        old_item.product_id
                    )
                    if not product:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=(
                                f"Product {old_item.product_id} not found."
                            )
                        )

                    destination_inventory = (
                        InventoryRepository
                        .get_product_inventory(
                            db,
                            old_item.product_id,
                            new_warehouse_id
                        )
                    )
                    if not destination_inventory:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=(
                                f"Inventory not found for "
                                f"{product.product_name} in the new warehouse."
                            )
                        )

                    if destination_inventory.stock < quantity:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Insufficient stock for "
                                f"{product.product_name} in the new warehouse. "
                                f"Available stock = {destination_inventory.stock}, "
                                f"required = {quantity}."
                            )
                        )

                # Restore old warehouse and deduct new warehouse.
                for old_item in existing_items_for_move:
                    quantity = int(old_item.quantity or 0)
                    if quantity <= 0:
                        continue

                    product = ProductRepository.get_by_id(
                        db,
                        old_item.product_id
                    )
                    if not product:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=(
                                f"Product {old_item.product_id} not found."
                            )
                        )

                    SalesOrderService._restore_stock(
                        db=db,
                        product=product,
                        warehouse_id=old_warehouse_id,
                        quantity=quantity,
                        selling_price=old_item.selling_price,
                        sales_order_id=sales_order.id,
                        current_user=current_user,
                        transaction_type="SALE_UPDATE_RETURN",
                        remarks=(
                            "Stock restored because sales order warehouse changed."
                        )
                    )

                    destination_inventory = (
                        InventoryRepository
                        .get_product_inventory(
                            db,
                            old_item.product_id,
                            new_warehouse_id
                        )
                    )

                    SalesOrderService._deduct_stock(
                        db=db,
                        product=product,
                        inventory=destination_inventory,
                        quantity=quantity,
                        selling_price=old_item.selling_price,
                        sales_order_id=sales_order.id,
                        current_user=current_user
                    )

            # =================================================
            # Apply Header Updates
            # =================================================

            for key, value in update_data.items():

                setattr(
                    sales_order,
                    key,
                    value
                )

            # =================================================
            # Final Payment Validation
            # =================================================

            final_grand_total = Decimal(
                str(
                    sales_order.grand_total
                    or 0
                )
            )

            final_paid_amount = Decimal(
                str(
                    sales_order.paid_amount
                    or 0
                )
            )

            if final_paid_amount > final_grand_total:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Paid amount cannot be "
                        "greater than the grand total."
                    )
                )

            final_payment_status = (
                sales_order.payment_status
            )

            if final_payment_status == "PENDING":

                if final_paid_amount != Decimal("0.00"):

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Paid amount must be 0 "
                            "when payment status is PENDING."
                        )
                    )

            elif final_payment_status in {
                "PARTIALLY_RECEIVED_BY_HAND",
                "PARTIALLY_RECEIVED_TO_ACCOUNT"
            }:

                if final_paid_amount <= Decimal("0.00"):

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Partially received payment "
                            "amount must be greater than 0."
                        )
                    )

                if final_paid_amount >= final_grand_total:

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Partially received payment "
                            "amount must be less than the grand total."
                        )
                    )

            elif final_payment_status in {
                "RECEIVED_BY_HAND",
                "RECEIVED_TO_ACCOUNT"
            }:

                if final_paid_amount != final_grand_total:

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Paid amount must equal the grand total "
                            "for a fully received payment."
                        )
                    )

            # =================================================
            # Audit
            # =================================================

            sales_order.updated_by = (
                current_user.id
            )

            # =================================================
            # Clear Old PDF After Item Changes
            # =================================================

            if items_were_supplied:

                sales_order.pdf_file = None
                sales_order.pdf_file_name = None
                sales_order.pdf_generated_at = None

            # =================================================
            # Save
            # =================================================

            SalesOrderRepository.update(
                db,
                sales_order
            )

            db.commit()

            db.refresh(
                sales_order
            )

            return sales_order

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

            import traceback

            db.rollback()

            traceback.print_exc()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Sales Order Update Failed : "
                    f"{str(e)}"
                )
            )

    # =====================================================
    # Delete Sales Order
    # =====================================================

    @staticmethod
    def delete_sales_order(
        db: Session,
        sales_order_id: int,
        current_user=None
    ):

        try:

            sales_order = (
                SalesOrderRepository.get_by_id(
                    db,
                    sales_order_id
                )
            )

            if not sales_order:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sales Order not found."
                )

            # =================================================
            # Restore Stock For Any Active Sale
            #
            # Stock is deducted when the sale is created, so both
            # PENDING and COMPLETED sales must return their quantities.
            # =================================================

            if sales_order.status in {"PENDING", "COMPLETED"}:

                delete_user = current_user

                if delete_user is None:
                    delete_user = type(
                        "User",
                        (),
                        {
                            "id": getattr(
                                sales_order,
                                "updated_by",
                                None
                            )
                        }
                    )()

                for item in (
                    getattr(
                        sales_order,
                        "items",
                        []
                    )
                    or []
                ):

                    quantity = int(
                        item.quantity
                        or 0
                    )

                    if quantity <= 0:
                        continue

                    product = (
                        ProductRepository.get_by_id(
                            db,
                            item.product_id
                        )
                    )

                    if not product:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=(
                                f"Product "
                                f"{item.product_id} "
                                f"not found."
                            )
                        )

                    SalesOrderService._restore_stock(
                        db=db,
                        product=product,
                        warehouse_id=sales_order.warehouse_id,
                        quantity=quantity,
                        selling_price=item.selling_price,
                        sales_order_id=sales_order.id,
                        current_user=delete_user,
                        transaction_type="SALE_RETURN",
                        remarks=(
                            "Stock restored after "
                            "sales order deletion."
                        )
                    )

            # =================================================
            # Delete Sales Order
            # =================================================

            SalesOrderRepository.delete(
                db,
                sales_order
            )

            db.commit()

            return {
                "success": True,
                "message": (
                    "Sales Order deleted successfully."
                )
            }

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            import traceback

            db.rollback()

            traceback.print_exc()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Sales Order Deletion Failed : "
                    f"{str(e)}"
                )
            )

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return SalesOrderRepository.dashboard(
            db
        )

    # =====================================================
    # Export Sales Orders to Excel
    # =====================================================

    @staticmethod
    def export_sales_orders(
        db: Session,
        search=None,
        customer_id=None,
        product_id=None,
        warehouse_id=None,
        status=None,
        payment_status=None,
        date_from=None,
        date_to=None
    ):

        # =================================================
        # Base Query
        # =================================================

        query = (
            db.query(
                SalesOrder,
                Customer.customer_name.label(
                    "customer_name"
                ),
                Warehouse.warehouse_name.label(
                    "warehouse_name"
                )
            )
            .outerjoin(
                Customer,
                Customer.id
                == SalesOrder.customer_id
            )
            .outerjoin(
                Warehouse,
                Warehouse.id
                == SalesOrder.warehouse_id
            )
        )

        # =================================================
        # Search
        # =================================================

        if search:

            search_value = (
                f"%{search}%"
            )

            query = query.filter(
                SalesOrder.so_number.ilike(
                    search_value
                )
            )

        # =================================================
        # Customer
        # =================================================

        if customer_id:

            query = query.filter(
                SalesOrder.customer_id
                == customer_id
            )

        # =================================================
        # Product
        # =================================================

        if product_id:

            query = query.filter(
                SalesOrder.items.any(
                    SalesOrderItem.product_id
                    == product_id
                )
            )

        # =================================================
        # Warehouse
        # =================================================

        if warehouse_id:

            query = query.filter(
                SalesOrder.warehouse_id
                == warehouse_id
            )

        # =================================================
        # Status
        # =================================================

        if status:

            query = query.filter(
                SalesOrder.status
                == status
            )

        # =================================================
        # Payment Status
        # =================================================

        if payment_status:

            query = query.filter(
                SalesOrder.payment_status
                == payment_status
            )

        # =================================================
        # Date From
        # =================================================

        if date_from:

            query = query.filter(
                SalesOrder.order_date
                >= date_from
            )

        # =================================================
        # Date To
        # =================================================

        if date_to:

            query = query.filter(
                SalesOrder.order_date
                <= date_to
            )

        # =================================================
        # Get Orders
        # =================================================

        orders = (
            query
            .order_by(
                SalesOrder.id.desc()
            )
            .all()
        )

        # =================================================
        # Create Excel
        # =================================================

        workbook = Workbook()

        worksheet = (
            workbook.active
        )

        worksheet.title = (
            "Sales Orders"
        )

        # =================================================
        # Headers
        # =================================================

        headers = [
            "Order No.",
            "Order Date",
            "Customer",
            "Reference By",
            "Warehouse",
            "Status",
            "Payment Status",
            "Payment Method",
            "Paid Amount",
            "Subtotal",
            "Discount",
            "GST",
            "Other Charges",
            "Grand Total",
            "Remarks"
        ]

        worksheet.append(
            headers
        )

        # =================================================
        # Data
        # =================================================

        for (
            order,
            customer_name,
            warehouse_name
        ) in orders:

            row = [

                order.so_number,

                order.order_date,

                customer_name,

                order.reference,

                warehouse_name,

                order.status,

                order.payment_status,

                order.payment_method,

                float(
                    order.paid_amount
                    or 0
                ),

                float(
                    order.subtotal
                    or 0
                ),

                float(
                    order.discount_amount
                    or 0
                ),

                float(
                    order.gst_amount
                    or 0
                ),

                float(
                    order.other_charges
                    or 0
                ),

                float(
                    order.grand_total
                    or 0
                ),

                order.remarks
            ]

            worksheet.append(
                row
            )

        # =================================================
        # Header Formatting
        # =================================================

        for cell in worksheet[1]:

            cell.font = (
                cell.font.copy(
                    bold=True
                )
            )

        # =================================================
        # Freeze Header
        # =================================================

        worksheet.freeze_panes = (
            "A2"
        )

        # =================================================
        # Auto Width
        # =================================================

        for column in worksheet.columns:

            max_length = 0

            column_letter = (
                column[0].column_letter
            )

            for cell in column:

                value = cell.value

                if value is not None:

                    max_length = max(
                        max_length,
                        len(
                            str(value)
                        )
                    )

            worksheet.column_dimensions[
                column_letter
            ].width = min(
                max_length + 2,
                30
            )

        # =================================================
        # Save To Memory
        # =================================================

        output = BytesIO()

        workbook.save(
            output
        )

        output.seek(0)

        return output