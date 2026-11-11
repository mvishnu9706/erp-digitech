from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.customer_payment import CustomerPayment
from app.models.customer_payment_invoice import CustomerPaymentInvoice


class CustomerPaymentRepository:

    # =====================================================
    # Create Payment
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        payment: CustomerPayment,
        invoices: list[CustomerPaymentInvoice]
    ):

        db.add(payment)

        db.flush()

        for invoice in invoices:

            invoice.customer_payment_id = payment.id

            db.add(invoice)

        return payment

    # =====================================================
    # Get All Payments
    # =====================================================

    @staticmethod
    def get_all(

        db: Session,

        search: str = None,

        customer_id: int = None,

        payment_mode: str = None,

        skip: int = 0,

        limit: int = 10

    ):

        query = db.query(CustomerPayment)

        # -----------------------------
        # Search
        # -----------------------------

        if search:

            query = query.filter(

                CustomerPayment.payment_number.ilike(
                    f"%{search}%"
                )

            )

        # -----------------------------
        # Filters
        # -----------------------------

        if customer_id:

            query = query.filter(
                CustomerPayment.customer_id == customer_id
            )

        if payment_mode:

            query = query.filter(
                CustomerPayment.payment_mode == payment_mode
            )

        return (

            query

            .order_by(
                CustomerPayment.id.desc()
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

            db.query(CustomerPayment)

            .filter(
                CustomerPayment.id == payment_id
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

            db.query(CustomerPaymentInvoice)

            .filter(
                CustomerPaymentInvoice.customer_payment_id == payment_id
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

            db.query(CustomerPayment)

            .order_by(
                CustomerPayment.id.desc()
            )

            .first()

        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        payment: CustomerPayment
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
        payment: CustomerPayment
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

                db.query(CustomerPayment).count(),

            "total_collection":

                db.query(

                    func.coalesce(

                        func.sum(
                            CustomerPayment.amount
                        ),

                        0

                    )

                ).scalar(),

            "today_collection":

                db.query(

                    func.coalesce(

                        func.sum(
                            CustomerPayment.amount
                        ),

                        0

                    )

                )
                .filter(
                    func.current_date() == CustomerPayment.payment_date
                )
                .scalar(),

            "monthly_collection":

                db.query(

                    func.coalesce(

                        func.sum(
                            CustomerPayment.amount
                        ),

                        0

                    )

                )
                .filter(

                    func.extract(
                        "month",
                        CustomerPayment.payment_date
                    ) == func.extract(
                        "month",
                        func.current_date()
                    ),

                    func.extract(
                        "year",
                        CustomerPayment.payment_date
                    ) == func.extract(
                        "year",
                        func.current_date()
                    )

                )
                .scalar()

        }