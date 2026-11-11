from typing import Optional

from sqlalchemy.orm import Session

from app.models.rental_bill import RentalBill


class RentalBillRepository:
    """
    Database operations for RentalBill.

    Handles:
    - Creating rental bills
    - Fetching bills
    - Customer-specific bill queries
    - Machine/month queries
    - Previous bill lookup
    - Searching and pagination
    - Updating bills
    - Counting bills
    - Deleting bills
    """

    # ============================================================
    # CREATE
    # ============================================================

    @staticmethod
    def create(
        db: Session,
        rental_bill: RentalBill,
    ) -> RentalBill:

        db.add(rental_bill)
        # SQLAlchemy tracks changes made to the RentalBill object by the
        # service. Flush first so all changed fields are written before the
        # transaction is committed.
        db.flush()
        db.commit()
        db.refresh(rental_bill)

        return rental_bill

    # ============================================================
    # GET BY ID
    # ============================================================

    @staticmethod
    def get_by_id(
        db: Session,
        bill_id: int,
    ) -> Optional[RentalBill]:

        return (
            db.query(RentalBill)
            .filter(
                RentalBill.id == bill_id
            )
            .first()
        )

    # ============================================================
    # GET BY ID FOR CUSTOMER
    # ============================================================

    @staticmethod
    def get_by_id_for_customer(
        db: Session,
        bill_id: int,
        customer_id: int,
    ) -> Optional[RentalBill]:

        return (
            db.query(RentalBill)
            .filter(
                RentalBill.id == bill_id,
                RentalBill.customer_id == customer_id,
            )
            .first()
        )

    # ============================================================
    # GET BILL FOR MACHINE + MONTH
    # ============================================================

    @staticmethod
    def get_by_machine_and_month(
        db: Session,
        machine_id: int,
        billing_month: str,
    ) -> Optional[RentalBill]:

        return (
            db.query(RentalBill)
            .filter(
                RentalBill.machine_id == machine_id,
                RentalBill.billing_month == billing_month,
            )
            .first()
        )

    # ============================================================
    # GET PREVIOUS BILL FOR MACHINE
    # ============================================================

    @staticmethod
    def get_previous_bill_for_machine(
        db: Session,
        machine_id: int,
        billing_month: str,
    ) -> Optional[RentalBill]:

        return (
            db.query(RentalBill)
            .filter(
                RentalBill.machine_id == machine_id,
                RentalBill.billing_month < billing_month,
                RentalBill.payment_status != "CANCELLED",
            )
            .order_by(
                RentalBill.billing_month.desc(),
                RentalBill.id.desc(),
            )
            .first()
        )

    # ============================================================
    # GET CUSTOMER BILLS
    # ============================================================

    @staticmethod
    def get_customer_bills(
        db: Session,
        customer_id: int,
        machine_id: Optional[int] = None,
        billing_month: Optional[str] = None,
        payment_status: Optional[str] = None,
    ) -> list[RentalBill]:

        query = (
            db.query(RentalBill)
            .filter(
                RentalBill.customer_id == customer_id
            )
        )

        # --------------------------------------------------------
        # Machine filter
        # --------------------------------------------------------

        if machine_id is not None:

            query = query.filter(
                RentalBill.machine_id == machine_id
            )

        # --------------------------------------------------------
        # Billing month filter
        # --------------------------------------------------------

        if billing_month is not None:

            query = query.filter(
                RentalBill.billing_month == billing_month
            )

        # --------------------------------------------------------
        # Payment status filter
        # --------------------------------------------------------

        if payment_status is not None:

            query = query.filter(
                RentalBill.payment_status == payment_status
            )

        return (
            query
            .order_by(
                RentalBill.billing_month.desc(),
                RentalBill.id.desc(),
            )
            .all()
        )

    # ============================================================
    # GET ALL BILLS
    # ============================================================

    @staticmethod
    def get_all(
        db: Session,
        search: Optional[str] = None,
        customer_id: Optional[int] = None,
        machine_id: Optional[int] = None,
        billing_month: Optional[str] = None,
        payment_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[RentalBill]:

        query = db.query(RentalBill)

        # --------------------------------------------------------
        # Search
        #
        # Search supported on fields that belong directly to
        # RentalBill.
        # --------------------------------------------------------

        if search:

            keyword = search.strip()

            if keyword:

                search_filters = []

                if hasattr(RentalBill, "bill_number"):
                    search_filters.append(
                        RentalBill.bill_number.ilike(
                            f"%{keyword}%"
                        )
                    )

                if hasattr(RentalBill, "billing_month"):
                    search_filters.append(
                        RentalBill.billing_month.ilike(
                            f"%{keyword}%"
                        )
                    )

                if hasattr(RentalBill, "remarks"):
                    search_filters.append(
                        RentalBill.remarks.ilike(
                            f"%{keyword}%"
                        )
                    )

                if search_filters:

                    from sqlalchemy import or_

                    query = query.filter(
                        or_(*search_filters)
                    )

        # --------------------------------------------------------
        # Customer filter
        # --------------------------------------------------------

        if customer_id is not None:

            query = query.filter(
                RentalBill.customer_id == customer_id
            )

        # --------------------------------------------------------
        # Machine filter
        # --------------------------------------------------------

        if machine_id is not None:

            query = query.filter(
                RentalBill.machine_id == machine_id
            )

        # --------------------------------------------------------
        # Billing month filter
        # --------------------------------------------------------

        if billing_month is not None:

            query = query.filter(
                RentalBill.billing_month == billing_month
            )

        # --------------------------------------------------------
        # Payment status filter
        # --------------------------------------------------------

        if payment_status is not None:

            query = query.filter(
                RentalBill.payment_status == payment_status
            )

        # --------------------------------------------------------
        # Ordering
        # --------------------------------------------------------

        query = query.order_by(
            RentalBill.billing_month.desc(),
            RentalBill.id.desc(),
        )

        # --------------------------------------------------------
        # Pagination
        # --------------------------------------------------------

        if skip < 0:
            skip = 0

        if limit is None or limit <= 0:
            limit = 20

        query = (
            query
            .offset(skip)
            .limit(limit)
        )

        return query.all()

    # ============================================================
    # COUNT ALL BILLS
    # ============================================================

    @staticmethod
    def count(
        db: Session,
        search: Optional[str] = None,
        customer_id: Optional[int] = None,
        machine_id: Optional[int] = None,
        billing_month: Optional[str] = None,
        payment_status: Optional[str] = None,
    ) -> int:

        query = db.query(RentalBill)

        # --------------------------------------------------------
        # Search
        # --------------------------------------------------------

        if search:

            keyword = search.strip()

            if keyword:

                search_filters = []

                if hasattr(RentalBill, "bill_number"):
                    search_filters.append(
                        RentalBill.bill_number.ilike(
                            f"%{keyword}%"
                        )
                    )

                if hasattr(RentalBill, "billing_month"):
                    search_filters.append(
                        RentalBill.billing_month.ilike(
                            f"%{keyword}%"
                        )
                    )

                if hasattr(RentalBill, "remarks"):
                    search_filters.append(
                        RentalBill.remarks.ilike(
                            f"%{keyword}%"
                        )
                    )

                if search_filters:

                    from sqlalchemy import or_

                    query = query.filter(
                        or_(*search_filters)
                    )

        # --------------------------------------------------------
        # Customer filter
        # --------------------------------------------------------

        if customer_id is not None:

            query = query.filter(
                RentalBill.customer_id == customer_id
            )

        # --------------------------------------------------------
        # Machine filter
        # --------------------------------------------------------

        if machine_id is not None:

            query = query.filter(
                RentalBill.machine_id == machine_id
            )

        # --------------------------------------------------------
        # Billing month filter
        # --------------------------------------------------------

        if billing_month is not None:

            query = query.filter(
                RentalBill.billing_month == billing_month
            )

        # --------------------------------------------------------
        # Payment status filter
        # --------------------------------------------------------

        if payment_status is not None:

            query = query.filter(
                RentalBill.payment_status == payment_status
            )

        return query.count()

    # ============================================================
    # UPDATE
    # ============================================================

    @staticmethod
    def update(
        db: Session,
        rental_bill: Optional[RentalBill] = None,
        bill: Optional[RentalBill] = None,
    ) -> RentalBill:

        """
        Update an existing RentalBill.

        Supports both:

            RentalBillRepository.update(
                db,
                rental_bill
            )

        and:

            RentalBillRepository.update(
                db=db,
                bill=bill
            )

        This keeps compatibility with the current
        RentalBillService.
        """

        # --------------------------------------------------------
        # Support current service call:
        #
        # RentalBillRepository.update(
        #     db=db,
        #     bill=bill
        # )
        # --------------------------------------------------------

        rental_bill = rental_bill or bill

        if rental_bill is None:

            raise ValueError(
                "RentalBillRepository.update() requires "
                "a RentalBill instance."
            )

        db.commit()
        db.refresh(rental_bill)

        return rental_bill

    # ============================================================
    # DELETE
    # ============================================================

    @staticmethod
    def delete(
        db: Session,
        rental_bill: RentalBill,
    ) -> bool:

        db.delete(rental_bill)
        db.commit()

        return True