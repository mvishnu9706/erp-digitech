from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.brand import Brand
from app.models.category import Category
from app.models.warehouse import Warehouse


class InventoryRepository:

    # =====================================================
    # Create
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        inventory: Inventory
    ):
        # -------------------------------------------------
        # Update Stock Status
        # -------------------------------------------------

        if inventory.stock <= 0:
            inventory.stock_status = "OUT_OF_STOCK"
        elif inventory.stock <= 5:
            inventory.stock_status = "LOW_STOCK"
        else:
            inventory.stock_status = "IN_STOCK"

        db.add(inventory)
        db.flush()
        db.refresh(inventory)

        return inventory

    # =====================================================
    # Get All
    # =====================================================

    @staticmethod
    def get_all(
        db: Session,
        search: str = None,
        warehouse_id: int = None,
        product_id: int = None,
        stock_status: str = None,
        skip: int = 0,
        limit: int = 10
    ):

        query = (
            db.query(Inventory)
            .join(
                Product,
                Inventory.product_id == Product.id
            )
            .join(
                Warehouse,
                Inventory.warehouse_id == Warehouse.id
            )
            .join(
                Brand,
                Product.brand_id == Brand.id,
                isouter=True
            )
            .join(
                Category,
                Product.category_id == Category.id,
                isouter=True
            )
            .options(
                joinedload(Inventory.product),
                joinedload(Inventory.warehouse)
            )
        )

        # -------------------------------------------------
        # Search
        # -------------------------------------------------

        if search:
            query = query.filter(
                or_(
                    Product.product_name.ilike(
                        f"%{search}%"
                    ),
                    Product.sku.ilike(
                        f"%{search}%"
                    ),
                    Product.barcode.ilike(
                        f"%{search}%"
                    ),
                    Product.model_no.ilike(
                        f"%{search}%"
                    ),
                    Brand.name.ilike(
                        f"%{search}%"
                    ),
                    Category.name.ilike(
                        f"%{search}%"
                    ),
                    Warehouse.warehouse_name.ilike(
                        f"%{search}%"
                    ),
                    Inventory.rack_location.ilike(
                        f"%{search}%"
                    ),
                )
            )

        # -------------------------------------------------
        # Warehouse Filter
        # -------------------------------------------------

        if warehouse_id:
            query = query.filter(
                Inventory.warehouse_id == warehouse_id
            )

        # -------------------------------------------------
        # Product Filter
        # -------------------------------------------------

        if product_id:
            query = query.filter(
                Inventory.product_id == product_id
            )

        # -------------------------------------------------
        # Stock Status Filter
        # -------------------------------------------------

        if stock_status:
            query = query.filter(
                Inventory.stock_status == stock_status
            )

        return (
            query
            .order_by(Inventory.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # =====================================================
    # Get By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        inventory_id: int
    ):

        return (
            db.query(Inventory)
            .options(
                joinedload(Inventory.product),
                joinedload(Inventory.warehouse)
            )
            .filter(
                Inventory.id == inventory_id
            )
            .first()
        )

    # =====================================================
    # Get Product Inventory
    # =====================================================

    @staticmethod
    def get_product_inventory(
        db: Session,
        product_id: int,
        warehouse_id: int
    ):

        return (
            db.query(Inventory)
            .filter(
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id
            )
            .first()
        )

    # =====================================================
    # Create Inventory
    # =====================================================

    @staticmethod
    def create_inventory(
        db: Session,
        product_id: int,
        warehouse_id: int,
        quantity: int,
        purchase_price,
        user_id: int
    ):

        # -------------------------------------------------
        # Calculate Stock Status
        # -------------------------------------------------

        if quantity <= 0:
            status = "OUT_OF_STOCK"
        elif quantity <= 5:
            status = "LOW_STOCK"
        else:
            status = "IN_STOCK"

        inventory = Inventory(
            product_id=product_id,
            warehouse_id=warehouse_id,
            stock=quantity,
            stock_status=status,
            last_purchase_price=purchase_price,
            created_by=user_id,
            updated_by=user_id
        )

        db.add(inventory)
        db.flush()
        db.refresh(inventory)

        return inventory

    # =====================================================
    # Increase Stock (Purchase)
    # =====================================================

    @staticmethod
    def increase_stock(
        db: Session,
        product_id: int,
        warehouse_id: int,
        quantity: int,
        purchase_price,
        purchase_date,
        user_id: int,
    ):

        inventory = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db=db,
                product_id=product_id,
                warehouse_id=warehouse_id,
            )
        )

        # ------------------------------------------
        # Inventory Exists
        # ------------------------------------------

        if inventory:

            inventory.stock += quantity

            inventory.last_purchase_price = (
                purchase_price
            )

            inventory.last_purchase_date = (
                purchase_date
            )

            inventory.updated_by = user_id

            # --------------------------------------
            # Update Stock Status
            # --------------------------------------

            if inventory.stock <= 0:
                inventory.stock_status = (
                    "OUT_OF_STOCK"
                )

            elif inventory.stock <= 5:
                inventory.stock_status = (
                    "LOW_STOCK"
                )

            else:
                inventory.stock_status = (
                    "IN_STOCK"
                )

            db.flush()
            db.refresh(inventory)

            return inventory

        # ------------------------------------------
        # Inventory Doesn't Exist
        # ------------------------------------------

        inventory = Inventory(
            product_id=product_id,
            warehouse_id=warehouse_id,
            stock=quantity,
            last_purchase_price=purchase_price,
            last_purchase_date=purchase_date,
            stock_status=(
                "OUT_OF_STOCK"
                if quantity <= 0
                else (
                    "LOW_STOCK"
                    if quantity <= 5
                    else "IN_STOCK"
                )
            ),
            created_by=user_id,
            updated_by=user_id,
        )

        db.add(inventory)
        db.flush()
        db.refresh(inventory)

        return inventory

    # =====================================================
    # Product Wise
    # =====================================================

    @staticmethod
    def get_by_product(
        db: Session,
        product_id: int
    ):

        return (
            db.query(Inventory)
            .filter(
                Inventory.product_id == product_id
            )
            .all()
        )

    # =====================================================
    # Warehouse Wise
    # =====================================================

    @staticmethod
    def get_by_warehouse(
        db: Session,
        warehouse_id: int
    ):

        return (
            db.query(Inventory)
            .filter(
                Inventory.warehouse_id == warehouse_id
            )
            .all()
        )

    # =====================================================
    # Low Stock
    # =====================================================

    @staticmethod
    def low_stock(
        db: Session
    ):

        return (
            db.query(Inventory)
            .filter(
                Inventory.stock_status == "LOW_STOCK"
            )
            .all()
        )

    # =====================================================
    # Out Of Stock
    # =====================================================

    @staticmethod
    def out_of_stock(
        db: Session
    ):

        return (
            db.query(Inventory)
            .filter(
                Inventory.stock_status == "OUT_OF_STOCK"
            )
            .all()
        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        inventory: Inventory
    ):

        # -------------------------------------------------
        # Update Stock Status From Actual Stock
        # -------------------------------------------------

        if inventory.stock <= 0:
            inventory.stock_status = (
                "OUT_OF_STOCK"
            )

        elif inventory.stock <= 5:
            inventory.stock_status = (
                "LOW_STOCK"
            )

        else:
            inventory.stock_status = (
                "IN_STOCK"
            )

        db.flush()
        db.refresh(inventory)

        return inventory

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        inventory: Inventory
    ):

        db.delete(inventory)
        db.flush()

        return True

    # =====================================================
    # Dashboard Helpers
    # =====================================================

    @staticmethod
    def total_products(
        db: Session
    ):

        return (
            db.query(
                func.count(
                    func.distinct(
                        Inventory.product_id
                    )
                )
            )
            .scalar()
        )

    # =====================================================
    # Total Records
    # =====================================================

    @staticmethod
    def total_records(
        db: Session,
        search: str = None,
        warehouse_id: int = None,
        product_id: int = None,
        stock_status: str = None,
    ):

        query = (
            db.query(Inventory)
            .join(
                Product,
                Inventory.product_id == Product.id
            )
            .join(
                Warehouse,
                Inventory.warehouse_id == Warehouse.id
            )
            .join(
                Brand,
                Product.brand_id == Brand.id,
                isouter=True
            )
            .join(
                Category,
                Product.category_id == Category.id,
                isouter=True
            )
        )

        # -------------------------------------------------
        # Search
        # -------------------------------------------------

        if search:
            query = query.filter(
                or_(
                    Product.product_name.ilike(
                        f"%{search}%"
                    ),
                    Product.sku.ilike(
                        f"%{search}%"
                    ),
                    Product.barcode.ilike(
                        f"%{search}%"
                    ),
                    Product.model_no.ilike(
                        f"%{search}%"
                    ),
                    Brand.name.ilike(
                        f"%{search}%"
                    ),
                    Category.name.ilike(
                        f"%{search}%"
                    ),
                    Warehouse.warehouse_name.ilike(
                        f"%{search}%"
                    ),
                    Inventory.rack_location.ilike(
                        f"%{search}%"
                    ),
                )
            )

        # -------------------------------------------------
        # Warehouse
        # -------------------------------------------------

        if warehouse_id:
            query = query.filter(
                Inventory.warehouse_id == warehouse_id
            )

        # -------------------------------------------------
        # Product
        # -------------------------------------------------

        if product_id:
            query = query.filter(
                Inventory.product_id == product_id
            )

        # -------------------------------------------------
        # Stock Status
        # -------------------------------------------------

        if stock_status:
            query = query.filter(
                Inventory.stock_status == stock_status
            )

        return query.count()

    # =====================================================
    # Total Low Stock
    # =====================================================

    @staticmethod
    def total_low_stock(
        db: Session
    ):

        return (
            db.query(Inventory)
            .filter(
                Inventory.stock_status == "LOW_STOCK"
            )
            .count()
        )

    # =====================================================
    # Total Out Of Stock
    # =====================================================

    @staticmethod
    def total_out_of_stock(
        db: Session
    ):

        return (
            db.query(Inventory)
            .filter(
                Inventory.stock_status == "OUT_OF_STOCK"
            )
            .count()
        )

    # =====================================================
    # Total Stock
    # =====================================================

    @staticmethod
    def total_stock(
        db: Session
    ):

        return (
            db.query(
                func.coalesce(
                    func.sum(
                        Inventory.stock
                    ),
                    0
                )
            )
            .scalar()
        )

    # =====================================================
    # Total Inventory Value
    # =====================================================

    @staticmethod
    def total_inventory_value(
        db: Session
    ):

        return (
            db.query(
                func.coalesce(
                    func.sum(
                        Inventory.stock
                        * Inventory.last_purchase_price
                    ),
                    0
                )
            )
            .scalar()
        )

    # =====================================================
    # Total Incoming Stock
    # =====================================================

    @staticmethod
    def total_incoming_stock(
        db: Session
    ):

        return 0

    # =====================================================
    # Get By Product & Warehouse
    # =====================================================

    @staticmethod
    def get_by_product_and_warehouse(
        db: Session,
        product_id: int,
        warehouse_id: int,
    ):

        return (
            db.query(Inventory)
            .filter(
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id,
            )
            .first()
        )

    # =====================================================
    # Get Stock
    # =====================================================

    @staticmethod
    def get_stock(
        db: Session,
        product_id,
        warehouse_id,
    ):

        return (
            db.query(Inventory)
            .filter(
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id,
            )
            .first()
        )

    # =====================================================
    # Check Inventory
    # =====================================================

    @staticmethod
    def check_inventory(
        db: Session,
        product_id: int,
        warehouse_id: int,
    ):

        inventory = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db,
                product_id,
                warehouse_id,
            )
        )

        return {
            "exists": inventory is not None,
            "inventory_id": (
                inventory.id
                if inventory
                else None
            ),
        }

    # =====================================================
    # Dashboard Summary
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session,
        search: str = None,
        warehouse_id: int = None,
        product_id: int = None,
        stock_status: str = None,
    ):

        query = (
            db.query(Inventory)
            .join(
                Product,
                Inventory.product_id == Product.id
            )
            .join(
                Warehouse,
                Inventory.warehouse_id == Warehouse.id
            )
            .join(
                Brand,
                Product.brand_id == Brand.id,
                isouter=True
            )
            .join(
                Category,
                Product.category_id == Category.id,
                isouter=True
            )
        )

        # -------------------------------------------------
        # Search
        # -------------------------------------------------

        if search:
            query = query.filter(
                or_(
                    Product.product_name.ilike(
                        f"%{search}%"
                    ),
                    Product.sku.ilike(
                        f"%{search}%"
                    ),
                    Product.barcode.ilike(
                        f"%{search}%"
                    ),
                    Product.model_no.ilike(
                        f"%{search}%"
                    ),
                    Brand.name.ilike(
                        f"%{search}%"
                    ),
                    Category.name.ilike(
                        f"%{search}%"
                    ),
                    Warehouse.warehouse_name.ilike(
                        f"%{search}%"
                    ),
                    Inventory.rack_location.ilike(
                        f"%{search}%"
                    ),
                )
            )

        # -------------------------------------------------
        # Warehouse
        # -------------------------------------------------

        if warehouse_id:
            query = query.filter(
                Inventory.warehouse_id == warehouse_id
            )

        # -------------------------------------------------
        # Product
        # -------------------------------------------------

        if product_id:
            query = query.filter(
                Inventory.product_id == product_id
            )

        # -------------------------------------------------
        # Stock Status
        # -------------------------------------------------

        if stock_status:
            query = query.filter(
                Inventory.stock_status == stock_status
            )

        # -------------------------------------------------
        # Dashboard Result
        # -------------------------------------------------

        return {

            "total_products":
                query.with_entities(
                    func.count(
                        func.distinct(
                            Inventory.product_id
                        )
                    )
                ).scalar() or 0,

            "stock":
                query.with_entities(
                    func.coalesce(
                        func.sum(
                            Inventory.stock
                        ),
                        0
                    )
                ).scalar(),

            "low_stock":
                query.filter(
                    Inventory.stock_status
                    == "LOW_STOCK"
                ).count(),

            "out_of_stock":
                query.filter(
                    Inventory.stock_status
                    == "OUT_OF_STOCK"
                ).count(),

            "incoming_stock": 0,

            "inventory_value":
                query.with_entities(
                    func.coalesce(
                        func.sum(
                            Inventory.stock
                            * Inventory.last_purchase_price
                        ),
                        0
                    )
                ).scalar(),
        }