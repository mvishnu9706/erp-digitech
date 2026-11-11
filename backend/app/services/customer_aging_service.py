from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.customer_aging_repository import CustomerAgingRepository
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer_aging import CustomerAgingEntry


class CustomerAgingService:

    @staticmethod
    def get_aging(db: Session, customer_id: int | None = None):
        if customer_id is not None:
            customer = CustomerRepository.get_by_id(db, customer_id)
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found.")

        today = date.today()
        summary = {}

        for invoice, customer in CustomerAgingRepository.get_outstanding_invoices(db, customer_id):
            due_date = invoice.due_date
            amount = Decimal(str(invoice.balance_amount or 0))
            bucket = "current"

            days_due = 0
            if due_date:
                days_due = (today - due_date).days

            if days_due <= 0:
                bucket = "current"
            elif days_due <= 30:
                bucket = "days_1_30"
            elif days_due <= 60:
                bucket = "days_31_60"
            elif days_due <= 90:
                bucket = "days_61_90"
            else:
                bucket = "days_90_plus"

            if customer.id not in summary:
                summary[customer.id] = {
                    "customer_id": customer.id,
                    "customer_name": customer.customer_name,
                    "current": Decimal("0"),
                    "days_1_30": Decimal("0"),
                    "days_31_60": Decimal("0"),
                    "days_61_90": Decimal("0"),
                    "days_90_plus": Decimal("0"),
                    "total_outstanding": Decimal("0"),
                }

            summary[customer.id][bucket] += amount
            summary[customer.id]["total_outstanding"] += amount

        return sorted(
            [
                CustomerAgingEntry(
                    customer_id=item["customer_id"],
                    customer_name=item["customer_name"],
                    current=item["current"],
                    days_1_30=item["days_1_30"],
                    days_31_60=item["days_31_60"],
                    days_61_90=item["days_61_90"],
                    days_90_plus=item["days_90_plus"],
                    total_outstanding=item["total_outstanding"],
                )
                for item in summary.values()
            ],
            key=lambda x: x.customer_name
        )
