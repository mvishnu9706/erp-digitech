from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Text
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ServiceSparePart(Base):

    __tablename__ = "service_spare_parts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    service_visit_id = Column(
        Integer,
        ForeignKey("service_visits.id"),
        nullable=False,
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True
    )

    quantity = Column(
        Numeric(12,2),
        nullable=False
    )

    unit_price = Column(
        Numeric(12,2),
        default=0
    )

    total_price = Column(
        Numeric(12,2),
        default=0
    )

    is_billable = Column(
        Integer,
        default=1
    )

    remarks = Column(Text)

    created_by = Column(
        Integer,
        ForeignKey("users.id")
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    service_visit = relationship(
        "ServiceVisit"
    )

    product = relationship(
        "Product"
    )

    warehouse = relationship(
        "Warehouse"
    )