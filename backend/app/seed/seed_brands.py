from sqlalchemy.orm import Session

from app.models.brand import Brand

brands = [
    ("Canon", "BR001"),
    ("HP", "BR002"),
    ("Epson", "BR003"),
    ("Brother", "BR004"),
    ("Kyocera", "BR005"),
    ("Ricoh", "BR006"),
    ("Konica Minolta", "BR007"),
    ("Sharp", "BR008"),
    ("Xerox", "BR009"),
    ("Pantum", "BR010"),
]


def seed_brands(db: Session):

    for name, code in brands:

        brand = (
            db.query(Brand)
            .filter(Brand.code == code)
            .first()
        )

        if not brand:

            db.add(
                Brand(
                    name=name,
                    code=code,
                    description=f"{name} Brand",
                    is_active=True
                )
            )

    db.commit()

    print("✅ Brands Seeded Successfully")