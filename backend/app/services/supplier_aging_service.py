from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.supplier_aging_repository import SupplierAgingRepository
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.supplier_aging import SupplierAgingEntry


class SupplierAgingService:

    @staticmethod
    def get_aging(db: Session, supplier_id: int | None = None):
        if supplier_id is not None:
            supplier = SupplierRepository.get_by_id(db, supplier_id)
            if not supplier:
                raise HTTPException(status_code=404, detail="Supplier not found.")

        today = date.today()
        summary = {}

        for invoice, supplier in SupplierAgingRepository.get_outstanding_invoices(db, supplier_id):
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

            if supplier.id not in summary:
                summary[supplier.id] = {
                    "supplier_id": supplier.id,
                    "supplier_name": supplier.company_name,
                    "current": Decimal("0"),
                    "days_1_30": Decimal("0"),
                    "days_31_60": Decimal("0"),
                    "days_61_90": Decimal("0"),
                    "days_90_plus": Decimal("0"),
                    "total_outstanding": Decimal("0"),
                }

            summary[supplier.id][bucket] += amount
            summary[supplier.id]["total_outstanding"] += amount

        return sorted(
            [
                SupplierAgingEntry(
                    supplier_id=item["supplier_id"],
                    supplier_name=item["supplier_name"],
                    current=item["current"],
                    days_1_30=item["days_1_30"],
                    days_31_60=item["days_31_60"],
                    days_61_90=item["days_61_90"],
                    days_90_plus=item["days_90_plus"],
                    total_outstanding=item["total_outstanding"],
                )
                for item in summary.values()
            ],
            key=lambda x: x.supplier_name
        )
