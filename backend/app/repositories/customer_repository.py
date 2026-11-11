from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:

    # =====================================================
    # Create Customer
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        customer: Customer
    ):

        db.add(customer)

        db.flush()

        db.refresh(customer)

        return customer


    # =====================================================
    # Get All Customers
    #
    # Used by:
    #   - Customer Management table
    #   - Customer search
    #   - Customer filters
    #   - Customer Excel export
    #
    # Filters:
    #   - search
    #   - city
    #   - state
    #   - is_active
    #
    # IMPORTANT:
    #
    # is_active = None
    #     -> ALL customers
    #
    # is_active = True
    #     -> ACTIVE customers only
    #
    # is_active = False
    #     -> INACTIVE customers only
    # =====================================================

    @staticmethod
    def get_all(
        db: Session,
        search: str = None,
        city: str = None,
        state: str = None,
        is_active: bool = None,
        skip: int = 0,
        limit: int = 10
    ):

        # =================================================
        # Base Query
        # =================================================

        query = db.query(Customer)


        # =================================================
        # SEARCH
        #
        # Search across:
        #
        # Customer Name
        # Customer Code
        # Contact Person
        # Phone
        # Email
        # GSTIN
        # PAN
        # City
        # State
        # =================================================

        if search:

            search_value = search.strip()

            if search_value:

                search_term = (
                    f"%{search_value}%"
                )

                query = query.filter(

                    or_(

                        Customer.customer_name.ilike(
                            search_term
                        ),

                        Customer.customer_code.ilike(
                            search_term
                        ),

                        Customer.contact_person.ilike(
                            search_term
                        ),

                        Customer.phone.ilike(
                            search_term
                        ),

                        Customer.email.ilike(
                            search_term
                        ),

                        Customer.gstin.ilike(
                            search_term
                        ),

                        Customer.pan.ilike(
                            search_term
                        ),

                        Customer.city.ilike(
                            search_term
                        ),

                        Customer.state.ilike(
                            search_term
                        )

                    )

                )


        # =================================================
        # CITY FILTER
        #
        # Partial matching:
        #
        # "Hyd" can match "Hyderabad"
        # =================================================

        if city:

            city_value = city.strip()

            if city_value:

                query = query.filter(

                    Customer.city.ilike(
                        f"%{city_value}%"
                    )

                )


        # =================================================
        # STATE FILTER
        #
        # Partial matching
        # =================================================

        if state:

            state_value = state.strip()

            if state_value:

                query = query.filter(

                    Customer.state.ilike(
                        f"%{state_value}%"
                    )

                )


        # =================================================
        # STATUS FILTER
        #
        # None  -> ALL
        # True  -> ACTIVE
        # False -> INACTIVE
        # =================================================

        if is_active is not None:

            query = query.filter(

                Customer.is_active ==
                is_active

            )


        # =================================================
        # Pagination
        # =================================================

        customers = (

            query

            .order_by(
                Customer.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )


        return customers


    # =====================================================
    # Get By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        customer_id: int
    ):

        return (

            db.query(Customer)

            .filter(
                Customer.id == customer_id
            )

            .first()

        )


    # =====================================================
    # Get By Customer Code
    # =====================================================

    @staticmethod
    def get_by_customer_code(
        db: Session,
        customer_code: str
    ):

        return (

            db.query(Customer)

            .filter(
                Customer.customer_code ==
                customer_code
            )

            .first()

        )


    # =====================================================
    # Get By Customer Name
    # =====================================================

    @staticmethod
    def get_by_customer_name(
        db: Session,
        customer_name: str
    ):

        return (

            db.query(Customer)

            .filter(
                Customer.customer_name ==
                customer_name
            )

            .first()

        )


    # =====================================================
    # Get By Email
    # =====================================================

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ):

        return (

            db.query(Customer)

            .filter(
                Customer.email ==
                email
            )

            .first()

        )


    # =====================================================
    # Get By GSTIN
    # =====================================================

    @staticmethod
    def get_by_gstin(
        db: Session,
        gstin: str
    ):

        return (

            db.query(Customer)

            .filter(
                Customer.gstin ==
                gstin
            )

            .first()

        )


    # =====================================================
    # Get By PAN
    # =====================================================

    @staticmethod
    def get_by_pan(
        db: Session,
        pan: str
    ):

        return (

            db.query(Customer)

            .filter(
                Customer.pan ==
                pan
            )

            .first()

        )


    # =====================================================
    # Last Customer
    # =====================================================

    @staticmethod
    def last_customer(
        db: Session
    ):

        return (

            db.query(Customer)

            .order_by(
                Customer.id.desc()
            )

            .first()

        )


    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        customer: Customer
    ):

        db.flush()

        db.refresh(customer)

        return customer


    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        customer: Customer
    ):

        db.delete(customer)

        db.flush()

        return customer


    # =====================================================
    # Total Customers
    # =====================================================

    @staticmethod
    def count(
        db: Session
    ):

        return (

            db.query(Customer)

            .count()

        )


    # =====================================================
    # Active Customers
    # =====================================================

    @staticmethod
    def active_count(
        db: Session
    ):

        return (

            db.query(Customer)

            .filter(
                Customer.is_active == True
            )

            .count()

        )


    # =====================================================
    # Inactive Customers
    # =====================================================

    @staticmethod
    def inactive_count(
        db: Session
    ):

        return (

            db.query(Customer)

            .filter(
                Customer.is_active == False
            )

            .count()

        )


    # =====================================================
    # Total Outstanding
    # =====================================================

    @staticmethod
    def total_outstanding(
        db: Session
    ):

        return (

            db.query(

                func.coalesce(

                    func.sum(
                        Customer.current_balance
                    ),

                    0

                )

            )

            .scalar()

        )


    # =====================================================
    # Total Credit Limit
    # =====================================================

    @staticmethod
    def total_credit_limit(
        db: Session
    ):

        return (

            db.query(

                func.coalesce(

                    func.sum(
                        Customer.credit_limit
                    ),

                    0

                )

            )

            .scalar()

        )


    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return {

            "total_customers":
                CustomerRepository.count(db),

            "active_customers":
                CustomerRepository.active_count(db),

            "inactive_customers":
                CustomerRepository.inactive_count(db),

            "total_outstanding":
                CustomerRepository.total_outstanding(db),

            "total_credit_limit":
                CustomerRepository.total_credit_limit(db)

        }