from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.customer_ledger_repository import CustomerLedgerRepository
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer_ledger import CustomerLedgerResponse


class CustomerLedgerService:

    @staticmethod
    def get_ledger(db: Session, customer_id: int, from_date=None, to_date=None):
        customer = CustomerRepository.get_by_id(db, customer_id)

        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found.")

        opening_balance = CustomerLedgerRepository.get_opening_balance(db, customer_id, from_date)
        running_balance = opening_balance
        entries = []

        for transaction in CustomerLedgerRepository.get_transactions(db, customer_id, from_date, to_date):
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

        return CustomerLedgerResponse(
            customer_name=customer.customer_name,
            opening_balance=opening_balance,
            entries=entries,
            closing_balance=running_balance,
        )
