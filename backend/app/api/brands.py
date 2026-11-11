from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.brand import (
    BrandCreate,
    BrandUpdate,
    BrandResponse,
)
from app.services.brand_service import BrandService
from app.core.dependencies import (
    get_current_admin,
    get_current_user,
)

router = APIRouter(
    prefix="/brands",
    tags=["Brands"]
)


# ==========================================
# Create Brand
# ==========================================

@router.post(
    "/",
    response_model=BrandResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Brand"
)
def create_brand(
    brand: BrandCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    return BrandService.create_brand(
        db=db,
        data=brand,
        current_user=current_user
    )


# ==========================================
# Get All Brands
# ==========================================

@router.get(
    "/",
    response_model=list[BrandResponse],
    summary="Get All Brands"
)
def get_brands(
    search: Optional[str] = Query(
        default=None,
        description="Search Brand"
    ),
    page: int = Query(
        default=1,
        ge=1
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return BrandService.get_brands(
        db=db,
        search=search,
        page=page,
        page_size=page_size
    )


# ==========================================
# Get Single Brand
# ==========================================

@router.get(
    "/{brand_id}",
    response_model=BrandResponse,
    summary="Get Brand"
)
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return BrandService.get_brand(
        db=db,
        brand_id=brand_id
    )


# ==========================================
# Update Brand
# ==========================================

@router.put(
    "/{brand_id}",
    response_model=BrandResponse,
    summary="Update Brand"
)
def update_brand(
    brand_id: int,
    brand: BrandUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    return BrandService.update_brand(
        db=db,
        brand_id=brand_id,
        data=brand,
        current_user=current_user
    )


# ==========================================
# Delete Brand
# ==========================================

@router.delete(
    "/{brand_id}",
    summary="Delete Brand"
)
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    BrandService.delete_brand(
        db=db,
        brand_id=brand_id
    )

    return {
        "success": True,
        "message": "Brand deleted successfully."
    }