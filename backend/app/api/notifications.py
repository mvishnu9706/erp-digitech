from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models import Notification

from app.core.dependencies import (
    get_current_notification_user,
)


# =====================================================
# Router
# =====================================================

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


# =====================================================
# GET UNREAD NOTIFICATION COUNT
# =====================================================
#
# GET:
#
#     /notifications/unread-count
#
# Works for:
#
#     ADMIN
#     SUPER_ADMIN
#     CUSTOMER
#
# =====================================================

@router.get(
    "/unread-count",
    summary="Get Unread Notification Count",
)
def get_unread_notification_count(
    current_user=Depends(
        get_current_notification_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    count = (
        db.query(Notification)
        .filter(
            Notification.user_id
            == current_user.id,

            Notification.is_read
            == False,
        )
        .count()
    )

    return {
        "success": True,
        "count": count,
    }


# =====================================================
# GET NOTIFICATIONS
# =====================================================
#
# GET:
#
#     /notifications/
#
# Returns ONLY notifications belonging to the
# currently logged-in user.
#
# =====================================================

@router.get(
    "/",
    summary="Get Notifications",
)
def get_notifications(
    current_user=Depends(
        get_current_notification_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id
            == current_user.id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )

    return {
        "success": True,

        "notifications": [
            {
                "id": notification.id,

                "user_id": notification.user_id,

                "title": notification.title,

                "message": notification.message,

                "notification_type":
                    notification.notification_type,

                "is_read":
                    notification.is_read,

                "reference_type":
                    notification.reference_type,

                "reference_id":
                    notification.reference_id,

                "created_at":
                    notification.created_at,
            }

            for notification in notifications
        ],
    }


# =====================================================
# MARK ALL NOTIFICATIONS AS READ
# =====================================================
#
# PUT:
#
#     /notifications/read-all
#
# Works for:
#
#     ADMIN
#     SUPER_ADMIN
#     CUSTOMER
#
# IMPORTANT:
#
# Only notifications belonging to the logged-in
# user are updated.
#
# =====================================================

@router.put(
    "/read-all",
    summary="Mark All Notifications As Read",
)
def mark_all_notifications_as_read(
    current_user=Depends(
        get_current_notification_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    updated_count = (
        db.query(Notification)
        .filter(
            Notification.user_id
            == current_user.id,

            Notification.is_read
            == False,
        )
        .update(
            {
                Notification.is_read: True
            },
            synchronize_session=False,
        )
    )

    db.commit()

    return {
        "success": True,

        "message": (
            "All notifications marked as read"
        ),

        "updated_count": updated_count,
    }


# =====================================================
# MARK ONE NOTIFICATION AS READ
# =====================================================
#
# PUT:
#
#     /notifications/{notification_id}/read
#
# IMPORTANT:
#
# A user can ONLY mark their own notification as read.
#
# =====================================================

@router.put(
    "/{notification_id}/read",
    summary="Mark Notification As Read",
)
def mark_notification_as_read(
    notification_id: int,

    current_user=Depends(
        get_current_notification_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    notification = (
        db.query(Notification)
        .filter(
            Notification.id
            == notification_id,

            Notification.user_id
            == current_user.id,
        )
        .first()
    )

    # -------------------------------------------------
    # Notification not found
    # -------------------------------------------------

    if not notification:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    # -------------------------------------------------
    # Mark read
    # -------------------------------------------------

    notification.is_read = True

    db.commit()

    db.refresh(
        notification
    )

    return {
        "success": True,

        "message": (
            "Notification marked as read"
        ),

        "notification": {
            "id":
                notification.id,

            "user_id":
                notification.user_id,

            "title":
                notification.title,

            "message":
                notification.message,

            "notification_type":
                notification.notification_type,

            "is_read":
                notification.is_read,

            "reference_type":
                notification.reference_type,

            "reference_id":
                notification.reference_id,

            "created_at":
                notification.created_at,
        },
    }