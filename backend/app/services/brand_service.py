from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.brand import Brand
from app.repositories.brand_repository import BrandRepository


class BrandService:

    @staticmethod
    def create_brand(
        db: Session,
        data,
        current_user
    ):

        # Check duplicate brand name
        existing_name = BrandRepository.get_by_name(
            db,
            data.name
        )

        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brand name already exists."
            )

        # Check duplicate brand code
        existing_code = BrandRepository.get_by_code(
            db,
            data.code.upper()
        )

        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brand code already exists."
            )

        brand = Brand(
            name=data.name,
            code=data.code.upper(),
            logo=data.logo,
            website=data.website,
            email=data.email,
            phone=data.phone,
            description=data.description,
            is_active=data.is_active,
            created_by=current_user.id,
            updated_by=current_user.id
        )

        return BrandRepository.create(db, brand)

    @staticmethod
    def get_brands(
        db: Session,
        search: str = None,
        page: int = 1,
        page_size: int = 10
    ):

        skip = (page - 1) * page_size

        return BrandRepository.get_all(
            db=db,
            search=search,
            skip=skip,
            limit=page_size
        )

    @staticmethod
    def get_brand(
        db: Session,
        brand_id: int
    ):

        brand = BrandRepository.get_by_id(
            db,
            brand_id
        )

        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found."
            )

        return brand

    @staticmethod
    def update_brand(
        db: Session,
        brand_id: int,
        data,
        current_user
    ):

        brand = BrandRepository.get_by_id(
            db,
            brand_id
        )

        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found."
            )

        if data.name is not None:

            duplicate = BrandRepository.get_by_name(
                db,
                data.name
            )

            if duplicate and duplicate.id != brand.id:
                raise HTTPException(
                    status_code=400,
                    detail="Brand name already exists."
                )

            brand.name = data.name

        if data.code is not None:

            code = data.code.upper()

            duplicate = BrandRepository.get_by_code(
                db,
                code
            )

            if duplicate and duplicate.id != brand.id:
                raise HTTPException(
                    status_code=400,
                    detail="Brand code already exists."
                )

            brand.code = code

        if data.logo is not None:
            brand.logo = data.logo

        if data.website is not None:
            brand.website = data.website

        if data.email is not None:
            brand.email = data.email

        if data.phone is not None:
            brand.phone = data.phone

        if data.description is not None:
            brand.description = data.description

        if data.is_active is not None:
            brand.is_active = data.is_active

        brand.updated_by = current_user.id

        return BrandRepository.update(
            db,
            brand
        )

    @staticmethod
    def delete_brand(
        db: Session,
        brand_id: int
    ):

        brand = BrandRepository.get_by_id(
            db,
            brand_id
        )

        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found."
            )

        return BrandRepository.delete(
            db,
            brand
        )