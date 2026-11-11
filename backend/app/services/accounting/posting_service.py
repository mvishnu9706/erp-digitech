from sqlalchemy.orm import Session

from app.services.accounting.purchase_posting import (
    PurchasePostingService
)

from app.services.accounting.sales_posting import (
    SalesPostingService
)

from app.services.accounting.customer_payment_posting import (
    CustomerPaymentPostingService
)

from app.services.accounting.supplier_payment_posting import (
    SupplierPaymentPostingService
)


class PostingService:

    # =====================================================
    # Purchase Invoice
    # =====================================================

    @staticmethod
    def post_purchase_invoice(
        db: Session,
        purchase_invoice,
        current_user
    ):
        return PurchasePostingService.post(
            db,
            purchase_invoice,
            current_user
        )

    # =====================================================
    # Sales Invoice
    # =====================================================

    @staticmethod
    def post_sales_invoice(
        db: Session,
        sales_invoice,
        current_user
    ):
        return SalesPostingService.post(
            db,
            sales_invoice,
            current_user
        )

    # =====================================================
    # Customer Payment
    # =====================================================

    @staticmethod
    def post_customer_payment(
        db: Session,
        payment,
        current_user
    ):
        return CustomerPaymentPostingService.post(
            db,
            payment,
            current_user
        )

    # =====================================================
    # Supplier Payment
    # =====================================================

    @staticmethod
    def post_supplier_payment(
        db: Session,
        payment,
        current_user
    ):
        return SupplierPaymentPostingService.post(
            db,
            payment,
            current_user
        )