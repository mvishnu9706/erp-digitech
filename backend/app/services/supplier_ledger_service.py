from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.supplier_ledger_repository import SupplierLedgerRepository
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.supplier_ledger import SupplierLedgerResponse


class SupplierLedgerService:

    @staticmethod
    def get_ledger(db: Session, supplier_id: int, from_date=None, to_date=None):
        supplier = SupplierRepository.get_by_id(db, supplier_id)

        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found.")

        opening_balance = SupplierLedgerRepository.get_opening_balance(db, supplier_id, from_date)
        running_balance = opening_balance
        entries = []

        for transaction in SupplierLedgerRepository.get_transactions(db, supplier_id, from_date, to_date):
            running_balance += Decimal(str(transaction["debit"] or 0))
            running_balance -= Decimal(str(transaction["credit"] or 0))

            entries.append(
                {
                    "date": transaction["date"],
                    "voucher_type": transaction["voucher_type"],
                    "voucher_number": transaction["voucher_number"],
                    "debit": Decimal(str(transaction["debit"] or 0)),
                    "credit": Decimal(str(transaction["credit"] or 0)),
                    "balance": running_balance,
                }
            )

        return SupplierLedgerResponse(
            supplier_name=supplier.company_name,
            opening_balance=opening_balance,
            entries=entries,
            closing_balance=running_balance,
        )
