from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    UniqueConstraint,
)

from app.database import Base


class RolePermission(Base):

    __tablename__ = "role_permissions"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # =====================================================
    # ROLE
    # =====================================================
    #
    # Supported roles:
    #
    # ADMIN
    # CUSTOMER
    # ENGINEER
    # SALES_PERSON
    #
    # SUPER_ADMIN is intentionally NOT stored here.
    #
    # SUPER_ADMIN automatically has:
    #
    # Access  = TRUE
    # View    = TRUE
    # Create  = TRUE
    # Update  = TRUE
    # Delete  = TRUE
    #
    # =====================================================

    role = Column(
        String(50),
        nullable=False,
        index=True,
    )

    # =====================================================
    # PAGE
    # =====================================================
    #
    # Examples:
    #
    # DASHBOARD
    # PRODUCT_MASTER
    # CUSTOMERS
    # SUPPLIERS
    # PURCHASE
    # SALES
    # INVENTORY
    # SERVICE
    # RENTAL_AMC
    # REPORTS
    # SETTINGS
    #
    # =====================================================

    page = Column(
        String(100),
        nullable=False,
        index=True,
    )

    # =====================================================
    # ACCESS
    # =====================================================
    #
    # Controls whether the user can access the page.
    #
    # TRUE:
    #     Page can be shown/accessed.
    #
    # FALSE:
    #     Page should not be shown in the sidebar
    #     and direct page navigation should be blocked.
    #
    # =====================================================

    can_access = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # =====================================================
    # VIEW
    # =====================================================
    #
    # Controls whether the user can view/read data
    # on the page.
    #
    # =====================================================

    can_view = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # =====================================================
    # CREATE
    # =====================================================

    can_create = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # =====================================================
    # UPDATE
    # =====================================================

    can_update = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # =====================================================
    # DELETE
    # =====================================================

    can_delete = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # =====================================================
    # CONSTRAINT
    # =====================================================
    #
    # One role can have only ONE permission record
    # for each page.
    #
    # Example:
    #
    # SALES_PERSON + SALES
    #
    # can exist only once.
    #
    # =====================================================

    __table_args__ = (
        UniqueConstraint(
            "role",
            "page",
            name="uq_role_permissions_role_page",
        ),
    )