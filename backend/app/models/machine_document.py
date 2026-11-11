from sqlalchemy import (
    Column,
    Integer,
    String,
    LargeBinary,
    ForeignKey,
    DateTime,
)

from sqlalchemy.orm import relationship

from app.database import Base


class MachineDocument(Base):

    __tablename__ = "machine_documents"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =========================================================
    # MACHINE
    # =========================================================

    machine_id = Column(
        Integer,
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # =========================================================
    # RENTAL AGREEMENT
    # =========================================================

    rental_agreement = Column(
        LargeBinary,
        nullable=True
    )

    rental_agreement_name = Column(
        String(255),
        nullable=True
    )

    rental_agreement_type = Column(
        String(100),
        nullable=True
    )

    rental_agreement_size = Column(
        Integer,
        nullable=True
    )

    # =========================================================
    # INSTALLATION REPORT
    # =========================================================

    installation_report = Column(
        LargeBinary,
        nullable=True
    )

    installation_report_name = Column(
        String(255),
        nullable=True
    )

    installation_report_type = Column(
        String(100),
        nullable=True
    )

    installation_report_size = Column(
        Integer,
        nullable=True
    )

    # =========================================================
    # AUDIT
    # =========================================================

    created_at = Column(
        DateTime,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        nullable=False
    )

    # =========================================================
    # RELATIONSHIP
    # =========================================================

    machine = relationship(
        "Machine",
        back_populates="documents"
    )