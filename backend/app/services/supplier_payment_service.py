from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.services.accounting.posting_service import PostingService
from app.models.supplier_payment import SupplierPayment
from app.models.supplier_payment_invoice import SupplierPaymentInvoice

from app.repositories.supplier_payment_repository import (
    SupplierPaymentRepository
)

from app.repositories.supplier_repository import (
    SupplierRepository
)

from app.repositories.purchase_invoice_repository import (
    PurchaseInvoiceRepository
)

from app.schemas.supplier_payment import (
    SupplierPaymentCreate
)

from app.utils.supplier_payment_number import (
    SupplierPaymentNumberGenerator
)


class SupplierPaymentService:

    # =====================================================
    # Create Supplier Payment
    # =====================================================

    @staticmethod
    def create_supplier_payment(
        db: Session,
        data: SupplierPaymentCreate,
        current_user
    ):

        try:

            # =====================================================
            # Validate Supplier
            # =====================================================

            supplier = SupplierRepository.get_by_id(
                db,
                data.supplier_id
            )

            if not supplier:

                raise HTTPException(
                    status_code=404,
                    detail="Supplier not found."
                )

            # =====================================================
            # Generate Payment Number
            # =====================================================

            last_payment = SupplierPaymentRepository.last_payment(db)

            if last_payment:

                payment_number = SupplierPaymentNumberGenerator.generate(
                    last_payment.id + 1
                )

            else:

                payment_number = SupplierPaymentNumberGenerator.generate(1)

            payment = SupplierPayment(

                payment_number=payment_number,

                supplier_id=data.supplier_id,

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

            # =====================================================
            # Allocate Payment
            # =====================================================

            for allocation in data.invoices:

                invoice = PurchaseInvoiceRepository.get_by_id(

                    db,

                    allocation.purchase_invoice_id

                )

                if not invoice:

                    raise HTTPException(

                        status_code=404,

                        detail=f"Purchase Invoice {allocation.purchase_invoice_id} not found."

                    )

                if invoice.supplier_id != data.supplier_id:

                    raise HTTPException(

                        status_code=400,

                        detail="Purchase Invoice belongs to another supplier."

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

                if invoice.balance_amount == 0:

                    invoice.status = "PAID"

                elif invoice.paid_amount > 0:

                    invoice.status = "PARTIALLY_PAID"

                else:

                    invoice.status = "UNPAID"

                db.add(invoice)

                payment_invoice = SupplierPaymentInvoice(

                    purchase_invoice_id=invoice.id,

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
            # Update Supplier Outstanding
            # =====================================================

            supplier.current_balance -= data.amount

            if supplier.current_balance < 0:

                supplier.current_balance = Decimal("0")

            # =====================================================
            # Save Payment
            # =====================================================

            payment = SupplierPaymentRepository.create(

                db,

                payment,

                payment_invoices

            )

            # =====================================================
            # Flush Payment
            # =====================================================

            db.flush()

            # =====================================================
            # Accounting Posting
            # =====================================================

            PostingService.post_supplier_payment(

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

                detail=f"Supplier Payment Failed : {str(e)}"

            )
            # =====================================================
    # Get Supplier Payments
    # =====================================================

    @staticmethod
    def get_supplier_payments(

        db: Session,

        search=None,

        supplier_id=None,

        payment_mode=None,

        page=1,

        page_size=10

    ):

        skip = (page - 1) * page_size

        return SupplierPaymentRepository.get_all(

            db=db,

            search=search,

            supplier_id=supplier_id,

            payment_mode=payment_mode,

            skip=skip,

            limit=page_size

        )
        # =====================================================
    # Get Supplier Payment
    # =====================================================

    @staticmethod
    def get_supplier_payment(

        db: Session,

        payment_id: int

    ):

        payment = SupplierPaymentRepository.get_by_id(

            db,

            payment_id

        )

        if not payment:

            raise HTTPException(

                status_code=404,

                detail="Supplier Payment not found."

            )

        return payment
        # =====================================================
    # Update Supplier Payment
    # =====================================================

    @staticmethod
    def update_supplier_payment(

        db: Session,

        payment_id: int,

        data,

        current_user

    ):

        payment = SupplierPaymentRepository.get_by_id(

            db,

            payment_id

        )

        if not payment:

            raise HTTPException(

                status_code=404,

                detail="Supplier Payment not found."

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

        SupplierPaymentRepository.update(

            db,

            payment

        )

        db.commit()

        db.refresh(payment)

        return payment
        # =====================================================
    # Delete Supplier Payment
    # =====================================================

    @staticmethod
    def delete_supplier_payment(

        db: Session,

        payment_id: int

    ):

        payment = SupplierPaymentRepository.get_by_id(

            db,

            payment_id

        )

        if not payment:

            raise HTTPException(

                status_code=404,

                detail="Supplier Payment not found."

            )

        SupplierPaymentRepository.delete(

            db,

            payment

        )

        db.commit()

        return {

            "success": True,

            "message": "Supplier Payment deleted successfully."

        }
        # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return SupplierPaymentRepository.dashboard(db)