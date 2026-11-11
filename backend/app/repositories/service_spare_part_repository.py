from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.service_spare_part import ServiceSparePart


class ServiceSparePartRepository:

    # =====================================================
    # Create
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        spare_part: ServiceSparePart
    ):

        db.add(spare_part)

        return spare_part

    # =====================================================
    # Get All
    # =====================================================

    @staticmethod
    def get_all(

        db: Session,

        service_visit_id: int = None,

        product_id: int = None,

        warehouse_id: int = None,

        is_billable: bool = None,

        skip: int = 0,

        limit: int = 10

    ):

        query = db.query(ServiceSparePart)

        if service_visit_id:

            query = query.filter(

                ServiceSparePart.service_visit_id == service_visit_id

            )

        if product_id:

            query = query.filter(

                ServiceSparePart.product_id == product_id

            )

        if warehouse_id:

            query = query.filter(

                ServiceSparePart.warehouse_id == warehouse_id

            )

        if is_billable is not None:

            query = query.filter(

                ServiceSparePart.is_billable == is_billable

            )

        return (

            query

            .order_by(

                ServiceSparePart.id.desc()

            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # Count
    # =====================================================

    @staticmethod
    def count(

        db: Session,

        service_visit_id=None,

        product_id=None,

        warehouse_id=None,

        is_billable=None

    ):

        query = db.query(ServiceSparePart)

        if service_visit_id:

            query = query.filter(

                ServiceSparePart.service_visit_id == service_visit_id

            )

        if product_id:

            query = query.filter(

                ServiceSparePart.product_id == product_id

            )

        if warehouse_id:

            query = query.filter(

                ServiceSparePart.warehouse_id == warehouse_id

            )

        if is_billable is not None:

            query = query.filter(

                ServiceSparePart.is_billable == is_billable

            )

        return query.count()

    # =====================================================
    # Get By ID
    # =====================================================

    @staticmethod
    def get_by_id(

        db: Session,

        spare_part_id: int

    ):

        return (

            db.query(ServiceSparePart)

            .filter(

                ServiceSparePart.id == spare_part_id

            )

            .first()

        )

    # =====================================================
    # Get By Service Visit
    # =====================================================

    @staticmethod
    def get_by_service_visit(

        db: Session,

        service_visit_id: int

    ):

        return (

            db.query(ServiceSparePart)

            .filter(

                ServiceSparePart.service_visit_id == service_visit_id

            )

            .order_by(

                ServiceSparePart.id.desc()

            )

            .all()

        )
        # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        spare_part: ServiceSparePart
    ):

        db.commit()

        db.refresh(spare_part)

        return spare_part

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        spare_part: ServiceSparePart
    ):

        db.delete(spare_part)

        db.commit()

        return True

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        total_parts = db.query(
            ServiceSparePart
        ).count()

        total_quantity = db.query(

            func.coalesce(

                func.sum(
                    ServiceSparePart.quantity
                ),

                Decimal("0")

            )

        ).scalar()

        total_cost = db.query(

            func.coalesce(

                func.sum(
                    ServiceSparePart.total_price
                ),

                Decimal("0")

            )

        ).scalar()

        billable_parts = db.query(

            ServiceSparePart

        ).filter(

            ServiceSparePart.is_billable == True

        ).count()

        warranty_parts = db.query(

            ServiceSparePart

        ).filter(

            ServiceSparePart.is_billable == False

        ).count()

        return {

            "total_parts_used": total_parts,

            "total_quantity": total_quantity,

            "total_cost": total_cost,

            "billable_parts": billable_parts,

            "warranty_parts": warranty_parts

        }