from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import OAuth2PasswordBearer

from jose import (
    JWTError,
    jwt,
)

from sqlalchemy.orm import Session

from app.core.config import settings

from app.database import get_db

from app.repositories.user_repository import (
    UserRepository,
)

from app.models import Customer


# =====================================================
# OAuth2
# =====================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# =====================================================
# Get Current User
# =====================================================
#
# JWT contains:
#
#     id
#     email
#     role
#     customer_id
#
# BUT:
#
# The database User record remains the source of truth.
#
# The JWT is used only to identify the authenticated user.
#
# =====================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or Expired Token",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    # =================================================
    # Decode JWT
    # =================================================

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ],
        )

        user_id = payload.get("id")

        email = payload.get("email")

        if user_id is None and email is None:

            raise credentials_exception

    except JWTError:

        raise credentials_exception

    # =================================================
    # Find User
    # =================================================
    #
    # Prefer ID because it is the primary key.
    #
    # Database remains the source of truth for:
    #
    #     role
    #     customer_id
    #     is_active
    #
    # =================================================

    user = None

    if user_id is not None:

        try:

            user = UserRepository.get_by_id(
                db,
                int(user_id),
            )

        except (
            TypeError,
            ValueError,
        ):

            raise credentials_exception

    # -------------------------------------------------
    # Fallback to Email
    # -------------------------------------------------

    if user is None and email is not None:

        user = UserRepository.get_by_email(
            db,
            str(email).strip().lower(),
        )

    # -------------------------------------------------
    # User Not Found
    # -------------------------------------------------

    if user is None:

        raise credentials_exception

    # =================================================
    # Account Status
    # =================================================

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


# =====================================================
# Generic Role Authorization
# =====================================================

def require_roles(*roles):

    allowed_roles = {
        str(role).strip().upper()
        for role in roles
    }

    def role_checker(
        current_user=Depends(
            get_current_user
        ),
    ):

        current_role = (
            current_user.role or ""
        ).strip().upper()

        if current_role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission Denied",
            )

        return current_user

    return role_checker


# =====================================================
# SUPER ADMIN
# =====================================================

def get_current_super_admin(
    current_user=Depends(
        get_current_user
    ),
):

    if (
        current_user.role or ""
    ).strip().upper() != "SUPER_ADMIN":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin Access Required",
        )

    return current_user


# =====================================================
# ADMIN
#
# SUPER_ADMIN + ADMIN
# =====================================================

def get_current_admin(
    current_user=Depends(
        get_current_user
    ),
):

    current_role = (
        current_user.role or ""
    ).strip().upper()

    if current_role not in {
        "SUPER_ADMIN",
        "ADMIN",
    }:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin Access Required",
        )

    return current_user


# =====================================================
# ENGINEER
# =====================================================

def get_current_engineer(
    current_user=Depends(
        get_current_user
    ),
):

    if (
        current_user.role or ""
    ).strip().upper() != "ENGINEER":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Engineer Access Required",
        )

    return current_user


# =====================================================
# CUSTOMER
# =====================================================
#
# CUSTOMER ROLE ONLY
#
# This is the general Customer Portal dependency.
#
# It verifies:
#
#     role == CUSTOMER
#     customer_id != NULL
#     linked customer exists
#     linked customer is active
#
# IMPORTANT:
#
# This does NOT check service_enabled.
#
# Customer Portal access and Service Portal access
# are separate concepts.
#
# =====================================================

def get_current_customer(
    current_user=Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    # -------------------------------------------------
    # 1. Verify CUSTOMER role
    # -------------------------------------------------

    if (
        current_user.role or ""
    ).strip().upper() != "CUSTOMER":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer Access Required",
        )

    # -------------------------------------------------
    # 2. Customer ID must exist
    # -------------------------------------------------

    if current_user.customer_id is None:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Customer account is not linked "
                "to a customer"
            ),
        )

    # -------------------------------------------------
    # 3. Find actual Customer record
    # -------------------------------------------------

    customer = (
        db.query(Customer)
        .filter(
            Customer.id
            == current_user.customer_id
        )
        .first()
    )

    # -------------------------------------------------
    # 4. Customer record must exist
    # -------------------------------------------------

    if not customer:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer record not found",
        )

    # -------------------------------------------------
    # 5. Customer must be active
    # -------------------------------------------------

    if not customer.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer account is inactive",
        )

    return current_user


# =====================================================
# CUSTOMER SERVICE PORTAL
# =====================================================
#
# CUSTOMER ROLE
# +
# VALID CUSTOMER
# +
# ACTIVE CUSTOMER
# +
# SERVICE ENABLED
#
# Use this dependency ONLY for service-related APIs.
#
# =====================================================

def get_current_service_customer(
    current_user=Depends(
        get_current_customer
    ),
    db: Session = Depends(
        get_db
    ),
):

    # -------------------------------------------------
    # Find the customer's actual record
    # -------------------------------------------------

    customer = (
        db.query(Customer)
        .filter(
            Customer.id
            == current_user.customer_id
        )
        .first()
    )

    # -------------------------------------------------
    # Customer record does not exist
    # -------------------------------------------------

    if not customer:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer record not found",
        )

    # -------------------------------------------------
    # Customer must be active
    # -------------------------------------------------

    if not customer.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer account is inactive",
        )

    # -------------------------------------------------
    # Service Portal Access
    # -------------------------------------------------

    if not customer.service_enabled:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Service portal access is disabled "
                "for this customer"
            ),
        )

    return current_user


# =====================================================
# CUSTOMER RENTAL PORTAL
# =====================================================
#
# CUSTOMER ROLE
# + VALID CUSTOMER
# + ACTIVE CUSTOMER
# + USER RENTAL ACCESS ENABLED
#
# Use this dependency ONLY for rental-related APIs.
# =====================================================

def get_current_rental_customer(
    current_user=Depends(
        get_current_customer
    ),
):

    # Rental portal access is controlled at USER level.
    # Rental-only customers must be allowed even when
    # service_access/service_enabled is disabled.
    rental_access = getattr(
        current_user,
        "rental_access",
        False,
    )

    if isinstance(rental_access, str):
        rental_access = rental_access.strip().lower() in {
            "true",
            "1",
            "yes",
        }

    if not rental_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Rental access is disabled "
                "for this portal user"
            ),
        )

    return current_user


# =====================================================
# NOTIFICATION USER
# =====================================================
#
# Used ONLY by the notification APIs.
#
# Allowed:
#
#     SUPER_ADMIN
#     ADMIN
#     CUSTOMER
#
# CUSTOMER validation:
#
#     role == CUSTOMER
#     customer_id exists
#     customer exists
#     customer active
#     service portal enabled
#
# This allows the same notification API to work for:
#
#     Admin Navbar
#     Customer Portal
#
# IMPORTANT:
#
# Do NOT replace get_current_admin globally.
# Other admin APIs must remain admin-only.
#
# =====================================================

def get_current_notification_user(
    current_user=Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    # -------------------------------------------------
    # Normalize Role
    # -------------------------------------------------

    current_role = (
        str(
            current_user.role or ""
        )
        .strip()
        .upper()
        .replace(" ", "_")
    )

    # =================================================
    # ADMIN / SUPER ADMIN
    # =================================================

    if current_role in {
        "SUPER_ADMIN",
        "ADMIN",
    }:

        return current_user

    # =================================================
    # ENGINEER
    # =================================================
    #
    # Engineers are allowed to use the same notification
    # API as Admin and Customer users.
    #
    # IMPORTANT:
    #
    # Notification queries already filter by:
    #
    #     Notification.user_id == current_user.id
    #
    # Therefore returning the authenticated ENGINEER here
    # ensures that an engineer only receives notifications
    # created for that engineer's own user ID.
    #
    # =================================================

    if current_role == "ENGINEER":

        return current_user

    # =================================================
    # CUSTOMER
    # =================================================

    if current_role == "CUSTOMER":

        # -------------------------------------------------
        # Customer ID must exist
        # -------------------------------------------------

        if current_user.customer_id is None:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Customer account is not linked "
                    "to a customer"
                ),
            )

        # -------------------------------------------------
        # Find Customer
        # -------------------------------------------------

        customer = (
            db.query(Customer)
            .filter(
                Customer.id
                == current_user.customer_id
            )
            .first()
        )

        # -------------------------------------------------
        # Customer must exist
        # -------------------------------------------------

        if not customer:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customer record not found",
            )

        # -------------------------------------------------
        # Customer must be active
        # -------------------------------------------------

        if not customer.is_active:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customer account is inactive",
            )

        # -------------------------------------------------
        # Notification access is independent from Service access.
        # A customer may have: Service only, Rental only, or both.
        # The notification API must therefore use the logged-in
        # user's portal module permissions instead of requiring
        # customer.service_enabled.
        # -------------------------------------------------

        service_access = getattr(
            current_user,
            "service_access",
            False,
        )

        rental_access = getattr(
            current_user,
            "rental_access",
            False,
        )

        def _enabled(value):
            if value is True or value == 1:
                return True

            if isinstance(value, str):
                return value.strip().lower() in {
                    "true",
                    "1",
                    "yes",
                }

            return False

        if not (
            _enabled(service_access)
            or _enabled(rental_access)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Customer notification access is disabled. "
                    "Enable Service or Rental portal access."
                ),
            )

        return current_user

    # =================================================
    # EVERYTHING ELSE
    # =================================================

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Notification Access Required",
    )


# =====================================================
# SALES PERSON
# =====================================================

def get_current_sales_person(
    current_user=Depends(
        get_current_user
    ),
):

    if (
        current_user.role or ""
    ).strip().upper() != "SALES_PERSON":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sales Person Access Required",
        )

    return current_user