from sqlalchemy.orm import Session

from app.models import User


class UserRepository:

    # =====================================================
    # Create User
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        user: User
    ):

        db.add(user)

        db.commit()

        db.refresh(user)

        return user


    # =====================================================
    # Get All Users
    # =====================================================

    @staticmethod
    def get_all(
        db: Session
    ):

        return (
            db.query(User)
            .order_by(User.id.desc())
            .all()
        )


    # =====================================================
    # Get User By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int
    ):

        return (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )


    # =====================================================
    # Get User By Email
    # =====================================================

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ):

        return (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )


    # =====================================================
    # Get User By Phone
    # =====================================================
    #
    # Used for login with mobile number.
    #
    # Example:
    #
    # 9876500011
    #
    # =====================================================

    @staticmethod
    def get_by_phone(
        db: Session,
        phone: str
    ):

        return (
            db.query(User)
            .filter(
                User.phone == phone
            )
            .first()
        )


    # =====================================================
    # Get CUSTOMER User By Customer ID
    # =====================================================
    #
    # Used for Customer Portal access management.
    #
    # One customer should have only one CUSTOMER login.
    #
    # This works together with:
    #
    # User.customer_id -> Customer.id
    # User.role == "CUSTOMER"
    # User.customer_id UNIQUE
    #
    # =====================================================

    @staticmethod
    def get_customer_user_by_customer_id(
        db: Session,
        customer_id: int
    ):

        return (
            db.query(User)
            .filter(
                User.customer_id == customer_id,
                User.role == "CUSTOMER"
            )
            .first()
        )


    # =====================================================
    # Get User By Customer ID
    # =====================================================
    #
    # Generic lookup when the authenticated customer
    # relationship is required.
    #
    # Normally this should return the same single CUSTOMER
    # user because customer_id is UNIQUE.
    #
    # =====================================================

    @staticmethod
    def get_by_customer_id(
        db: Session,
        customer_id: int
    ):

        return (
            db.query(User)
            .filter(
                User.customer_id == customer_id
            )
            .first()
        )


    # =====================================================
    # Delete User
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        user: User
    ):

        db.delete(user)

        db.commit()

        return True