from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.supplier import Supplier


class SupplierRepository:

    # =====================================================
    # Create Supplier
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        supplier: Supplier
    ):

        db.add(supplier)

        db.commit()

        db.refresh(supplier)

        return supplier


    # =====================================================
    # Get All Suppliers
    #
    # Used by:
    #   - Supplier Management table
    #   - Supplier Export
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
    #     -> ALL suppliers
    #
    # is_active = True
    #     -> ACTIVE suppliers only
    #
    # is_active = False
    #     -> INACTIVE suppliers only
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

        query = db.query(Supplier)


        # =====================================================
        # SEARCH
        #
        # Search across:
        #
        # Supplier Code
        # Company Name
        # Contact Person
        # Phone
        # Alternate Phone
        # Email
        # GSTIN
        # PAN
        # City
        # State
        # =====================================================

        if search:

            search_value = search.strip()

            if search_value:

                search_pattern = (
                    f"%{search_value}%"
                )

                query = query.filter(

                    or_(

                        Supplier.supplier_code.ilike(
                            search_pattern
                        ),

                        Supplier.company_name.ilike(
                            search_pattern
                        ),

                        Supplier.contact_person.ilike(
                            search_pattern
                        ),

                        Supplier.phone.ilike(
                            search_pattern
                        ),

                        Supplier.alternate_phone.ilike(
                            search_pattern
                        ),

                        Supplier.email.ilike(
                            search_pattern
                        ),

                        Supplier.gstin.ilike(
                            search_pattern
                        ),

                        Supplier.pan.ilike(
                            search_pattern
                        ),

                        Supplier.city.ilike(
                            search_pattern
                        ),

                        Supplier.state.ilike(
                            search_pattern
                        ),

                    )

                )


        # =====================================================
        # CITY FILTER
        # =====================================================

        if city:

            city_value = city.strip()

            if city_value:

                query = query.filter(

                    Supplier.city.ilike(
                        f"%{city_value}%"
                    )

                )


        # =====================================================
        # STATE FILTER
        # =====================================================

        if state:

            state_value = state.strip()

            if state_value:

                query = query.filter(

                    Supplier.state.ilike(
                        f"%{state_value}%"
                    )

                )


        # =====================================================
        # STATUS FILTER
        #
        # None  -> ALL
        # True  -> ACTIVE
        # False -> INACTIVE
        # =====================================================

        if is_active is not None:

            query = query.filter(

                Supplier.is_active ==
                is_active

            )


        # =====================================================
        # TOTAL RECORDS
        # =====================================================

        total_records = query.count()


        # =====================================================
        # SUPPLIERS
        # =====================================================

        suppliers = (

            query

            .order_by(
                Supplier.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )


        return (
            total_records,
            suppliers
        )


    # =====================================================
    # Get By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        supplier_id: int
    ):

        return (

            db.query(Supplier)

            .filter(
                Supplier.id == supplier_id
            )

            .first()

        )


    # =====================================================
    # Get By Supplier Code
    # =====================================================

    @staticmethod
    def get_by_supplier_code(
        db: Session,
        supplier_code: str
    ):

        return (

            db.query(Supplier)

            .filter(
                Supplier.supplier_code ==
                supplier_code
            )

            .first()

        )


    # =====================================================
    # Get By Company Name
    # =====================================================

    @staticmethod
    def get_by_company_name(
        db: Session,
        company_name: str
    ):

        return (

            db.query(Supplier)

            .filter(
                Supplier.company_name ==
                company_name
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

            db.query(Supplier)

            .filter(
                Supplier.email ==
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

            db.query(Supplier)

            .filter(
                Supplier.gstin ==
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

            db.query(Supplier)

            .filter(
                Supplier.pan ==
                pan
            )

            .first()

        )


    # =====================================================
    # Last Supplier
    # =====================================================

    @staticmethod
    def last_supplier(
        db: Session
    ):

        return (

            db.query(Supplier)

            .order_by(
                Supplier.id.desc()
            )

            .first()

        )


    # =====================================================
    # Update Supplier
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        supplier: Supplier
    ):

        db.commit()

        db.refresh(supplier)

        return supplier


    # =====================================================
    # Soft Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        supplier: Supplier
    ):

        supplier.is_active = False

        db.commit()

        db.refresh(supplier)

        return supplier


    # =====================================================
    # Count
    # =====================================================

    @staticmethod
    def count(
        db: Session
    ):

        return (
            db.query(Supplier)
            .count()
        )


    # =====================================================
    # Active Count
    # =====================================================

    @staticmethod
    def active_count(
        db: Session
    ):

        return (

            db.query(Supplier)

            .filter(
                Supplier.is_active == True
            )

            .count()

        )


    # =====================================================
    # Inactive Count
    # =====================================================

    @staticmethod
    def inactive_count(
        db: Session
    ):

        return (

            db.query(Supplier)

            .filter(
                Supplier.is_active == False
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
                        Supplier.current_balance
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
                        Supplier.credit_limit
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

            "total_suppliers":
                SupplierRepository.count(db),

            "active_suppliers":
                SupplierRepository.active_count(db),

            "inactive_suppliers":
                SupplierRepository.inactive_count(db),

            "total_outstanding":
                SupplierRepository.total_outstanding(db),

            "total_credit_limit":
                SupplierRepository.total_credit_limit(db)

        }