from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository


class CategoryService:

    @staticmethod
    def create_category(
        db: Session,
        data,
        current_user
    ):

        # Check duplicate category name
        existing_name = CategoryRepository.get_by_name(
            db,
            data.name
        )

        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists."
            )

        # Check duplicate category code
        existing_code = CategoryRepository.get_by_code(
            db,
            data.code.upper()
        )

        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category code already exists."
            )

        category = Category(
            name=data.name,
            code=data.code.upper(),
            description=data.description,
            is_active=data.is_active,
            created_by=current_user.id,
            updated_by=current_user.id
        )

        return CategoryRepository.create(
            db,
            category
        )

    @staticmethod
    def get_categories(
        db: Session,
        search: str = None,
        page: int = 1,
        page_size: int = 10
    ):

        skip = (page - 1) * page_size

        return CategoryRepository.get_all(
            db=db,
            search=search,
            skip=skip,
            limit=page_size
        )

    @staticmethod
    def get_category(
        db: Session,
        category_id: int
    ):

        category = CategoryRepository.get_by_id(
            db,
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )

        return category

    @staticmethod
    def update_category(
        db: Session,
        category_id: int,
        data,
        current_user
    ):

        category = CategoryRepository.get_by_id(
            db,
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )

        if data.name is not None:

            duplicate = CategoryRepository.get_by_name(
                db,
                data.name
            )

            if duplicate and duplicate.id != category.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category name already exists."
                )

            category.name = data.name

        if data.code is not None:

            code = data.code.upper()

            duplicate = CategoryRepository.get_by_code(
                db,
                code
            )

            if duplicate and duplicate.id != category.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category code already exists."
                )

            category.code = code

        if data.description is not None:
            category.description = data.description

        if data.is_active is not None:
            category.is_active = data.is_active

        category.updated_by = current_user.id

        return CategoryRepository.update(
            db,
            category
        )

    @staticmethod
    def delete_category(
        db: Session,
        category_id: int
    ):

        category = CategoryRepository.get_by_id(
            db,
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )

        return CategoryRepository.delete(
            db,
            category
        )