from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.brand import Brand

class BrandRepository:

    @staticmethod
    def create(db: Session, brand: Brand):
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return brand

    @staticmethod
    def get_all(
        db: Session,
        search: str = None,
        skip: int = 0,
        limit: int = 10
    ):

        query = db.query(Brand)

        if search:
            query = query.filter(
                or_(
                    Brand.name.ilike(f"%{search}%"),
                    Brand.code.ilike(f"%{search}%")
                )
            )

        return (
            query
            .order_by(Brand.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        brand_id: int
    ):

        return (
            db.query(Brand)
            .filter(Brand.id == brand_id)
            .first()
        )

    @staticmethod
    def get_by_name(
        db: Session,
        name: str
    ):

        return (
            db.query(Brand)
            .filter(Brand.name == name)
            .first()
        )

    @staticmethod
    def get_by_code(
        db: Session,
        code: str
    ):

        return (
            db.query(Brand)
            .filter(Brand.code == code)
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        brand: Brand
    ):

        db.commit()
        db.refresh(brand)
        return brand

    @staticmethod
    def delete(
        db: Session,
        brand: Brand
    ):

        db.delete(brand)
        db.commit()

        return True

    @staticmethod
    def count(
        db: Session
    ):

        return db.query(Brand).count()

    @staticmethod
    def create_from_name(
        db: Session,
        name: str
    ):

        brand = Brand(
            name=name.strip(),
            code=name.upper().replace(" ", "_")
        )

        db.add(brand)
        db.commit()
        db.refresh(brand)

        return brand
brand_repository = BrandRepository()
