from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):

    __tablename__ = "users"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # Company Information
    # =====================================================

    company_name = Column(
        String(200),
        nullable=True
    )

    contact_person_name = Column(
        String(150),
        nullable=True
    )

    # =====================================================
    # User Information
    # =====================================================

    full_name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    phone = Column(
        String(20),
        nullable=True
    )

    # =====================================================
    # Authentication
    # =====================================================
    #
    # password:
    #     Hashed password used for authentication.
    #
    # IMPORTANT:
    #     This field must contain ONLY the password hash.
    #
    # =====================================================

    password = Column(
        String(255),
        nullable=False
    )

    # =====================================================
    # PORTAL PASSWORD
    # =====================================================
    #
    # Stores the original portal password separately,
    # according to the requested portal-management design.
    #
    # This field is NOT used for authentication.
    #
    # Authentication always uses:
    #
    #     password
    #
    # =====================================================

    portal_password = Column(
        String(255),
        nullable=True
    )

    # =====================================================
    # Role
    # =====================================================

    role = Column(
        String(50),
        nullable=False,
        default="CUSTOMER",
        index=True
    )

    # =====================================================
    # CUSTOMER LINK
    # =====================================================
    #
    # CUSTOMER user:
    #
    #     users.customer_id -> customers.id
    #
    # Internal users:
    #
    #     customer_id = NULL
    #
    # unique=True means:
    #
    #     one customer = one CUSTOMER login
    #
    # =====================================================

    customer_id = Column(
        Integer,
        ForeignKey(
            "customers.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        unique=True,
        index=True
    )

    # =====================================================
    # CUSTOMER PORTAL MODULE ACCESS
    # =====================================================
    #
    # These two fields control which modules a CUSTOMER
    # can access from the Customer Portal.
    #
    # service_access:
    #     True  -> Customer can access Service
    #     False -> Customer cannot access Service
    #
    # rental_access:
    #     True  -> Customer can access Rental / AMC
    #     False -> Customer cannot access Rental / AMC
    #
    # Possible combinations:
    #
    # service_access=True
    # rental_access=False
    #     -> Service only
    #
    # service_access=False
    # rental_access=True
    #     -> Rental only
    #
    # service_access=True
    # rental_access=True
    #     -> Rental + Service
    #
    # service_access=False
    # rental_access=False
    #     -> No module access
    #
    # =====================================================

    service_access = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True
    )

    rental_access = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True
    )

    # =====================================================
    # Account Status
    # =====================================================

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True
    )

    # =====================================================
    # Audit
    # =====================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # =====================================================
    # CUSTOMER RELATIONSHIP
    # =====================================================

    customer = relationship(
        "Customer",
        foreign_keys=[customer_id],
        back_populates="portal_user",
        uselist=False,
    )