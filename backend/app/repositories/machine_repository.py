from datetime import date, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.machine import Machine


class MachineRepository:

    # =====================================================
    # Create
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        machine: Machine
    ):
        db.add(machine)

        return machine

    # =====================================================
    # Get All
    # =====================================================

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 20
    ):
        return (
            db.query(Machine)
            .order_by(
                Machine.id.desc()
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
        db: Session
    ):
        return db.query(Machine).count()

    # =====================================================
    # Get By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        machine_id: int
    ):
        return (
            db.query(Machine)
            .filter(
                Machine.id == machine_id
            )
            .first()
        )

    # =====================================================
    # Get By Machine Number
    # =====================================================

    @staticmethod
    def get_by_machine_number(
        db: Session,
        machine_number: str
    ):
        return (
            db.query(Machine)
            .filter(
                Machine.machine_number == machine_number
            )
            .first()
        )

    # =====================================================
    # Get By Serial Number
    # =====================================================

    @staticmethod
    def get_by_serial_number(
        db: Session,
        serial_number: str
    ):
        return (
            db.query(Machine)
            .filter(
                Machine.serial_number == serial_number
            )
            .first()
        )

    # =====================================================
    # Get By Machine Name
    # =====================================================

    @staticmethod
    def get_by_machine_name(
        db: Session,
        machine_name: str
    ):
        return (
            db.query(Machine)
            .filter(
                Machine.machine_name == machine_name
            )
            .first()
        )

    # =====================================================
    # Search
    # =====================================================

    @staticmethod
    def search(
        db: Session,
        keyword: str
    ):
        search_keyword = f"%{keyword}%"

        return (
            db.query(Machine)
            .filter(
                or_(
                    Machine.machine_number.ilike(
                        search_keyword
                    ),
                    Machine.machine_name.ilike(
                        search_keyword
                    ),
                    Machine.serial_number.ilike(
                        search_keyword
                    ),
                    Machine.asset_tag.ilike(
                        search_keyword
                    )
                )
            )
            .all()
        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        machine: Machine
    ):
        db.commit()

        db.refresh(machine)

        return machine

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        machine: Machine
    ):
        db.delete(machine)

        db.commit()

        return True

    # =====================================================
    # Last Machine
    # =====================================================

    @staticmethod
    def last_machine(
        db: Session
    ):
        return (
            db.query(Machine)
            .order_by(
                Machine.id.desc()
            )
            .first()
        )

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):
        today = date.today()

        next_month = today + timedelta(days=30)

        return {
            "total_machines":
                db.query(Machine).count(),

            "active_machines":
                db.query(Machine)
                .filter(
                    Machine.status == "ACTIVE"
                )
                .count(),

            "warranty_expiring":
                db.query(Machine)
                .filter(
                    Machine.warranty_end >= today,
                    Machine.warranty_end <= next_month
                )
                .count(),

            "amc_expiring":
                db.query(Machine)
                .filter(
                    Machine.amc_end >= today,
                    Machine.amc_end <= next_month
                )
                .count(),

            "rental_machines":
                db.query(Machine)
                .filter(
                    Machine.rental_rate > 0
                )
                .count()
        }

    # =====================================================
    # Warranty Expiring
    # =====================================================

    @staticmethod
    def warranty_expiring(
        db: Session
    ):
        today = date.today()

        next_month = today + timedelta(days=30)

        return (
            db.query(Machine)
            .filter(
                Machine.warranty_end >= today,
                Machine.warranty_end <= next_month
            )
            .all()
        )

    # =====================================================
    # AMC Expiring
    # =====================================================

    @staticmethod
    def amc_expiring(
        db: Session
    ):
        today = date.today()

        next_month = today + timedelta(days=30)

        return (
            db.query(Machine)
            .filter(
                Machine.amc_end >= today,
                Machine.amc_end <= next_month
            )
            .all()
        )

    # =====================================================
    # CUSTOMER PORTAL
    # =====================================================
    #
    # These methods are ONLY for the customer portal.
    #
    # IMPORTANT:
    #
    # We NEVER accept customer_id from the frontend.
    #
    # customer_id must come from the authenticated
    # customer's User record.
    #
    # Example:
    #
    # current_user.customer_id = 4
    #
    # Then:
    #
    # Machine.customer_id == 4
    #
    # Only those machines are returned.
    #
    # =====================================================

    # =====================================================
    # Get Customer Machines
    # =====================================================

    @staticmethod
    def get_by_customer_id(
        db: Session,
        customer_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        return (
            db.query(Machine)
            .filter(
                Machine.customer_id == customer_id,
                Machine.is_active == True
            )
            .order_by(
                Machine.id.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    # =====================================================
    # Count Customer Machines
    # =====================================================

    @staticmethod
    def count_by_customer_id(
        db: Session,
        customer_id: int
    ):
        return (
            db.query(Machine)
            .filter(
                Machine.customer_id == customer_id,
                Machine.is_active == True
            )
            .count()
        )

    # =====================================================
    # Get One Customer Machine
    # =====================================================
    #
    # SECURITY IMPORTANT:
    #
    # We check BOTH:
    #
    # machine.id
    #
    # AND
    #
    # machine.customer_id
    #
    # Therefore:
    #
    # /customer/machines/10
    #
    # cannot return machine 10 if it belongs to
    # another customer.
    #
    # =====================================================

    @staticmethod
    def get_customer_machine_by_id(
        db: Session,
        machine_id: int,
        customer_id: int
    ):
        return (
            db.query(Machine)
            .filter(
                Machine.id == machine_id,
                Machine.customer_id == customer_id,
                Machine.is_active == True
            )
            .first()
        )

    # =====================================================
    # Search Customer Machines
    # =====================================================
    #
    # Customer can search only inside their own machines.
    #
    # =====================================================

    @staticmethod
    def search_customer_machines(
        db: Session,
        customer_id: int,
        keyword: str,
        skip: int = 0,
        limit: int = 100
    ):
        search_keyword = f"%{keyword}%"

        return (
            db.query(Machine)
            .filter(
                Machine.customer_id == customer_id,
                Machine.is_active == True,
                or_(
                    Machine.machine_number.ilike(
                        search_keyword
                    ),
                    Machine.machine_name.ilike(
                        search_keyword
                    ),
                    Machine.serial_number.ilike(
                        search_keyword
                    ),
                    Machine.asset_tag.ilike(
                        search_keyword
                    )
                )
            )
            .order_by(
                Machine.id.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    # =====================================================
    # Customer Machine Dashboard
    # =====================================================
    #
    # Used later by the Customer Portal dashboard.
    #
    # =====================================================

    @staticmethod
    def customer_dashboard(
        db: Session,
        customer_id: int
    ):
        today = date.today()

        next_month = today + timedelta(days=30)

        total_machines = (
            db.query(Machine)
            .filter(
                Machine.customer_id == customer_id,
                Machine.is_active == True
            )
            .count()
        )

        active_machines = (
            db.query(Machine)
            .filter(
                Machine.customer_id == customer_id,
                Machine.is_active == True,
                Machine.status == "ACTIVE"
            )
            .count()
        )

        warranty_expiring = (
            db.query(Machine)
            .filter(
                Machine.customer_id == customer_id,
                Machine.is_active == True,
                Machine.warranty_end >= today,
                Machine.warranty_end <= next_month
            )
            .count()
        )

        amc_expiring = (
            db.query(Machine)
            .filter(
                Machine.customer_id == customer_id,
                Machine.is_active == True,
                Machine.amc_end >= today,
                Machine.amc_end <= next_month
            )
            .count()
        )

        return {
            "total_machines": total_machines,
            "active_machines": active_machines,
            "warranty_expiring": warranty_expiring,
            "amc_expiring": amc_expiring
        }