from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.supplier_payment import SupplierPayment
from app.models.supplier_payment_invoice import SupplierPaymentInvoice


class SupplierPaymentRepository:

    # =====================================================
    # Create Supplier Payment
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        payment: SupplierPayment,
        invoices: list[SupplierPaymentInvoice]
    ):

        db.add(payment)

        db.flush()

        for invoice in invoices:

            invoice.supplier_payment_id = payment.id

            db.add(invoice)

        return payment

    # =====================================================
    # Get All Payments
    # =====================================================

    @staticmethod
    def get_all(

        db: Session,

        search: str = None,

        supplier_id: int = None,

        payment_mode: str = None,

        skip: int = 0,

        limit: int = 10

    ):

        query = db.query(SupplierPayment)

        # ---------------------------------------
        # Search
        # ---------------------------------------

        if search:

            query = query.filter(

                SupplierPayment.payment_number.ilike(
                    f"%{search}%"
                )

            )

        # ---------------------------------------
        # Filters
        # ---------------------------------------

        if supplier_id:

            query = query.filter(
                SupplierPayment.supplier_id == supplier_id
            )

        if payment_mode:

            query = query.filter(
                SupplierPayment.payment_mode == payment_mode
            )

        return (

            query

            .order_by(
                SupplierPayment.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # Get Payment
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        payment_id: int
    ):

        return (

            db.query(SupplierPayment)

            .filter(
                SupplierPayment.id == payment_id
            )

            .first()

        )

    # =====================================================
    # Get Payment Invoices
    # =====================================================

    @staticmethod
    def get_payment_invoices(
        db: Session,
        payment_id: int
    ):

        return (

            db.query(SupplierPaymentInvoice)

            .filter(
                SupplierPaymentInvoice.supplier_payment_id == payment_id
            )

            .all()

        )

    # =====================================================
    # Last Payment
    # =====================================================

    @staticmethod
    def last_payment(
        db: Session
    ):

        return (

            db.query(SupplierPayment)

            .order_by(
                SupplierPayment.id.desc()
            )

            .first()

        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        payment: SupplierPayment
    ):

        db.flush()

        db.refresh(payment)

        return payment

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        payment: SupplierPayment
    ):

        db.delete(payment)

        db.flush()

        return True

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return {

            "total_payments":

                db.query(SupplierPayment).count(),

            "total_payment_amount":

                db.query(

                    func.coalesce(

                        func.sum(
                            SupplierPayment.amount
                        ),

                        0

                    )

                ).scalar(),

            "today_payment":

                db.query(

                    func.coalesce(

                        func.sum(
                            SupplierPayment.amount
                        ),

                        0

                    )

                )
                .filter(
                    func.current_date() == SupplierPayment.payment_date
                )
                .scalar(),

            "monthly_payment":

                db.query(

                    func.coalesce(

                        func.sum(
                            SupplierPayment.amount
                        ),

                        0

                    )

                )
                .filter(

                    func.extract(
                        "month",
                        SupplierPayment.payment_date
                    ) == func.extract(
                        "month",
                        func.current_date()
                    ),

                    func.extract(
                        "year",
                        SupplierPayment.payment_date
                    ) == func.extract(
                        "year",
                        func.current_date()
                    )

                )
                .scalar()

        }