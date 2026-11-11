from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:

    @staticmethod
    def create(
        db: Session,
        notification: Notification
    ):

        db.add(notification)

        db.commit()

        db.refresh(notification)

        return notification

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int
    ):

        return (

            db.query(Notification)

            .filter(

                Notification.user_id == user_id

            )

            .order_by(

                Notification.id.desc()

            )

            .all()

        )

    @staticmethod
    def mark_read(
        db: Session,
        notification_id: int
    ):

        notification = (

            db.query(Notification)

            .filter(

                Notification.id == notification_id

            )

            .first()

        )

        if notification:

            notification.is_read = True

            db.commit()

            db.refresh(notification)

        return notification