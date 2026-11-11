from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.inventory import Inventory
from app.models.category import Category
from app.models.brand import Brand
from app.models.unit import Unit
from app.models.warehouse import Warehouse


def seed_products(db: Session):

    # =====================================================
    # Category Map
    # =====================================================

    category_map = {
        c.name: c.id
        for c in db.query(Category).all()
    }

    # =====================================================
    # Brand Map
    # =====================================================

    brand_map = {
        b.name: b.id
        for b in db.query(Brand).all()
    }

    # =====================================================
    # Default Unit
    # =====================================================

    unit = (
        db.query(Unit)
        .first()
    )

    if not unit:
        print(
            "❌ No unit found. "
            "Please seed units before products."
        )
        return

    unit_id = unit.id

    # =====================================================
    # Default Warehouse
    # =====================================================

    warehouse = (
        db.query(Warehouse)
        .first()
    )

    if not warehouse:
        print(
            "❌ No warehouse found. "
            "Please seed warehouses before products."
        )
        return

    warehouse_id = warehouse.id

    # =====================================================
    # Products
    # =====================================================

    products = [

        {
            "product_name": "Canon imageRUNNER 2425",
            "model_no": "IR2425",
            "sku": "CAN-2425",
            "barcode": "890100000001",
            "category": "Copier",
            "brand": "Canon",
            "cost_price": 35000,
            "dtp_price": 39500,
            "retail_price": 42000,
            "gst": 18,
            "stock": 10,
            "minimum_stock": 2,
            "hsn": "84433100"
        },

        {
            "product_name": "HP LaserJet MFP M236DW",
            "model_no": "M236DW",
            "sku": "HP236DW",
            "barcode": "890100000002",
            "category": "Printer",
            "brand": "HP",
            "cost_price": 14500,
            "dtp_price": 16500,
            "retail_price": 17500,
            "gst": 18,
            "stock": 12,
            "minimum_stock": 3,
            "hsn": "84433100"
        },

        {
            "product_name": "Epson EcoTank L3250",
            "model_no": "L3250",
            "sku": "EPS3250",
            "barcode": "890100000003",
            "category": "Printer",
            "brand": "Epson",
            "cost_price": 11800,
            "dtp_price": 12800,
            "retail_price": 13900,
            "gst": 18,
            "stock": 15,
            "minimum_stock": 5,
            "hsn": "84433100"
        },

        {
            "product_name": "Brother DCP-B7535DW",
            "model_no": "B7535DW",
            "sku": "BRO7535",
            "barcode": "890100000004",
            "category": "Printer",
            "brand": "Brother",
            "cost_price": 16500,
            "dtp_price": 17900,
            "retail_price": 18900,
            "gst": 18,
            "stock": 8,
            "minimum_stock": 2,
            "hsn": "84433100"
        },

        {
            "product_name": "Kyocera TASKalfa 2554ci",
            "model_no": "2554CI",
            "sku": "KYO2554",
            "barcode": "890100000005",
            "category": "Copier",
            "brand": "Kyocera",
            "cost_price": 165000,
            "dtp_price": 179000,
            "retail_price": 189000,
            "gst": 18,
            "stock": 3,
            "minimum_stock": 1,
            "hsn": "84433100"
        }

    ]

    # =====================================================
    # Create Products
    # =====================================================

    for p in products:

        # =================================================
        # Check Existing Product
        # =================================================

        exists = (
            db.query(Product)
            .filter(
                Product.sku == p["sku"]
            )
            .first()
        )

        if exists:
            continue

        # =================================================
        # Calculate Margin
        # =================================================

        if p["retail_price"]:

            margin = (
                (
                    p["retail_price"]
                    - p["cost_price"]
                )
                / p["retail_price"]
            ) * 100

        else:

            margin = 0

        # =================================================
        # Create Product
        #
        # IMPORTANT:
        #
        # Stock is NOT stored on Product anymore.
        #
        # Stock belongs to Inventory.
        # =================================================

        product = Product(

            product_name=p["product_name"],

            model_no=p["model_no"],

            sku=p["sku"],

            barcode=p["barcode"],

            category_id=category_map[
                p["category"]
            ],

            brand_id=brand_map[
                p["brand"]
            ],

            unit_id=unit_id,

            warehouse_id=warehouse_id,

            cost_price=p["cost_price"],

            dtp_price=p["dtp_price"],

            retail_price=p["retail_price"],

            margin_percentage=round(
                margin,
                2
            ),

            gst_percentage=p["gst"],

            hsn_code=p["hsn"],

            minimum_stock=p["minimum_stock"],

            status="Active"

        )

        db.add(product)

        # =================================================
        # Get Product ID
        # =================================================

        db.flush()

        # =================================================
        # Create Inventory
        #
        # ONLY ONE STOCK FIELD:
        #
        # inventory.stock
        #
        # No:
        #
        # current_stock
        # reserved_stock
        # available_stock
        # =================================================

        inventory = Inventory(

            product_id=product.id,

            warehouse_id=warehouse_id,

            stock=p["stock"],

            stock_status=(
                "OUT_OF_STOCK"
                if p["stock"] <= 0
                else (
                    "LOW_STOCK"
                    if p["stock"] <= p["minimum_stock"]
                    else "IN_STOCK"
                )
            )

        )

        db.add(inventory)

    # =====================================================
    # Commit
    # =====================================================

    db.commit()

    print(
        "✅ Products and Inventory Seeded Successfully"
    )