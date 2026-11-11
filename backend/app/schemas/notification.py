from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):

    id: int

    title: str

    message: str

    notification_type: str

    is_read: bool

    reference_type: str | None = None

    reference_id: int | None = None

    created_at: datetime

    class Config:
        from_attributes = True