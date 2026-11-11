from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.service_spare_part import ServiceSparePart

from app.repositories.service_spare_part_repository import (
    ServiceSparePartRepository
)

from app.repositories.service_visit_repository import (
    ServiceVisitRepository
)

from app.repositories.product_repository import (
    ProductRepository
)

from app.repositories.warehouse_repository import (
    WarehouseRepository
)

from app.repositories.inventory_repository import (
    InventoryRepository
)

from app.schemas.service_spare_part import (
    ServiceSparePartCreate,
    ServiceSparePartUpdate
)


class ServiceSparePartService:

    # =====================================================
    # Create Spare Part
    # =====================================================

    @staticmethod
    def create_spare_part(
        db: Session,
        data: ServiceSparePartCreate,
        current_user
    ):

        try:

            # ==========================================
            # Validate Service Visit
            # ==========================================

            visit = ServiceVisitRepository.get_by_id(
                db,
                data.service_visit_id
            )

            if not visit:

                raise HTTPException(
                    status_code=404,
                    detail="Service Visit not found."
                )

            # ==========================================
            # Validate Product
            # ==========================================

            product = ProductRepository.get_by_id(
                db,
                data.product_id
            )

            if not product:

                raise HTTPException(
                    status_code=404,
                    detail="Product not found."
                )

            # ==========================================
            # Validate Warehouse
            # ==========================================

            warehouse = WarehouseRepository.get_by_id(
                db,
                data.warehouse_id
            )

            if not warehouse:

                raise HTTPException(
                    status_code=404,
                    detail="Warehouse not found."
                )

            # ==========================================
            # Inventory Validation
            # ==========================================

            inventory = InventoryRepository.get_inventory(

                db,

                data.product_id,

                data.warehouse_id

            )

            if not inventory:

                raise HTTPException(

                    status_code=404,

                    detail="Inventory not found."

                )

            if inventory.quantity < data.quantity:

                raise HTTPException(

                    status_code=400,

                    detail="Insufficient stock."

                )

            # ==========================================
            # Calculate Total
            # ==========================================

            total_price = Decimal(data.quantity) * Decimal(data.unit_price)

            # ==========================================
            # Create Spare Part
            # ==========================================

            spare_part = ServiceSparePart(

                service_visit_id=data.service_visit_id,

                product_id=data.product_id,

                warehouse_id=data.warehouse_id,

                quantity=data.quantity,

                unit_price=data.unit_price,

                total_price=total_price,

                is_billable=data.is_billable,

                remarks=data.remarks,

                created_by=current_user.id

            )

            spare_part = ServiceSparePartRepository.create(

                db,

                spare_part

            )

            # ==========================================
            # Reduce Inventory
            # ==========================================

            inventory.quantity -= data.quantity

            db.commit()

            db.refresh(spare_part)

            return spare_part

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(

                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=f"Spare Part Issue Failed : {str(e)}"

            )
            # =====================================================
    # Get Spare Parts
    # =====================================================

    @staticmethod
    def get_spare_parts(

        db: Session,

        service_visit_id: int = None,

        product_id: int = None,

        warehouse_id: int = None,

        is_billable: bool = None,

        page: int = 1,

        page_size: int = 10

    ):

        skip = (page - 1) * page_size

        spare_parts = ServiceSparePartRepository.get_all(

            db=db,

            service_visit_id=service_visit_id,

            product_id=product_id,

            warehouse_id=warehouse_id,

            is_billable=is_billable,

            skip=skip,

            limit=page_size

        )

        total = ServiceSparePartRepository.count(

            db=db,

            service_visit_id=service_visit_id,

            product_id=product_id,

            warehouse_id=warehouse_id,

            is_billable=is_billable

        )

        return {

            "total": total,

            "page": page,

            "page_size": page_size,

            "items": spare_parts

        }

    # =====================================================
    # Get Spare Part
    # =====================================================

    @staticmethod
    def get_spare_part(

        db: Session,

        spare_part_id: int

    ):

        spare_part = ServiceSparePartRepository.get_by_id(

            db,

            spare_part_id

        )

        if not spare_part:

            raise HTTPException(

                status_code=404,

                detail="Service Spare Part not found."

            )

        return spare_part

    # =====================================================
    # Update Spare Part
    # =====================================================

    @staticmethod
    def update_spare_part(

        db: Session,

        spare_part_id: int,

        data: ServiceSparePartUpdate,

        current_user

    ):

        try:

            spare_part = ServiceSparePartRepository.get_by_id(

                db,

                spare_part_id

            )

            if not spare_part:

                raise HTTPException(

                    status_code=404,

                    detail="Service Spare Part not found."

                )

            update_data = data.model_dump(

                exclude_unset=True

            )

            for key, value in update_data.items():

                setattr(

                    spare_part,

                    key,

                    value

                )

            if data.quantity is not None or data.unit_price is not None:

                quantity = (
                    data.quantity
                    if data.quantity is not None
                    else spare_part.quantity
                )

                unit_price = (
                    data.unit_price
                    if data.unit_price is not None
                    else spare_part.unit_price
                )

                spare_part.total_price = (
                    Decimal(quantity) * Decimal(unit_price)
                )

            ServiceSparePartRepository.update(

                db,

                spare_part

            )

            return spare_part

        except HTTPException:

            raise

        except Exception as e:

            raise HTTPException(

                status_code=500,

                detail=str(e)

            )

    # =====================================================
    # Delete Spare Part
    # =====================================================

    @staticmethod
    def delete_spare_part(

        db: Session,

        spare_part_id: int

    ):

        spare_part = ServiceSparePartRepository.get_by_id(

            db,

            spare_part_id

        )

        if not spare_part:

            raise HTTPException(

                status_code=404,

                detail="Service Spare Part not found."

            )

        ServiceSparePartRepository.delete(

            db,

            spare_part

        )

        return {

            "success": True,

            "message": "Service Spare Part deleted successfully."

        }

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(

        db: Session

    ):

        return ServiceSparePartRepository.dashboard(db)