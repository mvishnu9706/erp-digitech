from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse
from app.repositories.warehouse_repository import WarehouseRepository


class WarehouseService:

    @staticmethod
    def create_warehouse(
        db: Session,
        data,
        current_user
    ):

        # ---------------------------------------
        # Duplicate Warehouse Code
        # ---------------------------------------

        warehouse_code = data.warehouse_code.upper()

        if WarehouseRepository.get_by_code(
            db,
            warehouse_code
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Warehouse code already exists."
            )

        # ---------------------------------------
        # Duplicate Warehouse Name
        # ---------------------------------------

        if WarehouseRepository.get_by_name(
            db,
            data.warehouse_name
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Warehouse name already exists."
            )

        # ---------------------------------------
        # Only One Default Warehouse
        # ---------------------------------------

        if data.is_default:

            old_default = WarehouseRepository.get_default(db)

            if old_default:
                old_default.is_default = False
                WarehouseRepository.update(
                    db,
                    old_default
                )

        warehouse = Warehouse(

            warehouse_code=warehouse_code,

            warehouse_name=data.warehouse_name,

            contact_person=data.contact_person,

            phone=data.phone,

            email=data.email,

            address=data.address,

            city=data.city,

            state=data.state,

            country=data.country,

            pincode=data.pincode,

            is_default=data.is_default,

            is_active=data.is_active,

            created_by=current_user.id,

            updated_by=current_user.id
        )

        return WarehouseRepository.create(
            db,
            warehouse
        )

    @staticmethod
    def get_warehouses(
        db: Session,
        search=None,
        is_active=None,
        is_default=None,
        page=1,
        page_size=10
    ):

        skip = (page - 1) * page_size

        return WarehouseRepository.get_all(

            db=db,

            search=search,

            is_active=is_active,

            is_default=is_default,

            skip=skip,

            limit=page_size
        )

    @staticmethod
    def get_warehouse(
        db: Session,
        warehouse_id: int
    ):

        warehouse = WarehouseRepository.get_by_id(
            db,
            warehouse_id
        )

        if not warehouse:

            raise HTTPException(
                status_code=404,
                detail="Warehouse not found."
            )

        return warehouse

    @staticmethod
    def update_warehouse(
        db: Session,
        warehouse_id: int,
        data,
        current_user
    ):

        warehouse = WarehouseRepository.get_by_id(
            db,
            warehouse_id
        )

        if not warehouse:

            raise HTTPException(
                status_code=404,
                detail="Warehouse not found."
            )

        # ---------------------------------------
        # Warehouse Code
        # ---------------------------------------

        if data.warehouse_code is not None:

            code = data.warehouse_code.upper()

            duplicate = WarehouseRepository.get_by_code(
                db,
                code
            )

            if duplicate and duplicate.id != warehouse.id:

                raise HTTPException(
                    status_code=400,
                    detail="Warehouse code already exists."
                )

            warehouse.warehouse_code = code

        # ---------------------------------------
        # Warehouse Name
        # ---------------------------------------

        if data.warehouse_name is not None:

            duplicate = WarehouseRepository.get_by_name(
                db,
                data.warehouse_name
            )

            if duplicate and duplicate.id != warehouse.id:

                raise HTTPException(
                    status_code=400,
                    detail="Warehouse name already exists."
                )

            warehouse.warehouse_name = data.warehouse_name

        # ---------------------------------------
        # Other Fields
        # ---------------------------------------

        fields = [

            "contact_person",

            "phone",

            "email",

            "address",

            "city",

            "state",

            "country",

            "pincode",

            "is_active"

        ]

        for field in fields:

            value = getattr(data, field)

            if value is not None:

                setattr(
                    warehouse,
                    field,
                    value
                )

        # ---------------------------------------
        # Default Warehouse
        # ---------------------------------------

        if data.is_default is not None:

            if data.is_default:

                old_default = WarehouseRepository.get_default(
                    db
                )

                if old_default and old_default.id != warehouse.id:

                    old_default.is_default = False

                    WarehouseRepository.update(
                        db,
                        old_default
                    )

            warehouse.is_default = data.is_default

        warehouse.updated_by = current_user.id

        return WarehouseRepository.update(
            db,
            warehouse
        )

    @staticmethod
    def delete_warehouse(
        db: Session,
        warehouse_id: int
    ):

        warehouse = WarehouseRepository.get_by_id(
            db,
            warehouse_id
        )

        if not warehouse:

            raise HTTPException(
                status_code=404,
                detail="Warehouse not found."
            )

        if warehouse.is_default:

            raise HTTPException(
                status_code=400,
                detail="Default warehouse cannot be deleted."
            )

        return WarehouseRepository.delete(
            db,
            warehouse
        )