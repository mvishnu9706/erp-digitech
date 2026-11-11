from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.auth import (
    Token,
    LoginRequest,
)

from app.services.auth_service import (
    AuthService,
)

from app.core.dependencies import (
    get_current_user,
)


# =====================================================
# Router
# =====================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =====================================================
# Login
# =====================================================
#
# User can login using:
#
# Email + Password
#
# OR
#
# Mobile + Password
#
# CUSTOMER users use the same users table as:
#
# ADMIN
# ENGINEER
# SALES_PERSON
#
# CUSTOMER mapping:
#
# users.role = "CUSTOMER"
# users.customer_id = customers.id
#
# =====================================================

@router.post(
    "/login",
    response_model=Token,
    summary="User Login",
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user using either email or
    mobile number and return a JWT access token.
    """

    token = AuthService.login(
        db=db,
        identifier=login_data.identifier,
        password=login_data.password,
    )

    # -------------------------------------------------
    # Invalid Login
    # -------------------------------------------------

    if token is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=(
                "Invalid Email/Mobile or Password"
            ),

            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    return token


# =====================================================
# Current Logged-in User
# =====================================================
#
# GET /auth/me
#
# IMPORTANT:
#
# service_access and rental_access come directly
# from the database User record.
#
# These values control Customer Portal modules.
#
# service_access = True
#     Customer can access Service Portal.
#
# rental_access = True
#     Customer can access Rental Portal.
#
# Possible combinations:
#
# True  / False = Service only
# False / True  = Rental only
# True  / True  = Service + Rental
# False / False = No Portal Access
#
# =====================================================

@router.get(
    "/me",
    summary="Get Current Logged-in User",
)
def get_logged_in_user(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Returns the currently authenticated user.

    The database user is the source of truth for
    service_access and rental_access.
    """

    return {

        # -------------------------------------------------
        # Basic User Information
        # -------------------------------------------------

        "id":
            current_user.id,

        "company_name":
            current_user.company_name,

        "contact_person_name":
            current_user.contact_person_name,

        "full_name":
            current_user.full_name,

        "email":
            current_user.email,

        "phone":
            current_user.phone,

        "role":
            current_user.role,

        "customer_id":
            current_user.customer_id,

        "is_active":
            current_user.is_active,

        # -------------------------------------------------
        # Customer Portal Module Access
        # -------------------------------------------------

        "service_access":
            bool(
                getattr(
                    current_user,
                    "service_access",
                    False,
                )
            ),

        "rental_access":
            bool(
                getattr(
                    current_user,
                    "rental_access",
                    False,
                )
            ),
    }


# =====================================================
# Logout
# =====================================================
#
# JWT authentication is stateless.
#
# The frontend removes its stored authentication
# session when the user logs out.
#
# =====================================================

@router.post(
    "/logout",
    summary="Logout User",
)
def logout():
    """
    JWT authentication is stateless.

    The frontend should remove the stored access token
    when the user logs out.
    """

    return {

        "success":
            True,

        "message":
            "Logout Successful. Please remove the token from the client.",
    }