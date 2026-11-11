from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    DateTime,
    Text
)

from sqlalchemy.sql import func

from app.database import Base


class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # Journal Entry
    # =====================================================

    journal_entry_id = Column(
        Integer,
        ForeignKey("journal_entries.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Ledger Account
    # =====================================================

    account_id = Column(
        Integer,
        ForeignKey("chart_of_accounts.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Debit
    # =====================================================

    debit = Column(
        Numeric(12,2),
        default=0
    )

    # =====================================================
    # Credit
    # =====================================================

    credit = Column(
        Numeric(12,2),
        default=0
    )

    # =====================================================
    # Description
    # =====================================================

    description = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # Audit
    # =====================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )