from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services.accounting.posting_service import PostingService

from app.models.sales_invoice import SalesInvoice
from app.models.sales_invoice_item import SalesInvoiceItem

from app.repositories.sales_invoice_repository import (
    SalesInvoiceRepository
)

from app.repositories.sales_order_repository import (
    SalesOrderRepository
)

from app.repositories.customer_repository import (
    CustomerRepository
)

from app.repositories.warehouse_repository import (
    WarehouseRepository
)

from app.schemas.sales_invoice import (
    SalesInvoiceCreate
)

from app.utils.sales_invoice_number import (
    SalesInvoiceNumberGenerator
)


class SalesInvoiceService:

    # =====================================================
    # Create Sales Invoice
    # =====================================================

    @staticmethod
    def create_sales_invoice(
        db: Session,
        data: SalesInvoiceCreate,
        current_user
    ):

        try:

            # -----------------------------------------
            # Validate Sales Order
            # -----------------------------------------

            sales_order = SalesOrderRepository.get_by_id(
                db,
                data.sales_order_id
            )

            if not sales_order:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sales Order not found."
                )

            # -----------------------------------------
            # Validate Sales Order Status
            # -----------------------------------------

            if sales_order.status == "CANCELLED":

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot create invoice for a cancelled Sales Order."
                )

            # -----------------------------------------
            # Validate Customer
            # -----------------------------------------

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

            # -----------------------------------------
            # Validate Customer belongs to Sales Order
            # -----------------------------------------

            if sales_order.customer_id != customer.id:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Customer does not belong to this Sales Order."
                )

            # -----------------------------------------
            # Validate Warehouse
            # -----------------------------------------

            warehouse = WarehouseRepository.get_by_id(
                db,
                data.warehouse_id
            )

            if not warehouse:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Warehouse not found."
                )

            if not warehouse.is_active:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Warehouse is inactive."
                )

            # -----------------------------------------
            # Validate Warehouse belongs to Sales Order
            # -----------------------------------------

            if sales_order.warehouse_id != warehouse.id:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Warehouse does not belong to this Sales Order."
                )

            # -----------------------------------------
            # Check Duplicate Invoice
            # -----------------------------------------

            existing_invoices = SalesInvoiceRepository.get_all(
                db=db,
                customer_id=customer.id,
                warehouse_id=warehouse.id,
                skip=0,
                limit=1000
            )

            for existing_invoice in existing_invoices:

                if (
                    getattr(existing_invoice, "sales_order_id", None)
                    == sales_order.id
                ):

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Sales Invoice already exists for this Sales Order."
                    )

            # -----------------------------------------
            # Generate Invoice Number
            # -----------------------------------------

            last_invoice = SalesInvoiceRepository.last_invoice(db)

            if last_invoice:

                invoice_number = (
                    SalesInvoiceNumberGenerator.generate(
                        last_invoice.id + 1
                    )
                )

            else:

                invoice_number = (
                    SalesInvoiceNumberGenerator.generate(1)
                )

            # -----------------------------------------
            # Initialize Totals
            # -----------------------------------------

            subtotal = Decimal("0")

            discount_total = Decimal("0")

            gst_total = Decimal("0")

            grand_total = Decimal("0")

            # -----------------------------------------
            # Invoice Header
            # -----------------------------------------

            invoice = SalesInvoice(

                invoice_number=invoice_number,

                sales_order_id=sales_order.id,

                customer_id=customer.id,

                warehouse_id=warehouse.id,

                invoice_date=data.invoice_date,

                due_date=data.due_date,

                status="DRAFT",

                payment_status="UNPAID",

                subtotal=Decimal("0"),

                discount_amount=Decimal("0"),

                gst_amount=Decimal("0"),

                other_charges=Decimal("0"),

                grand_total=Decimal("0"),

                paid_amount=Decimal("0"),

                balance_amount=Decimal("0"),

                remarks=data.remarks,

                created_by=current_user.id,

                updated_by=current_user.id
            )

            # -----------------------------------------
            # Invoice Items
            # -----------------------------------------

            items = []

            # -----------------------------------------
            # Process Items From Request
            # -----------------------------------------

            for item in data.items:

                quantity = Decimal(
                    str(item.quantity)
                )

                selling_price = Decimal(
                    str(item.selling_price)
                )

                discount_percentage = Decimal(
                    str(
                        item.discount_percentage
                        if item.discount_percentage is not None
                        else 0
                    )
                )

                gst_percentage = Decimal(
                    str(
                        item.gst_percentage
                        if item.gst_percentage is not None
                        else 0
                    )
                )

                # -------------------------------------
                # Validate Quantity
                # -------------------------------------

                if quantity <= 0:

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Quantity must be greater than zero."
                    )

                # -------------------------------------
                # Validate Selling Price
                # -------------------------------------

                if selling_price < 0:

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Selling price cannot be negative."
                    )

                # -------------------------------------
                # Line Subtotal
                # -------------------------------------

                line_subtotal = (
                    quantity *
                    selling_price
                )

                # -------------------------------------
                # Discount
                # -------------------------------------

                discount_amount = (
                    line_subtotal *
                    discount_percentage /
                    Decimal("100")
                )

                # -------------------------------------
                # Taxable Amount
                # -------------------------------------

                taxable = (
                    line_subtotal -
                    discount_amount
                )

                # -------------------------------------
                # GST
                # -------------------------------------

                gst_amount = (
                    taxable *
                    gst_percentage /
                    Decimal("100")
                )

                # -------------------------------------
                # Line Total
                # -------------------------------------

                line_total = (
                    taxable +
                    gst_amount
                )

                # -------------------------------------
                # Invoice Totals
                # -------------------------------------

                subtotal += line_subtotal

                discount_total += discount_amount

                gst_total += gst_amount

                grand_total += line_total

                # -------------------------------------
                # Create Invoice Item
                # -------------------------------------

                invoice_item = SalesInvoiceItem(

                    product_id=item.product_id,

                    quantity=item.quantity,

                    selling_price=item.selling_price,

                    discount_percentage=(
                        item.discount_percentage
                        if item.discount_percentage is not None
                        else 0
                    ),

                    discount_amount=discount_amount,

                    gst_percentage=(
                        item.gst_percentage
                        if item.gst_percentage is not None
                        else 0
                    ),

                    gst_amount=gst_amount,

                    line_total=line_total,

                    product_name=(
                        item.product_name
                        if getattr(
                            item,
                            "product_name",
                            None
                        )
                        else ""
                    ),

                    sku=(
                        item.sku
                        if getattr(
                            item,
                            "sku",
                            None
                        )
                        else ""
                    ),

                    model_no=(
                        item.model_no
                        if getattr(
                            item,
                            "model_no",
                            None
                        )
                        else ""
                    ),

                    remarks=item.remarks
                )

                items.append(
                    invoice_item
                )

            # -----------------------------------------
            # Make Sure Items Exist
            # -----------------------------------------

            if not items:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one invoice item is required."
                )

            # -----------------------------------------
            # Update Invoice Totals
            # -----------------------------------------

            invoice.subtotal = subtotal

            invoice.discount_amount = discount_total

            invoice.gst_amount = gst_total

            invoice.grand_total = grand_total

            invoice.balance_amount = grand_total

            # -----------------------------------------
            # Save Invoice
            # -----------------------------------------

            invoice = SalesInvoiceRepository.create(
                db,
                invoice,
                items
            )

            # -----------------------------------------
            # Update Customer Outstanding
            # -----------------------------------------

            current_balance = (
                customer.current_balance
                if customer.current_balance is not None
                else Decimal("0")
            )

            customer.current_balance = (
                current_balance +
                grand_total
            )

            # -----------------------------------------
            # Accounting Posting
            # -----------------------------------------

            PostingService.post_sales_invoice(
                db,
                invoice,
                current_user
            )

            # -----------------------------------------
            # Commit
            # -----------------------------------------

            db.commit()

            db.refresh(invoice)

            return invoice

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            import traceback

            traceback.print_exc()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Sales Invoice Creation Failed : "
                    f"{str(e)}"
                )
            )

    # =====================================================
    # Get Sales Invoices
    # =====================================================

    @staticmethod
    def get_sales_invoices(
        db: Session,
        search=None,
        customer_id=None,
        warehouse_id=None,
        status=None,
        page=1,
        page_size=10
    ):

        skip = (
            page - 1
        ) * page_size

        return SalesInvoiceRepository.get_all(

            db=db,

            search=search,

            customer_id=customer_id,

            warehouse_id=warehouse_id,

            status=status,

            skip=skip,

            limit=page_size
        )

    # =====================================================
    # Get Sales Invoice
    # =====================================================

    @staticmethod
    def get_sales_invoice(
        db: Session,
        sales_invoice_id: int
    ):

        invoice = SalesInvoiceRepository.get_by_id(
            db,
            sales_invoice_id
        )

        if not invoice:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales Invoice not found."
            )

        return invoice

    # =====================================================
    # Update Sales Invoice
    # =====================================================

    @staticmethod
    def update_sales_invoice(
        db: Session,
        sales_invoice_id: int,
        data,
        current_user
    ):

        try:

            invoice = SalesInvoiceRepository.get_by_id(
                db,
                sales_invoice_id
            )

            if not invoice:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sales Invoice not found."
                )

            update_data = data.model_dump(
                exclude_unset=True
            )

            # -----------------------------------------
            # Do not allow relationship fields
            # to be changed accidentally
            # -----------------------------------------

            protected_fields = {
                "id",
                "invoice_number",
                "sales_order_id",
                "customer_id",
                "warehouse_id"
            }

            for key, value in update_data.items():

                if key in protected_fields:
                    continue

                setattr(
                    invoice,
                    key,
                    value
                )

            invoice.updated_by = (
                current_user.id
            )

            # -----------------------------------------
            # Recalculate Balance
            # -----------------------------------------

            if (
                hasattr(invoice, "grand_total")
                and hasattr(invoice, "paid_amount")
                and hasattr(invoice, "balance_amount")
            ):

                grand_total = Decimal(
                    str(
                        invoice.grand_total
                        or 0
                    )
                )

                paid_amount = Decimal(
                    str(
                        invoice.paid_amount
                        or 0
                    )
                )

                invoice.balance_amount = max(
                    Decimal("0"),
                    grand_total - paid_amount
                )

                if paid_amount <= 0:

                    invoice.payment_status = "UNPAID"

                elif paid_amount >= grand_total:

                    invoice.payment_status = "PAID"

                else:

                    invoice.payment_status = "PARTIAL"

            SalesInvoiceRepository.update(
                db,
                invoice
            )

            db.commit()

            db.refresh(invoice)

            return invoice

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            import traceback

            traceback.print_exc()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Sales Invoice Update Failed : "
                    f"{str(e)}"
                )
            )

    # =====================================================
    # Delete / Cancel Sales Invoice
    # =====================================================

    @staticmethod
    def delete_sales_invoice(
        db: Session,
        sales_invoice_id: int
    ):

        try:

            invoice = SalesInvoiceRepository.get_by_id(
                db,
                sales_invoice_id
            )

            if not invoice:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sales Invoice not found."
                )

            # -----------------------------------------
            # Preserve invoice history
            # -----------------------------------------

            if hasattr(invoice, "status"):

                invoice.status = "CANCELLED"

            if hasattr(invoice, "payment_status"):

                invoice.payment_status = "CANCELLED"

            SalesInvoiceRepository.update(
                db,
                invoice
            )

            db.commit()

            db.refresh(invoice)

            return invoice

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            import traceback

            traceback.print_exc()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Sales Invoice Cancellation Failed : "
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

        return SalesInvoiceRepository.dashboard(
            db
        )