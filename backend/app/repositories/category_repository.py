from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.category import Category

class CategoryRepository:

    @staticmethod
    def create(
        db: Session,
        category: Category
    ):
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_all(
        db: Session,
        search: str = None,
        skip: int = 0,
        limit: int = 10
    ):

        query = db.query(Category)

        if search:
            query = query.filter(
                or_(
                    Category.name.ilike(f"%{search}%"),
                    Category.code.ilike(f"%{search}%")
                )
            )

        return (
            query
            .order_by(Category.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        category_id: int
    ):

        return (
            db.query(Category)
            .filter(Category.id == category_id)
            .first()
        )

    @staticmethod
    def get_by_name(
        db: Session,
        name: str
    ):

        return (
            db.query(Category)
            .filter(Category.name == name)
            .first()
        )

    @staticmethod
    def get_by_code(
        db: Session,
        code: str
    ):

        return (
            db.query(Category)
            .filter(Category.code == code)
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        category: Category
    ):

        db.commit()
        db.refresh(category)

        return category

    @staticmethod
    def delete(
        db: Session,
        category: Category
    ):

        db.delete(category)
        db.commit()

        return True

    @staticmethod
    def count(
        db: Session
    ):

        return db.query(Category).count()

    @staticmethod
    def create_from_name(
        db: Session,
        name: str
    ):

        category = Category(
            name=name.strip(),
            code=name.upper().replace(" ", "_")
        )

        db.add(category)
        db.commit()
        db.refresh(category)

        return category
category_repository = CategoryRepository()