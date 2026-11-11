from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.journal_entry import (
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryResponse,
    JournalEntryDashboardResponse
)

from app.services.journal_entry_service import (
    JournalEntryService
)

from app.core.dependencies import (
    get_current_admin,
    get_current_user
)

router = APIRouter(
    prefix="/journal-entries",
    tags=["Journal Entries"]
)


# =====================================================
# Create Journal Entry
# =====================================================

@router.post(
    "/",
    response_model=JournalEntryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_journal_entry(

    data: JournalEntryCreate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return JournalEntryService.create_journal_entry(

        db,

        data,

        current_user

    )


# =====================================================
# Get Journal Entries
# =====================================================

@router.get(
    "/",
    response_model=list[JournalEntryResponse]
)
def get_journal_entries(

    search: Optional[str] = Query(None),

    voucher_type: Optional[str] = Query(None),

    page: int = Query(1, ge=1),

    page_size: int = Query(20, ge=1, le=100),

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return JournalEntryService.get_journal_entries(

        db=db,

        search=search,

        voucher_type=voucher_type,

        page=page,

        page_size=page_size

    )


# =====================================================
# Get Journal Entry
# =====================================================

@router.get(
    "/{journal_id}",
    response_model=JournalEntryResponse
)
def get_journal_entry(

    journal_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return JournalEntryService.get_journal_entry(

        db,

        journal_id

    )


# =====================================================
# Update Journal Entry
# =====================================================

@router.put(
    "/{journal_id}",
    response_model=JournalEntryResponse
)
def update_journal_entry(

    journal_id: int,

    data: JournalEntryUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return JournalEntryService.update_journal_entry(

        db,

        journal_id,

        data,

        current_user

    )


# =====================================================
# Delete Journal Entry
# =====================================================

@router.delete(
    "/{journal_id}"
)
def delete_journal_entry(

    journal_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_admin)

):

    return JournalEntryService.delete_journal_entry(

        db,

        journal_id

    )


# =====================================================
# Dashboard
# =====================================================

@router.get(
    "/dashboard/summary",
    response_model=JournalEntryDashboardResponse
)
def dashboard(

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)

):

    return JournalEntryService.dashboard(db)