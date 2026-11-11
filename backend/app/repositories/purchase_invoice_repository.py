from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.purchase_invoice import PurchaseInvoice
from app.models.purchase_invoice_item import PurchaseInvoiceItem


class PurchaseInvoiceRepository:

    # =====================================================
    # Create Purchase Invoice
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        purchase_invoice: PurchaseInvoice,
        items: list[PurchaseInvoiceItem]
    ):

        db.add(purchase_invoice)

        db.flush()

        for item in items:

            item.purchase_invoice_id = purchase_invoice.id

            db.add(item)

        return purchase_invoice

    # =====================================================
    # Get All Purchase Invoices
    # =====================================================

    @staticmethod
    def get_all(

        db: Session,

        search: str = None,

        supplier_id: int = None,

        warehouse_id: int = None,

        status: str = None,

        skip: int = 0,

        limit: int = 10

    ):

        query = db.query(PurchaseInvoice)

        # ------------------------------------
        # Search
        # ------------------------------------

        if search:

            query = query.filter(

                PurchaseInvoice.invoice_number.ilike(
                    f"%{search}%"
                )

            )

        # ------------------------------------
        # Filters
        # ------------------------------------

        if supplier_id:

            query = query.filter(
                PurchaseInvoice.supplier_id == supplier_id
            )

        if warehouse_id:

            query = query.filter(
                PurchaseInvoice.warehouse_id == warehouse_id
            )

        if status:

            query = query.filter(
                PurchaseInvoice.status == status
            )

        total_records = query.count()

        purchase_invoices = (

            query

            .order_by(
                PurchaseInvoice.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

        return total_records, purchase_invoices

    # =====================================================
    # Get Purchase Invoice
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        purchase_invoice_id: int
    ):

        return (

            db.query(PurchaseInvoice)

            .filter(
                PurchaseInvoice.id == purchase_invoice_id
            )

            .first()

        )

    # =====================================================
    # Get Purchase Invoice Items
    # =====================================================

    @staticmethod
    def get_items(
        db: Session,
        purchase_invoice_id: int
    ):

        return (

            db.query(PurchaseInvoiceItem)

            .filter(
                PurchaseInvoiceItem.purchase_invoice_id == purchase_invoice_id
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

            db.query(PurchaseInvoice)

            .order_by(
                PurchaseInvoice.id.desc()
            )

            .first()

        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        purchase_invoice: PurchaseInvoice
    ):

        db.flush()

        db.refresh(purchase_invoice)

        return purchase_invoice

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        purchase_invoice: PurchaseInvoice
    ):

        purchase_invoice.status = "CANCELLED"

        db.flush()

        db.refresh(purchase_invoice)

        return purchase_invoice

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return {

            "total_invoices":

                db.query(PurchaseInvoice).count(),

            "unpaid_invoices":

                db.query(PurchaseInvoice)
                .filter(
                    PurchaseInvoice.status == "UNPAID"
                )
                .count(),

            "partially_paid_invoices":

                db.query(PurchaseInvoice)
                .filter(
                    PurchaseInvoice.status == "PARTIALLY_PAID"
                )
                .count(),

            "paid_invoices":

                db.query(PurchaseInvoice)
                .filter(
                    PurchaseInvoice.status == "PAID"
                )
                .count(),

            "cancelled_invoices":

                db.query(PurchaseInvoice)
                .filter(
                    PurchaseInvoice.status == "CANCELLED"
                )
                .count(),

            "total_purchase_amount":

                db.query(

                    func.coalesce(

                        func.sum(
                            PurchaseInvoice.grand_total
                        ),

                        0

                    )

                ).scalar(),

            "total_outstanding":

                db.query(

                    func.coalesce(

                        func.sum(
                            PurchaseInvoice.balance_amount
                        ),

                        0

                    )

                ).scalar(),

            "this_month_purchase":

                db.query(

                    func.coalesce(

                        func.sum(
                            PurchaseInvoice.grand_total
                        ),

                        0

                    )

                )
                .filter(
                    func.date_trunc(
                        "month",
                        PurchaseInvoice.created_at
                    ) == func.date_trunc(
                        "month",
                        func.now()
                    )
                )
                .scalar()

        }