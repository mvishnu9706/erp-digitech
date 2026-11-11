from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.sales_invoice import SalesInvoice


class CustomerAgingRepository:

    @staticmethod
    def get_outstanding_invoices(db: Session, customer_id: int | None = None):
        query = (
            db.query(SalesInvoice, Customer)
            .join(Customer, SalesInvoice.customer_id == Customer.id)
            .filter(Customer.is_active == True)
            .filter(SalesInvoice.status != "CANCELLED")
            .filter(SalesInvoice.balance_amount > 0)
        )

        if customer_id is not None:
            query = query.filter(SalesInvoice.customer_id == customer_id)

        query = query.order_by(
            Customer.customer_name,
            SalesInvoice.due_date,
            SalesInvoice.invoice_number,
        )

        return query.all()
