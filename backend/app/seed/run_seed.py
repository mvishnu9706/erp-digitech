from app.database import SessionLocal

from app.seed.seed_categories import seed_categories
from app.seed.seed_brands import seed_brands
from app.seed.seed_units import seed_units
from app.seed.seed_warehouses import seed_warehouses
from app.seed.seed_products import seed_products
from app.seed.seed_admin import seed_admin



def run():

    db = SessionLocal()

    try:

        print("=" * 60)
        print("DIGITECH ERP DATABASE SEEDER")
        print("=" * 60)

        seed_categories(db)
        seed_brands(db)
        seed_units(db)
        seed_warehouses(db)
        seed_products(db)
        seed_admin(db)

        print()
        print("🎉 Master Data Seeded Successfully")
        print("=" * 60)

    finally:

        db.close()


if __name__ == "__main__":
    run()