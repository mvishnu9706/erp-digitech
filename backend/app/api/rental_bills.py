from typing import Optional
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    Response,
    status,
)

from sqlalchemy.orm import Session

from ..database import get_db

from ..core.dependencies import (
    get_current_admin,
    get_current_rental_customer,
)

from ..models.user import User
from ..models.machine import Machine
from ..models.machine_document import MachineDocument

from ..schemas.rental_bill import (
    RentalBillCreate,
    RentalBillResponse,
    RentalBillUpdate,
    RentalBillPaymentUpdate,
)

from ..services.rental_bill_service import (
    RentalBillService,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/rental-bills",
    tags=["Rental Billing"],
)


# ============================================================
# CUSTOMER PORTAL
# GET MY RENTAL MACHINES
# ============================================================

@router.get(
    "/my-machines",
    summary="Get My Rental Machines",
)
def get_my_rental_machines(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_rental_customer
    ),
):
    """
    Return only rental machines belonging to
    the currently logged-in rental customer.
    """

    return RentalBillService.get_customer_machines(
        db=db,
        customer_id=current_user.customer_id,
    )


# ============================================================
# CUSTOMER PORTAL
# SUBMIT METER READING
# ============================================================

@router.post(
    "/my",
    response_model=RentalBillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit My Rental Meter Reading",
)
def create_my_rental_bill(
    data: RentalBillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_rental_customer
    ),
):
    """
    Customer submits a new rental meter reading.

    The customer_id is NEVER taken from the frontend.

    It comes from:
        current_user.customer_id
    """

    return RentalBillService.create_bill(
        db=db,
        customer_id=current_user.customer_id,
        data=data,
        current_user=current_user,
    )


# ============================================================
# CUSTOMER PORTAL
# GET MY RENTAL BILLS
# ============================================================

@router.get(
    "/my",
    response_model=list[RentalBillResponse],
    summary="Get My Rental Bills",
)
def get_my_rental_bills(
    machine_id: Optional[int] = Query(
        None,
        gt=0,
    ),
    billing_month: Optional[str] = Query(
        None,
    ),
    payment_status: Optional[str] = Query(
        None,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_rental_customer
    ),
):
    """
    Return only rental bills belonging to
    the authenticated rental customer.
    """

    return RentalBillService.get_customer_bills(
        db=db,
        customer_id=current_user.customer_id,
        machine_id=machine_id,
        billing_month=billing_month,
        payment_status=payment_status,
    )


# ============================================================
# CUSTOMER PORTAL
# GET SINGLE MY BILL
# ============================================================

@router.get(
    "/my/{bill_id}",
    response_model=RentalBillResponse,
    summary="Get My Rental Bill",
)
def get_my_rental_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_rental_customer
    ),
):
    """
    Return a rental bill only when it belongs
    to the authenticated customer.
    """

    return RentalBillService.get_customer_bill(
        db=db,
        customer_id=current_user.customer_id,
        bill_id=bill_id,
    )


# ============================================================
# ADMIN
# CREATE RENTAL BILL
# ============================================================

@router.post(
    "",
    response_model=RentalBillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin Create Rental Bill",
)
@router.post(
    "/",
    response_model=RentalBillResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_rental_bill(
    data: RentalBillCreate,
    customer_id: Optional[int] = Query(
        None,
        gt=0,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin
    ),
):
    """
    Admin creates a rental bill.

    Preferred request:

        POST /rental-bills/?customer_id=5

    JSON body:

        {
            "machine_id": 1,
            "billing_month": "2026-10",
            "billing_date": "2026-10-01",
            "previous_meter": 8500,
            "current_meter": 9800,
            "cost_per_copy": 0.40,
            "payment_status": "PENDING"
        }

    For compatibility, if customer_id is not supplied in the
    query string, this function also attempts to read customer_id
    from the request schema.

    The service remains responsible for validating that the
    selected machine belongs to the selected customer.
    """

    # ------------------------------------------------------------
    # Resolve customer ID
    # ------------------------------------------------------------

    resolved_customer_id = customer_id

    # Some versions of RentalBillCreate contain customer_id.
    # Use it when the query parameter was not supplied.
    if resolved_customer_id is None:

        body_customer_id = getattr(
            data,
            "customer_id",
            None,
        )

        if body_customer_id is not None:

            try:

                resolved_customer_id = int(
                    body_customer_id
                )

            except (TypeError, ValueError):

                resolved_customer_id = None

    # ------------------------------------------------------------
    # Validate customer ID
    # ------------------------------------------------------------

    if (
        resolved_customer_id is None
        or resolved_customer_id <= 0
    ):

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "loc": [
                        "query",
                        "customer_id",
                    ],
                    "msg": (
                        "customer_id is required. "
                        "Send it as ?customer_id=<id> "
                        "or include it in the request body."
                    ),
                    "type": "value_error.missing",
                }
            ],
        )

    # ------------------------------------------------------------
    # Create bill
    # ------------------------------------------------------------

    return RentalBillService.create_bill(
        db=db,
        customer_id=resolved_customer_id,
        data=data,
        current_user=current_user,
    )


# ============================================================
# ADMIN
# SAVE GENERATED RENTAL BILL PDF
# ============================================================

@router.post("/{bill_id}/pdf", summary="Save Generated Rental Bill PDF")
async def save_rental_bill_pdf(
    bill_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Save the PDF generated by the frontend into rental_bills.pdf_file."""
    file_name = (file.filename or "rental-bill.pdf").strip()
    if not file_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must have a .pdf extension.")
    data = await file.read()
    return RentalBillService.save_bill_pdf(
        db=db,
        bill_id=bill_id,
        pdf_data=data,
        file_name=file_name,
        content_type=file.content_type or "application/pdf",
    )


@router.post("/{bill_id}/generate-pdf", summary="Generate and Save Rental Bill PDF on Backend")
def generate_rental_bill_pdf(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Generate the invoice on the server and persist it in PostgreSQL."""
    return RentalBillService.generate_and_save_bill_pdf(db=db, bill_id=bill_id)


@router.get("/{bill_id}/pdf", summary="Download Saved Rental Bill PDF")
def get_rental_bill_pdf(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Return the stored PDF bytes for viewing or downloading."""
    from ..repositories.rental_bill_repository import RentalBillRepository
    bill = RentalBillRepository.get_by_id(db=db, bill_id=bill_id)
    if bill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rental bill not found.")
    if not bill.pdf_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No PDF has been saved for this rental bill yet.")
    return Response(
        content=bill.pdf_file,
        media_type=bill.pdf_content_type or "application/pdf",
        headers={"Content-Disposition": f'inline; filename="{bill.pdf_file_name or (bill.bill_number + ".pdf")}"'},
    )


# ============================================================
# ADMIN
# GET ALL RENTAL BILLS
# ============================================================

@router.get(
    "",
    response_model=list[RentalBillResponse],
    summary="Get All Rental Bills",
)
@router.get(
    "/",
    response_model=list[RentalBillResponse],
    include_in_schema=False,
)
def get_all_rental_bills(
    customer_id: Optional[int] = Query(
        None,
        gt=0,
    ),
    machine_id: Optional[int] = Query(
        None,
        gt=0,
    ),
    billing_month: Optional[str] = Query(
        None,
    ),
    payment_status: Optional[str] = Query(
        None,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin
    ),
):
    """
    Admin can view all rental bills.

    Optional filters:

        customer_id
        machine_id
        billing_month
        payment_status
    """

    return RentalBillService.get_all_bills(
        db=db,
        customer_id=customer_id,
        machine_id=machine_id,
        billing_month=billing_month,
        payment_status=payment_status,
    )


# ============================================================
# ADMIN
# GET SINGLE BILL
# ============================================================

@router.get(
    "/{bill_id}",
    response_model=RentalBillResponse,
    summary="Get Rental Bill",
)
def get_rental_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin
    ),
):
    """
    Admin gets a single rental bill.
    """

    return RentalBillService.get_bill(
        db=db,
        bill_id=bill_id,
    )


# ============================================================
# ADMIN
# UPDATE BILL
# ============================================================

@router.put(
    "/{bill_id}",
    response_model=RentalBillResponse,
    summary="Update Rental Bill",
)
def update_rental_bill(
    bill_id: int,
    data: RentalBillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin
    ),
):
    """
    Admin updates rental bill information.
    """

    return RentalBillService.update_bill(
        db=db,
        bill_id=bill_id,
        data=data,
        current_user=current_user,
    )


# ============================================================
# ADMIN
# UPDATE PAYMENT
# ============================================================

@router.patch(
    "/{bill_id}/payment",
    response_model=RentalBillResponse,
    summary="Update Rental Bill Payment",
)
def update_rental_bill_payment(
    bill_id: int,
    data: RentalBillPaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin
    ),
):
    """
    Update rental bill payment status and
    paid amount.
    """

    return RentalBillService.update_payment(
        db=db,
        bill_id=bill_id,
        data=data,
        current_user=current_user,
    )


# ============================================================
# ADMIN
# CANCEL BILL
# ============================================================

@router.delete(
    "/{bill_id}",
    response_model=RentalBillResponse,
    summary="Cancel Rental Bill",
)
def cancel_rental_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin
    ),
):
    """
    Cancel a rental bill.

    The database record remains.
    It is NOT physically deleted.
    """

    return RentalBillService.cancel_bill(
        db=db,
        bill_id=bill_id,
        current_user=current_user,
    )


# ============================================================
# MACHINE DOCUMENTS
# ADMIN
# UPLOAD RENTAL AGREEMENT / INSTALLATION REPORT
# ============================================================

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB


async def _read_pdf_file(
    file: UploadFile,
    document_name: str,
) -> bytes:
    """
    Read and validate an uploaded PDF.

    Checks:
    1. Content type
    2. File size
    3. Empty file
    4. PDF file signature
    """

    # --------------------------------------------------------
    # Content type
    # --------------------------------------------------------

    # Browser MIME type is not always reliable.
    # Validate the filename and actual PDF signature instead.
    file_name = (file.filename or "").strip()

    if not file_name.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{document_name} must be a PDF file.",
        )

    # --------------------------------------------------------
    # Read file
    # --------------------------------------------------------

    file_data = await file.read()

    # --------------------------------------------------------
    # Empty file
    # --------------------------------------------------------

    if len(file_data) == 0:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"{document_name} cannot be empty."
            ),
        )

    # --------------------------------------------------------
    # Maximum size
    # --------------------------------------------------------

    if len(file_data) > MAX_PDF_SIZE:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"{document_name} is too large. "
                "Maximum allowed size is 10 MB."
            ),
        )

    # --------------------------------------------------------
    # Basic PDF signature
    # --------------------------------------------------------

    if not file_data.startswith(b"%PDF"):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"{document_name} is not a valid PDF file."
            ),
        )

    return file_data


@router.get(
    "/machines/{machine_id}/documents/status",
    summary="Get Machine Document Status",
)
def get_machine_document_status(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    document = (
        db.query(MachineDocument)
        .filter(MachineDocument.machine_id == machine_id)
        .first()
    )

    if not document:
        return {
            "machine_id": machine_id,
            "rental_agreement_exists": False,
            "installation_report_exists": False,
            "rental_agreement_name": None,
            "installation_report_name": None,
        }

    return {
        "machine_id": machine_id,
        "rental_agreement_exists": bool(document.rental_agreement),
        "installation_report_exists": bool(document.installation_report),
        "rental_agreement_name": document.rental_agreement_name,
        "installation_report_name": document.installation_report_name,
    }


# ============================================================
# MACHINE DOCUMENTS
# ADMIN
# GET RENTAL AGREEMENT / INSTALLATION REPORT
# ============================================================

@router.get(
    "/machines/{machine_id}/documents/{document_type}",
    summary="Get Machine Document",
)
def get_machine_document(
    machine_id: int,
    document_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """
    Get a stored machine PDF.

    document_type must be:
        - rental_agreement
        - installation_report

    The PDF is returned directly from PostgreSQL.
    """

    document = (
        db.query(MachineDocument)
        .filter(
            MachineDocument.machine_id == machine_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine documents not found.",
        )

    if document_type == "rental_agreement":
        file_data = document.rental_agreement
        file_name = document.rental_agreement_name
        file_type = document.rental_agreement_type

    elif document_type == "installation_report":
        file_data = document.installation_report
        file_name = document.installation_report_name
        file_type = document.installation_report_type

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid document type. "
                "Use 'rental_agreement' or 'installation_report'."
            ),
        )

    if not file_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not uploaded.",
        )

    return Response(
        content=file_data,
        media_type=file_type or "application/pdf",
        headers={
            "Content-Disposition": (
                f'inline; filename="{file_name or "document.pdf"}"'
            )
        },
    )


# ============================================================
# MACHINE DOCUMENTS
# ADMIN
# UPLOAD RENTAL AGREEMENT / INSTALLATION REPORT
# ============================================================

@router.post(
    "/machines/{machine_id}/documents",
    summary="Upload Machine Documents",
)
async def upload_machine_documents(
    machine_id: int,

    rental_agreement: Optional[UploadFile] = File(
        default=None
    ),

    installation_report: Optional[UploadFile] = File(
        default=None
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_admin
    ),
):
    """
    Upload Rental Agreement and Installation Report
    for a machine.

    PDF files are stored directly in PostgreSQL.
    """

    print("========================================")
    print("MACHINE DOCUMENT UPLOAD")
    print("Machine ID:", machine_id)
    print(
        "Rental Agreement:",
        rental_agreement.filename if rental_agreement else None,
        rental_agreement.content_type if rental_agreement else None,
    )
    print(
        "Installation Report:",
        installation_report.filename if installation_report else None,
        installation_report.content_type if installation_report else None,
    )
    print("========================================")

    # ========================================================
    # FIND MACHINE
    # ========================================================

    machine = (
        db.query(Machine)
        .filter(
            Machine.id == machine_id
        )
        .first()
    )

    if not machine:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found.",
        )

    # ========================================================
    # REQUIRE AT LEAST ONE FILE
    # ========================================================

    if (
        rental_agreement is None
        and installation_report is None
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Please upload at least one PDF document."
            ),
        )

    # ========================================================
    # READ PDF FILES
    # ========================================================

    rental_agreement_data = None
    installation_report_data = None

    if rental_agreement:

        rental_agreement_data = await _read_pdf_file(
            rental_agreement,
            "Rental Agreement",
        )

    if installation_report:

        installation_report_data = await _read_pdf_file(
            installation_report,
            "Installation Report",
        )

    # ========================================================
    # FIND EXISTING DOCUMENT RECORD
    # ========================================================

    document = (
        db.query(MachineDocument)
        .filter(
            MachineDocument.machine_id == machine_id
        )
        .first()
    )

    # ========================================================
    # CREATE DOCUMENT RECORD IF NOT EXISTS
    # ========================================================

    if not document:

        document = MachineDocument(
            machine_id=machine_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(document)

    # ========================================================
    # RENTAL AGREEMENT
    # ========================================================

    if rental_agreement_data is not None:

        document.rental_agreement = (
            rental_agreement_data
        )

        document.rental_agreement_name = (
            rental_agreement.filename
        )

        document.rental_agreement_type = (
            rental_agreement.content_type
            or "application/pdf"
        )

        document.rental_agreement_size = (
            len(rental_agreement_data)
        )

    # ========================================================
    # INSTALLATION REPORT
    # ========================================================

    if installation_report_data is not None:

        document.installation_report = (
            installation_report_data
        )

        document.installation_report_name = (
            installation_report.filename
        )

        document.installation_report_type = (
            installation_report.content_type
            or "application/pdf"
        )

        document.installation_report_size = (
            len(installation_report_data)
        )

    # ========================================================
    # UPDATE TIMESTAMP
    # ========================================================

    document.updated_at = datetime.utcnow()

    # ========================================================
    # SAVE TO DATABASE
    # ========================================================

    try:

        db.commit()
        db.refresh(document)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to save machine documents."
            ),
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "message": (
            "Machine documents uploaded successfully."
        ),

        "machine_id": machine_id,

        "rental_agreement": (
            {
                "filename": (
                    document.rental_agreement_name
                ),
                "content_type": (
                    document.rental_agreement_type
                ),
                "size": (
                    document.rental_agreement_size
                ),
            }
            if document.rental_agreement
            else None
        ),

        "installation_report": (
            {
                "filename": (
                    document.installation_report_name
                ),
                "content_type": (
                    document.installation_report_type
                ),
                "size": (
                    document.installation_report_size
                ),
            }
            if document.installation_report
            else None
        ),
    }