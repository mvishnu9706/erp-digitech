from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.pm_schedule import PMSchedule

from app.repositories.pm_schedule_repository import (
    PMScheduleRepository
)

from app.repositories.amc_contract_repository import (
    AMCContractRepository
)

from app.repositories.customer_repository import (
    CustomerRepository
)

from app.repositories.machine_repository import (
    MachineRepository
)

from app.repositories.user_repository import (
    UserRepository
)

from app.schemas.pm_schedule import (
    PMScheduleCreate,
    PMScheduleUpdate
)

from app.utils.pm_number import (
    PMNumberGenerator
)


class PMScheduleService:

    # =====================================================
    # Create PM
    # =====================================================

    @staticmethod
    def create_pm(
        db: Session,
        data: PMScheduleCreate,
        current_user
    ):

        try:

            # ==========================================
            # Validate AMC Contract
            # ==========================================

            contract = AMCContractRepository.get_by_id(
                db,
                data.amc_contract_id
            )

            if not contract:

                raise HTTPException(
                    status_code=404,
                    detail="AMC Contract not found."
                )

            # ==========================================
            # Validate Customer
            # ==========================================

            customer = CustomerRepository.get_by_id(
                db,
                data.customer_id
            )

            if not customer:

                raise HTTPException(
                    status_code=404,
                    detail="Customer not found."
                )

            # ==========================================
            # Validate Machine
            # ==========================================

            machine = MachineRepository.get_by_id(
                db,
                data.machine_id
            )

            if not machine:

                raise HTTPException(
                    status_code=404,
                    detail="Machine not found."
                )

            # ==========================================
            # Validate Engineer
            # ==========================================

            if data.engineer_id:

                engineer = UserRepository.get_by_id(
                    db,
                    data.engineer_id
                )

                if not engineer:

                    raise HTTPException(
                        status_code=404,
                        detail="Engineer not found."
                    )

            # ==========================================
            # Date Validation
            # ==========================================

            if data.scheduled_date < contract.start_date:

                raise HTTPException(
                    status_code=400,
                    detail="PM date cannot be before AMC start date."
                )

            if data.scheduled_date > contract.end_date:

                raise HTTPException(
                    status_code=400,
                    detail="PM date cannot exceed AMC expiry."
                )

            # ==========================================
            # Generate PM Number
            # ==========================================

            last_pm = PMScheduleRepository.last_pm(db)

            if last_pm:

                pm_number = PMNumberGenerator.generate(
                    last_pm.id + 1
                )

            else:

                pm_number = PMNumberGenerator.generate(1)

            # ==========================================
            # Create PM Schedule
            # ==========================================

            pm = PMSchedule(

                pm_number=pm_number,

                amc_contract_id=data.amc_contract_id,

                customer_id=data.customer_id,

                machine_id=data.machine_id,

                engineer_id=data.engineer_id,

                scheduled_date=data.scheduled_date,

                completed_date=data.completed_date,

                frequency_days=data.frequency_days,

                status=data.status,

                auto_generated=data.auto_generated,

                remarks=data.remarks,

                created_by=current_user.id,

                updated_by=current_user.id

            )

            pm = PMScheduleRepository.create(
                db,
                pm
            )

            db.commit()

            db.refresh(pm)

            return pm

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"PM Schedule creation failed: {str(e)}"
            )
            # =====================================================
    # Get PM Schedules
    # =====================================================

    @staticmethod
    def get_pms(

        db: Session,

        search: str = None,

        customer_id: int = None,

        machine_id: int = None,

        engineer_id: int = None,

        status: str = None,

        page: int = 1,

        page_size: int = 10

    ):

        skip = (page - 1) * page_size

        pms = PMScheduleRepository.get_all(

            db=db,

            search=search,

            customer_id=customer_id,

            machine_id=machine_id,

            engineer_id=engineer_id,

            status=status,

            skip=skip,

            limit=page_size

        )

        total = PMScheduleRepository.count(

            db=db,

            search=search,

            customer_id=customer_id,

            machine_id=machine_id,

            engineer_id=engineer_id,

            status=status

        )

        return {

            "total": total,

            "page": page,

            "page_size": page_size,

            "items": pms

        }

    # =====================================================
    # Get PM
    # =====================================================

    @staticmethod
    def get_pm(

        db: Session,

        pm_id: int

    ):

        pm = PMScheduleRepository.get_by_id(

            db,

            pm_id

        )

        if not pm:

            raise HTTPException(

                status_code=404,

                detail="PM Schedule not found."

            )

        return pm

    # =====================================================
    # Update PM
    # =====================================================

    @staticmethod
    def update_pm(

        db: Session,

        pm_id: int,

        data: PMScheduleUpdate,

        current_user

    ):

        try:

            pm = PMScheduleRepository.get_by_id(

                db,

                pm_id

            )

            if not pm:

                raise HTTPException(

                    status_code=404,

                    detail="PM Schedule not found."

                )

            update_data = data.model_dump(

                exclude_unset=True

            )

            for key, value in update_data.items():

                setattr(

                    pm,

                    key,

                    value

                )

            pm.updated_by = current_user.id

            PMScheduleRepository.update(

                db,

                pm

            )

            return pm

        except HTTPException:

            raise

        except Exception as e:

            raise HTTPException(

                status_code=500,

                detail=str(e)

            )

    # =====================================================
    # Delete PM
    # =====================================================

    @staticmethod
    def delete_pm(

        db: Session,

        pm_id: int

    ):

        pm = PMScheduleRepository.get_by_id(

            db,

            pm_id

        )

        if not pm:

            raise HTTPException(

                status_code=404,

                detail="PM Schedule not found."

            )

        PMScheduleRepository.delete(

            db,

            pm

        )

        return {

            "success": True,

            "message": "PM Schedule deleted successfully."

        }

    # =====================================================
    # Complete PM
    # =====================================================

    @staticmethod
    def complete_pm(

        db: Session,

        pm_id: int,

        current_user

    ):

        pm = PMScheduleRepository.get_by_id(

            db,

            pm_id

        )

        if not pm:

            raise HTTPException(

                status_code=404,

                detail="PM Schedule not found."

            )

        pm.status = "COMPLETED"

        pm.completed_date = date.today()

        pm.updated_by = current_user.id

        contract = AMCContractRepository.get_by_id(

            db,

            pm.amc_contract_id

        )

        if contract:

            contract.used_service_visits += 1

        PMScheduleRepository.update(

            db,

            pm

        )

        PMScheduleService.generate_next_pm(

            db,

            pm,

            current_user

        )

        return pm

    # =====================================================
    # Generate Next PM
    # =====================================================

    @staticmethod
    def generate_next_pm(

        db: Session,

        current_pm: PMSchedule,

        current_user

    ):

        contract = AMCContractRepository.get_by_id(

            db,

            current_pm.amc_contract_id

        )

        if not contract:

            return

        next_date = current_pm.scheduled_date + timedelta(

            days=current_pm.frequency_days

        )

        if next_date > contract.end_date:

            return

        last_pm = PMScheduleRepository.last_pm(db)

        pm_number = PMNumberGenerator.generate(

            (last_pm.id + 1) if last_pm else 1

        )

        next_pm = PMSchedule(

            pm_number=pm_number,

            amc_contract_id=current_pm.amc_contract_id,

            customer_id=current_pm.customer_id,

            machine_id=current_pm.machine_id,

            engineer_id=current_pm.engineer_id,

            scheduled_date=next_date,

            frequency_days=current_pm.frequency_days,

            status="PENDING",

            auto_generated=True,

            created_by=current_user.id,

            updated_by=current_user.id

        )

        PMScheduleRepository.create(

            db,

            next_pm

        )

        db.commit()

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(

        db: Session

    ):

        return PMScheduleRepository.dashboard(db)