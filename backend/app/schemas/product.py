from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.schemas.category import CategoryResponse
from app.schemas.brand import BrandResponse
from app.schemas.unit import UnitResponse
from app.schemas.warehouse import WarehouseResponse


# ======================================================
# Base Schema
# ======================================================

class ProductBase(BaseModel):

    product_name: str

    model_no: Optional[str] = None

    sku: Optional[str] = None

    barcode: Optional[str] = None

    category_name: str

    brand_name: str

    unit_id: int

    warehouse_id: int

    cost_price: Decimal

    dtp_price: Decimal

    retail_price: Decimal

    margin_percentage: Decimal

    gst_percentage: Decimal = Decimal("18.00")

    hsn_code: Optional[str] = None

    minimum_stock: int = Field(
        default=0,
        ge=0
    )

    status: str = "Active"


# ======================================================
# Create
# ======================================================

class ProductCreate(ProductBase):
    pass


# ======================================================
# Update
# ======================================================

class ProductUpdate(BaseModel):

    product_name: Optional[str] = None

    model_no: Optional[str] = None

    sku: Optional[str] = None

    barcode: Optional[str] = None

    category_name: Optional[str] = None

    brand_name: Optional[str] = None

    unit_id: Optional[int] = None

    warehouse_id: Optional[int] = None

    cost_price: Optional[Decimal] = None

    dtp_price: Optional[Decimal] = None

    retail_price: Optional[Decimal] = None

    margin_percentage: Optional[Decimal] = None

    gst_percentage: Optional[Decimal] = None

    hsn_code: Optional[str] = None

    minimum_stock: Optional[int] = Field(
        default=None,
        ge=0
    )

    status: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ======================================================
# Inventory Response
# ======================================================
#
# Inventory now maintains ONLY one stock quantity:
#
#     stock
#
# Removed:
#
#     current_stock
#     reserved_stock
#     available_stock
#
# Stock changes only when an actual inventory movement
# is completed.
# ======================================================

class InventoryResponse(BaseModel):

    warehouse: WarehouseResponse

    stock: int

    stock_status: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ======================================================
# Product Response
# ======================================================

class ProductResponse(BaseModel):

    id: int

    product_name: str

    model_no: Optional[str] = None

    sku: Optional[str] = None

    barcode: Optional[str] = None

    category: CategoryResponse

    brand: BrandResponse

    unit: UnitResponse

    warehouse: WarehouseResponse

    cost_price: Decimal

    dtp_price: Decimal

    retail_price: Decimal

    margin_percentage: Decimal

    gst_percentage: Decimal

    hsn_code: Optional[str] = None

    minimum_stock: int

    status: str

    created_by: Optional[int]

    updated_by: Optional[int]

    created_at: datetime

    updated_at: Optional[datetime]

    inventory: List[InventoryResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )