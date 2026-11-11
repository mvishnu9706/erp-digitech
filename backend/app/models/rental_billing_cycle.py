from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class RentalBillingCycle(Base):
    """
    Stores the single active rental billing month.

    Example:
        active_billing_month = "2026-10"

    The admin starts a new month once.
    Both admin and customer portals read this same value.
    """

    __tablename__ = "rental_billing_cycles"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    active_billing_month = Column(
        String(7),
        nullable=False,
        index=True,
    )

    cycle_started_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
