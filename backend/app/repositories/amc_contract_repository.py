from datetime import date

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.amc_contract import AMCContract


class AMCContractRepository:

    # =====================================================
    # Create
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        contract: AMCContract
    ):

        db.add(contract)

        return contract

    # =====================================================
    # Get All
    # =====================================================

    @staticmethod
    def get_all(

        db: Session,

        search: str = None,

        customer_id: int = None,

        machine_id: int = None,

        contract_type: str = None,

        status: str = None,

        skip: int = 0,

        limit: int = 10

    ):

        query = db.query(AMCContract)

        if search:

            query = query.filter(

                or_(

                    AMCContract.contract_number.ilike(
                        f"%{search}%"
                    ),

                    AMCContract.remarks.ilike(
                        f"%{search}%"
                    )

                )

            )

        if customer_id:

            query = query.filter(
                AMCContract.customer_id == customer_id
            )

        if machine_id:

            query = query.filter(
                AMCContract.machine_id == machine_id
            )

        if contract_type:

            query = query.filter(
                AMCContract.contract_type == contract_type
            )

        if status:

            query = query.filter(
                AMCContract.status == status
            )

        return (

            query

            .order_by(
                AMCContract.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # Count
    # =====================================================

    @staticmethod
    def count(

        db: Session,

        search=None,

        customer_id=None,

        machine_id=None,

        contract_type=None,

        status=None

    ):

        query = db.query(AMCContract)

        if search:

            query = query.filter(

                or_(

                    AMCContract.contract_number.ilike(
                        f"%{search}%"
                    ),

                    AMCContract.remarks.ilike(
                        f"%{search}%"
                    )

                )

            )

        if customer_id:

            query = query.filter(
                AMCContract.customer_id == customer_id
            )

        if machine_id:

            query = query.filter(
                AMCContract.machine_id == machine_id
            )

        if contract_type:

            query = query.filter(
                AMCContract.contract_type == contract_type
            )

        if status:

            query = query.filter(
                AMCContract.status == status
            )

        return query.count()

    # =====================================================
    # Get By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        contract_id: int
    ):

        return (

            db.query(AMCContract)

            .filter(
                AMCContract.id == contract_id
            )

            .first()

        )

    # =====================================================
    # Get By Contract Number
    # =====================================================

    @staticmethod
    def get_by_contract_number(
        db: Session,
        contract_number: str
    ):

        return (

            db.query(AMCContract)

            .filter(
                AMCContract.contract_number == contract_number
            )

            .first()

        )

    # =====================================================
    # Get By Machine
    # =====================================================

    @staticmethod
    def get_by_machine(
        db: Session,
        machine_id: int
    ):

        return (

            db.query(AMCContract)

            .filter(
                AMCContract.machine_id == machine_id
            )

            .order_by(
                AMCContract.id.desc()
            )

            .all()

        )

    # =====================================================
    # Get By Customer
    # =====================================================

    @staticmethod
    def get_by_customer(
        db: Session,
        customer_id: int
    ):

        return (

            db.query(AMCContract)

            .filter(
                AMCContract.customer_id == customer_id
            )

            .order_by(
                AMCContract.id.desc()
            )

            .all()

        )
        # =====================================================
    # Get Active Contract
    # =====================================================

    @staticmethod
    def get_active_contract(
        db: Session,
        machine_id: int
    ):

        today = date.today()

        return (

            db.query(AMCContract)

            .filter(

                AMCContract.machine_id == machine_id,

                AMCContract.status == "ACTIVE",

                AMCContract.start_date <= today,

                AMCContract.end_date >= today

            )

            .first()

        )

    # =====================================================
    # Last Contract
    # =====================================================

    @staticmethod
    def last_contract(
        db: Session
    ):

        return (

            db.query(AMCContract)

            .order_by(
                AMCContract.id.desc()
            )

            .first()

        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        contract: AMCContract
    ):

        db.commit()

        db.refresh(contract)

        return contract

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        contract: AMCContract
    ):

        db.delete(contract)

        db.commit()

        return True

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        today = date.today()

        total_contracts = db.query(
            AMCContract
        ).count()

        active_contracts = db.query(
            AMCContract
        ).filter(
            AMCContract.status == "ACTIVE"
        ).count()

        expired_contracts = db.query(
            AMCContract
        ).filter(
            AMCContract.end_date < today
        ).count()

        expiring_this_month = db.query(
            AMCContract
        ).filter(

            func.extract(
                "month",
                AMCContract.end_date
            ) == today.month,

            func.extract(
                "year",
                AMCContract.end_date
            ) == today.year

        ).count()

        renewal_due = db.query(
            AMCContract
        ).filter(

            AMCContract.end_date >= today,

            AMCContract.end_date <= func.current_date() + 30

        ).count()

        return {

            "total_contracts": total_contracts,

            "active_contracts": active_contracts,

            "expired_contracts": expired_contracts,

            "expiring_this_month": expiring_this_month,

            "renewal_due": renewal_due

        }