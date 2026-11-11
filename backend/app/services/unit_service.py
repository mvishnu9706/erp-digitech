from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.unit import Unit
from app.repositories.unit_repository import UnitRepository


class UnitService:

    @staticmethod
    def create_unit(
        db: Session,
        data,
        current_user
    ):

        if UnitRepository.get_by_name(db, data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit name already exists."
            )

        short_name = data.short_name.upper()

        if UnitRepository.get_by_short_name(db, short_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Short name already exists."
            )

        unit = Unit(
            name=data.name,
            short_name=short_name,
            is_active=data.is_active,
            created_by=current_user.id,
            updated_by=current_user.id
        )

        return UnitRepository.create(db, unit)

    @staticmethod
    def get_units(
        db: Session,
        search=None,
        page=1,
        page_size=10
    ):

        skip = (page - 1) * page_size

        return UnitRepository.get_all(
            db=db,
            search=search,
            skip=skip,
            limit=page_size
        )

    @staticmethod
    def get_unit(
        db: Session,
        unit_id: int
    ):

        unit = UnitRepository.get_by_id(
            db,
            unit_id
        )

        if not unit:
            raise HTTPException(
                status_code=404,
                detail="Unit not found."
            )

        return unit

    @staticmethod
    def update_unit(
        db: Session,
        unit_id: int,
        data,
        current_user
    ):

        unit = UnitRepository.get_by_id(
            db,
            unit_id
        )

        if not unit:
            raise HTTPException(
                status_code=404,
                detail="Unit not found."
            )

        if data.name is not None:

            duplicate = UnitRepository.get_by_name(
                db,
                data.name
            )

            if duplicate and duplicate.id != unit.id:
                raise HTTPException(
                    status_code=400,
                    detail="Unit name already exists."
                )

            unit.name = data.name

        if data.short_name is not None:

            short_name = data.short_name.upper()

            duplicate = UnitRepository.get_by_short_name(
                db,
                short_name
            )

            if duplicate and duplicate.id != unit.id:
                raise HTTPException(
                    status_code=400,
                    detail="Short name already exists."
                )

            unit.short_name = short_name

        if data.is_active is not None:
            unit.is_active = data.is_active

        unit.updated_by = current_user.id

        return UnitRepository.update(
            db,
            unit
        )

    @staticmethod
    def delete_unit(
        db: Session,
        unit_id: int
    ):

        unit = UnitRepository.get_by_id(
            db,
            unit_id
        )

        if not unit:
            raise HTTPException(
                status_code=404,
                detail="Unit not found."
            )

        return UnitRepository.delete(
            db,
            unit
        )