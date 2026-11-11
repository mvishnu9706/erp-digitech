from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.unit import Unit


class UnitRepository:

    @staticmethod
    def create(db: Session, unit: Unit):
        db.add(unit)
        db.commit()
        db.refresh(unit)
        return unit

    @staticmethod
    def get_all(
        db: Session,
        search: str = None,
        skip: int = 0,
        limit: int = 10
    ):

        query = db.query(Unit)

        if search:
            query = query.filter(
                or_(
                    Unit.name.ilike(f"%{search}%"),
                    Unit.short_name.ilike(f"%{search}%")
                )
            )

        return (
            query
            .order_by(Unit.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        unit_id: int
    ):
        return (
            db.query(Unit)
            .filter(Unit.id == unit_id)
            .first()
        )

    @staticmethod
    def get_by_name(
        db: Session,
        name: str
    ):
        return (
            db.query(Unit)
            .filter(Unit.name == name)
            .first()
        )

    @staticmethod
    def get_by_short_name(
        db: Session,
        short_name: str
    ):
        return (
            db.query(Unit)
            .filter(Unit.short_name == short_name)
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        unit: Unit
    ):
        db.commit()
        db.refresh(unit)
        return unit

    @staticmethod
    def delete(
        db: Session,
        unit: Unit
    ):
        db.delete(unit)
        db.commit()
        return True

    @staticmethod
    def count(db: Session):
        return db.query(Unit).count()


unit_repository = UnitRepository()