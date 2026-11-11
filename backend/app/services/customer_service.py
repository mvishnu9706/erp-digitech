from fastapi import (
    HTTPException,
    status,
)

from fastapi.responses import (
    StreamingResponse,
)

from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session

from io import BytesIO

from openpyxl import Workbook

from openpyxl.styles import (
    Font,
    Alignment,
)

from openpyxl.utils import (
    get_column_letter,
)

from app.models.customer import (
    Customer,
)

from app.models.machine import (
    Machine,
)

from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
)

from app.repositories.customer_repository import (
    CustomerRepository,
)

from app.repositories.machine_repository import (
    MachineRepository,
)

from app.utils.customer_code import (
    CustomerCodeGenerator,
)

from app.utils.machine_number import (
    MachineNumberGenerator,
)


class CustomerService:

    # =====================================================
    # Create Customer
    # =====================================================

    @staticmethod
    def create_customer(
        db: Session,
        data: CustomerCreate,
        current_user
    ):

        # =================================================
        # Customer Name Validation
        # =================================================

        customer = CustomerRepository.get_by_customer_name(
            db,
            data.customer_name.strip()
        )

        if customer:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer already exists."
            )

        # =================================================
        # Email Validation
        # =================================================

        if data.email:

            email = CustomerRepository.get_by_email(
                db,
                str(data.email)
            )

            if email:

                raise HTTPException(
                    status_code=400,
                    detail="Email already exists."
                )

        # =================================================
        # GSTIN Validation
        # =================================================

        if data.gstin:

            gst = CustomerRepository.get_by_gstin(
                db,
                data.gstin.strip().upper()
            )

            if gst:

                raise HTTPException(
                    status_code=400,
                    detail="GSTIN already exists."
                )

        # =================================================
        # PAN Validation
        # =================================================

        if data.pan:

            pan = CustomerRepository.get_by_pan(
                db,
                data.pan.strip().upper()
            )

            if pan:

                raise HTTPException(
                    status_code=400,
                    detail="PAN already exists."
                )

        # =================================================
        # Generate Customer Code
        # =================================================

        last_customer = CustomerRepository.last_customer(
            db
        )

        if last_customer:

            customer_code = (
                CustomerCodeGenerator.generate(
                    last_customer.customer_code
                )
            )

        else:

            customer_code = (
                CustomerCodeGenerator.generate()
            )

        # =================================================
        # Create Customer Object
        # =================================================

        customer = Customer(

            customer_code=customer_code,

            customer_name=data.customer_name.strip(),

            contact_person=(
                data.contact_person.strip()
                if data.contact_person
                else None
            ),

            phone=(
                data.phone.strip()
                if data.phone
                else None
            ),

            email=(
                str(data.email)
                if data.email
                else None
            ),

            website=(
                data.website.strip()
                if data.website
                else None
            ),

            gstin=(
                data.gstin.strip().upper()
                if data.gstin
                else None
            ),

            pan=(
                data.pan.strip().upper()
                if data.pan
                else None
            ),

            billing_address=data.billing_address,

            shipping_address=data.shipping_address,

            city=data.city,

            state=data.state,

            country=data.country,

            pincode=data.pincode,

            credit_limit=data.credit_limit,

            credit_days=data.credit_days,

            opening_balance=data.opening_balance,

            current_balance=data.opening_balance,

            remarks=data.remarks,

            is_active=data.is_active,

            # =================================================
            # CUSTOMER SERVICE PORTAL
            # =================================================
            #
            # New customers use the value supplied by the
            # customer form.
            #
            service_enabled=data.service_enabled,

            created_by=current_user.id,

            updated_by=current_user.id
        )

        # =================================================
        # Save Customer + Machines
        # =================================================
        #
        # A customer can have zero, one, or multiple machines.
        # Each machine contains only:
        #   - machine_name
        #   - machine_serial_number
        #
        # Product is intentionally None for machines created
        # from the Customer form.
        # =================================================

        try:

            CustomerRepository.create(
                db,
                customer
            )

            machines_data = getattr(
                data,
                "machines",
                []
            ) or []

            # -------------------------------------------------
            # Create All Machines From Customer Form
            # -------------------------------------------------

            request_serial_numbers = set()

            for machine_data in machines_data:

                machine_name = (
                    machine_data.machine_name.strip()
                    if machine_data.machine_name
                    else ""
                )

                machine_serial_number = (
                    machine_data.machine_serial_number.strip()
                    if machine_data.machine_serial_number
                    else ""
                )

                if not machine_name or not machine_serial_number:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Machine Name and Machine Serial Number "
                            "must both be provided."
                        )
                    )

                # -------------------------------------------------
                # Duplicate Serial Number In This Request
                # -------------------------------------------------

                serial_key = machine_serial_number.lower()

                if serial_key in request_serial_numbers:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Duplicate Machine Serial Number "
                            "in the customer machines."
                        )
                    )

                request_serial_numbers.add(
                    serial_key
                )

                # -------------------------------------------------
                # Duplicate Serial Number In Database
                # -------------------------------------------------

                existing_machine = (
                    MachineRepository.get_by_serial_number(
                        db,
                        machine_serial_number
                    )
                )

                if existing_machine:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Machine Serial Number already exists."
                        )
                    )

                # -------------------------------------------------
                # Generate Machine Number
                # -------------------------------------------------

                last_machine = (
                    MachineRepository.last_machine(db)
                )

                if last_machine:
                    machine_number = (
                        MachineNumberGenerator.generate(
                            last_machine.id + 1
                        )
                    )
                else:
                    machine_number = (
                        MachineNumberGenerator.generate(1)
                    )

                # -------------------------------------------------
                # Create Machine
                # -------------------------------------------------

                machine = Machine(
                    machine_number=machine_number,
                    machine_name=machine_name,
                    customer_id=customer.id,
                    product_id=None,
                    serial_number=machine_serial_number,

                    # -------------------------------------------------
                    # Rental / Billing
                    # -------------------------------------------------

                    rental_rate=(
                        machine_data.rental_rate
                        if machine_data.rental_rate is not None
                        else 0
                    ),

                    rental_advance=(
                        machine_data.rental_advance
                        if machine_data.rental_advance is not None
                        else 0
                    ),

                    free_prints_per_month=(
                        machine_data.free_prints_per_month
                        if machine_data.free_prints_per_month is not None
                        else 0
                    ),

                    # Individual monthly free-copy allowances.
                    a4_bw_free_copies=(
                        getattr(machine_data, "a4_bw_free_copies", None) or 0
                    ),
                    a4_color_free_copies=(
                        getattr(machine_data, "a4_color_free_copies", None) or 0
                    ),
                    a3_bw_free_copies=(
                        getattr(machine_data, "a3_bw_free_copies", None) or 0
                    ),
                    a3_color_free_copies=(
                        getattr(machine_data, "a3_color_free_copies", None) or 0
                    ),

                    # -------------------------------------------------
                    # Copy Rates
                    # -------------------------------------------------

                    a4_bw_rate=(
                        machine_data.a4_bw_rate
                        if machine_data.a4_bw_rate is not None
                        else 0
                    ),

                    a4_color_rate=(
                        machine_data.a4_color_rate
                        if machine_data.a4_color_rate is not None
                        else 0
                    ),

                    a3_bw_rate=(
                        machine_data.a3_bw_rate
                        if machine_data.a3_bw_rate is not None
                        else 0
                    ),

                    a3_color_rate=(
                        machine_data.a3_color_rate
                        if machine_data.a3_color_rate is not None
                        else 0
                    ),

                    is_active=True,
                    status="ACTIVE",
                    created_by=current_user.id,
                    updated_by=current_user.id
                )

                MachineRepository.create(
                    db,
                    machine
                )

            # -------------------------------------------------
            # Commit Customer + All Machines Together
            # -------------------------------------------------

            db.commit()

            db.refresh(customer)

            CustomerService._attach_machines(
                db,
                [customer]
            )

            return customer


        except HTTPException:

            db.rollback()
            raise

        except IntegrityError:

            db.rollback()

            raise HTTPException(
                status_code=400,
                detail=(
                    "Customer could not be created "
                    "because a unique value already exists."
                )
            )

    # =====================================================
    # Attach Customer Machines
    # =====================================================
    #
    # Machines are stored in the machines table and linked
    # through machines.customer_id.
    #
    # A customer can have MULTIPLE machines.
    #
    # This helper loads every machine belonging to each
    # customer and exposes:
    #
    #   customer.machines
    #
    # It also keeps the existing single-machine fields for
    # backward compatibility:
    #
    #   customer.machine_id
    #   customer.machine_name
    #   customer.machine_serial_number
    #
    # The first machine is used for those legacy single-machine
    # fields. The complete list is available in customer.machines.
    #
    # =====================================================

    @staticmethod
    def _attach_machines(
        db: Session,
        customers
    ):

        if not customers:
            return customers

        customer_ids = [
            customer.id
            for customer in customers
            if customer and customer.id is not None
        ]

        if not customer_ids:
            return customers

        machines = (
            db.query(Machine)
            .filter(
                Machine.customer_id.in_(customer_ids)
            )
            .order_by(
                Machine.id.asc()
            )
            .all()
        )

        machines_by_customer = {}

        for machine in machines:
            machines_by_customer.setdefault(
                machine.customer_id,
                []
            ).append(machine)

        for customer in customers:

            customer_machines = machines_by_customer.get(
                customer.id,
                []
            )

            # Complete machine list for the customer.
            customer.machines = customer_machines

            # Backward-compatible single-machine fields.
            first_machine = (
                customer_machines[0]
                if customer_machines
                else None
            )

            customer.machine_id = (
                first_machine.id
                if first_machine
                else None
            )

            customer.machine_name = (
                first_machine.machine_name
                if first_machine
                else None
            )

            customer.machine_serial_number = (
                first_machine.serial_number
                if first_machine
                else None
            )

        return customers

    # =====================================================
    # Get Customers
    # =====================================================

    @staticmethod
    def get_customers(
        db: Session,
        search=None,
        city=None,
        state=None,
        is_active=None,
        page=1,
        page_size=10
    ):

        skip = (
            (page - 1)
            * page_size
        )

        customers = CustomerRepository.get_all(

            db=db,

            search=search,

            city=city,

            state=state,

            is_active=is_active,

            skip=skip,

            limit=page_size

        )

        # IMPORTANT:
        # CustomerRepository returns customer records only.
        # Machine information is stored in the separate
        # machines table, so load and attach all machines here.
        return CustomerService._attach_machines(
            db,
            customers
        )

    # =====================================================
    # Get Customer By ID
    # =====================================================

    @staticmethod
    def get_customer(
        db: Session,
        customer_id: int
    ):

        customer = CustomerRepository.get_by_id(
            db,
            customer_id
        )

        if not customer:

            raise HTTPException(
                status_code=404,
                detail="Customer not found."
            )

        # Attach all machines belonging to this customer.
        CustomerService._attach_machines(
            db,
            [customer]
        )

        return customer

    # =====================================================
    # Update Customer
    # =====================================================

    @staticmethod
    def update_customer(
        db: Session,
        customer_id: int,
        data: CustomerUpdate,
        current_user
    ):

        customer = CustomerRepository.get_by_id(
            db,
            customer_id
        )

        if not customer:

            raise HTTPException(
                status_code=404,
                detail="Customer not found."
            )

        # =================================================
        # Get Only Supplied Fields
        # =================================================

        update_data = data.model_dump(
            exclude_unset=True
        )

        # =================================================
        # MACHINE DATA
        # =================================================
        #
        # "machines" belongs to the Machine table and must
        # never be passed to setattr(customer, ...).
        #
        # Existing machine:
        #     id = existing machine id
        #
        # New machine:
        #     id = None
        #
        # This supports multiple machines for one customer.
        # =================================================

        machines_data = update_data.pop(
            "machines",
            None
        )

        # Keep the old single-machine fields working.
        machine_id = update_data.pop(
            "machine_id",
            None
        )

        machine_name = update_data.pop(
            "machine_name",
            None
        )

        machine_serial_number = update_data.pop(
            "machine_serial_number",
            None
        )

        # =================================================
        # Customer Name Validation
        # =================================================

        if "customer_name" in update_data:

            if update_data["customer_name"]:

                new_name = (
                    update_data["customer_name"].strip()
                )

                existing = (
                    CustomerRepository
                    .get_by_customer_name(
                        db,
                        new_name
                    )
                )

                if (
                    existing
                    and existing.id != customer.id
                ):
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Customer name already exists."
                        )
                    )

                update_data[
                    "customer_name"
                ] = new_name

        # =================================================
        # Email Validation
        # =================================================

        if (
            "email" in update_data
            and update_data["email"]
        ):

            email = CustomerRepository.get_by_email(
                db,
                str(update_data["email"])
            )

            if (
                email
                and email.id != customer.id
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Email already exists."
                )

            update_data["email"] = str(
                update_data["email"]
            )

        # =================================================
        # GSTIN Validation
        # =================================================

        if (
            "gstin" in update_data
            and update_data["gstin"]
        ):

            gstin = (
                update_data["gstin"]
                .strip()
                .upper()
            )

            existing = (
                CustomerRepository.get_by_gstin(
                    db,
                    gstin
                )
            )

            if (
                existing
                and existing.id != customer.id
            ):
                raise HTTPException(
                    status_code=400,
                    detail="GSTIN already exists."
                )

            update_data[
                "gstin"
            ] = gstin

        # =================================================
        # PAN Validation
        # =================================================

        if (
            "pan" in update_data
            and update_data["pan"]
        ):

            pan = (
                update_data["pan"]
                .strip()
                .upper()
            )

            existing = (
                CustomerRepository.get_by_pan(
                    db,
                    pan
                )
            )

            if (
                existing
                and existing.id != customer.id
            ):
                raise HTTPException(
                    status_code=400,
                    detail="PAN already exists."
                )

            update_data[
                "pan"
            ] = pan

        # =================================================
        # Apply Customer Updates
        # =================================================

        for key, value in update_data.items():

            setattr(
                customer,
                key,
                value
            )

        customer.updated_by = current_user.id

        # =================================================
        # Update / Add Multiple Machines
        # =================================================

        try:

            # -------------------------------------------------
            # New Multiple-Machine Format
            # -------------------------------------------------

            if machines_data is not None:

                request_serial_numbers = set()

                for machine_data in machines_data:

                    machine_id_value = (
                        machine_data.get("id")
                        if isinstance(
                            machine_data,
                            dict
                        )
                        else getattr(
                            machine_data,
                            "id",
                            None
                        )
                    )

                    name_value = (
                        machine_data.get("machine_name")
                        if isinstance(
                            machine_data,
                            dict
                        )
                        else getattr(
                            machine_data,
                            "machine_name",
                            None
                        )
                    )

                    serial_value = (
                        machine_data.get(
                            "machine_serial_number"
                        )
                        if isinstance(
                            machine_data,
                            dict
                        )
                        else getattr(
                            machine_data,
                            "machine_serial_number",
                            None
                        )
                    )

                    name_value = (
                        name_value.strip()
                        if name_value
                        else ""
                    )

                    serial_value = (
                        serial_value.strip()
                        if serial_value
                        else ""
                    )

                    # -------------------------------------------------
                    # Rental / Billing Values
                    # -------------------------------------------------

                    rental_rate_value = (
                        machine_data.get("rental_rate")
                        if isinstance(machine_data, dict)
                        else getattr(
                            machine_data,
                            "rental_rate",
                            0
                        )
                    )

                    rental_advance_value = (
                        machine_data.get("rental_advance")
                        if isinstance(machine_data, dict)
                        else getattr(
                            machine_data,
                            "rental_advance",
                            0
                        )
                    )

                    free_prints_value = (
                        machine_data.get("free_prints_per_month")
                        if isinstance(machine_data, dict)
                        else getattr(
                            machine_data,
                            "free_prints_per_month",
                            0
                        )
                    )

                    # Individual monthly free-copy allowances.
                    a4_bw_free_copies_value = (
                        machine_data.get("a4_bw_free_copies")
                        if isinstance(machine_data, dict)
                        else getattr(machine_data, "a4_bw_free_copies", None)
                    )
                    a4_color_free_copies_value = (
                        machine_data.get("a4_color_free_copies")
                        if isinstance(machine_data, dict)
                        else getattr(machine_data, "a4_color_free_copies", None)
                    )
                    a3_bw_free_copies_value = (
                        machine_data.get("a3_bw_free_copies")
                        if isinstance(machine_data, dict)
                        else getattr(machine_data, "a3_bw_free_copies", None)
                    )
                    a3_color_free_copies_value = (
                        machine_data.get("a3_color_free_copies")
                        if isinstance(machine_data, dict)
                        else getattr(machine_data, "a3_color_free_copies", None)
                    )

                    # -------------------------------------------------
                    # Copy Rates
                    # -------------------------------------------------

                    a4_bw_rate_value = (
                        machine_data.get("a4_bw_rate")
                        if isinstance(machine_data, dict)
                        else getattr(
                            machine_data,
                            "a4_bw_rate",
                            0
                        )
                    )

                    a4_color_rate_value = (
                        machine_data.get("a4_color_rate")
                        if isinstance(machine_data, dict)
                        else getattr(
                            machine_data,
                            "a4_color_rate",
                            0
                        )
                    )

                    a3_bw_rate_value = (
                        machine_data.get("a3_bw_rate")
                        if isinstance(machine_data, dict)
                        else getattr(
                            machine_data,
                            "a3_bw_rate",
                            0
                        )
                    )

                    a3_color_rate_value = (
                        machine_data.get("a3_color_rate")
                        if isinstance(machine_data, dict)
                        else getattr(
                            machine_data,
                            "a3_color_rate",
                            0
                        )
                    )

                    if not name_value or not serial_value:
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                "Machine Name and Machine "
                                "Serial Number must both "
                                "be provided."
                            )
                        )

                    # -------------------------------------------------
                    # Prevent duplicate serials inside this request
                    # -------------------------------------------------

                    serial_key = serial_value.lower()

                    if serial_key in request_serial_numbers:
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                "Duplicate Machine Serial Number "
                                "in the customer machines."
                            )
                        )

                    request_serial_numbers.add(
                        serial_key
                    )

                    # -------------------------------------------------
                    # Existing Machine -> Update
                    # -------------------------------------------------

                    if machine_id_value is not None:

                        machine = (
                            MachineRepository.get_by_id(
                                db,
                                int(machine_id_value)
                            )
                        )

                        if not machine:

                            raise HTTPException(
                                status_code=404,
                                detail=(
                                    f"Machine {machine_id_value} "
                                    "not found."
                                )
                            )

                        if machine.customer_id != customer.id:

                            raise HTTPException(
                                status_code=403,
                                detail=(
                                    "This machine does not belong "
                                    "to this customer."
                                )
                            )

                        existing_machine = (
                            MachineRepository
                            .get_by_serial_number(
                                db,
                                serial_value
                            )
                        )

                        if (
                            existing_machine
                            and existing_machine.id != machine.id
                        ):
                            raise HTTPException(
                                status_code=400,
                                detail=(
                                    "Machine Serial Number "
                                    "already exists."
                                )
                            )

                        machine.machine_name = name_value
                        machine.serial_number = serial_value

                        machine.rental_rate = (
                            rental_rate_value
                            if rental_rate_value is not None
                            else 0
                        )

                        machine.rental_advance = (
                            rental_advance_value
                            if rental_advance_value is not None
                            else 0
                        )

                        machine.free_prints_per_month = (
                            free_prints_value
                            if free_prints_value is not None
                            else 0
                        )

                        if a4_bw_free_copies_value is not None:
                            machine.a4_bw_free_copies = a4_bw_free_copies_value
                        if a4_color_free_copies_value is not None:
                            machine.a4_color_free_copies = a4_color_free_copies_value
                        if a3_bw_free_copies_value is not None:
                            machine.a3_bw_free_copies = a3_bw_free_copies_value
                        if a3_color_free_copies_value is not None:
                            machine.a3_color_free_copies = a3_color_free_copies_value

                        machine.a4_bw_rate = (
                            a4_bw_rate_value
                            if a4_bw_rate_value is not None
                            else 0
                        )

                        machine.a4_color_rate = (
                            a4_color_rate_value
                            if a4_color_rate_value is not None
                            else 0
                        )

                        machine.a3_bw_rate = (
                            a3_bw_rate_value
                            if a3_bw_rate_value is not None
                            else 0
                        )

                        machine.a3_color_rate = (
                            a3_color_rate_value
                            if a3_color_rate_value is not None
                            else 0
                        )

                        machine.updated_by = current_user.id

                        db.add(machine)

                    # -------------------------------------------------
                    # New Machine -> Create
                    # -------------------------------------------------

                    else:

                        existing_machine = (
                            MachineRepository
                            .get_by_serial_number(
                                db,
                                serial_value
                            )
                        )

                        if existing_machine:
                            raise HTTPException(
                                status_code=400,
                                detail=(
                                    "Machine Serial Number "
                                    "already exists."
                                )
                            )

                        last_machine = (
                            MachineRepository.last_machine(
                                db
                            )
                        )

                        if last_machine:

                            machine_number = (
                                MachineNumberGenerator.generate(
                                    last_machine.id + 1
                                )
                            )

                        else:

                            machine_number = (
                                MachineNumberGenerator.generate(
                                    1
                                )
                            )

                        machine = Machine(
                            machine_number=machine_number,
                            machine_name=name_value,
                            customer_id=customer.id,
                            product_id=None,
                            serial_number=serial_value,

                            # -------------------------------------------------
                            # Rental / Billing
                            # -------------------------------------------------

                            rental_rate=(
                                rental_rate_value
                                if rental_rate_value is not None
                                else 0
                            ),

                            rental_advance=(
                                rental_advance_value
                                if rental_advance_value is not None
                                else 0
                            ),

                            free_prints_per_month=(
                                free_prints_value
                                if free_prints_value is not None
                                else 0
                            ),

                            # Individual monthly free-copy allowances.
                            a4_bw_free_copies=(
                                a4_bw_free_copies_value
                                if a4_bw_free_copies_value is not None
                                else 0
                            ),
                            a4_color_free_copies=(
                                a4_color_free_copies_value
                                if a4_color_free_copies_value is not None
                                else 0
                            ),
                            a3_bw_free_copies=(
                                a3_bw_free_copies_value
                                if a3_bw_free_copies_value is not None
                                else 0
                            ),
                            a3_color_free_copies=(
                                a3_color_free_copies_value
                                if a3_color_free_copies_value is not None
                                else 0
                            ),

                            # -------------------------------------------------
                            # Copy Rates
                            # -------------------------------------------------

                            a4_bw_rate=(
                                a4_bw_rate_value
                                if a4_bw_rate_value is not None
                                else 0
                            ),

                            a4_color_rate=(
                                a4_color_rate_value
                                if a4_color_rate_value is not None
                                else 0
                            ),

                            a3_bw_rate=(
                                a3_bw_rate_value
                                if a3_bw_rate_value is not None
                                else 0
                            ),

                            a3_color_rate=(
                                a3_color_rate_value
                                if a3_color_rate_value is not None
                                else 0
                            ),

                            is_active=True,
                            status="ACTIVE",
                            created_by=current_user.id,
                            updated_by=current_user.id
                        )

                        MachineRepository.create(
                            db,
                            machine
                        )

            # -------------------------------------------------
            # Backward-Compatible Single-Machine Format
            # -------------------------------------------------

            elif (
                machine_id is not None
                or machine_name is not None
                or machine_serial_number is not None
            ):

                if machine_id is None:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "machine_id is required when "
                            "updating machine information."
                        )
                    )

                machine = (
                    MachineRepository.get_by_id(
                        db,
                        machine_id
                    )
                )

                if not machine:
                    raise HTTPException(
                        status_code=404,
                        detail="Machine not found."
                    )

                if machine.customer_id != customer.id:
                    raise HTTPException(
                        status_code=403,
                        detail=(
                            "This machine does not belong "
                            "to this customer."
                        )
                    )

                if machine_name is not None:

                    machine.machine_name = (
                        machine_name.strip()
                        if machine_name
                        else None
                    )

                if machine_serial_number is not None:

                    serial_value = (
                        machine_serial_number.strip()
                        if machine_serial_number
                        else ""
                    )

                    if not serial_value:
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                "Machine Serial Number "
                                "cannot be empty."
                            )
                        )

                    existing_machine = (
                        MachineRepository
                        .get_by_serial_number(
                            db,
                            serial_value
                        )
                    )

                    if (
                        existing_machine
                        and existing_machine.id != machine.id
                    ):
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                "Machine Serial Number "
                                "already exists."
                            )
                        )

                    machine.serial_number = serial_value

                machine.updated_by = current_user.id

                db.add(machine)

            # =================================================
            # Save Customer + Machine Changes Together
            # =================================================

            db.add(customer)

            db.commit()

            db.refresh(customer)

            CustomerService._attach_machines(
                db,
                [customer]
            )

            return customer

        except HTTPException:

            db.rollback()
            raise

        except IntegrityError:

            db.rollback()

            raise HTTPException(
                status_code=400,
                detail=(
                    "Customer could not be updated "
                    "because a unique value already exists."
                )
            )


    # =====================================================
    # Delete Customer
    # =====================================================

    @staticmethod
    def delete_customer(
        db: Session,
        customer_id: int
    ):

        customer = CustomerRepository.get_by_id(
            db,
            customer_id
        )

        if not customer:

            raise HTTPException(
                status_code=404,
                detail="Customer not found."
            )

        # Delete all machines belonging to this customer first.
        # Machines reference customers through customer_id, so deleting
        # the customer first can fail with a foreign-key constraint.
        machines = (
            db.query(Machine)
            .filter(Machine.customer_id == customer.id)
            .all()
        )

        for machine in machines:
            db.delete(machine)

        CustomerRepository.delete(
            db,
            customer
        )

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Customer could not be deleted because it is referenced by existing records."
                )
            )

        return {

            "success": True,

            "message":
                "Customer deleted successfully."

        }

    # =====================================================
    # EXPORT CUSTOMERS TO EXCEL
    # =====================================================

    @staticmethod
    def export_customers(
        db: Session,
        search=None,
        city=None,
        state=None,
        is_active=None
    ):

        # =================================================
        # Get ALL Matching Customers
        # =================================================

        customers = CustomerRepository.get_all(

            db=db,

            search=search,

            city=city,

            state=state,

            is_active=is_active,

            skip=0,

            limit=1000000

        )

        # =================================================
        # Create Workbook
        # =================================================

        workbook = Workbook()

        worksheet = workbook.active

        worksheet.title = "Customers"

        # =================================================
        # Excel Headers
        # =================================================

        headers = [

            "Customer Code",

            "Customer Name",

            "Contact Person",

            "Phone",

            "Email",

            "Website",

            "GSTIN",

            "PAN",

            "Billing Address",

            "Shipping Address",

            "City",

            "State",

            "Country",

            "Pincode",

            "Credit Limit",

            "Credit Days",

            "Opening Balance",

            "Current Balance",

            "Service Portal",

            "Remarks",

            "Status",

            "Created At",

        ]

        worksheet.append(headers)

        # =================================================
        # Header Formatting
        # =================================================

        for cell in worksheet[1]:

            cell.font = Font(
                bold=True
            )

            cell.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

        # =================================================
        # Customer Data
        # =================================================

        for customer in customers:

            worksheet.append([

                customer.customer_code,

                customer.customer_name,

                customer.contact_person,

                customer.phone,

                customer.email,

                customer.website,

                customer.gstin,

                customer.pan,

                customer.billing_address,

                customer.shipping_address,

                customer.city,

                customer.state,

                customer.country,

                customer.pincode,

                float(
                    customer.credit_limit or 0
                ),

                customer.credit_days,

                float(
                    customer.opening_balance or 0
                ),

                float(
                    customer.current_balance or 0
                ),

                (
                    "Enabled"
                    if customer.service_enabled
                    else "Disabled"
                ),

                customer.remarks,

                (
                    "Active"
                    if customer.is_active
                    else "Inactive"
                ),

                (
                    customer.created_at.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if customer.created_at
                    else ""
                ),

            ])

        # =================================================
        # Freeze Header
        # =================================================

        worksheet.freeze_panes = "A2"

        # =================================================
        # Auto Column Width
        # =================================================

        for column_cells in worksheet.columns:

            max_length = 0

            column_index = (
                column_cells[0].column
            )

            column_letter = (
                get_column_letter(
                    column_index
                )
            )

            for cell in column_cells:

                try:

                    value_length = len(
                        str(
                            cell.value
                        )
                    )

                    if value_length > max_length:

                        max_length = value_length

                except Exception:

                    pass

            worksheet.column_dimensions[
                column_letter
            ].width = min(
                max_length + 2,
                40
            )

        # =================================================
        # Create Excel File In Memory
        # =================================================

        output = BytesIO()

        workbook.save(
            output
        )

        output.seek(0)

        # =================================================
        # Return Excel File
        # =================================================

        return StreamingResponse(

            output,

            media_type=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),

            headers={

                "Content-Disposition":
                    "attachment; "
                    "filename=Customers.xlsx"

            }

        )

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        # =================================================
        # Existing Dashboard
        # =================================================

        dashboard_data = (
            CustomerRepository.dashboard(
                db
            )
        )

        # =================================================
        # Service Portal Counts
        # =================================================

        service_enabled_customers = (

            db.query(Customer)

            .filter(
                Customer.service_enabled == True
            )

            .count()

        )

        service_disabled_customers = (

            db.query(Customer)

            .filter(
                Customer.service_enabled == False
            )

            .count()

        )

        # =================================================
        # Return Existing Dashboard Data
        # +
        # Service Portal Data
        # =================================================

        return {

            "total_customers":
                dashboard_data.total_customers
                if hasattr(
                    dashboard_data,
                    "total_customers"
                )
                else dashboard_data[
                    "total_customers"
                ],

            "active_customers":
                dashboard_data.active_customers
                if hasattr(
                    dashboard_data,
                    "active_customers"
                )
                else dashboard_data[
                    "active_customers"
                ],

            "inactive_customers":
                dashboard_data.inactive_customers
                if hasattr(
                    dashboard_data,
                    "inactive_customers"
                )
                else dashboard_data[
                    "inactive_customers"
                ],

            "total_outstanding":
                dashboard_data.total_outstanding
                if hasattr(
                    dashboard_data,
                    "total_outstanding"
                )
                else dashboard_data[
                    "total_outstanding"
                ],

            "total_credit_limit":
                dashboard_data.total_credit_limit
                if hasattr(
                    dashboard_data,
                    "total_credit_limit"
                )
                else dashboard_data[
                    "total_credit_limit"
                ],

            "service_enabled_customers":
                service_enabled_customers,

            "service_disabled_customers":
                service_disabled_customers,

        }

    # =====================================================
    # CUSTOMER PORTAL
    # =====================================================
    #
    # Everything below this section is for the logged-in
    # CUSTOMER portal.
    #
    # It does NOT replace the existing Admin customer APIs.
    #
    # =====================================================

    # =====================================================
    # Get My Customer
    # =====================================================

    @staticmethod
    def get_my_customer(
        db: Session,
        current_user
    ):

        # -------------------------------------------------
        # Check Customer Link
        # -------------------------------------------------

        if not current_user.customer_id:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Customer account is not linked "
                    "to a customer"
                )
            )

        # -------------------------------------------------
        # Find Customer
        # -------------------------------------------------

        customer = CustomerRepository.get_by_id(
            db,
            current_user.customer_id
        )

        if not customer:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found."
            )

        # -------------------------------------------------
        # Check Active Customer
        # -------------------------------------------------

        if not customer.is_active:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customer account is inactive."
            )

        return customer

    # =====================================================
    # Check Service Portal Access
    # =====================================================
    #
    # CUSTOMER role alone does NOT mean service access.
    #
    # Customer must also have:
    #
    # service_enabled = TRUE
    #
    # =====================================================

    @staticmethod
    def check_service_portal_access(
        db: Session,
        current_user
    ):

        customer = (
            CustomerService.get_my_customer(
                db,
                current_user
            )
        )

        if not customer.service_enabled:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Service portal access is disabled "
                    "for this customer."
                )
            )

        return customer

    # =====================================================
    # Get My Machines
    # =====================================================
    #
    # Returns only machines belonging to the logged-in
    # customer's account.
    #
    # =====================================================

    @staticmethod
    def get_my_machines(
        db: Session,
        current_user,
        search: str | None = None,
        page: int = 1,
        page_size: int = 100
    ):

        customer = (
            CustomerService.check_service_portal_access(
                db,
                current_user
            )
        )

        # -------------------------------------------------
        # Pagination
        # -------------------------------------------------

        skip = (
            (page - 1)
            * page_size
        )

        # -------------------------------------------------
        # Search
        # -------------------------------------------------

        if search and search.strip():

            machines = (

                MachineRepository
                .search_customer_machines(

                    db=db,

                    customer_id=customer.id,

                    keyword=search.strip(),

                    skip=skip,

                    limit=page_size

                )

            )

        else:

            machines = (

                MachineRepository
                .get_by_customer_id(

                    db=db,

                    customer_id=customer.id,

                    skip=skip,

                    limit=page_size

                )

            )

        # -------------------------------------------------
        # Total
        # -------------------------------------------------

        total = (

            MachineRepository
            .count_by_customer_id(

                db,

                customer.id

            )

        )

        return {

            "total": total,

            "page": page,

            "page_size": page_size,

            "items": machines

        }

    # =====================================================
    # Get My Machine
    # =====================================================
    #
    # The machine must belong to the logged-in customer.
    #
    # =====================================================

    @staticmethod
    def get_my_machine(
        db: Session,
        machine_id: int,
        current_user
    ):

        customer = (
            CustomerService.check_service_portal_access(
                db,
                current_user
            )
        )

        machine = (

            MachineRepository
            .get_customer_machine_by_id(

                db=db,

                machine_id=machine_id,

                customer_id=customer.id

            )

        )

        if not machine:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Machine not found or does not "
                    "belong to your customer account."
                )
            )

        return machine

    # =====================================================
    # Customer Portal Dashboard
    # =====================================================

    @staticmethod
    def customer_portal_dashboard(
        db: Session,
        current_user
    ):

        customer = (
            CustomerService.check_service_portal_access(
                db,
                current_user
            )
        )

        machine_data = (

            MachineRepository
            .customer_dashboard(

                db,

                customer.id

            )

        )

        return {

            "customer_id":
                customer.id,

            "customer_code":
                customer.customer_code,

            "customer_name":
                customer.customer_name,

            "service_enabled":
                customer.service_enabled,

            "total_machines":
                machine_data[
                    "total_machines"
                ],

            "active_machines":
                machine_data[
                    "active_machines"
                ],

            "warranty_expiring":
                machine_data[
                    "warranty_expiring"
                ],

            "amc_expiring":
                machine_data[
                    "amc_expiring"
                ]

        }