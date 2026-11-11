from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)
from app.services.category_service import CategoryService
from app.core.dependencies import (
    get_current_admin,
    get_current_user,
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# =====================================================
# Create Category
# =====================================================

@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Category"
)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    return CategoryService.create_category(
        db=db,
        data=category,
        current_user=current_user
    )


# =====================================================
# Get All Categories
# =====================================================

@router.get(
    "/",
    response_model=list[CategoryResponse],
    summary="Get All Categories"
)
def get_categories(
    search: Optional[str] = Query(
        default=None,
        description="Search Category"
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

    return CategoryService.get_categories(
        db=db,
        search=search,
        page=page,
        page_size=page_size
    )


# =====================================================
# Get Category By ID
# =====================================================

@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get Category"
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return CategoryService.get_category(
        db=db,
        category_id=category_id
    )


# =====================================================
# Update Category
# =====================================================

@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update Category"
)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    return CategoryService.update_category(
        db=db,
        category_id=category_id,
        data=category,
        current_user=current_user
    )


# =====================================================
# Delete Category
# =====================================================

@router.delete(
    "/{category_id}",
    summary="Delete Category"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    CategoryService.delete_category(
        db=db,
        category_id=category_id
    )

    return {
        "success": True,
        "message": "Category deleted successfully."
    }