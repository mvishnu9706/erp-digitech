from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer_payment import CustomerPayment
from app.models.customer_payment_invoice import CustomerPaymentInvoice

from app.repositories.customer_payment_repository import (
    CustomerPaymentRepository
)

from app.repositories.customer_repository import (
    CustomerRepository
)

from app.repositories.sales_invoice_repository import (
    SalesInvoiceRepository
)

from app.schemas.customer_payment import (
    CustomerPaymentCreate
)

from app.utils.customer_payment_number import (
    CustomerPaymentNumberGenerator
)

from app.services.accounting.posting_service import (
    PostingService
)


class CustomerPaymentService:

    # =====================================================
    # Create Customer Payment
    # =====================================================

    @staticmethod
    def create_customer_payment(
        db: Session,
        data: CustomerPaymentCreate,
        current_user
    ):

        try:

            # -----------------------------------------
            # Validate Customer
            # -----------------------------------------

            customer = CustomerRepository.get_by_id(
                db,
                data.customer_id
            )

            if not customer:

                raise HTTPException(
                    status_code=404,
                    detail="Customer not found."
                )

            # -----------------------------------------
            # Generate Payment Number
            # -----------------------------------------

            last_payment = CustomerPaymentRepository.last_payment(db)

            if last_payment:

                payment_number = CustomerPaymentNumberGenerator.generate(
                    last_payment.id + 1
                )

            else:

                payment_number = CustomerPaymentNumberGenerator.generate(1)

            payment = CustomerPayment(

                payment_number=payment_number,

                customer_id=data.customer_id,

                payment_date=data.payment_date,

                payment_mode=data.payment_mode,

                reference_number=data.reference_number,

                amount=data.amount,

                remarks=data.remarks,

                created_by=current_user.id,

                updated_by=current_user.id

            )

            payment_invoices = []

            total_allocated = Decimal("0")

            print("STEP 1: Entered create_customer_payment")

            # -----------------------------------------
            # Allocate Payment
            # -----------------------------------------

            for allocation in data.invoices:

                invoice = SalesInvoiceRepository.get_by_id(

                    db,

                    allocation.sales_invoice_id

                )

                if not invoice:

                    raise HTTPException(

                        status_code=404,

                        detail=f"Invoice {allocation.sales_invoice_id} not found."

                    )

                if invoice.customer_id != data.customer_id:

                    raise HTTPException(

                        status_code=400,

                        detail="Invoice belongs to another customer."

                    )

                if allocation.paid_amount > invoice.balance_amount:

                    raise HTTPException(

                        status_code=400,

                        detail=(
                            f"Payment exceeds outstanding amount "
                            f"for invoice {invoice.invoice_number}"
                        )

                    )

                invoice.paid_amount += allocation.paid_amount

                invoice.balance_amount -= allocation.paid_amount

                if invoice.balance_amount <= 0:

                    invoice.balance_amount = Decimal("0")
                    invoice.payment_status = "PAID"

                elif invoice.paid_amount > 0:

                    invoice.payment_status = "PARTIALLY_PAID"

                else:

                    invoice.payment_status = "UNPAID"

                db.add(invoice)

                payment_invoice = CustomerPaymentInvoice(

                    sales_invoice_id=invoice.id,

                    paid_amount=allocation.paid_amount

                )

                payment_invoices.append(payment_invoice)

                total_allocated += allocation.paid_amount
                            # =====================================================
            # Validate Payment Amount
            # =====================================================

            if total_allocated != data.amount:

                raise HTTPException(

                    status_code=400,

                    detail=(
                        "Total allocated amount must equal "
                        "payment amount."
                    )

                )

            # =====================================================
            # Update Customer Outstanding
            # =====================================================

            customer.current_balance -= data.amount

            if customer.current_balance < 0:

                customer.current_balance = Decimal("0")

            # =====================================================
            # Save Payment
            # =====================================================

            payment = CustomerPaymentRepository.create(

                db,

                payment,

                payment_invoices

            )

            db.flush()

            # =====================================
            # Accounting Posting
            # =====================================

            PostingService.post_customer_payment(
                db,
                payment,
                current_user
            )

            # =====================================================
            # Commit
            # =====================================================

            db.commit()

            db.refresh(payment)

            return payment

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(

                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=f"Customer Payment Failed : {str(e)}"

            )
            # =====================================================
    # Get Customer Payments
    # =====================================================

    @staticmethod
    def get_customer_payments(

        db: Session,

        search=None,

        customer_id=None,

        payment_mode=None,

        page=1,

        page_size=10

    ):

        skip = (page - 1) * page_size

        return CustomerPaymentRepository.get_all(

            db=db,

            search=search,

            customer_id=customer_id,

            payment_mode=payment_mode,

            skip=skip,

            limit=page_size

        )
        # =====================================================
    # Get Customer Payment
    # =====================================================

    @staticmethod
    def get_customer_payment(

        db: Session,

        payment_id: int

    ):

        payment = CustomerPaymentRepository.get_by_id(

            db,

            payment_id

        )

        if not payment:

            raise HTTPException(

                status_code=404,

                detail="Customer Payment not found."

            )

        return payment
        # =====================================================
    # Update Customer Payment
    # =====================================================

    @staticmethod
    def update_customer_payment(

        db: Session,

        payment_id: int,

        data,

        current_user

    ):

        payment = CustomerPaymentRepository.get_by_id(

            db,

            payment_id

        )

        if not payment:

            raise HTTPException(

                status_code=404,

                detail="Customer Payment not found."

            )

        update_data = data.model_dump(

            exclude_unset=True

        )

        for key, value in update_data.items():

            setattr(

                payment,

                key,

                value

            )

        payment.updated_by = current_user.id

        CustomerPaymentRepository.update(

            db,

            payment

        )

        db.commit()

        db.refresh(payment)

        return payment
        # =====================================================
    # Delete Customer Payment
    # =====================================================

    @staticmethod
    def delete_customer_payment(

        db: Session,

        payment_id: int

    ):

        payment = CustomerPaymentRepository.get_by_id(

            db,

            payment_id

        )

        if not payment:

            raise HTTPException(

                status_code=404,

                detail="Customer Payment not found."

            )

        CustomerPaymentRepository.delete(

            db,

            payment

        )

        db.commit()

        return {

            "success": True,

            "message": "Customer Payment deleted successfully."

        }
        # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return CustomerPaymentRepository.dashboard(db)