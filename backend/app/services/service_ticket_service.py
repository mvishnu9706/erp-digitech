from fastapi import BackgroundTasks, HTTPException, status

from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime

from app.models.service_ticket import ServiceTicket

from app.models import (
    User,
    Notification,
)

from app.repositories.service_ticket_repository import (
    ServiceTicketRepository,
)

from app.repositories.customer_repository import (
    CustomerRepository,
)

from app.repositories.machine_repository import (
    MachineRepository,
)

from app.repositories.product_repository import (
    ProductRepository,
)

from app.repositories.user_repository import (
    UserRepository,
)

from app.schemas.service_ticket import (
    ServiceTicketCreate,
    ServiceTicketUpdate,
    CustomerServiceRequestCreate,
)

from app.utils.service_ticket_number import (
    ServiceTicketNumberGenerator,
)

from app.services.whatsapp_service import (
    WhatsAppService,
)


class ServiceTicketService:

    # =====================================================
    # CUSTOMER PORTAL NOTIFICATION HELPERS
    # =====================================================

    @staticmethod
    def _get_customer_portal_user(
        db: Session,
        customer_id,
    ):
        """
        Find the active CUSTOMER portal login for a customer.

        Primary mapping:
            users.customer_id -> customers.id

        Email is used as a safe fallback for older records/databases
        where the customer_id relationship is not populated.
        """
        if not customer_id:
            return None

        customer_id_column = getattr(User, "customer_id", None)

        query = db.query(User).filter(
            User.role == "CUSTOMER",
            User.is_active == True,
        )

        if customer_id_column is not None:
            portal_user = (
                query
                .filter(customer_id_column == customer_id)
                .first()
            )

            if portal_user:
                return portal_user

        # Fallback for older customer portal users.
        customer = CustomerRepository.get_by_id(
            db,
            customer_id,
        )

        customer_email = getattr(
            customer,
            "email",
            None,
        ) if customer else None

        if customer_email:
            return (
                query
                .filter(User.email == str(customer_email).strip().lower())
                .first()
            )

        return None

    @staticmethod
    def _get_engineer_name(
        engineer,
    ):
        """Return the best display name for an engineer/user."""
        if not engineer:
            return "Engineer"

        return (
            getattr(engineer, "full_name", None)
            or getattr(engineer, "contact_person_name", None)
            or getattr(engineer, "username", None)
            or getattr(engineer, "email", None)
            or "Engineer"
        )

    @staticmethod
    def _add_customer_notification(
        db: Session,
        ticket,
        title: str,
        message: str,
        notification_type: str,
    ):
        """
        Create an unread in-app notification for the customer portal.

        The caller commits the transaction. This keeps the ticket change
        and the notification in the same database transaction.
        """
        customer_user = (
            ServiceTicketService._get_customer_portal_user(
                db,
                getattr(ticket, "customer_id", None),
            )
        )

        if not customer_user:
            return False

        db.add(
            Notification(
                user_id=customer_user.id,
                title=title,
                message=message,
                notification_type=notification_type,
                is_read=False,
                reference_type="SERVICE_TICKET",
                reference_id=ticket.id,
            )
        )

        return True

    # =====================================================
    # ENGINEER IN-APP NOTIFICATION
    # =====================================================

    @staticmethod
    def _add_engineer_notification(
        db: Session,
        ticket,
        engineer_id: int,
    ):
        """Create an unread in-app notification for the assigned engineer."""

        if not engineer_id:
            return False

        ticket_number = (
            getattr(ticket, "ticket_number", None)
            or f"#{ticket.id}"
        )

        db.add(
            Notification(
                user_id=int(engineer_id),
                title="New Service Assigned",
                message=(
                    f"Service request {ticket_number} has been assigned "
                    f"to you. Please review the service details and "
                    f"accept the service."
                ),
                notification_type="SERVICE_ASSIGNED",
                is_read=False,
                reference_type="SERVICE_TICKET",
                reference_id=ticket.id,
            )
        )

        return True


    # =====================================================
    # ADMIN IN-APP NOTIFICATION
    # =====================================================

    @staticmethod
    def _add_admin_acceptance_notifications(
        db: Session,
        ticket,
        engineer,
    ):
        """
        Create an unread in-app notification for every active
        ADMIN / SUPER_ADMIN user when an engineer accepts a service.

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

        engineer_name = ServiceTicketService._get_engineer_name(
            engineer
        )

        ticket_number = (
            getattr(ticket, "ticket_number", None)
            or f"#{ticket.id}"
        )

        for admin in admins:
            db.add(
                Notification(
                    user_id=admin.id,
                    title="Service Accepted by Engineer",
                    message=(
                        f"Engineer {engineer_name} has accepted "
                        f"service request {ticket_number}. "
                        f"The service is now In Progress."
                    ),
                    notification_type="SERVICE_ACCEPTED",
                    is_read=False,
                    reference_type="SERVICE_TICKET",
                    reference_id=ticket.id,
                )
            )

        return len(admins)


    # =====================================================
    # ADMIN IN-APP COMPLETION NOTIFICATION
    # =====================================================

    @staticmethod
    def _add_admin_completion_notifications(
        db: Session,
        ticket,
        engineer,
    ):
        """
        Create an unread in-app notification for every active
        ADMIN / SUPER_ADMIN user when an engineer completes a service.
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

        engineer_name = ServiceTicketService._get_engineer_name(
            engineer
        )

        ticket_number = (
            getattr(ticket, "ticket_number", None)
            or f"#{ticket.id}"
        )

        for admin in admins:
            db.add(
                Notification(
                    user_id=admin.id,
                    title="Service Completed",
                    message=(
                        f"Engineer {engineer_name} has completed "
                        f"service request {ticket_number}. "
                        f"Material and service cost details are available "
                        f"in the completed service."
                    ),
                    notification_type="SERVICE_COMPLETED",
                    is_read=False,
                    reference_type="SERVICE_TICKET",
                    reference_id=ticket.id,
                )
            )

        return len(admins)


    # =====================================================
    # CUSTOMER PORTAL
    # CREATE SERVICE REQUEST
    # =====================================================
    # =====================================================
    # CUSTOMER PORTAL
    # CREATE SERVICE REQUEST
    # =====================================================
    #
    # This method is ONLY for a logged-in CUSTOMER.
    #
    # IMPORTANT:
    #
    # customer_id is NOT accepted from the frontend.
    #
    # The customer is determined from the logged-in user.
    #
    # The machine must:
    #
    # 1. Exist
    # 2. Belong to the logged-in customer
    # 3. Be active
    # 4. Have service_enabled = True
    #
    # Customer cannot choose:
    #
    # - customer_id
    # - engineer
    # - status
    # - ticket number
    # - created_by
    #
    # =====================================================

    @staticmethod
    def create_customer_service_request(
        db: Session,
        data: CustomerServiceRequestCreate,
        current_user,
        background_tasks: BackgroundTasks = None,
    ):

        try:

            # =================================================
            # USER VALIDATION
            # =================================================

            if not current_user:

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required.",
                )

            # =================================================
            # ROLE VALIDATION
            # =================================================

            user_role = str(
                current_user.role or ""
            ).strip().upper().replace(
                " ",
                "_",
            )

            if user_role != "CUSTOMER":

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "Only CUSTOMER users can raise "
                        "service requests."
                    ),
                )

            # =================================================
            # GET CUSTOMER
            # =================================================
            #
            # IMPORTANT:
            #
            # Your current User model does not contain a
            # customer_id yet.
            #
            # Therefore, for now we match the customer
            # using the logged-in user's email.
            #
            # This assumes the Customer.email and
            # User.email are the same for the customer
            # portal login.
            #
            # Later, the better production structure is:
            #
            # users.customer_id -> customers.id
            #
            # =================================================

            customer = None

            if current_user.email:

                customer = (
                    CustomerRepository.get_by_email(
                        db,
                        current_user.email,
                    )
                )

            if not customer:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "No customer account is linked "
                        "to this login."
                    ),
                )

            # =================================================
            # CUSTOMER ACTIVE CHECK
            # =================================================

            if not customer.is_active:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "Your customer account is inactive."
                    ),
                )

            # =================================================
            # SERVICE PORTAL CHECK
            # =================================================

            if not customer.service_enabled:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "Service Portal access is not "
                        "enabled for this customer."
                    ),
                )

            # =================================================
            # MACHINE VALIDATION
            # =================================================

            machine = MachineRepository.get_by_id(
                db,
                data.machine_id,
            )

            if not machine:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Machine not found.",
                )

            # =================================================
            # SECURITY:
            # MACHINE MUST BELONG TO CUSTOMER
            # =================================================

            if machine.customer_id != customer.id:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "You are not authorized to raise "
                        "a service request for this machine."
                    ),
                )

            # =================================================
            # MACHINE ACTIVE CHECK
            # =================================================

            if not machine.is_active:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "This machine is inactive and "
                        "cannot receive service requests."
                    ),
                )

            # =================================================
            # MACHINE SERVICE CHECK
            # =================================================

            if not machine.service_enabled:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "Service requests are disabled "
                        "for this machine."
                    ),
                )

            # =================================================
            # GENERATE TICKET NUMBER
            # =================================================

            last_ticket = (
                ServiceTicketRepository.last_ticket(
                    db
                )
            )

            if last_ticket:

                ticket_number = (
                    ServiceTicketNumberGenerator.generate(
                        last_ticket.id + 1
                    )
                )

            else:

                ticket_number = (
                    ServiceTicketNumberGenerator.generate(
                        1
                    )
                )

            # =================================================
            # CREATE CUSTOMER REQUEST
            # =================================================
            #
            # Backend controls:
            #
            # customer_id
            # status
            # created_by
            # reported_date
            # serial_number
            #
            # =================================================

            ticket = ServiceTicket(

                ticket_number=ticket_number,

                # -----------------------------------------
                # Subject
                # -----------------------------------------

                subject=data.subject,

                # -----------------------------------------
                # Complaint
                # -----------------------------------------

                complaint=data.complaint,

                # -----------------------------------------
                # Problem Description
                # -----------------------------------------

                problem_description=(
                    data.problem_description
                ),

                # -----------------------------------------
                # Customer's current machine meter reading
                # Accept both API field names.
                # -----------------------------------------

                meter_reading=(
                    data.meter_reading
                    if data.meter_reading is not None
                    else data.current_meter_reading
                ),

                # -----------------------------------------
                # Priority
                # -----------------------------------------

                priority=data.priority.value,

                # -----------------------------------------
                # Initial Status
                # -----------------------------------------

                status="REQUESTED",

                # -----------------------------------------
                # Request Source
                # -----------------------------------------

                request_source="CUSTOMER",

                # -----------------------------------------
                # Customer
                # -----------------------------------------

                customer_id=customer.id,

                # -----------------------------------------
                # Customer Login
                # -----------------------------------------

                requested_by_user_id=current_user.id,

                # -----------------------------------------
                # Machine
                # -----------------------------------------

                machine_id=machine.id,

                # -----------------------------------------
                # Machine Serial Number
                # -----------------------------------------

                serial_number=machine.serial_number,

                # -----------------------------------------
                # Engineer
                # -----------------------------------------

                assigned_engineer_id=None,

                # -----------------------------------------
                # Reported Date
                # -----------------------------------------

                reported_date=date.today(),

                # -----------------------------------------
                # Schedule
                # -----------------------------------------

                expected_visit_date=None,

                # -----------------------------------------
                # Completion
                # -----------------------------------------

                completed_date=None,

                # -----------------------------------------
                # Timeline
                # -----------------------------------------

                assigned_at=None,

                started_at=None,

                completed_at=None,

                closed_at=None,

                # -----------------------------------------
                # Resolution
                # -----------------------------------------

                resolution=None,

                # -----------------------------------------
                # Warranty
                # -----------------------------------------

                is_warranty="NO",

                # -----------------------------------------
                # AMC
                # -----------------------------------------

                is_amc="NO",

                # -----------------------------------------
                # Customer Status
                # -----------------------------------------

                customer_status="REQUESTED",

                # -----------------------------------------
                # Audit
                # -----------------------------------------

                created_by=current_user.id,

                updated_by=current_user.id,
            )

            # Meter reading is assigned to the ServiceTicket above
            # and is persisted by the repository create/commit flow.

            # =================================================
            # CREATE IN DATABASE
            # =================================================

            ticket = (
                ServiceTicketRepository.create(
                    db,
                    ticket,
                )
            )

            db.commit()

            db.refresh(ticket)

            # =================================================
            # WHATSAPP NOTIFICATION - CUSTOMER PORTAL
            # =================================================
            #
            # The customer record was already loaded above.
            # Build the address directly from the database.
            #
            # Priority:
            #   1. shipping_address
            #   2. billing_address
            #
            # Then append:
            #   city, state, country, pincode
            #
            # This becomes WhatsApp template {{6}}.
            # =================================================

            if background_tasks and customer.phone:

                address_parts = []

                base_address = (
                    customer.shipping_address
                    or customer.billing_address
                    or ""
                )

                if base_address:
                    address_parts.append(
                        str(base_address).strip()
                    )

                if customer.city:
                    address_parts.append(
                        str(customer.city).strip()
                    )

                if customer.state:
                    address_parts.append(
                        str(customer.state).strip()
                    )

                if customer.country:
                    address_parts.append(
                        str(customer.country).strip()
                    )

                if customer.pincode:
                    address_parts.append(
                        str(customer.pincode).strip()
                    )

                customer_address = ", ".join(
                    address_parts
                )

                if not customer_address:
                    customer_address = "Address not available"

                priority_value = (
                    data.priority.value
                    if hasattr(data.priority, "value")
                    else str(data.priority)
                )

                background_tasks.add_task(
                    WhatsAppService.send_new_service_request,
                    recipient_phone=customer.phone,
                    ticket_number=ticket.ticket_number,
                    customer_name=customer.customer_name,
                    machine_number=machine.machine_number,
                    priority=priority_value,
                    complaint=data.complaint or "",
                    address=customer_address,
                )

            return ticket

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Service request creation failed: "
                    f"{str(e)}"
                ),
            )

    # =====================================================
    # CUSTOMER PORTAL
    # GET MY MACHINES
    # =====================================================
    #
    # Returns ONLY machines belonging to the logged-in
    # customer.
    #
    # =====================================================

    @staticmethod
    def get_customer_machines(
        db: Session,
        current_user,
    ):

        # =================================================
        # USER VALIDATION
        # =================================================

        if not current_user:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required.",
            )

        # =================================================
        # ROLE
        # =================================================

        user_role = str(
            current_user.role or ""
        ).strip().upper().replace(
            " ",
            "_",
        )

        if user_role != "CUSTOMER":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only CUSTOMER users can access "
                    "the customer machine portal."
                ),
            )

        # =================================================
        # FIND CUSTOMER
        # =================================================

        customer = None

        if current_user.email:

            customer = (
                CustomerRepository.get_by_email(
                    db,
                    current_user.email,
                )
            )

        if not customer:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "No customer account is linked "
                    "to this login."
                ),
            )

        # =================================================
        # SERVICE ACCESS
        # =================================================

        if not customer.service_enabled:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Service Portal access is not "
                    "enabled for this customer."
                ),
            )

        # =================================================
        # GET CUSTOMER MACHINES
        # =================================================

        machines = (
            MachineRepository.get_by_customer(
                db,
                customer.id,
            )
        )

        # =================================================
        # ONLY ACTIVE + SERVICE ENABLED MACHINES
        # =================================================

        return [
            machine
            for machine in machines
            if machine.is_active
            and machine.service_enabled
        ]

    # =====================================================
    # CUSTOMER PORTAL
    # GET MY SERVICE REQUESTS
    # =====================================================

    @staticmethod
    def get_customer_service_requests(
        db: Session,
        current_user,
    ):

        # =================================================
        # USER VALIDATION
        # =================================================

        if not current_user:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required.",
            )

        # =================================================
        # ROLE
        # =================================================

        user_role = str(
            current_user.role or ""
        ).strip().upper().replace(
            " ",
            "_",
        )

        if user_role != "CUSTOMER":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only CUSTOMER users can access "
                    "customer service requests."
                ),
            )

        # =================================================
        # FIND CUSTOMER
        # =================================================

        customer = None

        if current_user.email:

            customer = (
                CustomerRepository.get_by_email(
                    db,
                    current_user.email,
                )
            )

        if not customer:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "No customer account is linked "
                    "to this login."
                ),
            )

        # =================================================
        # SERVICE ACCESS
        # =================================================

        if not customer.service_enabled:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Service Portal access is not "
                    "enabled for this customer."
                ),
            )

        # =================================================
        # GET CUSTOMER TICKETS
        # =================================================

        return (
            ServiceTicketRepository.get_all(
                db=db,
                customer_id=customer.id,
                skip=0,
                limit=500,
            )
        )

    # =====================================================
    # EXISTING ADMIN / INTERNAL CREATE
    # =====================================================

    @staticmethod
    def create_service_ticket(
        db: Session,
        data: ServiceTicketCreate,
        current_user,
        background_tasks=None,
    ):
        """
        Create an Admin/internal service ticket.

        This supports BOTH:
            1. normal new service entries
            2. manually entered / historical services

        The selected status is respected. Admin can therefore create a
        ticket directly as REQUESTED, ASSIGNED, IN_PROGRESS, ON_HOLD,
        PARTS_PENDING, COMPLETED, CLOSED or CANCELLED.

        Completion details can also be entered during creation:
            - material_used
            - service_cost
            - payment_status
            - completion_date
            - visit_date
        """

        try:
            # =================================================
            # AUTHENTICATION
            # =================================================

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required.",
                )

            # =================================================
            # CUSTOMER VALIDATION
            # =================================================

            customer = CustomerRepository.get_by_id(
                db,
                data.customer_id,
            )

            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found.",
                )

            # =================================================
            # MACHINE VALIDATION
            # =================================================

            machine = MachineRepository.get_by_id(
                db,
                data.machine_id,
            )

            if not machine:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Machine not found.",
                )

            # =================================================
            # MACHINE -> CUSTOMER VALIDATION
            # =================================================

            if (
                getattr(machine, "customer_id", None) is not None
                and int(machine.customer_id) != int(data.customer_id)
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Selected machine does not belong "
                        "to selected customer."
                    ),
                )

            # =================================================
            # ENGINEER VALIDATION
            # =================================================

            engineer = None

            if data.engineer_id:
                engineer = UserRepository.get_by_id(
                    db,
                    data.engineer_id,
                )

                if not engineer:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Engineer not found.",
                    )

                engineer_role = str(
                    getattr(engineer, "role", "") or ""
                ).strip().upper().replace(" ", "_")

                if engineer_role not in {
                    "ENGINEER",
                }:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Selected user is not an engineer.",
                    )

            # =================================================
            # NORMALIZE ENUM VALUES
            # =================================================

            ticket_type = (
                data.ticket_type.value
                if hasattr(data.ticket_type, "value")
                else str(data.ticket_type)
            )

            priority = (
                data.priority.value
                if hasattr(data.priority, "value")
                else str(data.priority)
            )

            selected_status = (
                data.status.value
                if hasattr(data.status, "value")
                else str(data.status)
            )

            selected_status = selected_status.strip().upper()

            allowed_statuses = {
                "REQUESTED",
                "ASSIGNED",
                "CONFIRMED",
                "IN_PROGRESS",
                "ON_HOLD",
                "PARTS_PENDING",
                "COMPLETED",
                "CLOSED",
                "CANCELLED",
            }

            if selected_status not in allowed_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Invalid service status: "
                        f"{selected_status}"
                    ),
                )

            # =================================================
            # PAYMENT STATUS
            # =================================================

            payment_status = str(
                data.payment_status or "PENDING"
            ).strip().upper()

            if payment_status not in {
                "PENDING",
                "RECEIVED",
            }:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Payment status must be "
                        "PENDING or RECEIVED."
                    ),
                )

            # =================================================
            # SERVICE COST
            # =================================================

            service_cost = data.service_cost

            if service_cost is not None and service_cost < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Service cost cannot be negative.",
                )

            # =================================================
            # GENERATE TICKET NUMBER
            # =================================================

            last_ticket = ServiceTicketRepository.last_ticket(db)

            if last_ticket:
                ticket_number = (
                    ServiceTicketNumberGenerator.generate(
                        last_ticket.id + 1
                    )
                )
            else:
                ticket_number = (
                    ServiceTicketNumberGenerator.generate(1)
                )

            # =================================================
            # TIMELINE
            #
            # For manually entered records, populate the
            # appropriate timestamps based on the selected status.
            # =================================================

            now = datetime.utcnow()

            assigned_at = None
            started_at = None
            completed_at = None
            closed_at = None

            if selected_status in {
                "ASSIGNED",
                "CONFIRMED",
                "IN_PROGRESS",
                "ON_HOLD",
                "PARTS_PENDING",
                "COMPLETED",
                "CLOSED",
            }:
                assigned_at = now

            if selected_status in {
                "IN_PROGRESS",
                "ON_HOLD",
                "PARTS_PENDING",
                "COMPLETED",
                "CLOSED",
            }:
                started_at = now

            if selected_status in {
                "COMPLETED",
                "CLOSED",
            }:
                completed_at = now

            if selected_status == "CLOSED":
                closed_at = now

            completion_date = data.completion_date

            # If a manual service is entered directly as COMPLETED
            # or CLOSED and no completion date was supplied, use the
            # service/reported date rather than leaving the record
            # without a completion date.
            if (
                selected_status in {"COMPLETED", "CLOSED"}
                and completion_date is None
            ):
                completion_date = data.reported_date

            # =================================================
            # CREATE TICKET
            #
            # IMPORTANT:
            # Current ServiceTicket model uses:
            #     assigned_engineer_id
            #     expected_visit_date
            #     completed_date
            #
            # It does NOT use:
            #     engineer_id
            #     scheduled_date
            # =================================================

            ticket = ServiceTicket(
                ticket_number=ticket_number,

                subject=(
                    data.subject
                    or data.complaint[:200]
                ),

                complaint=data.complaint,

                problem_description=(
                    data.problem_description
                ),

                customer_id=data.customer_id,

                requested_by_user_id=(
                    current_user.id
                ),

                machine_id=data.machine_id,

                serial_number=getattr(
                    machine,
                    "serial_number",
                    None,
                ),

                assigned_engineer_id=(
                    data.engineer_id
                ),

                priority=priority,

                reported_date=data.reported_date,

                expected_visit_date=(
                    data.expected_visit_date
                ),

                completed_date=completion_date,

                assigned_at=assigned_at,

                started_at=started_at,

                completed_at=completed_at,

                closed_at=closed_at,

                status=selected_status,

                resolution=None,

                is_warranty="NO",

                is_amc="NO",

                request_source="ADMIN",

                customer_status=selected_status,

                created_by=current_user.id,

                updated_by=current_user.id,
            )

            # =================================================
            # OPTIONAL METER READING
            #
            # Some existing database versions do not yet expose
            # meter_reading as a ServiceTicket model column.
            # Save it only when the model has the column.
            # =================================================

            if hasattr(ticket, "meter_reading"):
                ticket.meter_reading = data.meter_reading

            # =================================================
            # MATERIAL USED
            # =================================================

            if hasattr(ticket, "material_used"):
                ticket.material_used = (
                    data.material_used.strip()
                    if isinstance(data.material_used, str)
                    else data.material_used
                )

            # =================================================
            # SERVICE COST
            # =================================================

            if hasattr(ticket, "service_cost"):
                ticket.service_cost = service_cost

            # =================================================
            # PAYMENT STATUS
            # =================================================

            if hasattr(ticket, "payment_status"):
                ticket.payment_status = payment_status

            # =================================================
            # SAVE
            # =================================================

            ticket = ServiceTicketRepository.create(
                db,
                ticket,
            )

            # =================================================
            # ENGINEER NOTIFICATION
            #
            # Only send the normal assignment notification when
            # the manually created ticket is still actionable.
            # A historical COMPLETED/CLOSED service should not
            # generate a "please accept" notification.
            # =================================================

            if (
                data.engineer_id
                and selected_status in {
                    "REQUESTED",
                    "ASSIGNED",
                    "CONFIRMED",
                }
            ):
                ServiceTicketService._add_engineer_notification(
                    db=db,
                    ticket=ticket,
                    engineer_id=data.engineer_id,
                )

            # =================================================
            # COMMIT
            # =================================================

            db.commit()

            db.refresh(ticket)

            # =================================================
            # OPTIONAL WHATSAPP NOTIFICATION
            #
            # Only queue the new-service notification for a
            # service that is still an actionable request.
            # Historical completed/closed records should not send
            # a new request WhatsApp message.
            # =================================================

            if (
                background_tasks
                and selected_status in {
                    "REQUESTED",
                    "ASSIGNED",
                    "CONFIRMED",
                }
                and getattr(customer, "phone", None)
            ):
                address_parts = []

                base_address = (
                    getattr(
                        customer,
                        "shipping_address",
                        None,
                    )
                    or getattr(
                        customer,
                        "billing_address",
                        None,
                    )
                    or ""
                )

                if base_address:
                    address_parts.append(
                        str(base_address).strip()
                    )

                for field_name in (
                    "city",
                    "state",
                    "country",
                    "pincode",
                ):
                    value = getattr(
                        customer,
                        field_name,
                        None,
                    )

                    if value:
                        address_parts.append(
                            str(value).strip()
                        )

                customer_address = ", ".join(
                    address_parts
                )

                if not customer_address:
                    customer_address = (
                        "Address not available"
                    )

                background_tasks.add_task(
                    WhatsAppService.send_new_service_request,
                    recipient_phone=customer.phone,
                    ticket_number=ticket.ticket_number,
                    customer_name=(
                        getattr(
                            customer,
                            "customer_name",
                            None,
                        )
                        or getattr(
                            customer,
                            "name",
                            None,
                        )
                        or ""
                    ),
                    machine_number=(
                        getattr(
                            machine,
                            "machine_number",
                            None,
                        )
                        or ""
                    ),
                    priority=priority,
                    complaint=data.complaint or "",
                    address=customer_address,
                )

            # =================================================
            # OPTIONAL VISIT DATE
            # =================================================
            # The API accepts visit_date, but the current
            # SQLAlchemy model may not map it. Assign only when
            # the installed model actually supports the field.
            # =================================================

            if hasattr(ticket, "visit_date"):
                ticket.visit_date = data.visit_date
                db.commit()
                db.refresh(ticket)

            # =================================================
            # RETURN JSON-FRIENDLY ENRICHED RESPONSE
            # =================================================
            # ServiceTicketResponse expects nested dictionaries
            # for customer, machine and assigned_engineer.
            # =================================================

            response_data = ServiceTicketService.get_service_tickets(
                db=db,
                search=ticket.ticket_number,
                customer_id=None,
                machine_id=None,
                engineer_id=None,
                status=None,
                priority=None,
                ticket_type=None,
                page=1,
                page_size=1,
            )

            if response_data.get("items"):
                return response_data["items"][0]

            return ticket

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            db.rollback()

            import traceback
            traceback.print_exc()

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Service Ticket creation failed: "
                    f"{str(e)}"
                ),
            )

    # =====================================================
    # GET SERVICE TICKETS
    # =====================================================

    @staticmethod
    def get_service_tickets(
        db: Session,
        search: str = None,
        customer_id: int = None,
        machine_id: int = None,
        engineer_id: int = None,
        status: str = None,
        priority: str = None,
        ticket_type: str = None,
        page: int = 1,
        page_size: int = 10,
    ):
        # =====================================================
        # GET SERVICE TICKETS
        #
        # The ServiceTicket table stores only the foreign keys:
        #
        #   customer_id
        #   machine_id
        #   assigned_engineer_id
        #
        # The admin table needs the actual names as well.
        #
        # Therefore we enrich every ticket before returning it.
        # =====================================================

        skip = (
            page - 1
        ) * page_size

        # -----------------------------------------------------
        # Get paginated tickets using the existing repository.
        # -----------------------------------------------------
        tickets = (
            ServiceTicketRepository.get_all(
                db=db,
                search=search,
                customer_id=customer_id,
                machine_id=machine_id,
                engineer_id=engineer_id,
                status=status,
                priority=priority,
                ticket_type=ticket_type,
                skip=skip,
                limit=page_size,
            )
        )

        # -----------------------------------------------------
        # Total count
        # -----------------------------------------------------
        total = (
            ServiceTicketRepository.count(
                db=db,
                search=search,
                customer_id=customer_id,
                machine_id=machine_id,
                engineer_id=engineer_id,
                status=status,
                priority=priority,
                ticket_type=ticket_type,
            )
        )

        # =====================================================
        # ENRICH TICKETS
        # =====================================================

        items = []

        for ticket in tickets:

            # -------------------------------------------------
            # Customer
            # -------------------------------------------------

            customer = None

            if ticket.customer_id:
                customer = (
                    CustomerRepository.get_by_id(
                        db,
                        ticket.customer_id,
                    )
                )

            # -------------------------------------------------
            # Machine
            # -------------------------------------------------

            machine = None

            if ticket.machine_id:
                machine = (
                    MachineRepository.get_by_id(
                        db,
                        ticket.machine_id,
                    )
                )

            # -------------------------------------------------
            # Product
            #
            # Machine contains product_id, so the product is
            # loaded through the machine.
            # -------------------------------------------------

            product = None

            if machine and getattr(
                machine,
                "product_id",
                None,
            ):
                product = (
                    ProductRepository.get_by_id(
                        db,
                        machine.product_id,
                    )
                )

            # -------------------------------------------------
            # Assigned Engineer
            # -------------------------------------------------

            engineer = None

            engineer_id_value = getattr(
                ticket,
                "assigned_engineer_id",
                None,
            )

            if engineer_id_value:
                engineer = (
                    UserRepository.get_by_id(
                        db,
                        engineer_id_value,
                    )
                )

            # =================================================
            # CUSTOMER RESPONSE
            # =================================================

            customer_data = None

            if customer:
                customer_data = {
                    "id": customer.id,
                    "customer_name": getattr(
                        customer,
                        "customer_name",
                        None,
                    ),
                    "name": getattr(
                        customer,
                        "customer_name",
                        None,
                    ),
                    "phone": getattr(
                        customer,
                        "phone",
                        None,
                    ),
                    "mobile": getattr(
                        customer,
                        "phone",
                        None,
                    ),
                    "mobile_number": getattr(
                        customer,
                        "phone",
                        None,
                    ),
                    "email": getattr(
                        customer,
                        "email",
                        None,
                    ),
                    "billing_address": getattr(
                        customer,
                        "billing_address",
                        None,
                    ),
                    "shipping_address": getattr(
                        customer,
                        "shipping_address",
                        None,
                    ),
                    "address": (
                        getattr(
                            customer,
                            "shipping_address",
                            None,
                        )
                        or getattr(
                            customer,
                            "billing_address",
                            None,
                        )
                    ),
                    "city": getattr(
                        customer,
                        "city",
                        None,
                    ),
                    "state": getattr(
                        customer,
                        "state",
                        None,
                    ),
                    "country": getattr(
                        customer,
                        "country",
                        None,
                    ),
                    "pincode": getattr(
                        customer,
                        "pincode",
                        None,
                    ),
                }

            # =================================================
            # MACHINE RESPONSE
            # =================================================

            machine_data = None

            if machine:
                machine_data = {
                    "id": machine.id,
                    "machine_number": getattr(
                        machine,
                        "machine_number",
                        None,
                    ),
                    "serial_number": getattr(
                        machine,
                        "serial_number",
                        None,
                    ),
                    "asset_tag": getattr(
                        machine,
                        "asset_tag",
                        None,
                    ),
                    "product_id": getattr(
                        machine,
                        "product_id",
                        None,
                    ),
                    "machine_name": getattr(
                        machine,
                        "machine_number",
                        None,
                    ),
                }

            # =================================================
            # PRODUCT RESPONSE
            # =================================================

            product_name = None

            if product:
                product_name = getattr(
                    product,
                    "product_name",
                    None,
                )

            product_data = None

            if product:
                product_data = {
                    "id": product.id,
                    "product_name": product_name,
                    "name": product_name,
                    "sku": getattr(
                        product,
                        "sku",
                        None,
                    ),
                    "model_no": getattr(
                        product,
                        "model_no",
                        None,
                    ),
                }

            # =================================================
            # ENGINEER RESPONSE
            # =================================================

            engineer_data = None

            if engineer:
                engineer_name = (
                    getattr(
                        engineer,
                        "full_name",
                        None,
                    )
                    or getattr(
                        engineer,
                        "contact_person_name",
                        None,
                    )
                    or getattr(
                        engineer,
                        "username",
                        None,
                    )
                    or getattr(
                        engineer,
                        "email",
                        None,
                    )
                )

                engineer_data = {
                    "id": engineer.id,
                    "full_name": engineer_name,
                    "name": engineer_name,
                    "username": getattr(
                        engineer,
                        "username",
                        None,
                    ),
                    "email": getattr(
                        engineer,
                        "email",
                        None,
                    ),
                    "phone": getattr(
                        engineer,
                        "phone",
                        None,
                    ),
                }

            # =================================================
            # BASE TICKET DATA
            #
            # Use SQLAlchemy's mapped columns dynamically so
            # we keep ALL existing ServiceTicket fields without
            # manually listing them.
            # =================================================

            try:
                from sqlalchemy.inspection import (
                    inspect as sqlalchemy_inspect,
                )

                ticket_data = {
                    column.key: getattr(
                        ticket,
                        column.key,
                    )
                    for column in (
                        sqlalchemy_inspect(
                            ticket
                        ).mapper.column_attrs
                    )
                }

            except Exception:
                # Safe fallback if SQLAlchemy inspection is not
                # available for any reason.
                ticket_data = {
                    key: value
                    for key, value in (
                        getattr(
                            ticket,
                            "__dict__",
                            {},
                        )
                    ).items()
                    if not key.startswith("_")
                }

            # =================================================
            # ADD FRONTEND-FRIENDLY VALUES
            # =================================================

            ticket_data["customer"] = (
                customer_data
            )

            ticket_data["customer_details"] = (
                customer_data
            )

            ticket_data["customer_name"] = (
                getattr(
                    customer,
                    "customer_name",
                    None,
                )
                if customer
                else None
            )

            ticket_data["phone"] = (
                getattr(
                    customer,
                    "phone",
                    None,
                )
                if customer
                else None
            )

            ticket_data["email"] = (
                getattr(
                    customer,
                    "email",
                    None,
                )
                if customer
                else None
            )

            ticket_data["address"] = (
                (
                    getattr(
                        customer,
                        "shipping_address",
                        None,
                    )
                    or getattr(
                        customer,
                        "billing_address",
                        None,
                    )
                )
                if customer
                else None
            )

            ticket_data["machine"] = (
                machine_data
            )

            ticket_data["machine_details"] = (
                machine_data
            )

            ticket_data["product"] = (
                product_data
            )

            ticket_data["product_details"] = (
                product_data
            )

            ticket_data["product_name"] = (
                product_name
            )

            ticket_data["engineer"] = (
                engineer_data
            )

            ticket_data["assigned_engineer"] = (
                engineer_data
            )

            ticket_data["engineer_details"] = (
                engineer_data
            )

            ticket_data["engineer_name"] = (
                (
                    engineer_data.get(
                        "full_name"
                    )
                    if engineer_data
                    else None
                )
            )

            ticket_data["technician"] = (
                (
                    engineer_data.get(
                        "full_name"
                    )
                    if engineer_data
                    else None
                )
            )

            # -------------------------------------------------
            # Add machine/product IDs explicitly.
            # -------------------------------------------------

            ticket_data["machine_id"] = (
                ticket.machine_id
            )

            ticket_data["product_id"] = (
                getattr(
                    machine,
                    "product_id",
                    None,
                )
                if machine
                else None
            )

            ticket_data["serial_number"] = (
                getattr(
                    ticket,
                    "serial_number",
                    None,
                )
                or (
                    getattr(
                        machine,
                        "serial_number",
                        None,
                    )
                    if machine
                    else None
                )
            )

            items.append(
                ticket_data
            )

        # =====================================================
        # FINAL RESPONSE
        # =====================================================

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items,
        }

    # =====================================================
    # GET SERVICE TICKET
    # =====================================================

    @staticmethod
    def get_service_ticket(
        db: Session,
        ticket_id: int,
    ):

        ticket = (
            ServiceTicketRepository.get_by_id(
                db,
                ticket_id,
            )
        )

        if not ticket:

            raise HTTPException(
                status_code=404,
                detail="Service Ticket not found.",
            )

        return ticket

    # =====================================================
    # UPDATE SERVICE TICKET
    # =====================================================

    @staticmethod
    def update_service_ticket(
        db: Session,
        ticket_id: int,
        data: ServiceTicketUpdate,
        current_user,
    ):

        try:

            ticket = (
                ServiceTicketRepository.get_by_id(
                    db,
                    ticket_id,
                )
            )

            if not ticket:

                raise HTTPException(
                    status_code=404,
                    detail="Service Ticket not found.",
                )

            # -------------------------------------------------
            # Authorization
            #
            # ADMIN / SUPER_ADMIN:
            #     Keep the existing full update capability.
            #
            # ENGINEER:
            #     Can update only their own COMPLETED service
            #     completion details (material, cost, resolution,
            #     completion date).
            # -------------------------------------------------
            user_role = str(
                getattr(current_user, "role", "") or ""
            ).strip().upper().replace(
                " ",
                "_",
            )

            allowed_admin_roles = {
                "ADMIN",
                "SUPER_ADMIN",
            }

            if user_role not in allowed_admin_roles:
                if user_role != "ENGINEER":
                    raise HTTPException(
                        status_code=403,
                        detail="You are not authorized to update service tickets.",
                    )

                assigned_engineer_id = getattr(
                    ticket,
                    "assigned_engineer_id",
                    None,
                )

                if (
                    not assigned_engineer_id
                    or int(assigned_engineer_id) != int(current_user.id)
                ):
                    raise HTTPException(
                        status_code=403,
                        detail="You are not assigned to this service request.",
                    )

                current_status = str(
                    getattr(ticket, "status", "") or ""
                ).strip().upper()

                if current_status != "COMPLETED":
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Service details can be updated by the engineer "
                            "only after the service is completed."
                        ),
                    )

            # -------------------------------------------------
            # Capture the old engineer BEFORE applying changes.
            # -------------------------------------------------
            old_engineer_id = getattr(
                ticket,
                "assigned_engineer_id",
                None,
            )

            update_data = data.model_dump(
                exclude_unset=True
            )

            # -------------------------------------------------
            # ENGINEER UPDATE RESTRICTION
            # -------------------------------------------------
            # Engineers may change only completion details.
            # They cannot reassign customers/machines/engineers
            # or change the service status.
            if user_role == "ENGINEER":
                engineer_allowed_fields = {
                    "completion_date",
                    "material_used",
                    "service_cost",
                    "resolution",
                    "payment_status",
                }

                forbidden_fields = (
                    set(update_data.keys())
                    - engineer_allowed_fields
                )

                if forbidden_fields:
                    raise HTTPException(
                        status_code=403,
                        detail=(
                            "Engineers can update only material used, "
                            "service cost, resolution, completion date, "
                            "and payment status after completing the service."
                        ),
                    )

            # ---------------------------------------------
            # Convert enum values
            # ---------------------------------------------

            for key, value in list(
                update_data.items()
            ):

                if hasattr(
                    value,
                    "value",
                ):

                    update_data[key] = (
                        value.value
                    )

            # ---------------------------------------------
            # Map schema names to model names
            # ---------------------------------------------

            if (
                "engineer_id"
                in update_data
            ):

                update_data[
                    "assigned_engineer_id"
                ] = update_data.pop(
                    "engineer_id"
                )

            if (
                "scheduled_date"
                in update_data
            ):

                update_data[
                    "expected_visit_date"
                ] = update_data.pop(
                    "scheduled_date"
                )

            if (
                "completion_date"
                in update_data
            ):

                update_data[
                    "completed_date"
                ] = update_data.pop(
                    "completion_date"
                )

            # ---------------------------------------------
            # Detect engineer change.
            # ---------------------------------------------
            engineer_change_requested = (
                "assigned_engineer_id"
                in update_data
            )

            new_engineer_id = (
                update_data.get(
                    "assigned_engineer_id"
                )
                if engineer_change_requested
                else old_engineer_id
            )

            old_engineer = None

            if (
                engineer_change_requested
                and old_engineer_id
                and old_engineer_id != new_engineer_id
            ):
                old_engineer = (
                    UserRepository.get_by_id(
                        db,
                        old_engineer_id,
                    )
                )

            new_engineer = None

            if (
                engineer_change_requested
                and new_engineer_id
                and old_engineer_id != new_engineer_id
            ):
                new_engineer = (
                    UserRepository.get_by_id(
                        db,
                        new_engineer_id,
                    )
                )

                if not new_engineer:
                    raise HTTPException(
                        status_code=404,
                        detail="Engineer not found.",
                    )

                new_engineer_role = str(
                    new_engineer.role or ""
                ).strip().upper().replace(
                    " ",
                    "_",
                )

                if new_engineer_role != "ENGINEER":
                    raise HTTPException(
                        status_code=400,
                        detail="Selected user is not an engineer.",
                    )

            # ---------------------------------------------
            # Normalize payment status for engineer updates
            # ---------------------------------------------
            if "payment_status" in update_data:
                normalized_payment_status = (
                    str(
                        update_data.get("payment_status")
                        or "PENDING"
                    )
                    .strip()
                    .upper()
                )

                if normalized_payment_status not in {
                    "PENDING",
                    "RECEIVED",
                }:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=(
                            "Payment status must be PENDING or RECEIVED."
                        ),
                    )

                update_data["payment_status"] = (
                    normalized_payment_status
                )

            # ---------------------------------------------
            # Update
            # ---------------------------------------------

            for key, value in (
                update_data.items()
            ):

                # Only update existing model fields
                if hasattr(
                    ticket,
                    key,
                ):

                    setattr(
                        ticket,
                        key,
                        value,
                    )

            ticket.updated_by = (
                current_user.id
            )

            ServiceTicketRepository.update(
                db,
                ticket,
            )

            # ---------------------------------------------
            # CUSTOMER NOTIFICATION - ENGINEER CHANGE
            # ---------------------------------------------

            if (
                engineer_change_requested
                and old_engineer_id != new_engineer_id
            ):

                ticket_number = (
                    ticket.ticket_number
                )

                if new_engineer_id:
                    new_name = (
                        ServiceTicketService._get_engineer_name(
                            new_engineer
                        )
                    )

                    if old_engineer_id:
                        old_name = (
                            ServiceTicketService._get_engineer_name(
                                old_engineer
                            )
                        )

                        ServiceTicketService._add_customer_notification(
                            db=db,
                            ticket=ticket,
                            title="Service Engineer Changed",
                            message=(
                                f"The engineer for service request "
                                f"{ticket_number} has been changed "
                                f"from {old_name} to {new_name}."
                            ),
                            notification_type="ENGINEER_CHANGED",
                        )
                    else:
                        ServiceTicketService._add_customer_notification(
                            db=db,
                            ticket=ticket,
                            title="Engineer Assigned",
                            message=(
                                f"Engineer {new_name} has been assigned "
                                f"to your service request {ticket_number}."
                            ),
                            notification_type="ENGINEER_ASSIGNED",
                        )

                elif old_engineer_id:
                    old_name = (
                        ServiceTicketService._get_engineer_name(
                            old_engineer
                        )
                    )

                    ServiceTicketService._add_customer_notification(
                        db=db,
                        ticket=ticket,
                        title="Service Engineer Removed",
                        message=(
                            f"The engineer {old_name} has been removed "
                            f"from service request {ticket_number}."
                        ),
                        notification_type="ENGINEER_REMOVED",
                    )

            db.commit()

            db.refresh(ticket)

            # -------------------------------------------------
            # Return the same enriched JSON-friendly structure
            # used by the service list endpoint.
            #
            # This is important because ServiceTicketResponse
            # contains nested customer/machine/product/engineer
            # dictionaries. Returning the raw SQLAlchemy object
            # can make the database update succeed while Axios
            # still reports a response validation/network error.
            # -------------------------------------------------
            response_data = ServiceTicketService.get_service_tickets(
                db=db,
                search=ticket.ticket_number,
                customer_id=None,
                machine_id=None,
                engineer_id=None,
                status=None,
                priority=None,
                ticket_type=None,
                page=1,
                page_size=1,
            )

            if response_data.get("items"):
                return response_data["items"][0]

            return ticket

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e),
            )

    # =====================================================
    # DELETE SERVICE TICKET
    # =====================================================

    @staticmethod
    def delete_service_ticket(
        db: Session,
        ticket_id: int,
    ):

        try:

            ticket = (
                ServiceTicketRepository.get_by_id(
                    db,
                    ticket_id,
                )
            )

            if not ticket:

                raise HTTPException(
                    status_code=404,
                    detail="Service Ticket not found.",
                )

            # -------------------------------------------------
            # Save the ticket number before deleting the ticket.
            # -------------------------------------------------
            ticket_number = (
                ticket.ticket_number
            )

            # -------------------------------------------------
            # Create customer notification BEFORE deletion.
            # -------------------------------------------------
            # The notification uses reference_id=ticket.id, while
            # the ticket still exists. The ticket + notification are
            # committed together below.
            # -------------------------------------------------
            ServiceTicketService._add_customer_notification(
                db=db,
                ticket=ticket,
                title="Service Request Deleted",
                message=(
                    f"Your service request {ticket_number} "
                    f"has been deleted by the service team."
                ),
                notification_type="SERVICE_DELETED",
            )

            ServiceTicketRepository.delete(
                db,
                ticket,
            )

            db.commit()

            return {
                "success": True,
                "message": (
                    "Service Ticket deleted successfully."
                ),
            }

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e),
            )

    # =====================================================
    # ASSIGN ENGINEER
    # =====================================================

    @staticmethod
    def assign_engineer(
        db: Session,
        ticket_id: int,
        engineer_id: int,
        current_user,
        background_tasks: BackgroundTasks = None,
    ):
        """
        Assign an engineer to a service ticket.

        IMPORTANT:
        1. The ticket assignment is committed first.
        2. Customer notification is handled separately so a
           notification/database problem cannot undo the assignment.
        3. The response is returned as a JSON-friendly dictionary
           containing customer, machine, product and engineer data.
        """

        try:
            # =================================================
            # VALIDATE TICKET
            # =================================================

            ticket = (
                ServiceTicketRepository.get_by_id(
                    db,
                    ticket_id,
                )
            )

            if not ticket:
                raise HTTPException(
                    status_code=404,
                    detail="Service Ticket not found.",
                )

            # =================================================
            # VALIDATE ENGINEER
            # =================================================

            engineer = (
                UserRepository.get_by_id(
                    db,
                    engineer_id,
                )
            )

            if not engineer:
                raise HTTPException(
                    status_code=404,
                    detail="Engineer not found.",
                )

            engineer_role = str(
                getattr(engineer, "role", "") or ""
            ).strip().upper().replace(
                " ",
                "_",
            )

            if engineer_role != "ENGINEER":
                raise HTTPException(
                    status_code=400,
                    detail="Selected user is not an engineer.",
                )

            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required.",
                )

            # =================================================
            # CAPTURE OLD ENGINEER
            # =================================================

            old_engineer_id = getattr(
                ticket,
                "assigned_engineer_id",
                None,
            )

            # =================================================
            # ASSIGN ENGINEER
            # =================================================

            ticket.assigned_engineer_id = int(engineer_id)

            ticket.assigned_at = datetime.utcnow()

            ticket.status = "ASSIGNED"

            ticket.customer_status = "ASSIGNED"

            ticket.updated_by = current_user.id

            ServiceTicketRepository.update(
                db,
                ticket,
            )

            # =================================================
            # COMMIT ASSIGNMENT FIRST
            # =================================================
            #
            # This is intentionally before the customer
            # notification. If notification creation fails,
            # the engineer assignment must still remain saved.
            # =================================================

            db.commit()

            db.refresh(ticket)

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            db.rollback()

            import traceback
            traceback.print_exc()

            raise HTTPException(
                status_code=500,
                detail=f"Engineer assignment failed: {str(e)}",
            )

        # =====================================================
        # ENGINEER IN-APP NOTIFICATION
        # =====================================================
        #
        # The assignment has already been committed above.
        # A notification failure must never undo the assignment.
        # =====================================================

        if old_engineer_id != int(engineer_id):
            try:
                ServiceTicketService._add_engineer_notification(
                    db=db,
                    ticket=ticket,
                    engineer_id=int(engineer_id),
                )

                db.commit()

            except Exception:
                db.rollback()

                import traceback
                print(
                    "ENGINEER NOTIFICATION FAILED "
                    "(ENGINEER ASSIGNMENT WAS SUCCESSFUL):"
                )
                traceback.print_exc()

        # =====================================================
        # CUSTOMER NOTIFICATION
        # =====================================================
        #
        # Notification failure must NEVER undo the successful
        # engineer assignment.
        # =====================================================

        try:
            if old_engineer_id != int(engineer_id):

                if old_engineer_id:
                    old_engineer = (
                        UserRepository.get_by_id(
                            db,
                            old_engineer_id,
                        )
                    )

                    old_engineer_name = (
                        ServiceTicketService._get_engineer_name(
                            old_engineer
                        )
                    )

                    new_engineer_name = (
                        ServiceTicketService._get_engineer_name(
                            engineer
                        )
                    )

                    ServiceTicketService._add_customer_notification(
                        db=db,
                        ticket=ticket,
                        title="Service Engineer Changed",
                        message=(
                            f"The engineer for service request "
                            f"{ticket.ticket_number} has been changed "
                            f"from {old_engineer_name} to "
                            f"{new_engineer_name}."
                        ),
                        notification_type="ENGINEER_CHANGED",
                    )

                else:
                    engineer_name = (
                        ServiceTicketService._get_engineer_name(
                            engineer
                        )
                    )

                    ServiceTicketService._add_customer_notification(
                        db=db,
                        ticket=ticket,
                        title="Engineer Assigned",
                        message=(
                            f"Engineer {engineer_name} has been assigned "
                            f"to your service request "
                            f"{ticket.ticket_number}."
                        ),
                        notification_type="ENGINEER_ASSIGNED",
                    )

                db.commit()

        except Exception as notification_error:
            # The assignment is already committed.
            # Roll back only the failed notification transaction.
            db.rollback()

            import traceback
            print(
                "CUSTOMER NOTIFICATION FAILED "
                "(ENGINEER ASSIGNMENT WAS SUCCESSFUL):"
            )
            traceback.print_exc()

        # =====================================================
        # LOAD RELATED DATA FOR RESPONSE
        # =====================================================

        customer = None

        if ticket.customer_id:
            customer = CustomerRepository.get_by_id(
                db,
                ticket.customer_id,
            )

        machine = None

        if ticket.machine_id:
            machine = MachineRepository.get_by_id(
                db,
                ticket.machine_id,
            )

        product = None

        if machine and getattr(
            machine,
            "product_id",
            None,
        ):
            product = ProductRepository.get_by_id(
                db,
                machine.product_id,
            )

        engineer_name = (
            getattr(engineer, "full_name", None)
            or getattr(engineer, "contact_person_name", None)
            or getattr(engineer, "username", None)
            or getattr(engineer, "email", None)
            or "Engineer"
        )

        # =====================================================
        # CUSTOMER RESPONSE
        # =====================================================

        customer_data = None

        if customer:
            customer_data = {
                "id": customer.id,
                "customer_name": getattr(
                    customer,
                    "customer_name",
                    None,
                ),
                "name": getattr(
                    customer,
                    "customer_name",
                    None,
                ),
                "phone": getattr(
                    customer,
                    "phone",
                    None,
                ),
                "mobile": getattr(
                    customer,
                    "phone",
                    None,
                ),
                "mobile_number": getattr(
                    customer,
                    "phone",
                    None,
                ),
                "email": getattr(
                    customer,
                    "email",
                    None,
                ),
                "billing_address": getattr(
                    customer,
                    "billing_address",
                    None,
                ),
                "shipping_address": getattr(
                    customer,
                    "shipping_address",
                    None,
                ),
                "address": (
                    getattr(
                        customer,
                        "shipping_address",
                        None,
                    )
                    or getattr(
                        customer,
                        "billing_address",
                        None,
                    )
                ),
                "city": getattr(
                    customer,
                    "city",
                    None,
                ),
                "state": getattr(
                    customer,
                    "state",
                    None,
                ),
                "country": getattr(
                    customer,
                    "country",
                    None,
                ),
                "pincode": getattr(
                    customer,
                    "pincode",
                    None,
                ),
            }

        # =====================================================
        # MACHINE RESPONSE
        # =====================================================

        machine_data = None

        if machine:
            machine_data = {
                "id": machine.id,
                "machine_number": getattr(
                    machine,
                    "machine_number",
                    None,
                ),
                "serial_number": getattr(
                    machine,
                    "serial_number",
                    None,
                ),
                "asset_tag": getattr(
                    machine,
                    "asset_tag",
                    None,
                ),
                "product_id": getattr(
                    machine,
                    "product_id",
                    None,
                ),
                "machine_name": getattr(
                    machine,
                    "machine_number",
                    None,
                ),
            }

        # =====================================================
        # PRODUCT RESPONSE
        # =====================================================

        product_name = None

        if product:
            product_name = getattr(
                product,
                "product_name",
                None,
            )

        product_data = None

        if product:
            product_data = {
                "id": product.id,
                "product_name": product_name,
                "name": product_name,
                "sku": getattr(
                    product,
                    "sku",
                    None,
                ),
                "model_no": getattr(
                    product,
                    "model_no",
                    None,
                ),
            }

        # =====================================================
        # ENGINEER RESPONSE
        # =====================================================

        engineer_data = {
            "id": engineer.id,
            "full_name": engineer_name,
            "name": engineer_name,
            "username": getattr(
                engineer,
                "username",
                None,
            ),
            "email": getattr(
                engineer,
                "email",
                None,
            ),
            "phone": getattr(
                engineer,
                "phone",
                None,
            ),
        }

        # =====================================================
        # BASE TICKET DATA
        # =====================================================

        try:
            from sqlalchemy.inspection import (
                inspect as sqlalchemy_inspect,
            )

            ticket_data = {
                column.key: getattr(
                    ticket,
                    column.key,
                )
                for column in (
                    sqlalchemy_inspect(
                        ticket
                    ).mapper.column_attrs
                )
            }

        except Exception:
            ticket_data = {
                key: value
                for key, value in getattr(
                    ticket,
                    "__dict__",
                    {},
                ).items()
                if not key.startswith("_")
            }

        # =====================================================
        # FRONTEND/API FRIENDLY FIELDS
        # =====================================================

        ticket_data["customer"] = customer_data
        ticket_data["customer_details"] = customer_data

        ticket_data["customer_name"] = (
            getattr(
                customer,
                "customer_name",
                None,
            )
            if customer
            else None
        )

        ticket_data["phone"] = (
            getattr(
                customer,
                "phone",
                None,
            )
            if customer
            else None
        )

        ticket_data["email"] = (
            getattr(
                customer,
                "email",
                None,
            )
            if customer
            else None
        )

        ticket_data["address"] = (
            (
                getattr(
                    customer,
                    "shipping_address",
                    None,
                )
                or getattr(
                    customer,
                    "billing_address",
                    None,
                )
            )
            if customer
            else None
        )

        ticket_data["machine"] = machine_data
        ticket_data["machine_details"] = machine_data

        ticket_data["product"] = product_data
        ticket_data["product_details"] = product_data
        ticket_data["product_name"] = product_name

        ticket_data["engineer"] = engineer_data
        ticket_data["assigned_engineer"] = engineer_data
        ticket_data["engineer_details"] = engineer_data

        ticket_data["engineer_name"] = engineer_name
        ticket_data["technician"] = engineer_name

        ticket_data["machine_id"] = ticket.machine_id

        ticket_data["product_id"] = (
            getattr(
                machine,
                "product_id",
                None,
            )
            if machine
            else None
        )

        ticket_data["serial_number"] = (
            getattr(
                ticket,
                "serial_number",
                None,
            )
            or (
                getattr(
                    machine,
                    "serial_number",
                    None,
                )
                if machine
                else None
            )
        )

        # =====================================================
        # WHATSAPP - ENGINEER ASSIGNED
        # =====================================================

        if background_tasks:
            if customer and customer.phone:

                machine_number = (
                    (
                        getattr(
                            machine,
                            "machine_number",
                            None,
                        )
                        or getattr(
                            machine,
                            "serial_number",
                            None,
                        )
                        or ""
                    )
                    if machine
                    else ""
                )

                background_tasks.add_task(
                    WhatsAppService.send_engineer_assigned,
                    recipient_phone=customer.phone,
                    ticket_number=ticket.ticket_number,
                    customer_name=(
                        getattr(
                            customer,
                            "customer_name",
                            None,
                        )
                        or getattr(
                            customer,
                            "name",
                            None,
                        )
                        or ""
                    ),
                    engineer_name=engineer_name,
                    machine_number=machine_number,
                )

        # =====================================================
        # FINAL RESPONSE
        # =====================================================

        return ticket_data

    # =====================================================
    # ENGINEER ACCEPT SERVICE
    # =====================================================

    @staticmethod
    def accept_service(
        db: Session,
        ticket_id: int,
        current_user,
        background_tasks: BackgroundTasks = None,
    ):
        """
        Allow the assigned engineer to accept their service request.

        Status transition:
            ASSIGNED -> IN_PROGRESS

        When accepted:
            1. Service status becomes IN_PROGRESS.
            2. Customer receives an in-app notification.
            3. All active ADMIN / SUPER_ADMIN users receive an
               in-app acceptance notification.
            4. Optional WhatsApp customer status update is queued.
        """

        try:
            # =================================================
            # AUTHENTICATION
            # =================================================

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required.",
                )

            # =================================================
            # ROLE VALIDATION
            # =================================================

            user_role = str(
                getattr(current_user, "role", "") or ""
            ).strip().upper().replace(
                " ",
                "_",
            )

            if user_role != "ENGINEER":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only engineers can accept service requests.",
                )

            # =================================================
            # FIND SERVICE TICKET
            # =================================================

            ticket = ServiceTicketRepository.get_by_id(
                db,
                ticket_id,
            )

            if not ticket:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service Ticket not found.",
                )

            # =================================================
            # VERIFY ASSIGNED ENGINEER
            # =================================================

            assigned_engineer_id = getattr(
                ticket,
                "assigned_engineer_id",
                None,
            )

            if not assigned_engineer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No engineer is assigned to this service.",
                )

            if int(assigned_engineer_id) != int(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not assigned to this service request.",
                )

            # =================================================
            # VERIFY STATUS
            # =================================================

            current_status = str(
                getattr(ticket, "status", "") or ""
            ).strip().upper()

            # Already in progress: do not create duplicate notifications.
            if current_status == "IN_PROGRESS":
                return ticket

            # A previously confirmed ticket can safely be moved to
            # IN_PROGRESS as well.
            if current_status not in {"ASSIGNED", "CONFIRMED"}:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Service cannot be accepted because its current "
                        f"status is {current_status}."
                    ),
                )

            # =================================================
            # ACCEPT = MOVE DIRECTLY TO IN PROGRESS
            # =================================================

            ticket.status = "IN_PROGRESS"
            ticket.customer_status = "IN_PROGRESS"
            ticket.updated_by = current_user.id

            if not getattr(ticket, "started_at", None):
                ticket.started_at = datetime.utcnow()

            ServiceTicketRepository.update(
                db,
                ticket,
            )

            db.commit()
            db.refresh(ticket)

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            db.rollback()

            import traceback
            traceback.print_exc()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Service acceptance failed: {str(e)}",
            )

        # =====================================================
        # NOTIFICATIONS
        # =====================================================

        try:
            # -------------------------------------------------
            # Customer notification
            # -------------------------------------------------

            engineer_name = ServiceTicketService._get_engineer_name(
                current_user
            )

            ServiceTicketService._add_customer_notification(
                db=db,
                ticket=ticket,
                title="Service Engineer Accepted",
                message=(
                    f"Engineer {engineer_name} has accepted your service "
                    f"request {ticket.ticket_number}. The service is now "
                    f"in progress."
                ),
                notification_type="SERVICE_ACCEPTED",
            )

            # -------------------------------------------------
            # Admin / Super Admin notification
            # -------------------------------------------------

            ServiceTicketService._add_admin_acceptance_notifications(
                db=db,
                ticket=ticket,
                engineer=current_user,
            )

            db.commit()

        except Exception as notification_error:
            # The service has already successfully moved to IN_PROGRESS.
            # Do not undo that status just because a notification failed.
            db.rollback()

            import traceback
            traceback.print_exc()

            print(
                "WARNING: Service accepted successfully, "
                f"but notification creation failed: {notification_error}"
            )

        # =====================================================
        # OPTIONAL WHATSAPP CUSTOMER STATUS UPDATE
        # =====================================================

        if background_tasks:
            try:
                customer = None

                if ticket.customer_id:
                    customer = CustomerRepository.get_by_id(
                        db,
                        ticket.customer_id,
                    )

                if customer and customer.phone:
                    customer_name = (
                        getattr(customer, "customer_name", None)
                        or getattr(customer, "name", None)
                        or ""
                    )

                    background_tasks.add_task(
                        WhatsAppService.send_service_status_update,
                        recipient_phone=customer.phone,
                        ticket_number=ticket.ticket_number,
                        customer_name=customer_name,
                        status_value="IN_PROGRESS",
                    )

            except Exception as whatsapp_error:
                print(
                    "WARNING: Could not queue customer WhatsApp "
                    f"status update: {whatsapp_error}"
                )

        # =====================================================
        # BUILD JSON-FRIENDLY RESPONSE
        # =====================================================
        # ServiceTicketResponse expects nested dictionaries for
        # customer, machine, product and assigned_engineer.
        # =====================================================

        response_data = ServiceTicketService.get_service_tickets(
            db=db,
            search=ticket.ticket_number,
            customer_id=None,
            machine_id=None,
            engineer_id=current_user.id,
            status=None,
            priority=None,
            ticket_type=None,
            page=1,
            page_size=1,
        )

        if response_data.get("items"):
            return response_data["items"][0]

        return ticket

    # =====================================================
    # ADMIN IN-APP REJECTION NOTIFICATION
    # =====================================================

    @staticmethod
    def _add_admin_rejection_notifications(
        db: Session,
        ticket,
        engineer,
    ):
        """Create unread rejection notifications for active admins."""
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

        engineer_name = ServiceTicketService._get_engineer_name(engineer)
        ticket_number = getattr(ticket, "ticket_number", None) or f"#{ticket.id}"

        for admin in admins:
            db.add(
                Notification(
                    user_id=admin.id,
                    title="Service Rejected by Engineer",
                    message=(
                        f"Engineer {engineer_name} has rejected service request "
                        f"{ticket_number}. The service has been cancelled."
                    ),
                    notification_type="SERVICE_REJECTED",
                    is_read=False,
                    reference_type="SERVICE_TICKET",
                    reference_id=ticket.id,
                )
            )

        return len(admins)


    # =====================================================
    # ENGINEER REJECT SERVICE
    # =====================================================

    @staticmethod
    def reject_service(
        db: Session,
        ticket_id: int,
        current_user,
        background_tasks: BackgroundTasks = None,
    ):
        """
        Reject an assigned service.

        Status transition:
            ASSIGNED -> CANCELLED

        Only the engineer assigned to the ticket can reject it.
        The cancellation is committed before notifications are created.
        """
        try:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required.",
                )

            user_role = str(
                getattr(current_user, "role", "") or ""
            ).strip().upper().replace(" ", "_")

            if user_role != "ENGINEER":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only engineers can reject service requests.",
                )

            ticket = ServiceTicketRepository.get_by_id(db, ticket_id)

            if not ticket:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service Ticket not found.",
                )

            assigned_engineer_id = getattr(
                ticket, "assigned_engineer_id", None
            )

            if not assigned_engineer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No engineer is assigned to this service.",
                )

            if int(assigned_engineer_id) != int(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not assigned to this service request.",
                )

            current_status = str(
                getattr(ticket, "status", "") or ""
            ).strip().upper()

            if current_status == "CANCELLED":
                return ticket

            if current_status != "ASSIGNED":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Service can be rejected only when its current "
                        f"status is ASSIGNED. Current status is {current_status}."
                    ),
                )

            ticket.status = "CANCELLED"
            ticket.customer_status = "CANCELLED"
            ticket.updated_by = current_user.id

            ServiceTicketRepository.update(db, ticket)
            db.commit()
            db.refresh(ticket)

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Service rejection failed: {str(e)}",
            )

        # -----------------------------------------------------
        # Notifications are intentionally after the ticket commit.
        # -----------------------------------------------------
        try:
            engineer_name = ServiceTicketService._get_engineer_name(
                current_user
            )

            ServiceTicketService._add_customer_notification(
                db=db,
                ticket=ticket,
                title="Service Request Cancelled",
                message=(
                    f"Your service request {ticket.ticket_number} has been "
                    f"cancelled because the assigned engineer {engineer_name} "
                    f"rejected the service."
                ),
                notification_type="SERVICE_REJECTED",
            )

            ServiceTicketService._add_admin_rejection_notifications(
                db=db,
                ticket=ticket,
                engineer=current_user,
            )

            db.commit()

        except Exception as notification_error:
            db.rollback()
            import traceback
            traceback.print_exc()
            print(
                "WARNING: Service rejected successfully, but notification "
                f"creation failed: {notification_error}"
            )

        # -----------------------------------------------------
        # Optional customer WhatsApp status update.
        # -----------------------------------------------------
        if background_tasks:
            try:
                customer = None
                if ticket.customer_id:
                    customer = CustomerRepository.get_by_id(
                        db, ticket.customer_id
                    )

                if customer and customer.phone:
                    customer_name = (
                        getattr(customer, "customer_name", None)
                        or getattr(customer, "name", None)
                        or ""
                    )

                    background_tasks.add_task(
                        WhatsAppService.send_service_status_update,
                        recipient_phone=customer.phone,
                        ticket_number=ticket.ticket_number,
                        customer_name=customer_name,
                        status_value="CANCELLED",
                    )
            except Exception as whatsapp_error:
                print(
                    "WARNING: Could not queue customer WhatsApp rejection "
                    f"update: {whatsapp_error}"
                )

        # -----------------------------------------------------
        # Return the same enriched structure used by the engineer list.
        # -----------------------------------------------------
        response_data = ServiceTicketService.get_service_tickets(
            db=db,
            search=ticket.ticket_number,
            customer_id=None,
            machine_id=None,
            engineer_id=current_user.id,
            status=None,
            priority=None,
            ticket_type=None,
            page=1,
            page_size=1,
        )

        if response_data.get("items"):
            return response_data["items"][0]

        return ticket


    # =====================================================
    # ENGINEER COMPLETE SERVICE
    # =====================================================

    @staticmethod
    def complete_service(
        db: Session,
        ticket_id: int,
        current_user,
        material_used: Optional[str] = None,
        service_cost=None,
        resolution: Optional[str] = None,
        payment_status: Optional[str] = "PENDING",
        background_tasks: BackgroundTasks = None,
    ):
        """
        Complete a service from the Engineer Portal.

        Required workflow:
            IN_PROGRESS -> COMPLETED

        Completion fields:
            - material_used: optional; engineer may enter "No"
            - service_cost: optional; must be >= 0 when supplied
            - resolution: optional
            - payment_status: optional; PENDING or RECEIVED

        After completion:
            1. Ticket is saved as COMPLETED.
            2. completed_at / completed_date are saved.
            3. Admin and Super Admin receive an unread notification.
            4. Customer receives an in-app completion notification.
            5. Optional WhatsApp customer status update is queued.
        """

        try:
            # =================================================
            # AUTHENTICATION
            # =================================================

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required.",
                )

            # =================================================
            # ROLE VALIDATION
            # =================================================

            user_role = str(
                getattr(current_user, "role", "") or ""
            ).strip().upper().replace(
                " ",
                "_",
            )

            if user_role != "ENGINEER":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only engineers can complete service requests.",
                )

            # =================================================
            # FIND SERVICE TICKET
            # =================================================

            ticket = ServiceTicketRepository.get_by_id(
                db,
                ticket_id,
            )

            if not ticket:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service Ticket not found.",
                )

            # =================================================
            # VERIFY ASSIGNED ENGINEER
            # =================================================

            assigned_engineer_id = getattr(
                ticket,
                "assigned_engineer_id",
                None,
            )

            if not assigned_engineer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No engineer is assigned to this service.",
                )

            if int(assigned_engineer_id) != int(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not assigned to this service request.",
                )

            # =================================================
            # VERIFY CURRENT STATUS
            # =================================================

            current_status = str(
                getattr(ticket, "status", "") or ""
            ).strip().upper()

            if current_status == "COMPLETED":
                return ticket

            if current_status != "IN_PROGRESS":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Service can be completed only when it is "
                        f"IN_PROGRESS. Current status is {current_status}."
                    ),
                )

            # =================================================
            # VALIDATE SERVICE COST
            # =================================================

            if service_cost is not None:
                try:
                    if service_cost < 0:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Service cost cannot be negative.",
                        )
                except TypeError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid service cost.",
                    )

            # =================================================
            # SAVE COMPLETION DETAILS
            # =================================================

            # These fields are added to the ServiceTicket model in
            # the next database-model step. The guard keeps this
            # service method safe if the model has not been migrated yet.
            if hasattr(ticket, "material_used"):
                ticket.material_used = (
                    material_used.strip()
                    if isinstance(material_used, str)
                    else material_used
                )

            if hasattr(ticket, "service_cost"):
                ticket.service_cost = service_cost

            if resolution is not None and hasattr(
                ticket,
                "resolution",
            ):
                ticket.resolution = resolution.strip()

            # =================================================
            # PAYMENT STATUS
            # =================================================

            normalized_payment_status = (
                str(payment_status or "PENDING")
                .strip()
                .upper()
            )

            if normalized_payment_status not in {
                "PENDING",
                "RECEIVED",
            }:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Payment status must be PENDING or RECEIVED.",
                )

            if hasattr(ticket, "payment_status"):
                ticket.payment_status = normalized_payment_status

            # =================================================
            # STATUS + TIMELINE
            # =================================================

            now = datetime.utcnow()

            ticket.status = "COMPLETED"
            ticket.customer_status = "COMPLETED"
            ticket.completed_at = now
            ticket.completed_date = date.today()
            ticket.updated_by = current_user.id

            ServiceTicketRepository.update(
                db,
                ticket,
            )

            # -------------------------------------------------
            # Commit service completion first.
            # Notification failure must not undo completion.
            # -------------------------------------------------

            db.commit()
            db.refresh(ticket)

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            db.rollback()

            import traceback
            traceback.print_exc()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Service completion failed: {str(e)}",
            )

        # =====================================================
        # NOTIFICATIONS
        # =====================================================

        try:
            engineer_name = ServiceTicketService._get_engineer_name(
                current_user
            )

            # -------------------------------------------------
            # Customer notification
            # -------------------------------------------------

            ServiceTicketService._add_customer_notification(
                db=db,
                ticket=ticket,
                title="Service Completed",
                message=(
                    f"Engineer {engineer_name} has completed your "
                    f"service request {ticket.ticket_number}."
                ),
                notification_type="SERVICE_COMPLETED",
            )

            # -------------------------------------------------
            # Admin / Super Admin notification
            # -------------------------------------------------

            ServiceTicketService._add_admin_completion_notifications(
                db=db,
                ticket=ticket,
                engineer=current_user,
            )

            db.commit()

        except Exception as notification_error:
            # Completion was already committed successfully.
            db.rollback()

            import traceback
            traceback.print_exc()

            print(
                "WARNING: Service completed successfully, "
                f"but notification creation failed: {notification_error}"
            )

        # =====================================================
        # OPTIONAL WHATSAPP CUSTOMER STATUS UPDATE
        # =====================================================

        if background_tasks:
            try:
                customer = None

                if ticket.customer_id:
                    customer = CustomerRepository.get_by_id(
                        db,
                        ticket.customer_id,
                    )

                if customer and customer.phone:
                    customer_name = (
                        getattr(customer, "customer_name", None)
                        or getattr(customer, "name", None)
                        or ""
                    )

                    background_tasks.add_task(
                        WhatsAppService.send_service_status_update,
                        recipient_phone=customer.phone,
                        ticket_number=ticket.ticket_number,
                        customer_name=customer_name,
                        status_value="COMPLETED",
                    )

            except Exception as whatsapp_error:
                print(
                    "WARNING: Could not queue customer WhatsApp "
                    f"completion update: {whatsapp_error}"
                )

        # =====================================================
        # BUILD RESPONSE IN THE SAME JSON-FRIENDLY FORMAT USED
        # BY GET /service-tickets/engineer/my-services
        # =====================================================
        #
        # ServiceTicketResponse expects nested customer, machine,
        # product and engineer values as dictionaries. Returning
        # the raw SQLAlchemy ServiceTicket object causes FastAPI
        # ResponseValidationError.
        #
        # Reuse the existing list serializer instead of duplicating
        # the response-building logic here.
        # =====================================================

        response_data = ServiceTicketService.get_service_tickets(
            db=db,
            search=ticket.ticket_number,
            customer_id=None,
            machine_id=None,
            engineer_id=current_user.id,
            status=None,
            priority=None,
            ticket_type=None,
            page=1,
            page_size=1,
        )

        if response_data.get("items"):
            return response_data["items"][0]

        # Extremely unlikely fallback. The completion itself has
        # already been committed successfully.
        return {
            key: getattr(ticket, key)
            for key in (
                "id",
                "ticket_number",
                "subject",
                "complaint",
                "priority",
                "status",
                "customer_id",
                "machine_id",
                "assigned_engineer_id",
                "reported_date",
                "completed_date",
                "completed_at",
                "resolution",
                "material_used",
                "service_cost",
                "payment_status",
                "customer_status",
                "created_by",
                "updated_by",
                "created_at",
                "updated_at",
            )
            if hasattr(ticket, key)
        }


    # =====================================================
    # CHANGE STATUS
    # =====================================================

    @staticmethod
    def change_status(
        db: Session,
        ticket_id: int,
        status_value: str,
        current_user,
        background_tasks: BackgroundTasks = None,
    ):

        ticket = (
            ServiceTicketRepository.get_by_id(
                db,
                ticket_id,
            )
        )

        if not ticket:

            raise HTTPException(
                status_code=404,
                detail="Service Ticket not found.",
            )

        normalized_status = str(
            status_value
        ).strip().upper()

        allowed_statuses = {
            "REQUESTED",
            "ASSIGNED",
            "CONFIRMED",
            "REACHED",
            "IN_PROGRESS",
            "ON_HOLD",
            "PARTS_PENDING",
            "COMPLETED",
            "CLOSED",
            "CANCELLED",
        }

        if normalized_status not in (
            allowed_statuses
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid service ticket status."
                ),
            )

        # ---------------------------------------------
        # Update status
        # ---------------------------------------------

        ticket.status = (
            normalized_status
        )

        ticket.customer_status = (
            normalized_status
        )

        # ---------------------------------------------
        # Timeline
        # ---------------------------------------------

        now = datetime.utcnow()

        if normalized_status == "ASSIGNED":

            ticket.assigned_at = now

        elif normalized_status == "IN_PROGRESS":

            ticket.started_at = now

        elif normalized_status == "COMPLETED":

            ticket.completed_at = now

            ticket.completed_date = (
                date.today()
            )

        elif normalized_status == "CLOSED":

            ticket.closed_at = now

        # ---------------------------------------------
        # Audit
        # ---------------------------------------------

        ticket.updated_by = (
            current_user.id
        )

        ServiceTicketRepository.update(
            db,
            ticket,
        )

        db.commit()

        db.refresh(ticket)

        # =================================================
        # WHATSAPP - SERVICE STATUS UPDATE
        # =================================================

        if background_tasks:
            customer = None

            if ticket.customer_id:
                customer = CustomerRepository.get_by_id(
                    db,
                    ticket.customer_id,
                )

            if customer and customer.phone:
                customer_name = (
                    getattr(customer, "customer_name", None)
                    or getattr(customer, "name", None)
                    or ""
                )

                background_tasks.add_task(
                    WhatsAppService.send_service_status_update,
                    recipient_phone=customer.phone,
                    ticket_number=ticket.ticket_number,
                    customer_name=customer_name,
                    status_value=normalized_status,
                )

        # =====================================================
        # RETURN ENRICHED RESPONSE
        # =====================================================
        #
        # The database record is already updated above.
        # We only change the status to CANCELLED; we NEVER
        # delete the service ticket.
        #
        # ServiceTicketResponse expects customer, machine and
        # assigned_engineer as dictionaries. Therefore return
        # the same enriched structure used by the list endpoint
        # instead of returning the raw SQLAlchemy object.
        # =====================================================

        response_data = ServiceTicketService.get_service_tickets(
            db=db,
            search=ticket.ticket_number,
            customer_id=None,
            machine_id=None,
            engineer_id=None,
            status=None,
            priority=None,
            ticket_type=None,
            page=1,
            page_size=1,
        )

        if response_data.get("items"):
            return response_data["items"][0]

        # This fallback still does NOT delete anything.
        return ticket

    # =====================================================
    # DASHBOARD
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session,
    ):

        return (
            ServiceTicketRepository.dashboard(
                db
            )
        )