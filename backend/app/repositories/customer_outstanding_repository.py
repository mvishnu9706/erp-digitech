from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.sales_invoice import SalesInvoice


class CustomerOutstandingRepository:

    @staticmethod
    def get_outstanding_invoices(db: Session, customer_id: int | None = None):
        query = (
            db.query(SalesInvoice, Customer)
            .join(Customer, SalesInvoice.customer_id == Customer.id)
            .filter(SalesInvoice.status != "CANCELLED")
            .filter(SalesInvoice.balance_amount > 0)
            .filter(Customer.is_active == True)
        )

        if customer_id is not None:
            query = query.filter(SalesInvoice.customer_id == customer_id)

        invoices = (
            query
            .order_by(
                SalesInvoice.due_date,
                Customer.customer_name,
                SalesInvoice.invoice_number
            )
            .all()
        )
        today = date.today()
        result = []

        for invoice, customer in invoices:
            due_date = invoice.due_date
            overdue_days = 0

            if due_date and due_date < today:
                overdue_days = (today - due_date).days

            result.append(
                {
                    "customer_id": invoice.customer_id,
                    "customer_name": customer.customer_name,
                    "invoice_number": invoice.invoice_number,
                    "invoice_date": invoice.invoice_date,
                    "due_date": due_date,
                    "invoice_total": Decimal(str(invoice.grand_total or 0)),
                    "outstanding_amount": Decimal(str(invoice.balance_amount or 0)),
                    "days_overdue": overdue_days,
                }
            )

        return result
