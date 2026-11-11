from sqlalchemy.orm import Session

from app.models.unit import Unit

units = [
    ("Piece", "PCS"),
    ("Box", "BOX"),
    ("Pack", "PK"),
    ("Set", "SET"),
    
    
    ("Bottle", "BTL"),
    ("Kg", "KG"),
    ("Litre", "LTR"),
    ("Meter", "MTR"),
]


def seed_units(db: Session):

    for name, short_name in units:

        unit = (
            db.query(Unit)
            .filter(Unit.short_name == short_name)
            .first()
        )

        if not unit:

            db.add(
                Unit(
                    name=name,
                    short_name=short_name,
                    is_active=True
                )
            )

    db.commit()

    print("✅ Units Seeded Successfully")