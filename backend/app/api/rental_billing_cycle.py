from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import (
    get_current_admin,
    get_current_user,
)
from app.models.rental_billing_cycle import RentalBillingCycle
from app.models.rental_bill import RentalBill
from app.models import User, Notification


router = APIRouter(
    prefix="/rental-billing-cycle",
    tags=["Rental Billing Cycle"],
)


# ============================================================
# CURRENT MONTH
# ============================================================

def _current_month() -> str:
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"


# ============================================================
# GET OR CREATE BILLING CYCLE
# ============================================================

def _get_or_create_cycle(
    db: Session,
) -> RentalBillingCycle:

    try:

        cycle = (
            db.query(RentalBillingCycle)
            .order_by(
                RentalBillingCycle.id.asc()
            )
            .first()
        )

        if cycle:
            return cycle

        # ----------------------------------------------------
        # Find latest existing rental bill month
        # ----------------------------------------------------

        latest_bill_month = (
            db.query(
                func.max(
                    RentalBill.billing_month
                )
            )
            .scalar()
        )

        # ----------------------------------------------------
        # Create first billing cycle
        # ----------------------------------------------------

        cycle = RentalBillingCycle(
            active_billing_month=(
                latest_bill_month
                if latest_bill_month
                else _current_month()
            )
        )

        db.add(cycle)
        db.commit()
        db.refresh(cycle)

        return cycle

    except SQLAlchemyError as e:

        db.rollback()

        print(
            "\n========================================"
        )
        print(
            "RENTAL BILLING CYCLE DATABASE ERROR"
        )
        print(
            "========================================"
        )
        print(
            repr(e)
        )
        print(
            "========================================\n"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rental billing cycle database error: {str(e)}",
        )

    except Exception as e:

        db.rollback()

        print(
            "\n========================================"
        )
        print(
            "RENTAL BILLING CYCLE ERROR"
        )
        print(
            "========================================"
        )
        print(
            repr(e)
        )
        print(
            "========================================\n"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rental billing cycle error: {str(e)}",
        )


# ============================================================
# GET ACTIVE BILLING MONTH
# ============================================================

@router.get("/")
def get_active_billing_cycle(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    cycle = _get_or_create_cycle(db)

    return {
        "active_billing_month": (
            cycle.active_billing_month
        ),
        "cycle_started_at": (
            cycle.cycle_started_at
        ),
    }


# ============================================================
# ADD NEW MONTH NOTIFICATIONS
# ============================================================

def _add_new_month_notifications(
    db: Session,
    billing_month: str,
) -> int:
    """
    Create an unread in-app notification for every active
    CUSTOMER portal user when a new rental billing month starts.

    The notification is created in the same database transaction
    as the billing-cycle change.
    """

    # Only customers who actually have Rental portal access
    # should receive the new rental-month notification.
    # This includes both:
    #   - Rental-only customers
    #   - Service + Rental customers
    # and excludes Service-only customers.
    customer_users = (
        db.query(User)
        .filter(
            User.role == "CUSTOMER",
            User.is_active == True,
            User.rental_access == True,
        )
        .all()
    )

    if not customer_users:
        return 0

    month_label = datetime.strptime(
        billing_month,
        "%Y-%m",
    ).strftime("%B %Y")

    for customer_user in customer_users:
        db.add(
            Notification(
                user_id=customer_user.id,
                title="New Rental Billing Month",
                message=(
                    f"{month_label} rental billing is now open. "
                    f"Please enter your new meter reading for billing."
                ),
                notification_type="RENTAL_MONTH_STARTED",
                is_read=False,
                reference_type="RENTAL_BILLING_CYCLE",
                reference_id=None,
            )
        )

    return len(customer_users)


# ============================================================
# START NEW MONTH
# ============================================================

@router.post("/start")
def start_new_billing_month(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):

    cycle = _get_or_create_cycle(db)

    current_month = cycle.active_billing_month

    # --------------------------------------------------------
    # Validate stored month
    # --------------------------------------------------------

    try:

        year, month = map(
            int,
            current_month.split("-"),
        )

    except (
        ValueError,
        AttributeError,
    ):

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid stored rental billing month.",
        )

    if month < 1 or month > 12:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid stored rental billing month.",
        )

    # --------------------------------------------------------
    # Calculate next month
    # --------------------------------------------------------

    if month == 12:

        next_year = year + 1
        next_month = 1

    else:

        next_year = year
        next_month = month + 1

    next_billing_month = (
        f"{next_year}-{next_month:02d}"
    )

    # --------------------------------------------------------
    # Update cycle + notify all customer portal users
    # --------------------------------------------------------

    try:

        cycle.active_billing_month = (
            next_billing_month
        )

        # Create the notifications before commit so the billing
        # cycle and its customer notifications are saved together.
        customer_notifications_created = _add_new_month_notifications(
            db=db,
            billing_month=next_billing_month,
        )

        db.commit()
        db.refresh(cycle)

    except SQLAlchemyError as e:

        db.rollback()

        print(
            "\n========================================"
        )
        print(
            "START NEW MONTH DATABASE ERROR"
        )
        print(
            "========================================"
        )
        print(
            repr(e)
        )
        print(
            "========================================\n"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to start new rental month: {str(e)}",
        )

    except Exception as e:

        db.rollback()

        print(
            "\n========================================"
        )
        print(
            "START NEW MONTH ERROR"
        )
        print(
            "========================================"
        )
        print(
            repr(e)
        )
        print(
            "========================================\n"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to start new rental month: {str(e)}",
        )

    return {
        "message": (
            f"Rental billing month changed from "
            f"{current_month} to "
            f"{next_billing_month}."
        ),

        "previous_billing_month": (
            current_month
        ),

        "active_billing_month": (
            next_billing_month
        ),

        "cycle_started_at": (
            cycle.cycle_started_at
        ),

        "customer_notifications_created": (
            customer_notifications_created
        ),
    }
