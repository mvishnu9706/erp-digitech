from datetime import date

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.service_visit import ServiceVisit


class ServiceVisitRepository:

    # =====================================================
    # Create
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        visit: ServiceVisit
    ):

        db.add(visit)

        return visit

    # =====================================================
    # Get All
    # =====================================================

    @staticmethod
    def get_all(

        db: Session,

        search: str = None,

        ticket_id: int = None,

        machine_id: int = None,

        customer_id: int = None,

        engineer_id: int = None,

        status: str = None,

        skip: int = 0,

        limit: int = 10

    ):

        query = db.query(ServiceVisit)

        if search:

            query = query.filter(

                or_(

                    ServiceVisit.visit_number.ilike(
                        f"%{search}%"
                    ),

                    ServiceVisit.work_done.ilike(
                        f"%{search}%"
                    ),

                    ServiceVisit.problem_found.ilike(
                        f"%{search}%"
                    )

                )

            )

        if ticket_id:

            query = query.filter(
                ServiceVisit.ticket_id == ticket_id
            )

        if machine_id:

            query = query.filter(
                ServiceVisit.machine_id == machine_id
            )

        if customer_id:

            query = query.filter(
                ServiceVisit.customer_id == customer_id
            )

        if engineer_id:

            query = query.filter(
                ServiceVisit.engineer_id == engineer_id
            )

        if status:

            query = query.filter(
                ServiceVisit.status == status
            )

        return (

            query

            .order_by(
                ServiceVisit.id.desc()
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

        ticket_id=None,

        machine_id=None,

        customer_id=None,

        engineer_id=None,

        status=None

    ):

        query = db.query(ServiceVisit)

        if search:

            query = query.filter(

                or_(

                    ServiceVisit.visit_number.ilike(
                        f"%{search}%"
                    ),

                    ServiceVisit.work_done.ilike(
                        f"%{search}%"
                    ),

                    ServiceVisit.problem_found.ilike(
                        f"%{search}%"
                    )

                )

            )

        if ticket_id:

            query = query.filter(
                ServiceVisit.ticket_id == ticket_id
            )

        if machine_id:

            query = query.filter(
                ServiceVisit.machine_id == machine_id
            )

        if customer_id:

            query = query.filter(
                ServiceVisit.customer_id == customer_id
            )

        if engineer_id:

            query = query.filter(
                ServiceVisit.engineer_id == engineer_id
            )

        if status:

            query = query.filter(
                ServiceVisit.status == status
            )

        return query.count()

    # =====================================================
    # Get By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        visit_id: int
    ):

        return (

            db.query(ServiceVisit)

            .filter(
                ServiceVisit.id == visit_id
            )

            .first()

        )

    # =====================================================
    # Get By Visit Number
    # =====================================================

    @staticmethod
    def get_by_visit_number(
        db: Session,
        visit_number: str
    ):

        return (

            db.query(ServiceVisit)

            .filter(
                ServiceVisit.visit_number == visit_number
            )

            .first()

        )
        # =====================================================
    # Get By Ticket
    # =====================================================

    @staticmethod
    def get_by_ticket(
        db: Session,
        ticket_id: int
    ):

        return (

            db.query(ServiceVisit)

            .filter(
                ServiceVisit.ticket_id == ticket_id
            )

            .order_by(
                ServiceVisit.id.desc()
            )

            .all()

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

            db.query(ServiceVisit)

            .filter(
                ServiceVisit.machine_id == machine_id
            )

            .order_by(
                ServiceVisit.id.desc()
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

            db.query(ServiceVisit)

            .filter(
                ServiceVisit.customer_id == customer_id
            )

            .order_by(
                ServiceVisit.id.desc()
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

            db.query(ServiceVisit)

            .filter(
                ServiceVisit.engineer_id == engineer_id
            )

            .order_by(
                ServiceVisit.id.desc()
            )

            .all()

        )

    # =====================================================
    # Last Visit
    # =====================================================

    @staticmethod
    def last_visit(
        db: Session
    ):

        return (

            db.query(ServiceVisit)

            .order_by(
                ServiceVisit.id.desc()
            )

            .first()

        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        visit: ServiceVisit
    ):

        db.commit()

        db.refresh(visit)

        return visit

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        visit: ServiceVisit
    ):

        db.delete(visit)

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

        return {

            "total_visits":

                db.query(
                    ServiceVisit
                ).count(),

            "open_visits":

                db.query(
                    ServiceVisit
                )

                .filter(
                    ServiceVisit.status == "OPEN"
                )

                .count(),

            "completed_visits":

                db.query(
                    ServiceVisit
                )

                .filter(
                    ServiceVisit.status == "COMPLETED"
                )

                .count(),

            "cancelled_visits":

                db.query(
                    ServiceVisit
                )

                .filter(
                    ServiceVisit.status == "CANCELLED"
                )

                .count(),

            "today_visits":

                db.query(
                    ServiceVisit
                )

                .filter(
                    ServiceVisit.visit_date == today
                )

                .count(),

            "pending_visits":

                db.query(
                    ServiceVisit
                )

                .filter(
                    ServiceVisit.status.in_(
                        [
                            "OPEN",
                            "IN_PROGRESS"
                        ]
                    )
                )

                .count()

        }