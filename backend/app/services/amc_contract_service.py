from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.amc_contract import AMCContract

from app.repositories.amc_contract_repository import (
    AMCContractRepository
)

from app.repositories.customer_repository import (
    CustomerRepository
)

from app.repositories.machine_repository import (
    MachineRepository
)

from app.schemas.amc_contract import (
    AMCContractCreate,
    AMCContractUpdate
)

from app.utils.amc_contract_number import (
    AMCContractNumberGenerator
)


class AMCContractService:

    # =====================================================
    # Create Contract
    # =====================================================

    @staticmethod
    def create_contract(
        db: Session,
        data: AMCContractCreate,
        current_user
    ):

        try:

            # ==========================================
            # Customer Validation
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
            # Machine Validation
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
            # Duplicate Active Contract
            # ==========================================

            active_contract = AMCContractRepository.get_active_contract(
                db,
                data.machine_id
            )

            if active_contract:

                raise HTTPException(
                    status_code=400,
                    detail="An active AMC contract already exists."
                )

            # ==========================================
            # Date Validation
            # ==========================================

            if data.end_date <= data.start_date:

                raise HTTPException(
                    status_code=400,
                    detail="End date must be after start date."
                )

            # ==========================================
            # Generate Contract Number
            # ==========================================

            last_contract = AMCContractRepository.last_contract(db)

            if last_contract:

                contract_number = AMCContractNumberGenerator.generate(
                    last_contract.id + 1
                )

            else:

                contract_number = AMCContractNumberGenerator.generate(1)

            # ==========================================
            # Create Contract
            # ==========================================

            contract = AMCContract(

                contract_number=contract_number,

                customer_id=data.customer_id,

                machine_id=data.machine_id,

                contract_type=data.contract_type,

                start_date=data.start_date,

                end_date=data.end_date,

                amount=data.amount,

                gst_percentage=data.gst_percentage,

                free_black_copies=data.free_black_copies,

                free_color_copies=data.free_color_copies,

                black_cost_per_copy=data.black_cost_per_copy,

                color_cost_per_copy=data.color_cost_per_copy,

                included_service_visits=data.included_service_visits,

                used_service_visits=data.used_service_visits,

                auto_renew=data.auto_renew,

                renewal_reminder_days=data.renewal_reminder_days,

                status=data.status,

                remarks=data.remarks,

                created_by=current_user.id,

                updated_by=current_user.id

            )

            contract = AMCContractRepository.create(
                db,
                contract
            )

            db.commit()

            db.refresh(contract)

            return contract

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AMC Contract creation failed: {str(e)}"
            )
            # =====================================================
    # Get Contracts
    # =====================================================

    @staticmethod
    def get_contracts(

        db: Session,

        search: str = None,

        customer_id: int = None,

        machine_id: int = None,

        contract_type: str = None,

        status: str = None,

        page: int = 1,

        page_size: int = 10

    ):

        skip = (page - 1) * page_size

        contracts = AMCContractRepository.get_all(

            db=db,

            search=search,

            customer_id=customer_id,

            machine_id=machine_id,

            contract_type=contract_type,

            status=status,

            skip=skip,

            limit=page_size

        )

        total = AMCContractRepository.count(

            db=db,

            search=search,

            customer_id=customer_id,

            machine_id=machine_id,

            contract_type=contract_type,

            status=status

        )

        return {

            "total": total,

            "page": page,

            "page_size": page_size,

            "items": contracts

        }

    # =====================================================
    # Get Contract
    # =====================================================

    @staticmethod
    def get_contract(

        db: Session,

        contract_id: int

    ):

        contract = AMCContractRepository.get_by_id(

            db,

            contract_id

        )

        if not contract:

            raise HTTPException(

                status_code=404,

                detail="AMC Contract not found."

            )

        return contract

    # =====================================================
    # Update Contract
    # =====================================================

    @staticmethod
    def update_contract(

        db: Session,

        contract_id: int,

        data: AMCContractUpdate,

        current_user

    ):

        try:

            contract = AMCContractRepository.get_by_id(

                db,

                contract_id

            )

            if not contract:

                raise HTTPException(

                    status_code=404,

                    detail="AMC Contract not found."

                )

            update_data = data.model_dump(

                exclude_unset=True

            )

            for key, value in update_data.items():

                setattr(

                    contract,

                    key,

                    value

                )

            contract.updated_by = current_user.id

            AMCContractRepository.update(

                db,

                contract

            )

            return contract

        except HTTPException:

            raise

        except Exception as e:

            raise HTTPException(

                status_code=500,

                detail=str(e)

            )

    # =====================================================
    # Delete Contract
    # =====================================================

    @staticmethod
    def delete_contract(

        db: Session,

        contract_id: int

    ):

        contract = AMCContractRepository.get_by_id(

            db,

            contract_id

        )

        if not contract:

            raise HTTPException(

                status_code=404,

                detail="AMC Contract not found."

            )

        AMCContractRepository.delete(

            db,

            contract

        )

        return {

            "success": True,

            "message": "AMC Contract deleted successfully."

        }

    # =====================================================
    # Renew Contract
    # =====================================================

    @staticmethod
    def renew_contract(

        db: Session,

        contract_id: int,

        new_end_date: date,

        current_user

    ):

        contract = AMCContractRepository.get_by_id(

            db,

            contract_id

        )

        if not contract:

            raise HTTPException(

                status_code=404,

                detail="AMC Contract not found."

            )

        if new_end_date <= contract.end_date:

            raise HTTPException(

                status_code=400,

                detail="New end date must be greater than current end date."

            )

        contract.end_date = new_end_date

        contract.status = "ACTIVE"

        contract.updated_by = current_user.id

        AMCContractRepository.update(

            db,

            contract

        )

        return contract

    # =====================================================
    # Expire Contract
    # =====================================================

    @staticmethod
    def expire_contract(

        db: Session,

        contract_id: int,

        current_user

    ):

        contract = AMCContractRepository.get_by_id(

            db,

            contract_id

        )

        if not contract:

            raise HTTPException(

                status_code=404,

                detail="AMC Contract not found."

            )

        contract.status = "EXPIRED"

        contract.updated_by = current_user.id

        AMCContractRepository.update(

            db,

            contract

        )

        return contract

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(

        db: Session

    ):

        return AMCContractRepository.dashboard(db)