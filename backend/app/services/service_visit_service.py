from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.service_visit import ServiceVisit

from app.repositories.service_visit_repository import (
    ServiceVisitRepository
)

from app.repositories.service_ticket_repository import (
    ServiceTicketRepository
)

from app.repositories.machine_repository import (
    MachineRepository
)

from app.repositories.customer_repository import (
    CustomerRepository
)

from app.repositories.user_repository import (
    UserRepository
)

from app.schemas.service_visit import (
    ServiceVisitCreate,
    ServiceVisitUpdate
)

from app.utils.service_visit_number import (
    ServiceVisitNumberGenerator
)


class ServiceVisitService:

    # =====================================================
    # Create Service Visit
    # =====================================================

    @staticmethod
    def create_service_visit(
        db: Session,
        data: ServiceVisitCreate,
        current_user
    ):

        try:

            # ==========================================
            # Validate Ticket
            # ==========================================

            ticket = ServiceTicketRepository.get_by_id(
                db,
                data.ticket_id
            )

            if not ticket:

                raise HTTPException(
                    status_code=404,
                    detail="Service Ticket not found."
                )

            # ==========================================
            # Validate Machine
            # ==========================================

            machine = MachineRepository.get_by_id(
                db,
                data.machine_id
            )

            if not machine:

                raise HTTPException(
                    status_code=404,
                    detail="Machine not found."
                )

            # ==========================================
            # Validate Customer
            # ==========================================

            customer = CustomerRepository.get_by_id(
                db,
                data.customer_id
            )

            if not customer:

                raise HTTPException(
                    status_code=404,
                    detail="Customer not found."
                )

            # ==========================================
            # Validate Engineer
            # ==========================================

            engineer = UserRepository.get_by_id(
                db,
                data.engineer_id
            )

            if not engineer:

                raise HTTPException(
                    status_code=404,
                    detail="Engineer not found."
                )

            # ==========================================
            # Meter Validation
            # ==========================================

            if data.current_meter < data.previous_meter:

                raise HTTPException(
                    status_code=400,
                    detail="Current meter cannot be less than previous meter."
                )

            # ==========================================
            # Generate Visit Number
            # ==========================================

            last_visit = ServiceVisitRepository.last_visit(db)

            if last_visit:

                visit_number = ServiceVisitNumberGenerator.generate(
                    last_visit.id + 1
                )

            else:

                visit_number = ServiceVisitNumberGenerator.generate(1)

            # ==========================================
            # Create Visit
            # ==========================================

            visit = ServiceVisit(

                visit_number=visit_number,

                ticket_id=data.ticket_id,

                machine_id=data.machine_id,

                customer_id=data.customer_id,

                engineer_id=data.engineer_id,

                visit_date=data.visit_date,

                start_time=data.start_time,

                end_time=data.end_time,

                previous_meter=data.previous_meter,

                current_meter=data.current_meter,

                work_done=data.work_done,

                problem_found=data.problem_found,

                solution=data.solution,

                recommendations=data.recommendations,

                customer_name=data.customer_name,

                signature_path=data.signature_path,

                status=data.status,

                remarks=data.remarks,

                is_active=data.is_active,

                created_by=current_user.id,

                updated_by=current_user.id

            )

            visit = ServiceVisitRepository.create(

                db,

                visit

            )

            # ==========================================
            # Update Machine Meter
            # ==========================================

            machine.current_meter = data.current_meter

            # ==========================================
            # Update Ticket Status
            # ==========================================

            ticket.status = "IN_PROGRESS"

            db.commit()

            db.refresh(visit)

            return visit

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(

                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=f"Service Visit creation failed : {str(e)}"

            )
            # =====================================================
    # Get Service Visits
    # =====================================================

    @staticmethod
    def get_service_visits(

        db: Session,

        search: str = None,

        ticket_id: int = None,

        machine_id: int = None,

        customer_id: int = None,

        engineer_id: int = None,

        status: str = None,

        page: int = 1,

        page_size: int = 10

    ):

        skip = (page - 1) * page_size

        visits = ServiceVisitRepository.get_all(

            db=db,

            search=search,

            ticket_id=ticket_id,

            machine_id=machine_id,

            customer_id=customer_id,

            engineer_id=engineer_id,

            status=status,

            skip=skip,

            limit=page_size

        )

        total = ServiceVisitRepository.count(

            db=db,

            search=search,

            ticket_id=ticket_id,

            machine_id=machine_id,

            customer_id=customer_id,

            engineer_id=engineer_id,

            status=status

        )

        return {

            "total": total,

            "page": page,

            "page_size": page_size,

            "items": visits

        }

    # =====================================================
    # Get Service Visit
    # =====================================================

    @staticmethod
    def get_service_visit(

        db: Session,

        visit_id: int

    ):

        visit = ServiceVisitRepository.get_by_id(

            db,

            visit_id

        )

        if not visit:

            raise HTTPException(

                status_code=404,

                detail="Service Visit not found."

            )

        return visit

    # =====================================================
    # Update Service Visit
    # =====================================================

    @staticmethod
    def update_service_visit(

        db: Session,

        visit_id: int,

        data: ServiceVisitUpdate,

        current_user

    ):

        try:

            visit = ServiceVisitRepository.get_by_id(

                db,

                visit_id

            )

            if not visit:

                raise HTTPException(

                    status_code=404,

                    detail="Service Visit not found."

                )

            update_data = data.model_dump(

                exclude_unset=True

            )

            for key, value in update_data.items():

                setattr(

                    visit,

                    key,

                    value

                )

            visit.updated_by = current_user.id

            ServiceVisitRepository.update(

                db,

                visit

            )

            return visit

        except HTTPException:

            raise

        except Exception as e:

            raise HTTPException(

                status_code=500,

                detail=str(e)

            )

    # =====================================================
    # Delete Service Visit
    # =====================================================

    @staticmethod
    def delete_service_visit(

        db: Session,

        visit_id: int

    ):

        visit = ServiceVisitRepository.get_by_id(

            db,

            visit_id

        )

        if not visit:

            raise HTTPException(

                status_code=404,

                detail="Service Visit not found."

            )

        ServiceVisitRepository.delete(

            db,

            visit

        )

        return {

            "success": True,

            "message": "Service Visit deleted successfully."

        }

    # =====================================================
    # Start Visit
    # =====================================================

    @staticmethod
    def start_visit(

        db: Session,

        visit_id: int,

        current_user

    ):

        visit = ServiceVisitRepository.get_by_id(

            db,

            visit_id

        )

        if not visit:

            raise HTTPException(

                status_code=404,

                detail="Service Visit not found."

            )

        visit.start_time = datetime.now()

        visit.status = "IN_PROGRESS"

        visit.updated_by = current_user.id

        ServiceVisitRepository.update(

            db,

            visit

        )

        return visit

    # =====================================================
    # Complete Visit
    # =====================================================

    @staticmethod
    def complete_visit(

        db: Session,

        visit_id: int,

        current_user

    ):

        visit = ServiceVisitRepository.get_by_id(

            db,

            visit_id

        )

        if not visit:

            raise HTTPException(

                status_code=404,

                detail="Service Visit not found."

            )

        visit.end_time = datetime.now()

        visit.status = "COMPLETED"

        visit.updated_by = current_user.id

        ServiceVisitRepository.update(

            db,

            visit

        )

        # Update Ticket Status

        ticket = ServiceTicketRepository.get_by_id(

            db,

            visit.ticket_id

        )

        if ticket:

            ticket.status = "COMPLETED"

        # Update Machine Meter

        machine = MachineRepository.get_by_id(

            db,

            visit.machine_id

        )

        if machine:

            machine.current_meter = visit.current_meter

        db.commit()

        return visit

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(

        db: Session

    ):

        return ServiceVisitRepository.dashboard(db)