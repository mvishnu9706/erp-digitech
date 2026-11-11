from datetime import date

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.service_ticket import ServiceTicket


class ServiceTicketRepository:

    # =====================================================
    # CREATE
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        ticket: ServiceTicket
    ):

        db.add(ticket)

        db.flush()

        db.refresh(ticket)

        return ticket

    # =====================================================
    # GET ALL
    # =====================================================

    @staticmethod
    def get_all(
        db: Session,
        search: str = None,
        customer_id: int = None,
        machine_id: int = None,
        engineer_id: int = None,
        status: str = None,
        priority: str = None,
        ticket_type: str = None,
        skip: int = 0,
        limit: int = 10
    ):

        query = db.query(ServiceTicket)

        # -------------------------------------------------
        # Search
        # -------------------------------------------------

        if search:

            search_value = f"%{search}%"

            query = query.filter(

                or_(

                    ServiceTicket.ticket_number.ilike(
                        search_value
                    ),

                    ServiceTicket.subject.ilike(
                        search_value
                    ),

                    ServiceTicket.complaint.ilike(
                        search_value
                    ),

                    ServiceTicket.serial_number.ilike(
                        search_value
                    )

                )

            )

        # -------------------------------------------------
        # Customer
        # -------------------------------------------------

        if customer_id is not None:

            query = query.filter(
                ServiceTicket.customer_id == customer_id
            )

        # -------------------------------------------------
        # Machine
        # -------------------------------------------------

        if machine_id is not None:

            query = query.filter(
                ServiceTicket.machine_id == machine_id
            )

        # -------------------------------------------------
        # Engineer
        # IMPORTANT:
        # Current model uses assigned_engineer_id
        # -------------------------------------------------

        if engineer_id is not None:

            query = query.filter(
                ServiceTicket.assigned_engineer_id
                == engineer_id
            )

        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        if status:

            query = query.filter(
                ServiceTicket.status == status
            )

        # -------------------------------------------------
        # Priority
        # -------------------------------------------------

        if priority:

            query = query.filter(
                ServiceTicket.priority == priority
            )

        # -------------------------------------------------
        # Ticket Type
        # -------------------------------------------------

        if ticket_type:

            query = query.filter(
                ServiceTicket.ticket_type == ticket_type
            )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        return (

            query

            .order_by(
                ServiceTicket.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # COUNT
    # =====================================================

    @staticmethod
    def count(
        db: Session,
        search: str = None,
        customer_id: int = None,
        machine_id: int = None,
        engineer_id: int = None,
        status: str = None,
        priority: str = None,
        ticket_type: str = None
    ):

        query = db.query(ServiceTicket)

        # -------------------------------------------------
        # Search
        # -------------------------------------------------

        if search:

            search_value = f"%{search}%"

            query = query.filter(

                or_(

                    ServiceTicket.ticket_number.ilike(
                        search_value
                    ),

                    ServiceTicket.subject.ilike(
                        search_value
                    ),

                    ServiceTicket.complaint.ilike(
                        search_value
                    ),

                    ServiceTicket.serial_number.ilike(
                        search_value
                    )

                )

            )

        # -------------------------------------------------
        # Customer
        # -------------------------------------------------

        if customer_id is not None:

            query = query.filter(
                ServiceTicket.customer_id == customer_id
            )

        # -------------------------------------------------
        # Machine
        # -------------------------------------------------

        if machine_id is not None:

            query = query.filter(
                ServiceTicket.machine_id == machine_id
            )

        # -------------------------------------------------
        # Engineer
        # -------------------------------------------------

        if engineer_id is not None:

            query = query.filter(
                ServiceTicket.assigned_engineer_id
                == engineer_id
            )

        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        if status:

            query = query.filter(
                ServiceTicket.status == status
            )

        # -------------------------------------------------
        # Priority
        # -------------------------------------------------

        if priority:

            query = query.filter(
                ServiceTicket.priority == priority
            )

        # -------------------------------------------------
        # Ticket Type
        # -------------------------------------------------

        if ticket_type:

            query = query.filter(
                ServiceTicket.ticket_type == ticket_type
            )

        return query.count()

    # =====================================================
    # GET BY ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        ticket_id: int
    ):

        return (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.id == ticket_id
            )

            .first()

        )

    # =====================================================
    # GET BY ID FOR CUSTOMER
    #
    # IMPORTANT:
    #
    # Customer can only access their own ticket.
    #
    # =====================================================

    @staticmethod
    def get_customer_ticket(
        db: Session,
        ticket_id: int,
        customer_id: int
    ):

        return (

            db.query(ServiceTicket)

            .filter(

                ServiceTicket.id == ticket_id,

                ServiceTicket.customer_id == customer_id

            )

            .first()

        )

    # =====================================================
    # GET BY TICKET NUMBER
    # =====================================================

    @staticmethod
    def get_by_ticket_number(
        db: Session,
        ticket_number: str
    ):

        return (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.ticket_number
                == ticket_number
            )

            .first()

        )

    # =====================================================
    # GET BY MACHINE
    # =====================================================

    @staticmethod
    def get_by_machine(
        db: Session,
        machine_id: int
    ):

        return (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.machine_id
                == machine_id
            )

            .order_by(
                ServiceTicket.id.desc()
            )

            .all()

        )

    # =====================================================
    # GET BY CUSTOMER
    # =====================================================

    @staticmethod
    def get_by_customer(
        db: Session,
        customer_id: int
    ):

        return (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.customer_id
                == customer_id
            )

            .order_by(
                ServiceTicket.id.desc()
            )

            .all()

        )

    # =====================================================
    # GET CUSTOMER TICKETS PAGINATED
    # =====================================================

    @staticmethod
    def get_customer_tickets(
        db: Session,
        customer_id: int,
        skip: int = 0,
        limit: int = 100
    ):

        return (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.customer_id
                == customer_id
            )

            .order_by(
                ServiceTicket.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # COUNT CUSTOMER TICKETS
    # =====================================================

    @staticmethod
    def count_customer_tickets(
        db: Session,
        customer_id: int
    ):

        return (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.customer_id
                == customer_id
            )

            .count()

        )

    # =====================================================
    # GET BY ENGINEER
    # =====================================================

    @staticmethod
    def get_by_engineer(
        db: Session,
        engineer_id: int
    ):

        return (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.assigned_engineer_id
                == engineer_id
            )

            .order_by(
                ServiceTicket.id.desc()
            )

            .all()

        )

    # =====================================================
    # GET ENGINEER TICKETS PAGINATED
    # =====================================================

    @staticmethod
    def get_engineer_tickets(
        db: Session,
        engineer_id: int,
        skip: int = 0,
        limit: int = 100
    ):

        return (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.assigned_engineer_id
                == engineer_id
            )

            .order_by(
                ServiceTicket.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # LAST TICKET
    # =====================================================

    @staticmethod
    def last_ticket(
        db: Session
    ):

        return (

            db.query(ServiceTicket)

            .order_by(
                ServiceTicket.id.desc()
            )

            .first()

        )

    # =====================================================
    # UPDATE
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        ticket: ServiceTicket
    ):

        db.commit()

        db.refresh(ticket)

        return ticket

    # =====================================================
    # DELETE
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        ticket: ServiceTicket
    ):

        db.delete(ticket)

        db.commit()

        return True

    # =====================================================
    # DASHBOARD
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        today = date.today()

        # -------------------------------------------------
        # REQUESTED
        # -------------------------------------------------

        requested_count = (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.status
                == "REQUESTED"
            )

            .count()

        )

        # -------------------------------------------------
        # ASSIGNED
        # -------------------------------------------------

        assigned_count = (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.status
                == "ASSIGNED"
            )

            .count()

        )

        # -------------------------------------------------
        # IN PROGRESS
        # -------------------------------------------------

        in_progress_count = (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.status
                == "IN_PROGRESS"
            )

            .count()

        )

        # -------------------------------------------------
        # COMPLETED
        # -------------------------------------------------

        completed_count = (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.status
                == "COMPLETED"
            )

            .count()

        )

        # -------------------------------------------------
        # CLOSED
        # -------------------------------------------------

        closed_count = (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.status
                == "CLOSED"
            )

            .count()

        )

        # -------------------------------------------------
        # CANCELLED
        # -------------------------------------------------

        cancelled_count = (

            db.query(ServiceTicket)

            .filter(
                ServiceTicket.status
                == "CANCELLED"
            )

            .count()

        )

        # -------------------------------------------------
        # OVERDUE
        #
        # Current model uses expected_visit_date.
        #
        # -------------------------------------------------

        overdue_count = (

            db.query(ServiceTicket)

            .filter(

                ServiceTicket.expected_visit_date
                < today,

                ServiceTicket.status.notin_(

                    [
                        "COMPLETED",
                        "CLOSED",
                        "CANCELLED"
                    ]

                )

            )

            .count()

        )

        # -------------------------------------------------
        # TOTAL
        # -------------------------------------------------

        total_count = (

            db.query(ServiceTicket)

            .count()

        )

        return {

            "total_tickets": total_count,

            "requested_tickets":
                requested_count,

            "assigned_tickets":
                assigned_count,

            "in_progress_tickets":
                in_progress_count,

            "completed_tickets":
                completed_count,

            "closed_tickets":
                closed_count,

            "cancelled_tickets":
                cancelled_count,

            "overdue_tickets":
                overdue_count

        }