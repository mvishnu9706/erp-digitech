from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.sales_invoice import SalesInvoice
from app.models.sales_invoice_item import SalesInvoiceItem


class SalesInvoiceRepository:

    # =====================================================
    # Create Sales Invoice
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        sales_invoice: SalesInvoice,
        items: list[SalesInvoiceItem]
    ):

        db.add(sales_invoice)

        db.flush()

        for item in items:

            item.sales_invoice_id = sales_invoice.id

            db.add(item)

        return sales_invoice

    # =====================================================
    # Get All Sales Invoices
    # =====================================================

    @staticmethod
    def get_all(

        db: Session,

        search: str = None,

        customer_id: int = None,

        warehouse_id: int = None,

        status: str = None,

        delivery_challan_id: int = None,

        skip: int = 0,

        limit: int = 10

    ):

        query = db.query(SalesInvoice)

        # ----------------------------------------
        # Search
        # ----------------------------------------

        if search:

            query = query.filter(

                SalesInvoice.invoice_number.ilike(
                    f"%{search}%"
                )

            )

        # ----------------------------------------
        # Filters
        # ----------------------------------------

        if customer_id:

            query = query.filter(
                SalesInvoice.customer_id == customer_id
            )

        if warehouse_id:

            query = query.filter(
                SalesInvoice.warehouse_id == warehouse_id
            )

        if status:

            query = query.filter(
                SalesInvoice.status == status
            )

        if delivery_challan_id:

            query = query.filter(
                SalesInvoice.delivery_challan_id == delivery_challan_id
            )

        return (

            query

            .order_by(
                SalesInvoice.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # Get Invoice
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        sales_invoice_id: int
    ):

        return (

            db.query(SalesInvoice)

            .filter(
                SalesInvoice.id == sales_invoice_id
            )

            .first()

        )

    # =====================================================
    # Get By Delivery Challan
    # =====================================================

    @staticmethod
    def get_by_delivery_challan(
        db: Session,
        delivery_challan_id: int
    ):

        return (

            db.query(SalesInvoice)

            .filter(
                SalesInvoice.delivery_challan_id == delivery_challan_id
            )

            .first()

        )

    # =====================================================
    # Get Invoice Items
    # =====================================================

    @staticmethod
    def get_items(
        db: Session,
        sales_invoice_id: int
    ):

        return (

            db.query(SalesInvoiceItem)

            .filter(
                SalesInvoiceItem.sales_invoice_id == sales_invoice_id
            )

            .all()

        )

    # =====================================================
    # Last Invoice
    # =====================================================

    @staticmethod
    def last_invoice(
        db: Session
    ):

        return (

            db.query(SalesInvoice)

            .order_by(
                SalesInvoice.id.desc()
            )

            .first()

        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        sales_invoice: SalesInvoice
    ):

        db.flush()

        db.refresh(sales_invoice)

        return sales_invoice

    # =====================================================
    # Soft Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        sales_invoice: SalesInvoice
    ):

        sales_invoice.status = "CANCELLED"

        db.flush()

        db.refresh(sales_invoice)

        return sales_invoice

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return {

            "total_invoices":

                db.query(SalesInvoice).count(),

            "unpaid_invoices":

                db.query(SalesInvoice)
                .filter(
                    SalesInvoice.payment_status == "UNPAID"
                )
                .count(),

            "partially_paid_invoices":

                db.query(SalesInvoice)
                .filter(
                    SalesInvoice.payment_status == "PARTIALLY_PAID"
                )
                .count(),

            "paid_invoices":

                db.query(SalesInvoice)
                .filter(
                    SalesInvoice.payment_status == "PAID"
                )
                .count(),

            "cancelled_invoices":

                db.query(SalesInvoice)
                .filter(
                    SalesInvoice.status == "CANCELLED"
                )
                .count(),

            "total_sales":

                db.query(

                    func.coalesce(

                        func.sum(
                            SalesInvoice.grand_total
                        ),

                        0

                    )

                ).scalar()

        }