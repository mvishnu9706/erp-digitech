from sqlalchemy.orm import Session

from app.models.category import Category

categories = [
    ("Printer", "CAT001"),
    ("Copier", "CAT002"),
    ("Scanner", "CAT003"),
    ("Toner", "CAT004"),
    ("Drum Unit", "CAT005"),
    ("Developer", "CAT006"),
    ("Consumables", "CAT007"),
    ("Accessories", "CAT008"),
    ("Spare Parts", "CAT009"),
    ("Rental Machine", "CAT010"),
]


def seed_categories(db: Session):

    for name, code in categories:

        category = (
            db.query(Category)
            .filter(Category.code == code)
            .first()
        )

        if not category:

            db.add(
                Category(
                    name=name,
                    code=code,
                    description=f"{name} Category",
                    is_active=True
                )
            )

    db.commit()

    print("✅ Categories Seeded Successfully")