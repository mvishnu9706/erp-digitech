
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.machine import Machine
from app.schemas.machine import MachineCreate, MachineUpdate
from app.repositories.machine_repository import MachineRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.utils.machine_number import MachineNumberGenerator


class MachineService:

    @staticmethod
    def create_machine(
        db: Session,
        data: MachineCreate,
        current_user
    ):
        try:
            # Validate customer.
            customer = CustomerRepository.get_by_id(
                db, data.customer_id
            )
            if not customer:
                raise HTTPException(
                    status_code=404,
                    detail="Customer not found."
                )

            # Validate product when provided.
            if data.product_id is not None:
                product = ProductRepository.get_by_id(
                    db, data.product_id
                )
                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail="Product not found."
                    )

            # Validate installer when provided.
            if data.installed_by:
                installer = UserRepository.get_by_id(
                    db, data.installed_by
                )
                if not installer:
                    raise HTTPException(
                        status_code=404,
                        detail="Installer not found."
                    )

            # Prevent duplicate serial numbers.
            serial = MachineRepository.get_by_serial_number(
                db, data.serial_number
            )
            if serial:
                raise HTTPException(
                    status_code=400,
                    detail="Serial Number already exists."
                )

            # Prevent duplicate asset tags.
            if data.asset_tag:
                asset = MachineRepository.get_by_asset_tag(
                    db, data.asset_tag
                )
                if asset:
                    raise HTTPException(
                        status_code=400,
                        detail="Asset Tag already exists."
                    )

            # Validate warranty dates.
            if (
                data.warranty_start
                and data.warranty_end
                and data.warranty_end < data.warranty_start
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Warranty End must be greater "
                        "than Warranty Start."
                    )
                )

            # Validate AMC dates.
            if (
                data.amc_start
                and data.amc_end
                and data.amc_end < data.amc_start
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "AMC End must be greater than AMC Start."
                    )
                )

            # Validate legacy overall meter readings.
            if data.current_meter < data.opening_meter:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Current Meter cannot be less "
                        "than Opening Meter."
                    )
                )

            # Validate each new meter reading against zero.
            meter_fields = (
                "a4_bw_current_meter",
                "a4_color_current_meter",
                "a3_bw_current_meter",
                "a3_color_current_meter",
            )
            for field in meter_fields:
                if getattr(data, field) < 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"{field} cannot be negative."
                    )

            # Generate the next machine number.
            last_machine = MachineRepository.last_machine(db)
            next_id = last_machine.id + 1 if last_machine else 1
            machine_number = MachineNumberGenerator.generate(next_id)

            # Create machine, preserving legacy fields and adding
            # the four separate print rates and meter readings.
            machine = Machine(
                machine_number=machine_number,
                machine_name=data.machine_name,
                customer_id=data.customer_id,
                product_id=data.product_id,
                serial_number=data.serial_number,
                asset_tag=data.asset_tag,
                installation_date=data.installation_date,
                installation_address=data.installation_address,
                installed_by=data.installed_by,

                warranty_start_date=data.warranty_start,
                warranty_end_date=data.warranty_end,
                amc_start_date=data.amc_start,
                amc_end_date=data.amc_end,

                # Legacy overall meter readings.
                opening_meter=data.opening_meter,
                current_meter=data.current_meter,

                # Legacy rental rate fields.
                rental_rate=data.rental_rate,
                cost_per_copy=data.cost_per_copy,

                # Rental billing configuration.
                free_prints_per_month=data.free_prints_per_month,
                a4_bw_rate=data.a4_bw_rate,
                a4_color_rate=data.a4_color_rate,
                a3_bw_rate=data.a3_bw_rate,
                a3_color_rate=data.a3_color_rate,

                # Latest meter readings for each print type.
                a4_bw_current_meter=data.a4_bw_current_meter,
                a4_color_current_meter=data.a4_color_current_meter,
                a3_bw_current_meter=data.a3_bw_current_meter,
                a3_color_current_meter=data.a3_color_current_meter,

                status=data.status,
                is_active=data.is_active,
                remarks=data.remarks,
                created_by=current_user.id,
                updated_by=current_user.id,
            )

            machine = MachineRepository.create(db, machine)
            db.commit()
            db.refresh(machine)
            return machine

        except HTTPException:
            db.rollback()
            raise

        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Machine creation failed: {str(exc)}"
            ) from exc

    @staticmethod
    def get_machines(
        db: Session,
        search: str | None = None,
        customer_id: int | None = None,
        product_id: int | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ):
        # Validate pagination.
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        query = db.query(Machine)

        if customer_id is not None:
            query = query.filter(
                Machine.customer_id == customer_id
            )

        if product_id is not None:
            query = query.filter(
                Machine.product_id == product_id
            )

        if status:
            status_value = status.strip().upper()
            if status_value:
                query = query.filter(
                    Machine.status == status_value
                )

        if search and search.strip():
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Machine.machine_number.ilike(pattern),
                    Machine.machine_name.ilike(pattern),
                    Machine.serial_number.ilike(pattern),
                    Machine.asset_tag.ilike(pattern),
                )
            )

        total = query.count()
        skip = (page - 1) * page_size

        machines = (
            query
            .order_by(Machine.id.desc())
            .offset(skip)
            .limit(page_size)
            .all()
        )

        # Return ORM objects so the response schema can serialize
        # audit fields and the new billing fields.
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": machines,
        }

    @staticmethod
    def get_machine(db: Session, machine_id: int):
        machine = MachineRepository.get_by_id(db, machine_id)

        if not machine:
            raise HTTPException(
                status_code=404,
                detail="Machine not found."
            )

        return machine

    @staticmethod
    def update_machine(
        db: Session,
        machine_id: int,
        data: MachineUpdate,
        current_user
    ):
        try:
            machine = MachineRepository.get_by_id(
                db, machine_id
            )

            if not machine:
                raise HTTPException(
                    status_code=404,
                    detail="Machine not found."
                )

            # Validate a new customer if supplied.
            if data.customer_id is not None:
                customer = CustomerRepository.get_by_id(
                    db, data.customer_id
                )
                if not customer:
                    raise HTTPException(
                        status_code=404,
                        detail="Customer not found."
                    )

            # Validate a new product if supplied.
            if data.product_id is not None:
                product = ProductRepository.get_by_id(
                    db, data.product_id
                )
                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail="Product not found."
                    )

            # Validate installer if supplied.
            if data.installed_by is not None:
                installer = UserRepository.get_by_id(
                    db, data.installed_by
                )
                if not installer:
                    raise HTTPException(
                        status_code=404,
                        detail="Installer not found."
                    )

            # Prevent duplicate serial numbers.
            if data.serial_number:
                serial = MachineRepository.get_by_serial_number(
                    db, data.serial_number
                )
                if serial and serial.id != machine.id:
                    raise HTTPException(
                        status_code=400,
                        detail="Serial Number already exists."
                    )

            # Prevent duplicate asset tags.
            if data.asset_tag:
                asset = MachineRepository.get_by_asset_tag(
                    db, data.asset_tag
                )
                if asset and asset.id != machine.id:
                    raise HTTPException(
                        status_code=400,
                        detail="Asset Tag already exists."
                    )

            # Validate warranty dates using supplied values
            # or the machine's existing values.
            warranty_start = (
                data.warranty_start
                if data.warranty_start is not None
                else machine.warranty_start_date
            )
            warranty_end = (
                data.warranty_end
                if data.warranty_end is not None
                else machine.warranty_end_date
            )

            if (
                warranty_start
                and warranty_end
                and warranty_end < warranty_start
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Warranty End must be greater "
                        "than Warranty Start."
                    )
                )

            # Validate AMC dates.
            amc_start = (
                data.amc_start
                if data.amc_start is not None
                else machine.amc_start_date
            )
            amc_end = (
                data.amc_end
                if data.amc_end is not None
                else machine.amc_end_date
            )

            if (
                amc_start
                and amc_end
                and amc_end < amc_start
            ):
                raise HTTPException(
                    status_code=400,
                    detail="AMC End must be greater than AMC Start."
                )

            # Validate legacy overall meter readings.
            opening_meter = (
                data.opening_meter
                if data.opening_meter is not None
                else machine.opening_meter
            )
            current_meter = (
                data.current_meter
                if data.current_meter is not None
                else machine.current_meter
            )

            if current_meter < opening_meter:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Current Meter cannot be less "
                        "than Opening Meter."
                    )
                )

            # Validate each print-type meter reading.
            meter_fields = (
                "a4_bw_current_meter",
                "a4_color_current_meter",
                "a3_bw_current_meter",
                "a3_color_current_meter",
            )
            for field in meter_fields:
                value = getattr(data, field)
                if value is not None and value < 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"{field} cannot be negative."
                    )

            # Map public API date names to actual ORM column names.
            update_data = data.model_dump(exclude_unset=True)
            column_aliases = {
                "warranty_start": "warranty_start_date",
                "warranty_end": "warranty_end_date",
                "amc_start": "amc_start_date",
                "amc_end": "amc_end_date",
            }

            for key, value in update_data.items():
                orm_key = column_aliases.get(key, key)
                setattr(machine, orm_key, value)

            machine.updated_by = current_user.id

            MachineRepository.update(db, machine)
            db.commit()
            db.refresh(machine)
            return machine

        except HTTPException:
            db.rollback()
            raise

        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Machine update failed: {str(exc)}"
            ) from exc

    @staticmethod
    def delete_machine(db: Session, machine_id: int):
        machine = MachineRepository.get_by_id(db, machine_id)

        if not machine:
            raise HTTPException(
                status_code=404,
                detail="Machine not found."
            )

        # Soft delete to preserve existing ERP records.
        machine.is_active = False
        machine.status = "INACTIVE"

        MachineRepository.update(db, machine)
        db.commit()

        return {
            "success": True,
            "message": "Machine deleted successfully."
        }

    @staticmethod
    def dashboard(db: Session):
        return MachineRepository.dashboard(db)
