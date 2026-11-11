from sqlalchemy import (
    Column, Integer, String, Date, DateTime, ForeignKey, Numeric, Text,
    UniqueConstraint, LargeBinary,
)
from sqlalchemy.sql import func

from app.database import Base


class RentalBill(Base):
    __tablename__ = "rental_bills"

    id = Column(Integer, primary_key=True, index=True)
    bill_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id", ondelete="RESTRICT"), nullable=False, index=True)
    billing_month = Column(String(7), nullable=False, index=True)
    billing_date = Column(Date, nullable=False)

    # Legacy aggregate fields retained for older ERP functionality.
    previous_meter = Column(Integer, nullable=False, default=0)
    current_meter = Column(Integer, nullable=False)
    copies_used = Column(Integer, nullable=False, default=0)
    cost_per_copy = Column(Numeric(12, 2), nullable=False, default=0)

    # LEGACY for old bills; FOUR_TYPE for the new billing calculation.
    billing_mode = Column(String(20), nullable=False, default="LEGACY", server_default="LEGACY")

    # A4 Black and White
    a4_bw_previous_meter = Column(Integer, nullable=False, default=0, server_default="0")
    a4_bw_current_meter = Column(Integer, nullable=False, default=0, server_default="0")
    a4_bw_copies_used = Column(Integer, nullable=False, default=0, server_default="0")
    a4_bw_free_copies = Column(Integer, nullable=False, default=0, server_default="0")
    a4_bw_rate = Column(Numeric(12, 4), nullable=False, default=0, server_default="0")
    a4_bw_amount = Column(Numeric(12, 2), nullable=False, default=0, server_default="0")

    # A4 Color
    a4_color_previous_meter = Column(Integer, nullable=False, default=0, server_default="0")
    a4_color_current_meter = Column(Integer, nullable=False, default=0, server_default="0")
    a4_color_copies_used = Column(Integer, nullable=False, default=0, server_default="0")
    a4_color_free_copies = Column(Integer, nullable=False, default=0, server_default="0")
    a4_color_rate = Column(Numeric(12, 4), nullable=False, default=0, server_default="0")
    a4_color_amount = Column(Numeric(12, 2), nullable=False, default=0, server_default="0")

    # A3 Black and White
    a3_bw_previous_meter = Column(Integer, nullable=False, default=0, server_default="0")
    a3_bw_current_meter = Column(Integer, nullable=False, default=0, server_default="0")
    a3_bw_copies_used = Column(Integer, nullable=False, default=0, server_default="0")
    a3_bw_free_copies = Column(Integer, nullable=False, default=0, server_default="0")
    a3_bw_rate = Column(Numeric(12, 4), nullable=False, default=0, server_default="0")
    a3_bw_amount = Column(Numeric(12, 2), nullable=False, default=0, server_default="0")

    # A3 Color
    a3_color_previous_meter = Column(Integer, nullable=False, default=0, server_default="0")
    a3_color_current_meter = Column(Integer, nullable=False, default=0, server_default="0")
    a3_color_copies_used = Column(Integer, nullable=False, default=0, server_default="0")
    a3_color_free_copies = Column(Integer, nullable=False, default=0, server_default="0")
    a3_color_rate = Column(Numeric(12, 4), nullable=False, default=0, server_default="0")
    a3_color_amount = Column(Numeric(12, 2), nullable=False, default=0, server_default="0")

    # Rental and shared free-copy allowance.
    rental_amount = Column(Numeric(12, 2), nullable=False, default=0, server_default="0")
    free_copy_allowance = Column(Integer, nullable=False, default=0, server_default="0")
    free_copies_applied = Column(Integer, nullable=False, default=0, server_default="0")

    # Billing totals.
    copy_charges_amount = Column(Numeric(12, 2), nullable=False, default=0, server_default="0")
    subtotal_amount = Column(Numeric(12, 2), nullable=False, default=0, server_default="0")
    gst_rate = Column(Numeric(5, 2), nullable=False, default=0, server_default="0")
    gst_amount = Column(Numeric(12, 2), nullable=False, default=0, server_default="0")

    # Final amount, including GST for FOUR_TYPE bills.
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)

    # Existing payment tracking.
    payment_status = Column(String(20), nullable=False, default="PENDING", index=True)
    paid_amount = Column(Numeric(12, 2), nullable=False, default=0)
    outstanding_amount = Column(Numeric(12, 2), nullable=False, default=0)
    remarks = Column(Text, nullable=True)

    # Rental bill PDF fields: map to existing columns in public.rental_bills.
    pdf_file = Column(LargeBinary, nullable=True)
    pdf_file_name = Column(String(255), nullable=True)
    pdf_content_type = Column(String(100), nullable=True, default="application/pdf")
    pdf_generated_at = Column(DateTime(timezone=True), nullable=True)

    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("machine_id", "billing_month", name="uq_rental_bill_machine_month"),
    )
