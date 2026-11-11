from decimal import Decimal
from io import BytesIO

from openpyxl import Workbook

from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.brand import Brand
from app.models.product import Product

from app.repositories.brand_repository import brand_repository
from app.repositories.category_repository import category_repository
from app.repositories.product_repository import product_repository
from app.repositories.unit_repository import unit_repository
from app.repositories.warehouse_repository import warehouse_repository

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
)

from app.utils.excel_helper import ExcelHelper


class ProductService:

    # ==========================================================
    # Create Product
    # ==========================================================

    def create_product(
        self,
        db: Session,
        data: ProductCreate
    ):

        # ----------------------------------
        # Validate Minimum Stock
        # ----------------------------------

        if data.minimum_stock < 0:

            raise HTTPException(
                status_code=400,
                detail="Minimum stock cannot be negative."
            )

        # ----------------------------------
        # Calculate Margin
        # ----------------------------------

        if data.retail_price > 0:

            margin = (
                (data.retail_price - data.cost_price)
                / data.retail_price
            ) * 100

            data.margin_percentage = round(
                Decimal(margin),
                2
            )

        else:

            data.margin_percentage = Decimal("0.00")

        # ----------------------------------
        # Category
        # ----------------------------------

        category = category_repository.get_by_name(
            db,
            data.category_name.strip()
        )

        if category is None:

            category = category_repository.create(
                db,
                Category(
                    name=data.category_name.strip(),
                    code=data.category_name.upper().replace(
                        " ",
                        "_"
                    )
                )
            )

        # ----------------------------------
        # Brand
        # ----------------------------------

        brand = brand_repository.get_by_name(
            db,
            data.brand_name.strip()
        )

        if brand is None:

            brand = brand_repository.create(
                db,
                Brand(
                    name=data.brand_name.strip(),
                    code=data.brand_name.upper().replace(
                        " ",
                        "_"
                    )
                )
            )

        # ----------------------------------
        # Save Product
        # ----------------------------------

        return product_repository.create(
            db=db,
            data=data,
            category_id=category.id,
            brand_id=brand.id
        )


    # ==========================================================
    # Get Products
    # ==========================================================

    def get_products(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        search=None,
        category_id=None,
        brand_id=None,
        warehouse_id=None,
        status=None
    ):

        return product_repository.get_all(
            db=db,
            page=page,
            size=size,
            search=search,
            category_id=category_id,
            brand_id=brand_id,
            warehouse_id=warehouse_id,
            status=status
        )


    # ==========================================================
    # Get Product
    # ==========================================================

    def get_product(
        self,
        db: Session,
        product_id: int
    ):

        return product_repository.get_by_id(
            db,
            product_id
        )


    # ==========================================================
    # Update Product
    # ==========================================================

    def update_product(
        self,
        db: Session,
        product_id: int,
        data: ProductUpdate
    ):

        product = product_repository.get_by_id(
            db,
            product_id
        )

        if not product:

            return None

        # ----------------------------------
        # Validate Minimum Stock
        # ----------------------------------

        if (
            data.minimum_stock is not None
            and data.minimum_stock < 0
        ):

            raise HTTPException(
                status_code=400,
                detail="Minimum stock cannot be negative."
            )

        # ----------------------------------
        # Calculate Margin
        # ----------------------------------

        retail_price = (
            data.retail_price
            if data.retail_price is not None
            else product.retail_price
        )

        cost_price = (
            data.cost_price
            if data.cost_price is not None
            else product.cost_price
        )

        if retail_price > 0:

            margin = (
                (retail_price - cost_price)
                / retail_price
            ) * 100

            data.margin_percentage = round(
                Decimal(margin),
                2
            )

        else:

            data.margin_percentage = Decimal("0.00")

        # ----------------------------------
        # Category
        # ----------------------------------

        if data.category_name:

            category = category_repository.get_by_name(
                db,
                data.category_name.strip()
            )

            if category is None:

                category = category_repository.create(
                    db,
                    Category(
                        name=data.category_name.strip(),
                        code=data.category_name.upper().replace(
                            " ",
                            "_"
                        )
                    )
                )

            category_id = category.id

        else:

            category_id = product.category_id

        # ----------------------------------
        # Brand
        # ----------------------------------

        if data.brand_name:

            brand = brand_repository.get_by_name(
                db,
                data.brand_name.strip()
            )

            if brand is None:

                brand = brand_repository.create(
                    db,
                    Brand(
                        name=data.brand_name.strip(),
                        code=data.brand_name.upper().replace(
                            " ",
                            "_"
                        )
                    )
                )

            brand_id = brand.id

        else:

            brand_id = product.brand_id

        # ----------------------------------
        # Update Product
        # ----------------------------------

        return product_repository.update(
            db=db,
            product=product,
            data=data,
            category_id=category_id,
            brand_id=brand_id
        )


    # ==========================================================
    # Delete Product
    # ==========================================================

    def delete_product(
        self,
        db: Session,
        product_id: int
    ):

        product = product_repository.get_by_id(
            db,
            product_id
        )

        if not product:

            return None

        product_repository.delete(
            db,
            product
        )

        return {
            "message": "Product Deleted Successfully"
        }


    # ==========================================================
    # Import Products From Excel
    # ==========================================================

    def import_products(
        self,
        db: Session,
        file: UploadFile
    ):

        # ----------------------------------
        # Load Master Data
        # ----------------------------------

        categories = {
            category.name.lower(): category
            for category in category_repository.get_all(
                db,
                limit=1000
            )
        }

        brands = {
            brand.name.lower(): brand
            for brand in brand_repository.get_all(
                db,
                limit=1000
            )
        }

        units = {
            unit.name.lower(): unit
            for unit in unit_repository.get_all(
                db,
                limit=1000
            )
        }

        warehouses = {
            warehouse.warehouse_name.lower(): warehouse
            for warehouse in warehouse_repository.get_all(
                db,
                limit=1000
            )
        }

        existing_skus = product_repository.get_all_skus(db)

        excel_helper = ExcelHelper()

        rows = excel_helper.read_excel(file)

        errors = []

        products_to_create = []

        # ----------------------------------
        # Read Rows
        # ----------------------------------

        for row_number, row in enumerate(
            rows,
            start=2
        ):

            try:

                required_fields = {

                    "Product Name":
                        row.get("Product Name"),

                    "Category":
                        row.get("Category"),

                    "Brand":
                        row.get("Brand"),

                    "Unit":
                        row.get("Unit"),

                    "Warehouse":
                        row.get("Warehouse"),

                    "SKU":
                        row.get("SKU"),

                    "Cost Price":
                        row.get("Cost Price"),

                    "Retail Price":
                        row.get("Retail Price"),

                    "Status":
                        row.get("Status")

                }

                for (
                    field_name,
                    field_value
                ) in required_fields.items():

                    if (
                        field_value is None
                        or str(field_value).strip() == ""
                    ):

                        errors.append({

                            "row": row_number,

                            "message":
                                f"{field_name} is required"

                        })

                if any(
                    error["row"] == row_number
                    for error in errors
                ):

                    continue

                # ----------------------------------
                # Category
                # ----------------------------------

                category = categories.get(
                    str(
                        row["Category"]
                    ).strip().lower()
                )

                if not category:

                    errors.append({

                        "row": row_number,

                        "message":
                            "Category not found"

                    })

                    continue

                # ----------------------------------
                # Brand
                # ----------------------------------

                brand = brands.get(
                    str(
                        row["Brand"]
                    ).strip().lower()
                )

                if not brand:

                    errors.append({

                        "row": row_number,

                        "message":
                            "Brand not found"

                    })

                    continue

                # ----------------------------------
                # Unit
                # ----------------------------------

                unit = units.get(
                    str(
                        row["Unit"]
                    ).strip().lower()
                )

                if not unit:

                    errors.append({

                        "row": row_number,

                        "message":
                            "Unit not found"

                    })

                    continue

                # ----------------------------------
                # Warehouse
                # ----------------------------------

                warehouse = warehouses.get(
                    str(
                        row["Warehouse"]
                    ).strip().lower()
                )

                if not warehouse:

                    errors.append({

                        "row": row_number,

                        "message":
                            "Warehouse not found"

                    })

                    continue

                # ----------------------------------
                # SKU
                # ----------------------------------

                sku = str(
                    row["SKU"]
                ).strip()

                if sku in existing_skus:

                    errors.append({

                        "row": row_number,

                        "message":
                            "SKU already exists"

                    })

                    continue

                # ----------------------------------
                # Prices
                # ----------------------------------

                cost_price = Decimal(
                    str(
                        row["Cost Price"]
                    )
                )

                retail_price = Decimal(
                    str(
                        row["Retail Price"]
                    )
                )

                dtp_price = row.get(
                    "DTP Price",
                    Decimal("0")
                )

                dtp_price = (

                    Decimal(
                        str(dtp_price)
                    )

                    if dtp_price

                    else Decimal("0")

                )

                # ----------------------------------
                # Margin
                # ----------------------------------

                if retail_price > 0:

                    margin_percentage = round(

                        Decimal(

                            (
                                (
                                    retail_price -
                                    cost_price
                                )
                                /
                                retail_price
                            )
                            * 100

                        ),

                        2

                    )

                else:

                    margin_percentage = Decimal(
                        "0.00"
                    )

                # ----------------------------------
                # GST
                # ----------------------------------

                gst_percentage = row.get(
                    "GST Percentage",
                    18
                )

                gst_percentage = (

                    Decimal(
                        str(gst_percentage)
                    )

                    if gst_percentage

                    else Decimal("18")

                )

                # ----------------------------------
                # Minimum Stock
                # ----------------------------------

                minimum_stock = int(

                    row.get(
                        "Minimum Stock",
                        0
                    )

                    or 0

                )

                if minimum_stock < 0:

                    errors.append({

                        "row": row_number,

                        "message":
                            "Minimum Stock cannot be negative."

                    })

                    continue

                # ----------------------------------
                # Create Product
                # ----------------------------------

                product = Product(

                    product_name=str(
                        row["Product Name"]
                    ).strip(),

                    model_no=str(
                        row.get(
                            "Model No",
                            ""
                        )
                    ).strip(),

                    sku=sku,

                    barcode=str(
                        row.get(
                            "Barcode",
                            ""
                        )
                    ).strip(),

                    category_id=category.id,

                    brand_id=brand.id,

                    unit_id=unit.id,

                    warehouse_id=warehouse.id,

                    cost_price=cost_price,

                    dtp_price=dtp_price,

                    retail_price=retail_price,

                    margin_percentage=
                        margin_percentage,

                    gst_percentage=
                        gst_percentage,

                    hsn_code=str(
                        row.get(
                            "HSN Code",
                            ""
                        )
                    ).strip(),

                    minimum_stock=
                        minimum_stock,

                    status=str(
                        row["Status"]
                    ).strip()

                )

                products_to_create.append(
                    product
                )

            except Exception as e:

                errors.append({

                    "row": row_number,

                    "message": str(e)

                })

        # ----------------------------------
        # Save
        # ----------------------------------

        if products_to_create:

            product_repository.bulk_create_products(
                db,
                products_to_create
            )

        return {

            "success":
                len(errors) == 0,

            "imported":
                len(products_to_create),

            "failed":
                len(errors),

            "errors":
                errors

        }


    # ==========================================================
    # EXPORT PRODUCTS TO EXCEL
    #
    # Filters:
    #
    # search
    # category_id
    # brand_id
    # warehouse_id
    # status
    #
    # No filters = ALL products
    #
    # Any filters = matching products only
    # ==========================================================

    def export_products(
        self,
        db: Session,
        search=None,
        category_id=None,
        brand_id=None,
        warehouse_id=None,
        status=None
    ):

        # ======================================================
        # Get filtered products
        #
        # IMPORTANT:
        #
        # We use the same repository filtering logic as the
        # Product Master search/filter system.
        # ======================================================

        result = product_repository.get_all(

            db=db,

            page=1,

            # Export ALL matching records.
            #
            # We use a very large size so pagination does not
            # cut off the exported results.
            size=1000000,

            search=search,

            category_id=category_id,

            brand_id=brand_id,

            warehouse_id=warehouse_id,

            status=status

        )


        products = result.get(
            "items",
            []
        )


        # ======================================================
        # Create Excel Workbook
        # ======================================================

        wb = Workbook()

        ws = wb.active

        ws.title = "Products"


        # ======================================================
        # Excel Headers
        # ======================================================

        headers = [

            "ID",

            "Product Name",

            "Model",

            "SKU",

            "Barcode",

            "Category",

            "Brand",

            "Unit",

            "Warehouse",

            "Cost Price",

            "DTP Price",

            "Retail Price",

            "Margin %",

            "GST",

            "HSN",

            "Minimum Stock",

            "Status"

        ]


        ws.append(headers)


        # ======================================================
        # Add Products
        # ======================================================

        for product in products:

            ws.append([

                product.id,

                product.product_name,

                product.model_no,

                product.sku,

                product.barcode,

                (
                    product.category.name
                    if product.category
                    else ""
                ),

                (
                    product.brand.name
                    if product.brand
                    else ""
                ),

                (
                    product.unit.name
                    if product.unit
                    else ""
                ),

                (
                    product.warehouse.warehouse_name
                    if product.warehouse
                    else ""
                ),

                float(
                    product.cost_price
                ),

                float(
                    product.dtp_price
                ),

                float(
                    product.retail_price
                ),

                float(
                    product.margin_percentage
                ),

                float(
                    product.gst_percentage
                ),

                product.hsn_code,

                product.minimum_stock,

                product.status

            ])


        # ======================================================
        # Create File Stream
        # ======================================================

        stream = BytesIO()

        wb.save(stream)

        stream.seek(0)


        # ======================================================
        # Return Excel
        # ======================================================

        return StreamingResponse(

            stream,

            media_type=
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            headers={

                "Content-Disposition":
                    "attachment; filename=Products.xlsx"

            }

        )


# ==========================================================
# Product Service Instance
# ==========================================================

product_service = ProductService()