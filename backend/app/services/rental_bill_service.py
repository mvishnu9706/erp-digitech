from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.machine import Machine
from app.models.rental_bill import RentalBill
from app.models.user import User
from app.models.notification import Notification

from app.repositories.customer_repository import CustomerRepository
from app.repositories.machine_repository import MachineRepository
from app.repositories.rental_bill_repository import RentalBillRepository

from app.schemas.rental_bill import (
    RentalBillCreate,
    RentalBillPaymentUpdate,
    RentalBillUpdate,
)


class RentalBillService:

    # ============================================================
    # INTERNAL HELPERS
    # ============================================================

    @staticmethod
    def _get_customer(
        db: Session,
        customer_id: int,
    ) -> Customer:
        customer = CustomerRepository.get_by_id(
            db=db,
            customer_id=customer_id,
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        return customer

    # ------------------------------------------------------------

    @staticmethod
    def _get_customer_machine(
        db: Session,
        customer_id: int,
        machine_id: int,
    ) -> Machine:

        machine = MachineRepository.get_by_id(
            db=db,
            machine_id=machine_id,
        )

        if machine is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Machine not found.",
            )

        # --------------------------------------------------------
        # IMPORTANT:
        # Machine must belong to the logged-in customer.
        # --------------------------------------------------------

        if machine.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this machine.",
            )

        # --------------------------------------------------------
        # Only active machines can receive meter readings.
        # --------------------------------------------------------

        if hasattr(machine, "is_active") and machine.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This machine is inactive.",
            )

        if (
            hasattr(machine, "status")
            and machine.status
            and str(machine.status).upper() not in {
                "ACTIVE",
                "RUNNING",
            }
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This machine is not active.",
            )

        return machine

    # ------------------------------------------------------------

    @staticmethod
    def _validate_billing_month(
        billing_month: str,
    ) -> str:

        if not billing_month:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Billing month is required.",
            )

        billing_month = str(billing_month).strip()

        try:
            datetime.strptime(
                billing_month,
                "%Y-%m",
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Billing month must be in YYYY-MM format.",
            )

        return billing_month


    # ------------------------------------------------------------

    @staticmethod
    def _validate_billing_date(
        billing_date,
        billing_month: str,
    ):
        """Validate and return the reading/billing date."""
        if billing_date is None:
            billing_date = datetime.now().date()

        if not hasattr(billing_date, "year"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Billing date must be a valid date.",
            )

        expected_year, expected_month = map(
            int,
            billing_month.split("-"),
        )

        if (
            billing_date.year != expected_year
            or billing_date.month != expected_month
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Billing date must belong to billing month "
                    f"{billing_month}."
                ),
            )

        return billing_date

    # ------------------------------------------------------------

    @staticmethod
    def _validate_payment_status(
        payment_status: str,
    ) -> str:

        if payment_status is None:
            return "PENDING"

        value = str(payment_status).strip().upper()

        allowed_statuses = {
            "PENDING",
            "RECEIVED",
            "CANCELLED",
        }

        if value not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid payment status. "
                    "Allowed values: PENDING, RECEIVED, CANCELLED."
                ),
            )

        return value

    # ------------------------------------------------------------

    @staticmethod
    def _decimal(
        value,
        default="0",
    ) -> Decimal:

        if value is None:
            return Decimal(default)

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid monetary value.",
            )

    # ------------------------------------------------------------

    @staticmethod
    def _generate_bill_number(
        db: Session,
        billing_month: str,
    ) -> str:

        # --------------------------------------------------------
        # Generate using database ID after flush.
        #
        # create_bill() initially creates TEMP and then replaces
        # it after the database assigns the bill ID.
        # --------------------------------------------------------

        return f"RB-{billing_month.replace('-', '')}"

    # ============================================================
    # GET CUSTOMER MACHINES
    # ============================================================

    @staticmethod
    def get_customer_machines(
        db: Session,
        customer_id: int,
    ):

        RentalBillService._get_customer(
            db=db,
            customer_id=customer_id,
        )

        # --------------------------------------------------------
        # Use the existing Machine repository if it exposes the
        # customer-specific method.
        # --------------------------------------------------------

        if hasattr(MachineRepository, "get_by_customer"):

            machines = MachineRepository.get_by_customer(
                db=db,
                customer_id=customer_id,
            )

        elif hasattr(MachineRepository, "get_customer_machines"):

            machines = MachineRepository.get_customer_machines(
                db=db,
                customer_id=customer_id,
            )

        else:
            # Safe fallback using SQLAlchemy directly.
            query = db.query(Machine).filter(
                Machine.customer_id == customer_id
            )

            if hasattr(Machine, "is_active"):
                query = query.filter(
                    Machine.is_active.is_(True)
                )

            machines = query.order_by(
                Machine.id.asc()
            ).all()

        # Customer rental portal receives the current machine price.
        # This is READ-ONLY for the customer. The value always comes
        # directly from Machine.cost_per_copy, which is maintained by admin.
        return [
            {
                "id": machine.id,
                "machine_id": machine.id,
                "machine_number": machine.machine_number,
                "machine_name": getattr(machine, "machine_name", None),
                "serial_number": machine.serial_number,
                "asset_tag": getattr(machine, "asset_tag", None),
                "customer_id": machine.customer_id,
                "product_id": getattr(machine, "product_id", None),

                "opening_meter": getattr(machine, "opening_meter", 0),
                "current_meter": getattr(machine, "current_meter", 0),
                "a4_bw_current_meter": getattr(machine, "a4_bw_current_meter", 0),
                "a4_color_current_meter": getattr(machine, "a4_color_current_meter", 0),
                "a3_bw_current_meter": getattr(machine, "a3_bw_current_meter", 0),
                "a3_color_current_meter": getattr(machine, "a3_color_current_meter", 0),
                # Individual monthly free-copy allowances configured on the machine.
                "a4_bw_free_copies": getattr(machine, "a4_bw_free_copies", 0),
                "a4_color_free_copies": getattr(machine, "a4_color_free_copies", 0),
                "a3_bw_free_copies": getattr(machine, "a3_bw_free_copies", 0),
                "a3_color_free_copies": getattr(machine, "a3_color_free_copies", 0),
                "free_prints_per_month": getattr(machine, "free_prints_per_month", 0),
                "a4_bw_rate": getattr(machine, "a4_bw_rate", 0),
                "a4_color_rate": getattr(machine, "a4_color_rate", 0),
                "a3_bw_rate": getattr(machine, "a3_bw_rate", 0),
                "a3_color_rate": getattr(machine, "a3_color_rate", 0),

                # IMPORTANT: admin-configured rental price
                "cost_per_copy": (
                    machine.cost_per_copy
                    if machine.cost_per_copy is not None
                    else 0
                ),

                # Compatibility with older frontend code
                "costPerCopy": (
                    machine.cost_per_copy
                    if machine.cost_per_copy is not None
                    else 0
                ),
                "rate_per_copy": (
                    machine.cost_per_copy
                    if machine.cost_per_copy is not None
                    else 0
                ),

                "rental_rate": getattr(machine, "rental_rate", None),
                "status": getattr(machine, "status", None),
                "is_active": getattr(machine, "is_active", True),
                "remarks": getattr(machine, "remarks", None),
            }
            for machine in machines
            if getattr(machine, "is_active", True)
        ]


    # ============================================================
    # RENTAL NOTIFICATION HELPERS
    # ============================================================

    @staticmethod
    def _get_customer_portal_user(
        db: Session,
        customer_id: int,
    ):
        """
        Find the active CUSTOMER portal user for a customer.

        Primary mapping:
            users.customer_id -> customers.id

        Email is used as a fallback for older customer portal records.
        """
        if not customer_id:
            return None

        query = db.query(User).filter(
            User.role == "CUSTOMER",
            User.is_active == True,
        )

        customer_id_column = getattr(User, "customer_id", None)

        if customer_id_column is not None:
            portal_user = (
                query
                .filter(customer_id_column == customer_id)
                .first()
            )

            if portal_user:
                return portal_user

        customer = CustomerRepository.get_by_id(
            db=db,
            customer_id=customer_id,
        )

        customer_email = (
            getattr(customer, "email", None)
            if customer
            else None
        )

        if customer_email:
            return (
                query
                .filter(
                    User.email
                    == str(customer_email).strip().lower()
                )
                .first()
            )

        return None

    # ------------------------------------------------------------

    @staticmethod
    def _get_customer_display_name(
        customer,
    ) -> str:
        """Return a useful customer/company name for notifications."""

        if not customer:
            return "Customer"

        return (
            getattr(customer, "company_name", None)
            or getattr(customer, "customer_name", None)
            or getattr(customer, "name", None)
            or getattr(customer, "contact_person_name", None)
            or getattr(customer, "full_name", None)
            or getattr(customer, "email", None)
            or "Customer"
        )

    # ------------------------------------------------------------

    @staticmethod
    def _add_admin_reading_notification(
        db: Session,
        bill: RentalBill,
        customer,
    ) -> int:
        """
        Notify every active ADMIN / SUPER_ADMIN when a customer
        successfully submits a rental reading.

        The caller commits the transaction.
        """

        admins = (
            db.query(User)
            .filter(
                User.role.in_(["ADMIN", "SUPER_ADMIN"]),
                User.is_active == True,
            )
            .all()
        )

        if not admins:
            return 0

        customer_name = (
            RentalBillService._get_customer_display_name(customer)
        )

        month_label = datetime.strptime(
            bill.billing_month,
            "%Y-%m",
        ).strftime("%B %Y")

        for admin in admins:
            db.add(
                Notification(
                    user_id=admin.id,
                    title="Rental Reading Updated",
                    message=(
                        f"{customer_name} submitted the meter reading "
                        f"for {month_label}. The rental reading has been "
                        f"updated successfully for this month."
                    ),
                    notification_type="RENTAL_READING_SUBMITTED",
                    is_read=False,
                    reference_type="RENTAL_BILL",
                    reference_id=bill.id,
                )
            )

        return len(admins)

    # ------------------------------------------------------------

    @staticmethod
    def _add_customer_bill_update_notification(
        db: Session,
        bill: RentalBill,
        customer,
        reading_changed: bool,
        price_changed: bool,
    ) -> bool:
        """
        Notify the specific customer when an admin changes the
        selected rental bill's reading and/or price.

        The caller commits the transaction.
        """

        customer_user = (
            RentalBillService._get_customer_portal_user(
                db=db,
                customer_id=bill.customer_id,
            )
        )

        if not customer_user:
            return False

        month_label = datetime.strptime(
            bill.billing_month,
            "%Y-%m",
        ).strftime("%B %Y")

        if reading_changed and price_changed:
            change_text = "readings and price"
        elif reading_changed:
            change_text = "reading"
        elif price_changed:
            change_text = "price"
        else:
            return False

        db.add(
            Notification(
                user_id=customer_user.id,
                title="Rental Billing Updated",
                message=(
                    "Digitech Imaging Solutions changed your "
                    f"rental billing {change_text} for "
                    f"{month_label}. Please check your rental "
                    "billing details."
                ),
                notification_type="RENTAL_BILL_UPDATED",
                is_read=False,
                reference_type="RENTAL_BILL",
                reference_id=bill.id,
            )
        )

        return True

    @staticmethod
    def _calculate_four_type_breakdown(previous_readings, current_readings, rates, free_allowances):
        """Calculate each print type independently using its own free-copy allowance."""
        keys = ("a4_bw", "a4_color", "a3_bw", "a3_color")
        used = {}
        total_used = 0
        for key in keys:
            previous = int(previous_readings[key])
            current = int(current_readings[key])
            if current < previous:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{key} current reading cannot be less than previous reading ({previous}).",
                )
            used[key] = current - previous
            total_used += used[key]

        # free_allowances is a mapping keyed by print type. Do not share or
        # proportionally distribute allowances between A4/A3 or B/W/Color.
        free_by_type = {
            key: min(used[key], max(0, int((free_allowances or {}).get(key, 0) or 0)))
            for key in keys
        }

        result = {}
        copy_charges = Decimal("0.00")
        chargeable_total = 0
        free_total = sum(free_by_type.values())
        for key in keys:
            rate = RentalBillService._decimal(rates[key])
            chargeable = used[key] - free_by_type[key]
            amount = (Decimal(chargeable) * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            result[key] = {
                "previous_meter": int(previous_readings[key]),
                "current_meter": int(current_readings[key]),
                "copies_used": used[key],
                "free_copies": free_by_type[key],
                "rate": rate,
                "amount": amount,
            }
            copy_charges += amount
            chargeable_total += chargeable
        return result, total_used, free_total, copy_charges.quantize(Decimal("0.01")), chargeable_total

    # ============================================================
    # CREATE RENTAL BILL
    # ============================================================

    @staticmethod
    def create_bill(db: Session, customer_id: int, data: RentalBillCreate, current_user: User):
        try:
            customer = RentalBillService._get_customer(db=db, customer_id=customer_id)
            machine = RentalBillService._get_customer_machine(
                db=db, customer_id=customer_id, machine_id=data.machine_id
            )
            billing_month = RentalBillService._validate_billing_month(data.billing_month)
            existing_bill = RentalBillRepository.get_by_machine_and_month(
                db=db, machine_id=machine.id, billing_month=billing_month
            )
            if existing_bill is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rental bill already exists for this machine for the selected month.",
                )

            billing_date = RentalBillService._validate_billing_date(data.billing_date, billing_month)
            payment_status = RentalBillService._validate_payment_status(getattr(data, "payment_status", None))
            keys = ("a4_bw", "a4_color", "a3_bw", "a3_color")
            current_field_names = {
                "a4_bw": "a4_bw_current_meter",
                "a4_color": "a4_color_current_meter",
                "a3_bw": "a3_bw_current_meter",
                "a3_color": "a3_color_current_meter",
            }
            new_mode = any(getattr(data, name, None) is not None for name in current_field_names.values())

            if new_mode:
                previous_readings = {
                    key: int(getattr(machine, current_field_names[key], 0) or 0)
                    for key in keys
                }
                current_readings = {
                    key: int(getattr(data, current_field_names[key], None)
                             if getattr(data, current_field_names[key], None) is not None
                             else previous_readings[key])
                    for key in keys
                }
                rates = {
                    "a4_bw": RentalBillService._decimal(getattr(machine, "a4_bw_rate", 0)),
                    "a4_color": RentalBillService._decimal(getattr(machine, "a4_color_rate", 0)),
                    "a3_bw": RentalBillService._decimal(getattr(machine, "a3_bw_rate", 0)),
                    "a3_color": RentalBillService._decimal(getattr(machine, "a3_color_rate", 0)),
                }
                breakdown, copies_used, free_applied, copy_charges, chargeable_total = (
                    RentalBillService._calculate_four_type_breakdown(
                        previous_readings, current_readings, rates,
                        {
                            "a4_bw": getattr(machine, "a4_bw_free_copies", 0),
                            "a4_color": getattr(machine, "a4_color_free_copies", 0),
                            "a3_bw": getattr(machine, "a3_bw_free_copies", 0),
                            "a3_color": getattr(machine, "a3_color_free_copies", 0),
                        },
                    )
                )
                rental_amount = RentalBillService._decimal(getattr(machine, "rental_rate", 0)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                subtotal_amount = (rental_amount + copy_charges).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                gst_rate = Decimal("18.00")
                gst_amount = (subtotal_amount * gst_rate / Decimal("100")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                total_amount = subtotal_amount + gst_amount
                aggregate_previous = sum(previous_readings.values())
                aggregate_current = sum(current_readings.values())
                weighted_rate = (copy_charges / Decimal(chargeable_total)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ) if chargeable_total else Decimal("0.00")
                free_allowance_snapshot = sum(
                    max(0, int(getattr(machine, f"{key}_free_copies", 0) or 0))
                    for key in keys
                )
                billing_mode = "FOUR_TYPE"
            else:
                # Legacy single-meter path remains unchanged for existing clients.
                previous_reading = int(machine.current_meter or 0)
                if data.current_meter is None:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="current_meter is required for legacy single-meter billing.",
                    )
                current_reading = int(data.current_meter)
                if current_reading < previous_reading:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Current meter cannot be less than previous meter ({previous_reading}).",
                    )
                copies_used = current_reading - previous_reading
                submitted_price = getattr(data, "cost_per_copy", None)
                cost_per_copy = RentalBillService._decimal(
                    submitted_price if submitted_price is not None else machine.cost_per_copy,
                    default="0",
                )
                if cost_per_copy < 0:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Machine cost per copy cannot be negative.")
                total_amount = (Decimal(copies_used) * cost_per_copy).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                aggregate_previous = previous_reading
                aggregate_current = current_reading
                weighted_rate = cost_per_copy
                rental_amount = Decimal("0.00")
                free_allowance_snapshot = 0
                free_applied = 0
                copy_charges = total_amount
                subtotal_amount = total_amount
                gst_rate = Decimal("0.00")
                gst_amount = Decimal("0.00")
                breakdown = {
                    key: {"previous_meter": 0, "current_meter": 0, "copies_used": 0,
                          "free_copies": 0, "rate": Decimal("0.00"), "amount": Decimal("0.00")}
                    for key in keys
                }
                current_readings = {}
                billing_mode = "LEGACY"

            if payment_status == "RECEIVED":
                paid_amount = total_amount
                outstanding_amount = Decimal("0.00")
            else:
                paid_amount = Decimal("0.00")
                outstanding_amount = total_amount

            bill_values = dict(
                bill_number="TEMP", customer_id=customer.id, machine_id=machine.id,
                billing_month=billing_month, billing_date=billing_date,
                previous_meter=aggregate_previous, current_meter=aggregate_current,
                copies_used=copies_used, cost_per_copy=weighted_rate,
                total_amount=total_amount, payment_status=payment_status,
                paid_amount=paid_amount, outstanding_amount=outstanding_amount,
                remarks=getattr(data, "remarks", None), created_by=current_user.id,
                updated_by=current_user.id, billing_mode=billing_mode,
                rental_amount=rental_amount, free_copy_allowance=free_allowance_snapshot,
                free_copies_applied=free_applied, copy_charges_amount=copy_charges,
                subtotal_amount=subtotal_amount, gst_rate=gst_rate, gst_amount=gst_amount,
            )
            for key in keys:
                item = breakdown[key]
                for suffix in ("previous_meter", "current_meter", "copies_used", "free_copies", "rate", "amount"):
                    bill_values[f"{key}_{suffix}"] = item[suffix]
            bill = RentalBill(**bill_values)
            db.add(bill)
            db.flush()
            # Format: DISRB + bill-generation date (YYYYMMDD) + database ID (6 digits).
            # Example: DISRB20261017000024
            bill.bill_number = f"DISRB{datetime.now():%Y%m%d}{bill.id:06d}"

            if new_mode:
                for key, field_name in current_field_names.items():
                    setattr(machine, field_name, current_readings[key])
                # Keep legacy single-meter consumers aligned to A4 B/W.
                machine.current_meter = current_readings["a4_bw"]
            else:
                machine.current_meter = aggregate_current
            if hasattr(machine, "updated_by"):
                machine.updated_by = current_user.id

            customer_name = RentalBillService._get_customer_display_name(customer)
            admin_notifications_created = 0
            if str(getattr(current_user, "role", "")).strip().upper() == "CUSTOMER":
                admin_notifications_created = RentalBillService._add_admin_reading_notification(
                    db=db, bill=bill, customer=customer
                )
                if admin_notifications_created:
                    print(f"RENTAL READING NOTIFICATION: created {admin_notifications_created} admin notification(s) for {customer_name} - {billing_month}")

            db.commit()
            db.refresh(bill)
            db.refresh(machine)
            return bill
        except HTTPException:
            db.rollback()
            raise
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A rental bill already exists for this machine and billing month.",
            )
        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Rental bill creation failed: {str(exc)}",
            )

    # ============================================================
    # GENERATE PDF ON THE BACKEND AND SAVE TO POSTGRESQL
    # ============================================================

    @staticmethod
    def generate_and_save_bill_pdf(db: Session, bill_id: int):
        """Generate a rental invoice PDF from database values and persist it."""
        from io import BytesIO
        from xml.sax.saxutils import escape
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

        bill = RentalBillRepository.get_by_id(db=db, bill_id=bill_id)
        if bill is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rental bill not found.")

        machine = db.query(Machine).filter(Machine.id == bill.machine_id).first()
        customer = CustomerRepository.get_by_id(db=db, customer_id=bill.customer_id)
        if customer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer for this rental bill was not found.")

        def val(obj, field, default=""):
            value = getattr(obj, field, default) if obj is not None else default
            return default if value is None else value

        def money(value):
            try:
                return f"Rs. {Decimal(str(value or 0)):,.2f}"
            except Exception:
                return "Rs. 0.00"

        customer_name = RentalBillService._get_customer_display_name(customer)
        bill_number = str(val(bill, "bill_number", f"RENTAL-{bill.id}"))
        file_name = f"{bill_number}.pdf"
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm,
            topMargin=14*mm, bottomMargin=14*mm,
            title=f"Rental Invoice {bill_number}", author="Digitech Imaging Solutions"
        )
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="InvoiceTitle", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#17365D"), spaceAfter=5))
        styles.add(ParagraphStyle(name="SmallText", parent=styles["BodyText"], fontSize=8, leading=10))
        story = [
            Paragraph("DIGITECH IMAGING SOLUTIONS", styles["Heading1"]),
            Paragraph("RENTAL BILL / TAX INVOICE", styles["InvoiceTitle"]),
            Spacer(1, 5*mm),
        ]

        details = [
            ["Bill Number", escape(bill_number), "Billing Month", escape(str(val(bill, "billing_month", "-")))],
            ["Billing Date", escape(str(val(bill, "billing_date", "-"))), "Payment Status", escape(str(val(bill, "payment_status", "PENDING")))],
            ["Customer", escape(str(customer_name)), "Machine", escape(str(val(machine, "machine_name", val(machine, "machine_number", "-"))))],
            ["Serial Number", escape(str(val(machine, "serial_number", "-"))), "Machine ID", str(val(bill, "machine_id", "-"))],
        ]
        details_table = Table(details, colWidths=[28*mm, 58*mm, 28*mm, 58*mm])
        details_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#EAF0F8")),
            ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#EAF0F8")),
            ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#C9D3E0")),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.extend([details_table, Spacer(1, 7*mm)])

        if str(val(bill, "billing_mode", "LEGACY")).upper() == "FOUR_TYPE":
            meter_rows = [["Print Type", "Previous Reading", "Current Reading", "Copies Used", "Free Copies", "Rate / Copy", "Amount"]]
            for key, label in (("a4_bw", "A4 Black & White"), ("a4_color", "A4 Color"), ("a3_bw", "A3 Black & White"), ("a3_color", "A3 Color")):
                meter_rows.append([
                    label,
                    str(val(bill, f"{key}_previous_meter", 0)),
                    str(val(bill, f"{key}_current_meter", 0)),
                    str(val(bill, f"{key}_copies_used", 0)),
                    str(val(bill, f"{key}_free_copies", 0)),
                    money(val(bill, f"{key}_rate", 0)),
                    money(val(bill, f"{key}_amount", 0)),
                ])
            meter_table = Table(meter_rows, repeatRows=1, colWidths=[36*mm, 23*mm, 23*mm, 19*mm, 18*mm, 23*mm, 25*mm])
        else:
            meter_rows = [
                ["Description", "Previous Reading", "Current Reading", "Copies Used", "Rate / Copy", "Amount"],
                ["Meter Charges", str(val(bill, "previous_meter", 0)), str(val(bill, "current_meter", 0)), str(val(bill, "copies_used", 0)), money(val(bill, "cost_per_copy", 0)), money(val(bill, "total_amount", 0))],
            ]
            meter_table = Table(meter_rows, repeatRows=1, colWidths=[42*mm, 26*mm, 26*mm, 24*mm, 27*mm, 27*mm])
        meter_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17365D")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#C9D3E0")),
            ("FONTSIZE", (0,0), (-1,-1), 7),
            ("ALIGN", (1,1), (-1,-1), "RIGHT"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.extend([meter_table, Spacer(1, 7*mm)])

        totals = [
            ["Rental Amount", money(val(bill, "rental_amount", 0))],
            ["Copy Charges", money(val(bill, "copy_charges_amount", val(bill, "total_amount", 0)))],
            ["Subtotal", money(val(bill, "subtotal_amount", val(bill, "total_amount", 0)))],
            [f"GST ({val(bill, 'gst_rate', 0)}%)", money(val(bill, "gst_amount", 0))],
            ["GRAND TOTAL", money(val(bill, "total_amount", 0))],
            ["Amount Paid", money(val(bill, "paid_amount", 0))],
            ["Outstanding Amount", money(val(bill, "outstanding_amount", 0))],
        ]
        totals_table = Table(totals, colWidths=[52*mm, 40*mm], hAlign="RIGHT")
        totals_table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#C9D3E0")),
            ("ALIGN", (1,0), (1,-1), "RIGHT"),
            ("FONTNAME", (0,4), (-1,4), "Helvetica-Bold"),
            ("BACKGROUND", (0,4), (-1,4), colors.HexColor("#EAF0F8")),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 7), ("RIGHTPADDING", (0,0), (-1,-1), 7),
            ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        story.extend([totals_table, Spacer(1, 8*mm)])
        remarks = val(bill, "remarks", "")
        if remarks:
            story.append(Paragraph(f"<b>Remarks:</b> {escape(str(remarks))}", styles["SmallText"]))
        story.extend([Spacer(1, 8*mm), Paragraph("This invoice was generated electronically by Digitech Imaging Solutions.", styles["SmallText"])])
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # save_bill_pdf commits the bytes and metadata to PostgreSQL.
        result = RentalBillService.save_bill_pdf(
            db=db, bill_id=bill_id, pdf_data=pdf_bytes,
            file_name=file_name, content_type="application/pdf"
        )
        result["generated_by_backend"] = True
        return result

    # ============================================================
    # SAVE GENERATED PDF TO RENTAL BILL
    # ============================================================

    @staticmethod
    def save_bill_pdf(db: Session, bill_id: int, pdf_data: bytes, file_name: str, content_type: str = "application/pdf"):
        """Persist the frontend-generated PDF bytes on the existing bill."""
        try:
            bill = RentalBillRepository.get_by_id(db=db, bill_id=bill_id)
            if bill is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rental bill not found.")
            if not pdf_data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded PDF is empty.")
            if not pdf_data.startswith(b"%PDF"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded file is not a valid PDF.")
            if len(pdf_data) > 10 * 1024 * 1024:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="PDF must be 10 MB or smaller.")

            # These columns already exist in the user's rental_bills table.
            bill.pdf_file = pdf_data
            bill.pdf_file_name = (file_name or f"{bill.bill_number}.pdf")[:255]
            bill.pdf_content_type = content_type or "application/pdf"
            bill.pdf_generated_at = datetime.now().astimezone()
            db.add(bill)
            db.commit()
            db.refresh(bill)
            return {
                "success": True,
                "bill_id": bill.id,
                "bill_number": bill.bill_number,
                "pdf_file_name": bill.pdf_file_name,
                "pdf_content_type": bill.pdf_content_type,
                "pdf_generated_at": bill.pdf_generated_at,
                "pdf_size_bytes": len(pdf_data),
            }
        except HTTPException:
            db.rollback()
            raise
        except Exception as exc:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save rental bill PDF: {str(exc)}")

    # ============================================================
    # GET CUSTOMER BILLS
    # ============================================================

    @staticmethod
    def get_customer_bills(
        db: Session,
        customer_id: int,
        machine_id: int = None,
        billing_month: str = None,
        payment_status: str = None,
    ):

        RentalBillService._get_customer(
            db=db,
            customer_id=customer_id,
        )

        if billing_month:
            billing_month = (
                RentalBillService._validate_billing_month(
                    billing_month
                )
            )

        if payment_status:
            payment_status = (
                RentalBillService._validate_payment_status(
                    payment_status
                )
            )

        return RentalBillRepository.get_customer_bills(
            db=db,
            customer_id=customer_id,
            machine_id=machine_id,
            billing_month=billing_month,
            payment_status=payment_status,
        )

    # ============================================================
    # GET ONE CUSTOMER BILL
    # ============================================================

    @staticmethod
    def get_customer_bill(
        db: Session,
        customer_id: int,
        bill_id: int,
    ):

        RentalBillService._get_customer(
            db=db,
            customer_id=customer_id,
        )

        bill = (
            RentalBillRepository.get_by_id_for_customer(
                db=db,
                bill_id=bill_id,
                customer_id=customer_id,
            )
        )

        if bill is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rental bill not found.",
            )

        return bill

    # ============================================================
    # GET BILL - ADMIN
    # ============================================================

    @staticmethod
    def get_bill(
        db: Session,
        bill_id: int,
    ):

        bill = RentalBillRepository.get_by_id(
            db=db,
            bill_id=bill_id,
        )

        if bill is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rental bill not found.",
            )

        return bill

    # ============================================================
    # GET ALL BILLS - ADMIN
    # ============================================================

    @staticmethod
    def get_all_bills(
        db: Session,
        customer_id: int = None,
        machine_id: int = None,
        billing_month: str = None,
        payment_status: str = None,
    ):

        if billing_month:
            billing_month = (
                RentalBillService._validate_billing_month(
                    billing_month
                )
            )

        if payment_status:
            payment_status = (
                RentalBillService._validate_payment_status(
                    payment_status
                )
            )

        return RentalBillRepository.get_all(
            db=db,
            customer_id=customer_id,
            machine_id=machine_id,
            billing_month=billing_month,
            payment_status=payment_status,
        )

    # ============================================================
    # UPDATE RENTAL BILL - ADMIN
    # ============================================================

    @staticmethod
    def update_bill(db: Session, bill_id: int, data: RentalBillUpdate, current_user: User):
        """Update a bill while preserving legacy single-meter behavior."""
        try:
            bill = RentalBillRepository.get_by_id(db=db, bill_id=bill_id)
            if bill is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rental bill not found.")
            if str(bill.payment_status).upper() == "CANCELLED":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cancelled rental bills cannot be modified.")
            machine = MachineRepository.get_by_id(db=db, machine_id=bill.machine_id)
            if machine is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine for this rental bill was not found.")

            update_data = data.model_dump(exclude_unset=True)
            old_current_meter = int(bill.current_meter or 0)
            old_cost_per_copy = RentalBillService._decimal(bill.cost_per_copy)
            keys = ("a4_bw", "a4_color", "a3_bw", "a3_color")
            current_field_names = {key: f"{key}_current_meter" for key in keys}
            reading_fields_present = any(name in update_data for name in current_field_names.values())

            if getattr(bill, "billing_mode", "LEGACY") == "FOUR_TYPE":
                previous_readings = {key: int(getattr(bill, f"{key}_previous_meter") or 0) for key in keys}
                current_readings = {
                    key: int(update_data.get(current_field_names[key], getattr(bill, current_field_names[key])))
                    for key in keys
                }
                rates = {key: RentalBillService._decimal(getattr(bill, f"{key}_rate")) for key in keys}
                breakdown, copies_used, free_applied, copy_charges, chargeable_total = RentalBillService._calculate_four_type_breakdown(
                    previous_readings, current_readings, rates, {
                        "a4_bw": getattr(machine, "a4_bw_free_copies", 0),
                        "a4_color": getattr(machine, "a4_color_free_copies", 0),
                        "a3_bw": getattr(machine, "a3_bw_free_copies", 0),
                        "a3_color": getattr(machine, "a3_color_free_copies", 0),
                    }
                )
                rental_amount = RentalBillService._decimal(bill.rental_amount)
                subtotal_amount = (rental_amount + copy_charges).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                gst_rate = RentalBillService._decimal(bill.gst_rate, default="18")
                gst_amount = (subtotal_amount * gst_rate / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                total_amount = subtotal_amount + gst_amount
                aggregate_previous = sum(previous_readings.values())
                aggregate_current = sum(current_readings.values())
                weighted_rate = (copy_charges / Decimal(chargeable_total)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if chargeable_total else Decimal("0.00")
                bill.previous_meter = aggregate_previous
                bill.current_meter = aggregate_current
                bill.copies_used = copies_used
                bill.cost_per_copy = weighted_rate
                bill.rental_amount = rental_amount
                bill.free_copies_applied = free_applied
                bill.copy_charges_amount = copy_charges
                bill.subtotal_amount = subtotal_amount
                bill.gst_rate = gst_rate
                bill.gst_amount = gst_amount
                bill.total_amount = total_amount
                for key in keys:
                    item = breakdown[key]
                    for suffix in ("current_meter", "copies_used", "free_copies", "amount"):
                        setattr(bill, f"{key}_{suffix}", item[suffix])
                    # Rate and previous reading are immutable historical snapshots.
                    machine_field = current_field_names[key]
                    existing_machine_value = int(getattr(machine, machine_field, 0) or 0)
                    if current_readings[key] >= existing_machine_value:
                        setattr(machine, machine_field, current_readings[key])
                # Keep the legacy aggregate meter aligned to A4 B/W for older clients.
                machine.current_meter = int(getattr(machine, "a4_bw_current_meter", 0) or 0)
                price_changed = False  # Four-type prices are immutable snapshots on a bill.
            else:
                new_current_meter = int(update_data.get("current_meter", bill.current_meter))
                previous_meter = int(bill.previous_meter or 0)
                if new_current_meter < previous_meter:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Current meter cannot be less than previous meter ({previous_meter}).")
                if "cost_per_copy" in update_data and update_data["cost_per_copy"] is not None:
                    cost_per_copy = RentalBillService._decimal(update_data["cost_per_copy"])
                else:
                    cost_per_copy = RentalBillService._decimal(bill.cost_per_copy)
                if cost_per_copy < 0:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Price per copy cannot be negative.")
                copies_used = max(0, new_current_meter - previous_meter)
                total_amount = (Decimal(copies_used) * cost_per_copy).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                bill.current_meter = new_current_meter
                bill.copies_used = copies_used
                bill.cost_per_copy = cost_per_copy
                bill.total_amount = total_amount
                bill.subtotal_amount = total_amount
                bill.copy_charges_amount = total_amount
                bill.rental_amount = Decimal("0.00")
                bill.gst_rate = Decimal("0.00")
                bill.gst_amount = Decimal("0.00")
                if new_current_meter >= int(machine.current_meter or 0):
                    machine.current_meter = new_current_meter
                price_changed = cost_per_copy != old_cost_per_copy

            payment_status = RentalBillService._validate_payment_status(update_data.get("payment_status", bill.payment_status))
            paid_amount = RentalBillService._decimal(update_data.get("paid_amount", bill.paid_amount))
            if paid_amount < 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Paid amount cannot be negative.")
            if paid_amount > bill.total_amount:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Paid amount cannot be greater than the updated bill amount.")
            if "paid_amount" in update_data:
                if paid_amount == bill.total_amount:
                    payment_status = "RECEIVED"
                elif paid_amount == Decimal("0"):
                    payment_status = "PENDING"
            if payment_status == "RECEIVED" and "paid_amount" not in update_data:
                paid_amount = bill.total_amount
            outstanding_amount = bill.total_amount - paid_amount
            if paid_amount == bill.total_amount:
                payment_status = "RECEIVED"
            elif paid_amount == Decimal("0") and payment_status != "CANCELLED":
                payment_status = "PENDING"
            bill.payment_status = payment_status
            bill.paid_amount = paid_amount
            bill.outstanding_amount = outstanding_amount
            bill.updated_by = current_user.id
            if "remarks" in update_data:
                bill.remarks = update_data["remarks"]

            RentalBillRepository.update(db=db, bill=bill)
            reading_changed = int(bill.current_meter or 0) != old_current_meter
            if reading_changed or price_changed:
                RentalBillService._add_customer_bill_update_notification(
                    db=db, bill=bill,
                    customer=RentalBillService._get_customer(db=db, customer_id=bill.customer_id),
                    reading_changed=reading_changed, price_changed=price_changed,
                )
            db.commit()
            db.refresh(bill)
            db.refresh(machine)
            return bill
        except HTTPException:
            db.rollback()
            raise
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to update the rental bill because of a database constraint.")
        except Exception as exc:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Rental bill update failed: {str(exc)}")

    # ============================================================
    # UPDATE PAYMENT
    # ============================================================

    @staticmethod
    def update_payment(
        db: Session,
        bill_id: int,
        data: RentalBillPaymentUpdate,
        current_user: User,
    ):

        try:

            bill = RentalBillRepository.get_by_id(
                db=db,
                bill_id=bill_id,
            )

            if bill is None:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Rental bill not found.",
                )

            if (
                str(bill.payment_status).upper()
                == "CANCELLED"
            ):

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Payment cannot be updated for "
                        "a cancelled bill."
                    ),
                )

            payment_status = (
                RentalBillService._validate_payment_status(
                    data.payment_status
                )
            )

            paid_amount = (
                RentalBillService._decimal(
                    data.paid_amount
                )
            )

            if paid_amount < 0:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Paid amount cannot be negative.",
                )

            total_amount = (
                RentalBillService._decimal(
                    bill.total_amount
                )
            )

            if paid_amount > total_amount:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Paid amount cannot be greater than "
                        "the total bill amount."
                    ),
                )

            # ----------------------------------------------------
            # Cancelled
            # ----------------------------------------------------

            if payment_status == "CANCELLED":

                bill.payment_status = "CANCELLED"
                bill.paid_amount = paid_amount
                bill.outstanding_amount = (
                    total_amount -
                    paid_amount
                )

            # ----------------------------------------------------
            # Received
            # ----------------------------------------------------

            elif payment_status == "RECEIVED":

                # If marked received, payment must cover the bill.
                if paid_amount != total_amount:

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Payment status RECEIVED requires "
                            "the full bill amount to be paid."
                        ),
                    )

                bill.payment_status = "RECEIVED"
                bill.paid_amount = total_amount
                bill.outstanding_amount = Decimal("0.00")

            # ----------------------------------------------------
            # Pending
            # ----------------------------------------------------

            else:

                bill.payment_status = "PENDING"
                bill.paid_amount = paid_amount
                bill.outstanding_amount = (
                    total_amount -
                    paid_amount
                )

            if getattr(data, "remarks", None) is not None:

                bill.remarks = data.remarks

            bill.updated_by = current_user.id

            RentalBillRepository.update(
                db=db,
                bill=bill,
            )

            db.commit()

            db.refresh(bill)

            return bill

        except HTTPException:

            db.rollback()

            raise

        except Exception as exc:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Rental payment update failed: {str(exc)}"
                ),
            )

    # ============================================================
    # CANCEL RENTAL BILL
    # ============================================================

    @staticmethod
    def cancel_bill(
        db: Session,
        bill_id: int,
        current_user: User,
    ):

        try:

            bill = RentalBillRepository.get_by_id(
                db=db,
                bill_id=bill_id,
            )

            if bill is None:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Rental bill not found.",
                )

            if (
                str(bill.payment_status).upper()
                == "CANCELLED"
            ):

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rental bill is already cancelled.",
                )

            # ----------------------------------------------------
            # IMPORTANT:
            # Do NOT physically delete the bill.
            #
            # We preserve billing history and mark it cancelled.
            # ----------------------------------------------------

            bill.payment_status = "CANCELLED"
            bill.updated_by = current_user.id

            RentalBillRepository.update(
                db=db,
                bill=bill,
            )

            db.commit()

            db.refresh(bill)

            return bill

        except HTTPException:

            db.rollback()

            raise

        except Exception as exc:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Rental bill cancellation failed: {str(exc)}"
                ),
            )