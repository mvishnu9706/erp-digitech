from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.purchase_invoice import PurchaseInvoice
from app.models.supplier import Supplier


class SupplierAgingRepository:

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

        query = query.order_by(
            Supplier.company_name,
            PurchaseInvoice.due_date,
            PurchaseInvoice.invoice_number,
        )

        return query.all()
