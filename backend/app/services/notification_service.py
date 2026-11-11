from sqlalchemy.orm import Session

from app.models.notification import Notification

from app.repositories.notification_repository import (
    NotificationRepository
)


class NotificationService:

    @staticmethod
    def send(

        db: Session,

        user_id: int,

        title: str,

        message: str,

        notification_type="SYSTEM",

        reference_type=None,

        reference_id=None

    ):

        notification = Notification(

            user_id=user_id,

            title=title,

            message=message,

            notification_type=notification_type,

            reference_type=reference_type,

            reference_id=reference_id

        )

        return NotificationRepository.create(
            db,
            notification
        )

    @staticmethod
    def get_notifications(
        db: Session,
        user_id: int
    ):

        return NotificationRepository.get_user_notifications(
            db,
            user_id
        )

    @staticmethod
    def mark_read(
        db: Session,
        notification_id: int
    ):

        return NotificationRepository.mark_read(
            db,
            notification_id
        )