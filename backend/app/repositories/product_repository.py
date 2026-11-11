from typing import Optional

from sqlalchemy.orm import (
    Session,
    joinedload,
)

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException

from app.models.product import Product
from app.models.inventory import Inventory
from app.models.category import Category
from app.models.brand import Brand


class ProductRepository:

    # ==========================================================
    # CREATE PRODUCT
    # ==========================================================

    @staticmethod
    def create(
        db: Session,
        data,
        category_id: int,
        brand_id: int
    ):

        product = Product(

            product_name=data.product_name,

            model_no=data.model_no or None,

            sku=data.sku or None,

            barcode=data.barcode or None,

            category_id=category_id,

            brand_id=brand_id,

            unit_id=data.unit_id,

            warehouse_id=data.warehouse_id,

            cost_price=data.cost_price,

            dtp_price=data.dtp_price,

            retail_price=data.retail_price,

            margin_percentage=data.margin_percentage,

            gst_percentage=data.gst_percentage,

            hsn_code=data.hsn_code or None,

            minimum_stock=data.minimum_stock,

            status=data.status

        )

        db.add(product)

        db.flush()

        # ======================================================
        # DEFAULT INVENTORY
        # ======================================================

        inventory = Inventory(

            product_id=product.id,

            warehouse_id=data.warehouse_id,

            stock=0,

            stock_status="OUT_OF_STOCK"

        )

        db.add(inventory)

        db.commit()

        # ======================================================
        # RELOAD PRODUCT WITH RELATIONSHIPS
        # ======================================================

        product = (

            db.query(Product)

            .options(

                joinedload(Product.inventory),

                joinedload(Product.category),

                joinedload(Product.brand),

                joinedload(Product.unit),

                joinedload(Product.warehouse),

            )

            .filter(
                Product.id == product.id
            )

            .first()

        )

        return product


    # ==========================================================
    # GET PRODUCT BY ID
    # ==========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        product_id: int
    ):

        return (

            db.query(Product)

            .options(

                joinedload(Product.inventory),

                joinedload(Product.category),

                joinedload(Product.brand),

                joinedload(Product.unit),

                joinedload(Product.warehouse),

            )

            .filter(
                Product.id == product_id
            )

            .first()

        )


    # ==========================================================
    # GET PRODUCT INVENTORY
    # ==========================================================

    @staticmethod
    def get_product_inventory(
        db: Session,
        product_id: int,
        warehouse_id: int
    ):

        product = (

            db.query(Product)

            .options(
                joinedload(Product.inventory)
            )

            .filter(
                Product.id == product_id
            )

            .first()

        )

        if not product:

            return None

        return product


    # ==========================================================
    # UPDATE COST PRICE
    # ==========================================================

    @staticmethod
    def update_cost_price(
        db: Session,
        product_id: int,
        cost_price
    ):

        product = (

            db.query(Product)

            .filter(
                Product.id == product_id
            )

            .first()

        )

        if not product:

            return None

        product.cost_price = cost_price

        db.flush()

        db.refresh(product)

        return product


    # ==========================================================
    # GET PRODUCT BY SKU
    # ==========================================================

    @staticmethod
    def get_by_sku(
        db: Session,
        sku: str
    ):

        return (

            db.query(Product)

            .filter(
                Product.sku == sku
            )

            .first()

        )


    # ==========================================================
    # GET ALL SKUS
    # ==========================================================

    @staticmethod
    def get_all_skus(
        db: Session
    ):

        return {

            product[0]: product[1]

            for product in (

                db.query(
                    Product.sku,
                    Product.id
                )

                .all()

            )

        }


    # ==========================================================
    # GET PRODUCTS
    #
    # Used by:
    #
    # 1. Product Master
    # 2. Product Search
    # 3. Product Export
    #
    # Search fields:
    #
    # Product Name
    # Model No
    # SKU
    # Barcode
    # Category
    # Brand
    #
    # Filters:
    #
    # Category
    # Brand
    # Warehouse
    # Status
    # ==========================================================

    @staticmethod
    def get_all(

        db: Session,

        page: int = 1,

        size: int = 10,

        search: Optional[str] = None,

        category_id: Optional[int] = None,

        brand_id: Optional[int] = None,

        warehouse_id: Optional[int] = None,

        status: Optional[str] = None

    ):

        # ======================================================
        # BASE QUERY
        # ======================================================

        query = (

            db.query(Product)

            .options(

                joinedload(Product.inventory),

                joinedload(Product.category),

                joinedload(Product.brand),

                joinedload(Product.unit),

                joinedload(Product.warehouse),

            )

        )


        # ======================================================
        # SEARCH
        #
        # Search across:
        #
        # Product Name
        # Model
        # SKU
        # Barcode
        # Category Name
        # Brand Name
        # ======================================================

        if search:

            search_value = search.strip()

            if search_value:

                search_pattern = (
                    f"%{search_value}%"
                )

                query = (

                    query

                    .outerjoin(
                        Category,
                        Product.category_id ==
                        Category.id
                    )

                    .outerjoin(
                        Brand,
                        Product.brand_id ==
                        Brand.id
                    )

                    .filter(

                        or_(

                            Product.product_name.ilike(
                                search_pattern
                            ),

                            Product.model_no.ilike(
                                search_pattern
                            ),

                            Product.sku.ilike(
                                search_pattern
                            ),

                            Product.barcode.ilike(
                                search_pattern
                            ),

                            Category.name.ilike(
                                search_pattern
                            ),

                            Brand.name.ilike(
                                search_pattern
                            ),

                        )

                    )

                )


        # ======================================================
        # CATEGORY FILTER
        # ======================================================

        if category_id:

            query = query.filter(

                Product.category_id ==
                category_id

            )


        # ======================================================
        # BRAND FILTER
        # ======================================================

        if brand_id:

            query = query.filter(

                Product.brand_id ==
                brand_id

            )


        # ======================================================
        # WAREHOUSE FILTER
        # ======================================================

        if warehouse_id:

            query = query.filter(

                Product.warehouse_id ==
                warehouse_id

            )


        # ======================================================
        # STATUS FILTER
        # ======================================================

        if status:

            query = query.filter(

                Product.status ==
                status

            )


        # ======================================================
        # TOTAL RECORDS
        # ======================================================

        total = query.count()


        # ======================================================
        # PAGINATED PRODUCTS
        # ======================================================

        products = (

            query

            .order_by(
                Product.id.desc()
            )

            .offset(
                (page - 1) * size
            )

            .limit(size)

            .all()

        )


        # ======================================================
        # RETURN
        # ======================================================

        return {

            "items": products,

            "page": page,

            "size": size,

            "total": total,

            "pages": (

                (total + size - 1)
                // size

            )

        }


    # ==========================================================
    # GET ALL PRODUCTS
    #
    # Used elsewhere when all products are specifically needed.
    # ==========================================================

    @staticmethod
    def get_all_products(
        db: Session
    ):

        return (

            db.query(Product)

            .options(

                joinedload(Product.inventory),

                joinedload(Product.unit),

                joinedload(Product.brand),

                joinedload(Product.category),

                joinedload(Product.warehouse),

            )

            .all()

        )


    # ==========================================================
    # BULK CREATE PRODUCTS
    # ==========================================================

    @staticmethod
    def bulk_create_products(
        db: Session,
        products: list[Product]
    ):

        db.add_all(products)

        db.commit()

        for product in products:

            db.refresh(product)

        return products


    # ==========================================================
    # UPDATE PRODUCT
    # ==========================================================

    @staticmethod
    def update(
        db: Session,
        product: Product,
        data,
        category_id: int,
        brand_id: int
    ):
        try:
            update_data = data.model_dump(
                exclude_unset=True,
                exclude_none=True
            )

            # Normalize optional text values. Empty strings are stored as
            # NULL for optional identifiers, rather than as empty strings.
            optional_text_fields = (
                "model_no",
                "sku",
                "barcode",
                "hsn_code",
            )

            for field in optional_text_fields:
                if field in update_data:
                    value = update_data[field]
                    if isinstance(value, str):
                        update_data[field] = value.strip() or None

            # Apply fields present in the update payload.
            for field, value in update_data.items():
                # These are display fields used to resolve relationships.
                if field in ("category_name", "brand_name"):
                    continue

                # Ignore fields that are not actual Product model attributes.
                if not hasattr(product, field):
                    continue

                setattr(product, field, value)

            # Preserve/assign resolved category and brand relationships.
            product.category_id = category_id
            product.brand_id = brand_id

            db.commit()
            db.refresh(product)

            # Reload with relationships for the API response.
            return (
                db.query(Product)
                .options(
                    joinedload(Product.inventory),
                    joinedload(Product.category),
                    joinedload(Product.brand),
                    joinedload(Product.unit),
                    joinedload(Product.warehouse),
                )
                .filter(Product.id == product.id)
                .first()
            )

        except IntegrityError as exc:
            db.rollback()
            # Log the underlying database reason for diagnosis.
            print("Product update integrity error:", repr(exc.orig))
            raise HTTPException(
                status_code=400,
                detail=(
                    "Product update failed due to a database constraint. "
                    "Check SKU/barcode uniqueness and related field values."
                ),
            ) from exc

        except Exception:
            db.rollback()
            raise


    # ==========================================================
    # DELETE PRODUCT
    # ==========================================================

    @staticmethod
    def delete(
        db: Session,
        product: Product
    ):

        db.delete(product)

        db.commit()


# ==========================================================
# REPOSITORY INSTANCE
# ==========================================================

product_repository = ProductRepository()