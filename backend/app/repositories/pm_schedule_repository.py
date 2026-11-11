from datetime import date

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.pm_schedule import PMSchedule


class PMScheduleRepository:

    # =====================================================
    # Create
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        pm: PMSchedule
    ):

        db.add(pm)

        return pm

    # =====================================================
    # Get All
    # =====================================================

    @staticmethod
    def get_all(

        db: Session,

        search: str = None,

        customer_id: int = None,

        machine_id: int = None,

        engineer_id: int = None,

        status: str = None,

        skip: int = 0,

        limit: int = 10

    ):

        query = db.query(PMSchedule)

        if search:

            query = query.filter(

                or_(

                    PMSchedule.pm_number.ilike(
                        f"%{search}%"
                    ),

                    PMSchedule.remarks.ilike(
                        f"%{search}%"
                    )

                )

            )

        if customer_id:

            query = query.filter(
                PMSchedule.customer_id == customer_id
            )

        if machine_id:

            query = query.filter(
                PMSchedule.machine_id == machine_id
            )

        if engineer_id:

            query = query.filter(
                PMSchedule.engineer_id == engineer_id
            )

        if status:

            query = query.filter(
                PMSchedule.status == status
            )

        return (

            query

            .order_by(
                PMSchedule.scheduled_date.asc()
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

        engineer_id=None,

        status=None

    ):

        query = db.query(PMSchedule)

        if search:

            query = query.filter(

                or_(

                    PMSchedule.pm_number.ilike(
                        f"%{search}%"
                    ),

                    PMSchedule.remarks.ilike(
                        f"%{search}%"
                    )

                )

            )

        if customer_id:

            query = query.filter(
                PMSchedule.customer_id == customer_id
            )

        if machine_id:

            query = query.filter(
                PMSchedule.machine_id == machine_id
            )

        if engineer_id:

            query = query.filter(
                PMSchedule.engineer_id == engineer_id
            )

        if status:

            query = query.filter(
                PMSchedule.status == status
            )

        return query.count()

    # =====================================================
    # Get By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        pm_id: int
    ):

        return (

            db.query(PMSchedule)

            .filter(
                PMSchedule.id == pm_id
            )

            .first()

        )

    # =====================================================
    # Get By PM Number
    # =====================================================

    @staticmethod
    def get_by_pm_number(
        db: Session,
        pm_number: str
    ):

        return (

            db.query(PMSchedule)

            .filter(
                PMSchedule.pm_number == pm_number
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

            db.query(PMSchedule)

            .filter(
                PMSchedule.machine_id == machine_id
            )

            .order_by(
                PMSchedule.scheduled_date.desc()
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

            db.query(PMSchedule)

            .filter(
                PMSchedule.customer_id == customer_id
            )

            .order_by(
                PMSchedule.scheduled_date.desc()
            )

            .all()

        )

    # =====================================================
    # Get By Engineer
    # =====================================================

    @staticmethod
    def get_by_engineer(
        db: Session,
        engineer_id: int
    ):

        return (

            db.query(PMSchedule)

            .filter(
                PMSchedule.engineer_id == engineer_id
            )

            .order_by(
                PMSchedule.scheduled_date.asc()
            )

            .all()

        )
        # =====================================================
    # Get Due PM
    # =====================================================

    @staticmethod
    def get_due_pm(
        db: Session
    ):

        today = date.today()

        return (

            db.query(PMSchedule)

            .filter(

                PMSchedule.status == "PENDING",

                PMSchedule.scheduled_date <= today

            )

            .order_by(

                PMSchedule.scheduled_date.asc()

            )

            .all()

        )

    # =====================================================
    # Last PM
    # =====================================================

    @staticmethod
    def last_pm(
        db: Session
    ):

        return (

            db.query(PMSchedule)

            .order_by(

                PMSchedule.id.desc()

            )

            .first()

        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        pm: PMSchedule
    ):

        db.commit()

        db.refresh(pm)

        return pm

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        pm: PMSchedule
    ):

        db.delete(pm)

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

        total_pm = db.query(
            PMSchedule
        ).count()

        pending_pm = db.query(
            PMSchedule
        ).filter(
            PMSchedule.status == "PENDING"
        ).count()

        completed_pm = db.query(
            PMSchedule
        ).filter(
            PMSchedule.status == "COMPLETED"
        ).count()

        overdue_pm = db.query(
            PMSchedule
        ).filter(

            PMSchedule.status == "PENDING",

            PMSchedule.scheduled_date < today

        ).count()

        today_pm = db.query(
            PMSchedule
        ).filter(

            PMSchedule.scheduled_date == today

        ).count()

        return {

            "total_pm": total_pm,

            "pending_pm": pending_pm,

            "completed_pm": completed_pm,

            "overdue_pm": overdue_pm,

            "today_pm": today_pm

        }