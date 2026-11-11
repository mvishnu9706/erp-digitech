from sqlalchemy.orm import Session

from app.repositories.user_repository import (
    UserRepository,
)

from app.core.security import (
    verify_password,
    create_access_token,
)


class AuthService:

    # =====================================================
    # Login
    # =====================================================
    #
    # Login supports:
    #
    # 1. Email + Password
    #
    #    admin@digitech.com
    #
    # 2. Mobile + Password
    #
    #    9876500011
    #
    # The identifier is checked against both email
    # and phone.
    #
    # =====================================================

    @staticmethod
    def login(
        db: Session,
        identifier: str,
        password: str,
    ):

        # -------------------------------------------------
        # Clean Identifier
        # -------------------------------------------------

        identifier = (
            identifier or ""
        ).strip()

        if not identifier:

            return None

        # -------------------------------------------------
        # Find User
        # -------------------------------------------------
        #
        # First check email.
        #
        # If no user is found by email, check phone.
        #
        # -------------------------------------------------

        user = UserRepository.get_by_email(
            db,
            identifier.lower(),
        )

        # -------------------------------------------------
        # If Email Lookup Failed,
        # Try Mobile Number
        # -------------------------------------------------

        if user is None:

            user = UserRepository.get_by_phone(
                db,
                identifier,
            )

        # -------------------------------------------------
        # User Not Found
        # -------------------------------------------------

        if user is None:

            return None

        # -------------------------------------------------
        # Check Account Status
        # -------------------------------------------------

        if not user.is_active:

            return None

        # -------------------------------------------------
        # Verify Password
        # -------------------------------------------------

        if not verify_password(
            password,
            user.password,
        ):

            return None

        # -------------------------------------------------
        # Normalize Role
        #
        # Examples:
        #
        # Admin        -> ADMIN
        # admin        -> ADMIN
        # CUSTOMER     -> CUSTOMER
        # Sales Person -> SALES_PERSON
        #
        # -------------------------------------------------

        role = (
            user.role or ""
        ).strip().upper()

        # -------------------------------------------------
        # CUSTOMER VALIDATION
        # -------------------------------------------------
        #
        # A CUSTOMER login must always be linked to an
        # existing customer.
        #
        # users.role       = CUSTOMER
        # users.customer_id = customers.id
        #
        # If the mapping is missing, do not allow the
        # customer portal login.
        #
        # -------------------------------------------------

        if role == "CUSTOMER":

            if user.customer_id is None:

                return None

            customer = (
                UserRepository
                .get_customer_user_by_customer_id(
                    db,
                    user.customer_id,
                )
            )

            # -------------------------------------------------
            # Confirm that the linked CUSTOMER user is this
            # same authenticated user.
            # -------------------------------------------------

            if (
                customer is None
                or customer.id != user.id
            ):

                return None

        # -------------------------------------------------
        # Create JWT
        # -------------------------------------------------
        #
        # The JWT contains:
        #
        # id
        # email
        # role
        # customer_id
        #
        # For ADMIN / ENGINEER / SALES_PERSON:
        #
        # customer_id = None
        #
        # For CUSTOMER:
        #
        # customer_id = linked customers.id
        #
        # -------------------------------------------------

        token = create_access_token(
            {
                "id": user.id,
                "email": user.email,
                "role": role,
                "customer_id": user.customer_id,
            }
        )

        # -------------------------------------------------
        # Login Response
        # -------------------------------------------------

        return {

            "access_token": token,

            "token_type": "bearer",

            "role": role,

        }