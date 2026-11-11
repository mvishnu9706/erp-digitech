from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.purchase_invoice import PurchaseInvoice
from app.models.supplier import Supplier


class SupplierOutstandingRepository:

    @staticmethod
    def get_outstanding_invoices(db: Session, supplier_id: int | None = None):
        query = (
            db.query(PurchaseInvoice, Supplier)
            .join(Supplier, PurchaseInvoice.supplier_id == Supplier.id)
            .filter(Supplier.is_active == True)
            .filter(PurchaseInvoice.status != "CANCELLED")
            .filter(PurchaseInvoice.balance_amount > 0)
        )

        if supplier_id is not None:
            query = query.filter(PurchaseInvoice.supplier_id == supplier_id)

        invoices = (
            query
            .order_by(
                PurchaseInvoice.due_date,
                Supplier.company_name,
                PurchaseInvoice.invoice_number
            )
            .all()
        )
        today = date.today()
        result = []

        for invoice, supplier in invoices:
            due_date = invoice.due_date
            overdue_days = 0

            if due_date and due_date < today:
                overdue_days = (today - due_date).days

            result.append(
                {
                    "supplier_id": invoice.supplier_id,
                    "supplier_name": supplier.company_name,
                    "invoice_number": invoice.invoice_number,
                    "invoice_date": invoice.invoice_date,
                    "due_date": due_date,
                    "invoice_total": Decimal(str(invoice.grand_total or 0)),
                    "outstanding_amount": Decimal(str(invoice.balance_amount or 0)),
                    "days_overdue": overdue_days,
                    "is_overdue": overdue_days > 0,
                }
            )

        return result
