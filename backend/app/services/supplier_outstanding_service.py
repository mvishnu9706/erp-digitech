from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.supplier_outstanding_repository import SupplierOutstandingRepository
from app.repositories.supplier_repository import SupplierRepository


class SupplierOutstandingService:

    @staticmethod
    def get_outstanding(db: Session, supplier_id: int | None = None):
        if supplier_id is not None:
            supplier = SupplierRepository.get_by_id(db, supplier_id)
            if not supplier:
                raise HTTPException(status_code=404, detail="Supplier not found.")

        outstanding = SupplierOutstandingRepository.get_outstanding_invoices(db, supplier_id)
        return outstanding
