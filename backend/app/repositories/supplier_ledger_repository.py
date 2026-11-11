from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.purchase_invoice import PurchaseInvoice
from app.models.supplier import Supplier
from app.models.supplier_payment import SupplierPayment


class SupplierLedgerRepository:

    @staticmethod
    def get_transactions(db: Session, supplier_id: int, from_date=None, to_date=None):
        transactions = []

        query = (
            db.query(PurchaseInvoice)
            .filter(
                PurchaseInvoice.supplier_id == supplier_id,
                PurchaseInvoice.status != "CANCELLED"
            )
        )

        if from_date:
            query = query.filter(
                PurchaseInvoice.invoice_date >= from_date
            )

        if to_date:
            query = query.filter(
                PurchaseInvoice.invoice_date <= to_date
            )

        invoices = (
            query
            .order_by(PurchaseInvoice.invoice_date)
            .all()
        )

        for invoice in invoices:

            transactions.append(
                {
                    "date": invoice.invoice_date,
                    "voucher_type": "Purchase Invoice",
                    "voucher_number": invoice.invoice_number,
                    "debit": Decimal(str(invoice.grand_total or 0)),
                    "credit": Decimal("0"),
                }
            )

        query = (
            db.query(SupplierPayment)
            .filter(
                SupplierPayment.supplier_id == supplier_id
            )
        )

        if from_date:
            query = query.filter(
                SupplierPayment.payment_date >= from_date
            )

        if to_date:
            query = query.filter(
                SupplierPayment.payment_date <= to_date
            )

        payments = (
            query
            .order_by(SupplierPayment.payment_date)
            .all()
        )

        for payment in payments:

            transactions.append(
                {
                    "date": payment.payment_date,
                    "voucher_type": "Supplier Payment",
                    "voucher_number": payment.payment_number,
                    "debit": Decimal("0"),
                    "credit": Decimal(str(payment.amount or 0)),
                }
            )

        return sorted(
            transactions,
            key=lambda item: (item["date"], item["voucher_type"], item["voucher_number"]),
        )

    @staticmethod
    def get_opening_balance(db: Session, supplier_id: int, from_date=None):
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()

        if not supplier:
            return Decimal("0")

        opening_balance = Decimal(str(supplier.opening_balance or 0))

        if not from_date:
            return opening_balance

        invoices = (
            db.query(PurchaseInvoice)
            .filter(PurchaseInvoice.supplier_id == supplier_id)
            .filter(PurchaseInvoice.status != "CANCELLED")
            .all()
        )

        payments = (
            db.query(SupplierPayment)
            .filter(SupplierPayment.supplier_id == supplier_id)
            .all()
        )

        for invoice in invoices:
            if invoice.invoice_date < from_date:
                opening_balance += Decimal(str(invoice.grand_total or 0))

        for payment in payments:
            if payment.payment_date < from_date:
                opening_balance -= Decimal(str(payment.amount or 0))

        return opening_balance
