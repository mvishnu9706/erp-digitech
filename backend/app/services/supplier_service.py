from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

from app.models.supplier import Supplier

from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate
)

from app.repositories.supplier_repository import SupplierRepository

from app.utils.supplier_code import SupplierCodeGenerator


class SupplierService:

    # =====================================================
    # Create Supplier
    # =====================================================

    @staticmethod
    def create_supplier(
        db: Session,
        data: SupplierCreate,
        current_user
    ):

        # -------------------------
        # Normalize Data
        # -------------------------

        data.company_name = data.company_name.strip()

        data.contact_person = (
            data.contact_person.strip()
            if data.contact_person
            else None
        )

        data.phone = (
            data.phone.strip()
            if data.phone
            else None
        )

        data.alternate_phone = (
            data.alternate_phone.strip()
            if data.alternate_phone
            else None
        )

        data.contact_designation = (
            data.contact_designation.strip()
            if data.contact_designation
            else None
        )

        data.email = (
            str(data.email).strip()
            if data.email
            else None
        )

        data.website = (
            data.website.strip()
            if data.website
            else None
        )

        data.gstin = (
            data.gstin.strip()
            if data.gstin
            else None
        )

        data.pan = (
            data.pan.strip()
            if data.pan
            else None
        )

        data.address = (
            data.address.strip()
            if data.address
            else None
        )

        data.city = (
            data.city.strip()
            if data.city
            else None
        )

        data.state = (
            data.state.strip()
            if data.state
            else None
        )

        data.country = (
            data.country.strip()
            if data.country
            else None
        )

        data.pincode = (
            data.pincode.strip()
            if data.pincode
            else None
        )

        data.remarks = (
            data.remarks.strip()
            if data.remarks
            else None
        )


        # -------------------------
        # Company Name Validation
        # -------------------------

        supplier = (
            SupplierRepository.get_by_company_name(
                db,
                data.company_name
            )
        )


        if supplier:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company name already exists."
            )


        # -------------------------
        # GST Validation
        # -------------------------

        if data.gstin:

            gst = (
                SupplierRepository.get_by_gstin(
                    db,
                    data.gstin
                )
            )


            if gst:

                raise HTTPException(
                    status_code=400,
                    detail="GSTIN already exists."
                )


        # -------------------------
        # PAN Validation
        # -------------------------

        if data.pan:

            pan = (
                SupplierRepository.get_by_pan(
                    db,
                    data.pan
                )
            )


            if pan:

                raise HTTPException(
                    status_code=400,
                    detail="PAN already exists."
                )


        # -------------------------
        # Email Validation
        # -------------------------

        if data.email:

            email = (
                SupplierRepository.get_by_email(
                    db,
                    data.email
                )
            )


            if email:

                raise HTTPException(
                    status_code=400,
                    detail="Email already exists."
                )


        # -------------------------
        # Supplier Code
        # -------------------------

        last_supplier = (
            SupplierRepository.last_supplier(db)
        )


        if last_supplier:

            supplier_code = (
                SupplierCodeGenerator.generate(
                    last_supplier.id + 1
                )
            )

        else:

            supplier_code = "SUP000001"


        # -------------------------
        # Create Object
        # -------------------------

        supplier = Supplier(

            supplier_code=supplier_code,

            company_name=data.company_name,

            contact_person=data.contact_person,

            phone=data.phone,

            alternate_phone=data.alternate_phone,

            contact_designation=data.contact_designation,

            email=data.email,

            website=data.website,

            gstin=data.gstin,

            pan=data.pan,

            address=data.address,

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

            created_by=current_user.id,

            updated_by=current_user.id

        )


        return SupplierRepository.create(
            db,
            supplier
        )


    # =====================================================
    # Get Suppliers
    # =====================================================

    @staticmethod
    def get_suppliers(
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


        total_records, suppliers = (
            SupplierRepository.get_all(

                db=db,

                search=search,

                city=city,

                state=state,

                is_active=is_active,

                skip=skip,

                limit=page_size

            )
        )


        return {

            "total_records":
                total_records,

            "page":
                page,

            "page_size":
                page_size,

            "suppliers":
                suppliers

        }


    # =====================================================
    # Get Supplier
    # =====================================================

    @staticmethod
    def get_supplier(
        db: Session,
        supplier_id: int
    ):

        supplier = (
            SupplierRepository.get_by_id(
                db,
                supplier_id
            )
        )


        if not supplier:

            raise HTTPException(
                status_code=404,
                detail="Supplier not found."
            )


        return supplier


    # =====================================================
    # Update Supplier
    # =====================================================

    @staticmethod
    def update_supplier(
        db: Session,
        supplier_id: int,
        data: SupplierUpdate,
        current_user
    ):

        supplier = (
            SupplierRepository.get_by_id(
                db,
                supplier_id
            )
        )


        if not supplier:

            raise HTTPException(
                status_code=404,
                detail="Supplier not found."
            )


        # -------------------------
        # Company Name Validation
        # -------------------------

        if data.company_name:

            data.company_name = (
                data.company_name.strip()
            )


            existing = (
                SupplierRepository.get_by_company_name(
                    db,
                    data.company_name
                )
            )


            if (
                existing
                and existing.id != supplier.id
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Company name already exists."
                )


        # -------------------------
        # GST Validation
        # -------------------------

        if (
            data.gstin
            and data.gstin.strip()
        ):

            existing = (
                SupplierRepository.get_by_gstin(
                    db,
                    data.gstin.strip()
                )
            )


            if (
                existing
                and existing.id != supplier.id
            ):

                raise HTTPException(
                    status_code=400,
                    detail="GSTIN already exists."
                )


        # -------------------------
        # PAN Validation
        # -------------------------

        if (
            data.pan
            and data.pan.strip()
        ):

            existing = (
                SupplierRepository.get_by_pan(
                    db,
                    data.pan.strip()
                )
            )


            if (
                existing
                and existing.id != supplier.id
            ):

                raise HTTPException(
                    status_code=400,
                    detail="PAN already exists."
                )


        # -------------------------
        # Email Validation
        # -------------------------

        if (
            data.email
            and str(data.email).strip()
        ):

            existing = (
                SupplierRepository.get_by_email(
                    db,
                    str(data.email).strip()
                )
            )


            if (
                existing
                and existing.id != supplier.id
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Email already exists."
                )


        # -------------------------
        # Update Data
        # -------------------------

        update_data = data.model_dump(
            exclude_unset=True
        )


        for key, value in update_data.items():

            if isinstance(value, str):

                value = value.strip()


                if value == "":

                    value = None


            setattr(
                supplier,
                key,
                value
            )


        supplier.updated_by = (
            current_user.id
        )


        return SupplierRepository.update(
            db,
            supplier
        )


    # =====================================================
    # Soft Delete Supplier
    # =====================================================

    @staticmethod
    def delete_supplier(
        db: Session,
        supplier_id: int
    ):

        supplier = (
            SupplierRepository.get_by_id(
                db,
                supplier_id
            )
        )


        if not supplier:

            raise HTTPException(
                status_code=404,
                detail="Supplier not found."
            )


        return SupplierRepository.delete(
            db,
            supplier
        )


    # =====================================================
    # EXPORT SUPPLIERS
    #
    # No filters:
    #     Export ALL suppliers
    #
    # Filters:
    #     Export only matching suppliers
    #
    # Supported:
    #     search
    #     city
    #     state
    #     is_active
    # =====================================================

    @staticmethod
    def export_suppliers(
        db: Session,
        search=None,
        city=None,
        state=None,
        is_active=None
    ):

        # =================================================
        # Get filtered suppliers
        #
        # This uses the SAME repository filtering used
        # by the Supplier Management table.
        #
        # No pagination limit for the export.
        # =================================================

        total_records, suppliers = (
            SupplierRepository.get_all(

                db=db,

                search=search,

                city=city,

                state=state,

                is_active=is_active,

                skip=0,

                limit=1000000

            )
        )


        # =================================================
        # Create Excel Workbook
        # =================================================

        workbook = Workbook()

        worksheet = workbook.active

        worksheet.title = "Suppliers"


        # =================================================
        # Excel Headers
        # =================================================

        headers = [

            "Supplier Code",

            "Company Name",

            "Contact Person",

            "Contact Designation",

            "Phone",

            "Alternate Phone",

            "Email",

            "Website",

            "GSTIN",

            "PAN",

            "Address",

            "City",

            "State",

            "Country",

            "Pincode",

            "Credit Limit",

            "Credit Days",

            "Opening Balance",

            "Current Balance",

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
        # Add Supplier Rows
        # =================================================

        for supplier in suppliers:

            worksheet.append([

                supplier.supplier_code,

                supplier.company_name,

                supplier.contact_person,

                supplier.contact_designation,

                supplier.phone,

                supplier.alternate_phone,

                supplier.email,

                supplier.website,

                supplier.gstin,

                supplier.pan,

                supplier.address,

                supplier.city,

                supplier.state,

                supplier.country,

                supplier.pincode,

                float(
                    supplier.credit_limit or 0
                ),

                supplier.credit_days,

                float(
                    supplier.opening_balance or 0
                ),

                float(
                    supplier.current_balance or 0
                ),

                supplier.remarks,

                (
                    "Active"
                    if supplier.is_active
                    else "Inactive"
                ),

                (
                    supplier.created_at.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if supplier.created_at
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

                        max_length = (
                            value_length
                        )

                except Exception:

                    pass


            worksheet.column_dimensions[
                column_letter
            ].width = min(
                max_length + 2,
                40
            )


        # =================================================
        # Create Excel In Memory
        # =================================================

        output = BytesIO()

        workbook.save(output)

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
                    "filename=Suppliers.xlsx"

            }

        )


    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return SupplierRepository.dashboard(
            db
        )