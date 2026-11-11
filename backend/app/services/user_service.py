from sqlalchemy.orm import Session

from fastapi import (
    HTTPException,
    status,
)

from app.models import User, Customer

from app.repositories.user_repository import (
    UserRepository,
)

from app.core.security import (
    hash_password,
)


# =====================================================
# Allowed Roles
# =====================================================

ALLOWED_ROLES = {
    "SUPER_ADMIN",
    "ADMIN",
    "ENGINEER",
    "CUSTOMER",
    "SALES_PERSON",
}


# =====================================================
# User Service
# =====================================================

class UserService:

    # =================================================
    # CUSTOMER VALIDATION HELPER
    # =================================================

    @staticmethod
    def _validate_customer(
        db: Session,
        customer_id: int,
    ):
        """
        Validate that the selected customer exists
        and is active.
        """

        if customer_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer must be selected",
            )

        customer = (
            db.query(Customer)
            .filter(
                Customer.id == customer_id
            )
            .first()
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )

        if not customer.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer is inactive",
            )

        return customer

    # =================================================
    # CUSTOMER PORTAL MAPPING VALIDATION
    # =================================================

    @staticmethod
    def _validate_customer_portal_mapping(
        db: Session,
        customer_id: int,
        exclude_user_id: int | None = None,
    ):
        """
        Enforce the one-to-one mapping:

            customers.id
                 ↓
            users.customer_id

        A customer can have only one CUSTOMER login.
        """

        query = (
            db.query(User)
            .filter(
                User.customer_id == customer_id,
                User.role == "CUSTOMER",
            )
        )

        if exclude_user_id is not None:
            query = query.filter(
                User.id != exclude_user_id
            )

        existing_user = query.first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This customer already has a CUSTOMER portal "
                    "login account"
                ),
            )

        return True

    # =================================================
    # CREATE USER
    # =================================================

    @staticmethod
    def create_user(
        db: Session,
        data,
        current_user,
    ):

        # ---------------------------------------------
        # Normalize Email
        # ---------------------------------------------

        email = (
            str(data.email)
            .lower()
            .strip()
        )

        # ---------------------------------------------
        # Check Duplicate Email
        # ---------------------------------------------

        existing_user = (
            UserRepository.get_by_email(
                db,
                email,
            )
        )

        if existing_user:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # ---------------------------------------------
        # Requested Role
        # ---------------------------------------------

        requested_role = (
            getattr(
                data,
                "role",
                None,
            )
            or "CUSTOMER"
        ).strip().upper()

        # ---------------------------------------------
        # Validate Role
        # ---------------------------------------------

        if requested_role not in ALLOWED_ROLES:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user role",
            )

        # ---------------------------------------------
        # Current User Role
        # ---------------------------------------------

        current_role = (
            current_user.role or ""
        ).strip().upper()

        # ---------------------------------------------
        # ADMIN Cannot Create SUPER_ADMIN
        # ---------------------------------------------

        if (
            requested_role == "SUPER_ADMIN"
            and current_role != "SUPER_ADMIN"
        ):

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only SUPER_ADMIN can create "
                    "another SUPER_ADMIN"
                ),
            )

        # =================================================
        # CUSTOMER ASSIGNMENT
        # =================================================

        customer_id = getattr(
            data,
            "customer_id",
            None,
        )

        selected_customer = None

        if requested_role == "CUSTOMER":

            # ---------------------------------------------
            # CUSTOMER MUST HAVE CUSTOMER ID
            # ---------------------------------------------

            if customer_id is None:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "customer_id is required when "
                        "creating a CUSTOMER user"
                    ),
                )

            # ---------------------------------------------
            # Validate Customer
            # ---------------------------------------------

            selected_customer = UserService._validate_customer(
                db=db,
                customer_id=customer_id,
            )

            # ---------------------------------------------
            # ONE-TO-ONE CUSTOMER PORTAL MAPPING
            # ---------------------------------------------

            UserService._validate_customer_portal_mapping(
                db=db,
                customer_id=customer_id,
            )

            # ---------------------------------------------
            # CUSTOMER EMAIL MUST MATCH CUSTOMER MASTER
            # ---------------------------------------------

            customer_email = (
                str(selected_customer.email).lower().strip()
                if selected_customer.email
                else ""
            )

            if customer_email and customer_email != email:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "The login email must match the selected "
                        "customer's email address"
                    ),
                )

            if not customer_email:
                selected_customer.email = email

            # ---------------------------------------------
            # CUSTOMER PHONE IS MASTER DATA
            # ---------------------------------------------

            customer_phone = (
                str(selected_customer.phone).strip()
                if selected_customer.phone
                else None
            )

            if customer_phone:
                data_phone = customer_phone

            else:
                data_phone = getattr(
                    data,
                    "phone",
                    None,
                )

                if data_phone:
                    data_phone = str(data_phone).strip()
                    selected_customer.phone = data_phone

        else:

            # ---------------------------------------------
            # Non-CUSTOMER users do not have customer_id
            # ---------------------------------------------

            customer_id = None

            data_phone = getattr(
                data,
                "phone",
                None,
            )

        # ---------------------------------------------
        # Company Name
        # ---------------------------------------------

        company_name = getattr(
            data,
            "company_name",
            None,
        )

        if company_name is not None:

            company_name = (
                str(company_name)
                .strip()
            )

            if not company_name:
                company_name = None

        # ---------------------------------------------
        # Contact Person Name
        # ---------------------------------------------

        contact_person_name = getattr(
            data,
            "contact_person_name",
            None,
        )

        if contact_person_name is not None:

            contact_person_name = (
                str(contact_person_name)
                .strip()
            )

        # ---------------------------------------------
        # Full Name
        # ---------------------------------------------

        if requested_role == "CUSTOMER" and selected_customer:

            full_name = (
                selected_customer.contact_person
                or selected_customer.customer_name
                or getattr(
                    data,
                    "full_name",
                    None,
                )
                or ""
            ).strip()

            company_name = (
                selected_customer.customer_name
                or company_name
            )

        else:

            full_name = (
                contact_person_name
                or getattr(
                    data,
                    "full_name",
                    None,
                )
                or ""
            ).strip()

        if len(full_name) < 2:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Contact person name must contain "
                    "at least 2 characters"
                ),
            )

        # ---------------------------------------------
        # Phone
        # ---------------------------------------------

        phone = (
            data_phone
            if requested_role == "CUSTOMER"
            else getattr(
                data,
                "phone",
                None,
            )
        )

        if phone is not None:

            phone = str(phone).strip()

            if not phone:

                phone = None

            elif len(phone) > 20:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Phone number cannot exceed "
                        "20 characters"
                    ),
                )

        # ---------------------------------------------
        # Password
        # ---------------------------------------------

        hashed_password = hash_password(
            data.password
        )

        portal_password = getattr(
            data,
            "portal_password",
            None,
        )

        if requested_role == "CUSTOMER":

            # If portal_password was not explicitly supplied,
            # use the same password entered for the portal login.

            if not portal_password:
                portal_password = data.password

        else:

            # Internal staff users do not need a separate
            # portal password value.

            portal_password = None

        # =================================================
        # CUSTOMER PORTAL MODULE ACCESS
        # =================================================
        #
        # Only CUSTOMER users receive portal module access.
        #
        # Defaults:
        #
        #     Service = TRUE
        #     Rental  = FALSE
        #
        # Admin can explicitly send different values.
        # =================================================

        if requested_role == "CUSTOMER":

            service_access = getattr(
                data,
                "service_access",
                True,
            )

            rental_access = getattr(
                data,
                "rental_access",
                False,
            )

            service_access = bool(
                service_access
            )

            rental_access = bool(
                rental_access
            )

            # -------------------------------------------------
            # CUSTOMER SERVICE PORTAL
            # -------------------------------------------------
            # Keep the customer-level Service Portal flag
            # synchronized with the Service Access selected
            # for this CUSTOMER portal account.
            # -------------------------------------------------

            if selected_customer is not None:

                selected_customer.service_enabled = (
                    service_access
                )

        else:

            # Non-CUSTOMER users do not use Customer Portal
            # module access.

            service_access = False
            rental_access = False

        # =================================================
        # CREATE USER OBJECT
        # =================================================

        user = User(

            # ---------------------------------------------
            # Company
            # ---------------------------------------------

            company_name=company_name,

            # ---------------------------------------------
            # Contact Person
            # ---------------------------------------------

            contact_person_name=contact_person_name,

            # ---------------------------------------------
            # Full Name
            # ---------------------------------------------

            full_name=full_name,

            # ---------------------------------------------
            # Authentication
            # ---------------------------------------------

            email=email,

            phone=phone,

            password=hashed_password,

            # ---------------------------------------------
            # Portal Password
            # ---------------------------------------------

            portal_password=portal_password,

            # ---------------------------------------------
            # Role
            # ---------------------------------------------

            role=requested_role,

            # ---------------------------------------------
            # Customer Association
            # ---------------------------------------------

            customer_id=customer_id,

            # ---------------------------------------------
            # Customer Portal Module Access
            # ---------------------------------------------

            service_access=service_access,

            rental_access=rental_access,

            # ---------------------------------------------
            # Account Status
            # ---------------------------------------------

            is_active=True,
        )

        # ---------------------------------------------
        # Save User
        # ---------------------------------------------

        try:

            created_user = UserRepository.create(
                db,
                user,
            )

            return created_user

        except Exception:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create user",
            )

    # =================================================
    # GET ALL USERS
    # =================================================

    @staticmethod
    def get_users(
        db: Session,
    ):

        return UserRepository.get_all(
            db,
        )

    # =================================================
    # GET USER
    # =================================================

    @staticmethod
    def get_user(
        db: Session,
        user_id: int,
    ):

        return UserRepository.get_by_id(
            db,
            user_id,
        )

    # =================================================
    # UPDATE USER
    # =================================================

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        data,
        current_user,
    ):

        # ---------------------------------------------
        # Find User
        # ---------------------------------------------

        user = UserRepository.get_by_id(
            db,
            user_id,
        )

        if not user:
            return None

        # ---------------------------------------------
        # Current User Role
        # ---------------------------------------------

        current_role = (
            current_user.role or ""
        ).strip().upper()

        # ---------------------------------------------
        # Existing Target Role
        # ---------------------------------------------

        old_target_role = (
            user.role or ""
        ).strip().upper()

        # ---------------------------------------------
        # ADMIN Cannot Modify SUPER_ADMIN
        # ---------------------------------------------

        if (
            old_target_role == "SUPER_ADMIN"
            and current_role != "SUPER_ADMIN"
        ):

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only SUPER_ADMIN can modify "
                    "SUPER_ADMIN"
                ),
            )

        # =================================================
        # COMPANY NAME
        # =================================================

        if data.company_name is not None:

            company_name = (
                str(data.company_name)
                .strip()
            )

            if len(company_name) < 2:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Company name must contain "
                        "at least 2 characters"
                    ),
                )

            user.company_name = company_name

        # =================================================
        # CONTACT PERSON
        # =================================================

        if data.contact_person_name is not None:

            contact_person_name = (
                str(data.contact_person_name)
                .strip()
            )

            if len(contact_person_name) < 2:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Contact person name must contain "
                        "at least 2 characters"
                    ),
                )

            user.contact_person_name = (
                contact_person_name
            )

            # Keep full_name synchronized
            user.full_name = (
                contact_person_name
            )

        # =================================================
        # FULL NAME
        # =================================================

        if data.full_name is not None:

            full_name = (
                data.full_name
                .strip()
            )

            if len(full_name) < 2:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Full name must contain "
                        "at least 2 characters"
                    ),
                )

            user.full_name = full_name

        # =================================================
        # EMAIL
        # =================================================

        if data.email is not None:

            email = (
                str(data.email)
                .lower()
                .strip()
            )

            existing_user = (
                UserRepository.get_by_email(
                    db,
                    email,
                )
            )

            if (
                existing_user
                and existing_user.id != user.id
            ):

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            user.email = email

            # CUSTOMER login email must stay synchronized
            # with the linked customer master record.

            if old_target_role == "CUSTOMER":

                if user.customer_id is None:

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "CUSTOMER user is not linked to a customer"
                        ),
                    )

                linked_customer = (
                    UserService._validate_customer(
                        db=db,
                        customer_id=user.customer_id,
                    )
                )

                # The customer master is the source of truth.
                linked_customer.email = email

        # =================================================
        # PHONE
        # =================================================

        if data.phone is not None:

            phone = str(
                data.phone
            ).strip()

            if phone:

                if len(phone) > 20:

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Phone number cannot exceed "
                            "20 characters"
                        ),
                    )

                user.phone = phone

                if (
                    old_target_role == "CUSTOMER"
                    and user.customer_id
                ):

                    linked_customer = (
                        UserService._validate_customer(
                            db=db,
                            customer_id=user.customer_id,
                        )
                    )

                    linked_customer.phone = phone

            else:

                user.phone = None

                if (
                    old_target_role == "CUSTOMER"
                    and user.customer_id
                ):

                    linked_customer = (
                        UserService._validate_customer(
                            db=db,
                            customer_id=user.customer_id,
                        )
                    )

                    linked_customer.phone = None

        # =================================================
        # PORTAL PASSWORD
        # =================================================
        #
        # Only update this value when the admin explicitly
        # supplies a new portal_password.
        #
        # =================================================

        if data.portal_password is not None:

            if old_target_role != "CUSTOMER":

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Portal password can only be set "
                        "for CUSTOMER users"
                    ),
                )

            portal_password = (
                str(data.portal_password)
                .strip()
            )

            if len(portal_password) < 6:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Portal password must contain "
                        "at least 6 characters"
                    ),
                )

            user.portal_password = portal_password

        # =================================================
        # ROLE UPDATE
        # =================================================

        role_was_changed = False

        if data.role is not None:

            new_role = (
                data.role
                .strip()
                .upper()
            )

            # -----------------------------------------
            # Validate Role
            # -----------------------------------------

            if new_role not in ALLOWED_ROLES:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user role",
                )

            # -----------------------------------------
            # Only SUPER_ADMIN can assign
            # SUPER_ADMIN
            # -----------------------------------------

            if (
                new_role == "SUPER_ADMIN"
                and current_role != "SUPER_ADMIN"
            ):

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "Only SUPER_ADMIN can assign "
                        "SUPER_ADMIN role"
                    ),
                )

            # -----------------------------------------
            # ADMIN Cannot Modify SUPER_ADMIN
            # -----------------------------------------

            if (
                old_target_role == "SUPER_ADMIN"
                and current_role != "SUPER_ADMIN"
            ):

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "Only SUPER_ADMIN can modify "
                        "SUPER_ADMIN"
                    ),
                )

            user.role = new_role

            role_was_changed = (
                new_role != old_target_role
            )

            # -----------------------------------------
            # If changing AWAY from CUSTOMER,
            # remove customer association.
            # -----------------------------------------

            if new_role != "CUSTOMER":

                user.customer_id = None
                user.portal_password = None

                # -----------------------------------------
                # Customer Portal access is only valid for
                # CUSTOMER users.
                # -----------------------------------------

                user.service_access = False
                user.rental_access = False

        # =================================================
        # FINAL ROLE
        # =================================================

        final_role = (
            user.role or ""
        ).strip().upper()

        # =================================================
        # CUSTOMER ASSIGNMENT
        # =================================================

        supplied_customer_id = (
            data.customer_id
            if data.customer_id is not None
            else None
        )

        if final_role == "CUSTOMER":

            # ---------------------------------------------
            # Customer ID explicitly supplied
            # ---------------------------------------------

            if supplied_customer_id is not None:

                selected_customer = (
                    UserService._validate_customer(
                        db=db,
                        customer_id=supplied_customer_id,
                    )
                )

                # Do not allow another CUSTOMER user to point
                # to the same customer.

                UserService._validate_customer_portal_mapping(
                    db=db,
                    customer_id=supplied_customer_id,
                    exclude_user_id=user.id,
                )

                # Customer email is the portal login email
                # source of truth.

                if selected_customer.email:

                    customer_email = (
                        str(selected_customer.email)
                        .lower()
                        .strip()
                    )

                    if (
                        data.email is not None
                        and email != customer_email
                    ):

                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                "The login email must match the "
                                "selected customer's email address"
                            ),
                        )

                    user.email = customer_email

                elif data.email is not None:

                    customer_email = (
                        str(data.email)
                        .lower()
                        .strip()
                    )

                    selected_customer.email = customer_email
                    user.email = customer_email

                # Keep the portal user's phone aligned with the
                # customer master record when available.

                if selected_customer.phone:
                    user.phone = selected_customer.phone

                user.customer_id = (
                    supplied_customer_id
                )

            # ---------------------------------------------
            # Role was changed to CUSTOMER
            # but no customer was selected.
            # ---------------------------------------------

            elif role_was_changed:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "A customer must be selected "
                        "when assigning the CUSTOMER role"
                    ),
                )

            # ---------------------------------------------
            # Existing CUSTOMER
            # ---------------------------------------------

            elif user.customer_id is None:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "This CUSTOMER user is not linked "
                        "to a customer. Please select a customer."
                    ),
                )

            else:

                # Existing CUSTOMER mapping must remain one-to-one.

                UserService._validate_customer_portal_mapping(
                    db=db,
                    customer_id=user.customer_id,
                    exclude_user_id=user.id,
                )

                selected_customer = (
                    UserService._validate_customer(
                        db=db,
                        customer_id=user.customer_id,
                    )
                )

                # Customer email remains the source of truth.

                if selected_customer.email:

                    user.email = (
                        str(selected_customer.email)
                        .lower()
                        .strip()
                    )

                if selected_customer.phone:
                    user.phone = selected_customer.phone

        # =================================================
        # NON-CUSTOMER
        # =================================================

        else:

            # A non-CUSTOMER must never have customer_id.

            user.customer_id = None

            # A non-CUSTOMER must never retain Customer
            # Portal module access.

            user.service_access = False
            user.rental_access = False

        # =================================================
        # CUSTOMER PORTAL MODULE ACCESS
        # =================================================
        #
        # This is deliberately handled AFTER the final role
        # and customer assignment are determined.
        #
        # This allows:
        #
        #     service_access = true
        #     rental_access = false
        #
        # or:
        #
        #     service_access = false
        #     rental_access = true
        #
        # or:
        #
        #     service_access = true
        #     rental_access = true
        #
        # or:
        #
        #     service_access = false
        #     rental_access = false
        #
        # Only fields explicitly supplied in UserUpdate are
        # changed. This is important because UserUpdate is
        # a partial update.
        # =================================================

        if final_role == "CUSTOMER":

            # -------------------------------------------------
            # SERVICE ACCESS
            # -------------------------------------------------

            if data.service_access is not None:

                user.service_access = bool(
                    data.service_access
                )

                # Keep the linked customer's Service Portal
                # availability synchronized with the portal user's
                # Service Access setting.
                if user.customer_id is not None:

                    linked_customer = (
                        UserService._validate_customer(
                            db=db,
                            customer_id=user.customer_id,
                        )
                    )

                    linked_customer.service_enabled = (
                        user.service_access
                    )

            # -------------------------------------------------
            # RENTAL ACCESS
            # -------------------------------------------------

            if data.rental_access is not None:

                user.rental_access = bool(
                    data.rental_access
                )

        # =================================================
        # ACTIVE STATUS
        # =================================================

        if data.is_active is not None:

            # -----------------------------------------
            # Prevent ADMIN from changing
            # SUPER_ADMIN active status
            # -----------------------------------------

            if (
                old_target_role == "SUPER_ADMIN"
                and current_role != "SUPER_ADMIN"
            ):

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "Only SUPER_ADMIN can change "
                        "SUPER_ADMIN status"
                    ),
                )

            user.is_active = data.is_active

        # =================================================
        # SAVE CHANGES
        # =================================================

        try:

            db.commit()

            db.refresh(user)

        except Exception:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to update user",
            )

        return user

    # =================================================
    # CHANGE PASSWORD
    # =================================================

    @staticmethod
    def change_password(
        db: Session,
        user_id: int,
        data,
        current_user,
    ):

        # ---------------------------------------------
        # Validate New Password
        # ---------------------------------------------

        if not data.new_password:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password is required",
            )

        # ---------------------------------------------
        # Validate Confirm Password
        # ---------------------------------------------

        if (
            data.new_password
            != data.confirm_password
        ):

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match",
            )

        # ---------------------------------------------
        # Minimum Password Length
        # ---------------------------------------------

        if len(data.new_password) < 6:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Password must contain "
                    "at least 6 characters"
                ),
            )

        # ---------------------------------------------
        # Target User
        # ---------------------------------------------

        user = UserRepository.get_by_id(
            db,
            user_id,
        )

        if not user:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found",
            )

        # ---------------------------------------------
        # Current User Role
        # ---------------------------------------------

        current_role = (
            current_user.role or ""
        ).strip().upper()

        # ---------------------------------------------
        # Target User Role
        # ---------------------------------------------

        target_role = (
            user.role or ""
        ).strip().upper()

        # ---------------------------------------------
        # SUPER ADMIN
        # ---------------------------------------------

        if current_role == "SUPER_ADMIN":

            pass

        # ---------------------------------------------
        # ADMIN
        # ---------------------------------------------

        elif current_role == "ADMIN":

            if target_role == "SUPER_ADMIN":

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "ADMIN cannot change "
                        "SUPER_ADMIN password"
                    ),
                )

        # ---------------------------------------------
        # Other Roles
        # ---------------------------------------------

        else:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only ADMIN or SUPER_ADMIN "
                    "can change passwords"
                ),
            )

        # ---------------------------------------------
        # Hash New Password
        # ---------------------------------------------

        user.password = hash_password(
            data.new_password
        )

        # ---------------------------------------------
        # CUSTOMER PORTAL PASSWORD
        # ---------------------------------------------

        if target_role == "CUSTOMER":

            user.portal_password = (
                data.new_password
            )

        # ---------------------------------------------
        # Save Password
        # ---------------------------------------------

        try:

            db.commit()

            db.refresh(user)

        except Exception:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to change password",
            )

        return user

    # =================================================
    # DELETE USER
    # =================================================

    @staticmethod
    def delete_user(
        db: Session,
        user_id: int,
    ):

        # ---------------------------------------------
        # Find User
        # ---------------------------------------------

        user = UserRepository.get_by_id(
            db,
            user_id,
        )

        if not user:
            return False

        # ---------------------------------------------
        # Delete
        # ---------------------------------------------

        try:

            UserRepository.delete(
                db,
                user,
            )

        except Exception:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to delete user",
            )

        return True