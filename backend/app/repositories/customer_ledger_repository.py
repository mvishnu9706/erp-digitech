from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_payment import CustomerPayment
from app.models.sales_invoice import SalesInvoice


class CustomerLedgerRepository:

    @staticmethod
    def get_transactions(db: Session, customer_id: int, from_date=None, to_date=None):
        transactions = []

        query = (
            db.query(SalesInvoice)
            .filter(
                SalesInvoice.customer_id == customer_id,
                SalesInvoice.status != "CANCELLED"
            )
        )

        if from_date:
            query = query.filter(
                SalesInvoice.invoice_date >= from_date
            )

        if to_date:
            query = query.filter(
                SalesInvoice.invoice_date <= to_date
            )

        invoices = (
            query
            .order_by(SalesInvoice.invoice_date)
            .all()
        )

        for invoice in invoices:

            transactions.append(
                {
                    "date": invoice.invoice_date,
                    "voucher_type": "Sales Invoice",
                    "voucher_number": invoice.invoice_number,
                    "debit": Decimal(str(invoice.grand_total or 0)),
                    "credit": Decimal("0"),
                }
            )

        query = (
            db.query(CustomerPayment)
            .filter(
                CustomerPayment.customer_id == customer_id
            )
        )

        if from_date:
            query = query.filter(
                CustomerPayment.payment_date >= from_date
            )

        if to_date:
            query = query.filter(
                CustomerPayment.payment_date <= to_date
            )

        payments = (
            query
            .order_by(CustomerPayment.payment_date)
            .all()
        )

        for payment in payments:

            transactions.append(
                {
                    "date": payment.payment_date,
                    "voucher_type": "Customer Payment",
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
    def get_opening_balance(db: Session, customer_id: int, from_date=None):
        customer = db.query(Customer).filter(Customer.id == customer_id).first()

        if not customer:
            return Decimal("0")

        opening_balance = Decimal(str(customer.opening_balance or 0))

        if not from_date:
            return opening_balance

        invoices = (
            db.query(SalesInvoice)
            .filter(SalesInvoice.customer_id == customer_id)
            .filter(SalesInvoice.status != "CANCELLED")
            .all()
        )

        payments = (
            db.query(CustomerPayment)
            .filter(CustomerPayment.customer_id == customer_id)
            .all()
        )

        for invoice in invoices:
            if invoice.invoice_date < from_date:
                opening_balance += Decimal(str(invoice.grand_total or 0))

        for payment in payments:
            if payment.payment_date < from_date:
                opening_balance -= Decimal(str(payment.amount or 0))

        return opening_balance
