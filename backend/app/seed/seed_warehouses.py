from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse

warehouses = [

    {
        "warehouse_code": "WH001",
        "warehouse_name": "Main Warehouse",
        "city": "Bangalore"
    },

    {
        "warehouse_code": "WH002",
        "warehouse_name": "Service Warehouse",
        "city": "Bangalore"
    },

    {
        "warehouse_code": "WH003",
        "warehouse_name": "Rental Warehouse",
        "city": "Bangalore"
    },

    {
        "warehouse_code": "WH004",
        "warehouse_name": "Spare Parts Warehouse",
        "city": "Bangalore"
    }

]


def seed_warehouses(db: Session):

    for data in warehouses:

        warehouse = (
            db.query(Warehouse)
            .filter(
                Warehouse.warehouse_code == data["warehouse_code"]
            )
            .first()
        )

        if not warehouse:

            db.add(
                Warehouse(
                    warehouse_code=data["warehouse_code"],
                    warehouse_name=data["warehouse_name"],
                    city=data["city"],
                    is_default=False,
                    is_active=True
                )
            )

    db.commit()

    print("✅ Warehouses Seeded Successfully")