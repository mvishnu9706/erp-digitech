from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
    UploadFile,
    File,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)

from app.services.product_service import product_service


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# ==========================================================
# Get Products
# ==========================================================

@router.get("")
def get_products(
    page: int = Query(
        1,
        ge=1
    ),

    size: int = Query(
        10,
        ge=1
    ),

    search: Optional[str] = None,

    category_id: Optional[int] = None,

    brand_id: Optional[int] = None,

    warehouse_id: Optional[int] = None,

    status: Optional[str] = None,

    db: Session = Depends(get_db),
):

    return product_service.get_products(

        db=db,

        page=page,

        size=size,

        search=search,

        category_id=category_id,

        brand_id=brand_id,

        warehouse_id=warehouse_id,

        status=status,

    )


# ==========================================================
# Export Products
#
# Supports the Product Master filters:
#
# search
# category_id
# brand_id
# warehouse_id
# status
#
# If no filters are supplied:
#     Export ALL products
#
# If filters are supplied:
#     Export only matching products
# ==========================================================

@router.get("/export")
def export_products(

    search: Optional[str] = None,

    category_id: Optional[int] = None,

    brand_id: Optional[int] = None,

    warehouse_id: Optional[int] = None,

    status: Optional[str] = None,

    db: Session = Depends(get_db),

):

    return product_service.export_products(

        db=db,

        search=search,

        category_id=category_id,

        brand_id=brand_id,

        warehouse_id=warehouse_id,

        status=status,

    )


# ==========================================================
# Download Import Template
# ==========================================================

@router.get("/template")
def download_template():

    return product_service.download_template()


# ==========================================================
# Import Products
# ==========================================================

@router.post("/import")
def import_products(

    file: UploadFile = File(...),

    db: Session = Depends(get_db),

):

    return product_service.import_products(

        db,

        file

    )


# ==========================================================
# Get Product By ID
# ==========================================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(

    product_id: int,

    db: Session = Depends(get_db),

):

    product = product_service.get_product(

        db,

        product_id

    )


    if not product:

        raise HTTPException(

            status_code=404,

            detail="Product not found"

        )


    return product


# ==========================================================
# Create Product
# ==========================================================

@router.post(
    "",
    response_model=ProductResponse
)
def create_product(

    data: ProductCreate,

    db: Session = Depends(get_db),

):

    return product_service.create_product(

        db,

        data

    )


# ==========================================================
# Update Product
# ==========================================================

@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(

    product_id: int,

    data: ProductUpdate,

    db: Session = Depends(get_db),

):

    return product_service.update_product(

        db,

        product_id,

        data

    )


# ==========================================================
# Delete Product
# ==========================================================

@router.delete(
    "/{product_id}"
)
def delete_product(

    product_id: int,

    db: Session = Depends(get_db),

):

    return product_service.delete_product(

        db,

        product_id

    )