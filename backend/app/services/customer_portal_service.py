from datetime import date

from fastapi import (
    BackgroundTasks,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.models import (
    Machine,
    ServiceTicket,
    Customer,
    User,
    Notification,
)

from app.utils.service_ticket_number import (
    ServiceTicketNumberGenerator,
)

from app.services.whatsapp_service import (
    WhatsAppService,
)

from app.core.config import settings


class CustomerPortalService:

    # =====================================================
    # CREATE SERVICE REQUEST
    # =====================================================

    @staticmethod
    def create_service_request(
        db: Session,
        current_user,
        machine_id: int,
        complaint: str,
        priority: str = "MEDIUM",
        meter_reading: int | None = None,
        background_tasks: BackgroundTasks | None = None,
    ):

        try:

            # =================================================
            # CUSTOMER
            # =================================================

            customer_id = current_user.customer_id

            if customer_id is None:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Customer account is not linked.",
                )

            # =================================================
            # VERIFY CUSTOMER
            # =================================================

            customer = (
                db.query(Customer)
                .filter(
                    Customer.id == customer_id
                )
                .first()
            )

            if not customer:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found.",
                )

            # =================================================
            # SERVICE PORTAL CHECK
            # =================================================

            if not customer.service_enabled:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "Service portal access is disabled "
                        "for this customer."
                    ),
                )

            # =================================================
            # VERIFY MACHINE
            # =================================================
            #
            # Customer can only raise a request for a machine
            # belonging to the authenticated customer's account.
            #
            # =================================================

            machine = (
                db.query(Machine)
                .filter(
                    Machine.id == machine_id,
                    Machine.customer_id == customer_id,
                    Machine.is_active == True,
                )
                .first()
            )

            if not machine:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        "Machine not found for this customer."
                    ),
                )

            # =================================================
            # VALIDATE COMPLAINT
            # =================================================

            complaint = (
                complaint or ""
            ).strip()

            if len(complaint) < 5:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Complaint must contain at least "
                        "5 characters."
                    ),
                )

            if len(complaint) > 1000:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Complaint cannot exceed "
                        "1000 characters."
                    ),
                )

            # =================================================
            # VALIDATE PRIORITY
            # =================================================

            allowed_priorities = {
                "LOW",
                "MEDIUM",
                "HIGH",
                "URGENT",
            }

            priority = (
                priority or "MEDIUM"
            ).strip().upper()

            if priority not in allowed_priorities:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid service priority.",
                )

            # =================================================
            # MACHINE INFORMATION
            # =================================================

            machine_number = (
                getattr(
                    machine,
                    "machine_number",
                    None,
                )
                or f"Machine #{machine.id}"
            )

            serial_number = (
                machine.serial_number
                or "N/A"
            )

            # =================================================
            # SERVICE REQUEST SUBJECT
            # =================================================
            #
            # ServiceTicket.subject is NOT NULL in the
            # database, so it must always have a value.
            #
            # =================================================

            subject = (
                f"Service Request - {machine_number}"
            )

            subject = subject[:200]

            # =================================================
            # GENERATE TICKET NUMBER
            # =================================================
            #
            # Generate the next ticket number using the next
            # ServiceTicket ID.
            #
            # =================================================

            last_ticket = (
                db.query(ServiceTicket)
                .order_by(
                    ServiceTicket.id.desc()
                )
                .first()
            )

            if last_ticket:

                next_ticket_id = (
                    last_ticket.id + 1
                )

            else:

                next_ticket_id = 1

            ticket_number = (
                ServiceTicketNumberGenerator.generate(
                    next_ticket_id
                )
            )

            # =================================================
            # CREATE SERVICE TICKET
            # =================================================
            #
            # IMPORTANT REQUIRED FIELDS:
            #
            # subject
            # requested_by_user_id
            #
            # =================================================

            ticket = ServiceTicket(

                # Ticket
                ticket_number=ticket_number,

                # Required subject
                subject=subject,

                # Complaint
                complaint=complaint,

                # Customer's current machine meter reading
                meter_reading=meter_reading,

                # Priority
                priority=priority,

                # Initial status
                status="OPEN",

                # Request source
                request_source="CUSTOMER",

                # Customer
                customer_id=customer_id,

                # User who requested the service
                requested_by_user_id=current_user.id,

                # Machine
                machine_id=machine.id,

                serial_number=serial_number,

                # No engineer initially assigned
                assigned_engineer_id=None,

                # Dates
                reported_date=date.today(),

                expected_visit_date=None,

                completed_date=None,

                # Other service dates
                assigned_at=None,

                started_at=None,

                completed_at=None,

                closed_at=None,

                # Resolution
                resolution=None,

                # Warranty / AMC
                is_warranty="NO",

                is_amc="NO",

                # Customer status
                customer_status="REQUESTED",

                # Audit
                created_by=current_user.id,

                updated_by=current_user.id,
            )

            # =================================================
            # ADD TICKET
            # =================================================

            db.add(ticket)

            # =================================================
            # FLUSH
            # =================================================
            #
            # Generates ticket.id without committing yet.
            # This lets us use ticket.id as the notification
            # reference_id.
            #
            # =================================================

            db.flush()

            # =================================================
            # CREATE ADMIN / SUPER ADMIN NOTIFICATIONS
            # =================================================
            #
            # Every active ADMIN and SUPER_ADMIN receives an
            # unread notification.
            #
            # =================================================

            admin_users = (
                db.query(User)
                .filter(
                    User.is_active == True,

                    User.role.in_([
                        "ADMIN",
                        "SUPER_ADMIN",
                    ]),
                )
                .all()
            )

            # =================================================
            # WHATSAPP RECIPIENTS
            # =================================================
            #
            # Capture phone numbers before commit so the
            # background task only receives plain values and
            # never depends on the SQLAlchemy session.
            #
            # =================================================

            # Use the dedicated WhatsApp notification number from .env.
            # This keeps WhatsApp delivery independent from admin login
            # phone numbers.
            # Do not fail service-request creation when the optional
            # WhatsApp recipient setting is absent from Settings.
            # Configure WHATSAPP_NOTIFICATION_NUMBER in app.core.config
            # and your environment if WhatsApp notifications are needed.
            whatsapp_notification_number = str(
                getattr(settings, "WHATSAPP_NOTIFICATION_NUMBER", "") or ""
            ).strip()

            whatsapp_recipients = []

            if whatsapp_notification_number:
                whatsapp_recipients.append(
                    whatsapp_notification_number
                )

            # =================================================
            # CUSTOMER NAME
            # =================================================

            customer_name = (
                customer.customer_name
                or customer.contact_person
                or "Customer"
            )

            # =================================================
            # NOTIFICATION MESSAGE
            # =================================================

            notification_message = (
                f"{customer_name} raised a new service "
                f"request for {machine_number} "
                f"(Serial: {serial_number}). "
                f"Priority: {priority}. "
                f"Complaint: {complaint}"
            )

            # =================================================
            # CREATE NOTIFICATION FOR EACH ADMIN
            # =================================================

            for admin_user in admin_users:

                notification = Notification(

                    user_id=admin_user.id,

                    title="New Service Request",

                    message=notification_message,

                    notification_type="SERVICE_REQUEST",

                    is_read=False,

                    reference_type="SERVICE_TICKET",

                    reference_id=ticket.id,
                )

                db.add(notification)

            # =================================================
            # COMMIT EVERYTHING
            # =================================================
            #
            # Ticket + notifications are committed together.
            #
            # =================================================

            db.commit()

            # =================================================
            # REFRESH TICKET
            # =================================================

            db.refresh(ticket)

            # =================================================
            # WHATSAPP NOTIFICATION
            # =================================================
            #
            # WhatsApp is intentionally sent as a background
            # task. A WhatsApp failure must never make the
            # already-created service request fail.
            #
            # The API route must pass FastAPI BackgroundTasks
            # to this service method.
            #
            # =================================================

            if background_tasks is not None:

                for recipient_phone in whatsapp_recipients:

                    background_tasks.add_task(
                        WhatsAppService.send_new_service_request,

                        recipient_phone=recipient_phone,

                        ticket_number=ticket.ticket_number,

                        customer_name=customer_name,

                        machine_number=machine_number,

                        priority=priority,

                        complaint=complaint,
                    )

            # =================================================
            # RESPONSE
            # =================================================

            return {

                "success": True,

                "message": (
                    "Service request created successfully."
                ),

                "service_request": {

                    "id":
                        ticket.id,

                    "ticket_number":
                        ticket.ticket_number,

                    "subject":
                        ticket.subject,

                    "customer_id":
                        ticket.customer_id,

                    "requested_by_user_id":
                        ticket.requested_by_user_id,

                    "machine_id":
                        ticket.machine_id,

                    "serial_number":
                        ticket.serial_number,

                    "meter_reading":
                        ticket.meter_reading,

                    "complaint":
                        ticket.complaint,

                    "priority":
                        ticket.priority,

                    "status":
                        ticket.status,

                    "request_source":
                        ticket.request_source,

                    "customer_status":
                        ticket.customer_status,

                    "reported_date":
                        ticket.reported_date,
                },
            }

        # =====================================================
        # KNOWN API ERROR
        # =====================================================

        except HTTPException:

            db.rollback()

            raise

        # =====================================================
        # UNEXPECTED ERROR
        # =====================================================

        except Exception as e:

            db.rollback()

            import traceback

            print(
                "\n"
                + "=" * 80
            )

            print(
                "CREATE SERVICE REQUEST ERROR"
            )

            print(
                "=" * 80
            )

            print(
                "ERROR TYPE:",
                type(e).__name__
            )

            print(
                "ERROR:",
                e
            )

            traceback.print_exc()

            print(
                "=" * 80
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),

                detail=str(e),
            )