from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse


class WarehouseRepository:

    @staticmethod
    def create(
        db: Session,
        warehouse: Warehouse
    ):
        db.add(warehouse)
        db.commit()
        db.refresh(warehouse)
        return warehouse

    @staticmethod
    def get_all(
        db: Session,
        search: str = None,
        is_active: bool = None,
        is_default: bool = None,
        skip: int = 0,
        limit: int = 10
    ):

        query = db.query(Warehouse)

        # -----------------------------
        # Search
        # -----------------------------

        if search:
            query = query.filter(
                or_(
                    Warehouse.warehouse_code.ilike(f"%{search}%"),
                    Warehouse.warehouse_name.ilike(f"%{search}%"),
                    Warehouse.city.ilike(f"%{search}%"),
                    Warehouse.contact_person.ilike(f"%{search}%")
                )
            )

        # -----------------------------
        # Filters
        # -----------------------------

        if is_active is not None:
            query = query.filter(
                Warehouse.is_active == is_active
            )

        if is_default is not None:
            query = query.filter(
                Warehouse.is_default == is_default
            )

        return (
            query
            .order_by(Warehouse.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        warehouse_id: int
    ):

        return (
            db.query(Warehouse)
            .filter(
                Warehouse.id == warehouse_id
            )
            .first()
        )

    @staticmethod
    def get_by_code(
        db: Session,
        warehouse_code: str
    ):

        return (
            db.query(Warehouse)
            .filter(
                Warehouse.warehouse_code == warehouse_code
            )
            .first()
        )

    @staticmethod
    def get_by_name(
        db: Session,
        warehouse_name: str
    ):

        return (
            db.query(Warehouse)
            .filter(
                Warehouse.warehouse_name == warehouse_name
            )
            .first()
        )

    @staticmethod
    def get_default(
        db: Session
    ):

        return (
            db.query(Warehouse)
            .filter(
                Warehouse.is_default == True
            )
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        warehouse: Warehouse
    ):

        db.commit()
        db.refresh(warehouse)

        return warehouse

    @staticmethod
    def delete(
        db: Session,
        warehouse: Warehouse
    ):

        db.delete(warehouse)
        db.commit()

        return True

    @staticmethod
    def count(
        db: Session
    ):

        return db.query(Warehouse).count()

    @staticmethod
    def active_count(
        db: Session
    ):

        return (
            db.query(Warehouse)
            .filter(
                Warehouse.is_active == True
            )
            .count()
        )

    @staticmethod
    def inactive_count(
        db: Session
    ):

        return (
            db.query(Warehouse)
            .filter(
                Warehouse.is_active == False
            )
            .count()
        )


warehouse_repository = WarehouseRepository()