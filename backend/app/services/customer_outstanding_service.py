from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.customer_outstanding_repository import CustomerOutstandingRepository
from app.repositories.customer_repository import CustomerRepository


class CustomerOutstandingService:

    @staticmethod
    def get_outstanding(db: Session, customer_id: int | None = None):
        if customer_id is not None:
            customer = CustomerRepository.get_by_id(db, customer_id)
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found.")

        outstanding = CustomerOutstandingRepository.get_outstanding_invoices(db, customer_id)
        return outstanding
