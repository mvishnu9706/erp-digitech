from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.chart_of_account import ChartOfAccount

from app.repositories.chart_of_account_repository import (
    ChartOfAccountRepository
)

from app.schemas.chart_of_account import (
    ChartOfAccountCreate,
    ChartOfAccountUpdate
)


class ChartOfAccountService:

    # =====================================================
    # Create Account
    # =====================================================

    @staticmethod
    def create_account(
        db: Session,
        data: ChartOfAccountCreate
    ):

        existing = ChartOfAccountRepository.get_by_code(
            db,
            data.account_code
        )

        if existing:

            raise HTTPException(
                status_code=400,
                detail="Account code already exists."
            )

        account = ChartOfAccount(

            account_code=data.account_code,

            account_name=data.account_name,

            parent_account_id=data.parent_account_id,

            account_type=data.account_type,

            account_nature=data.account_nature,

            description=data.description,

            is_active=data.is_active

        )

        return ChartOfAccountRepository.create(
            db,
            account
        )

    # =====================================================
    # Get All Accounts
    # =====================================================

    @staticmethod
    def get_accounts(

        db: Session,

        search=None,

        account_type=None,

        is_active=None,

        page=1,

        page_size=20

    ):

        skip = (page - 1) * page_size

        return ChartOfAccountRepository.get_all(

            db=db,

            search=search,

            account_type=account_type,

            is_active=is_active,

            skip=skip,

            limit=page_size

        )

    # =====================================================
    # Get Account
    # =====================================================

    @staticmethod
    def get_account(

        db: Session,

        account_id: int

    ):

        account = ChartOfAccountRepository.get_by_id(

            db,

            account_id

        )

        if not account:

            raise HTTPException(

                status_code=404,

                detail="Account not found."

            )

        return account

    # =====================================================
    # Update Account
    # =====================================================

    @staticmethod
    def update_account(

        db: Session,

        account_id: int,

        data: ChartOfAccountUpdate

    ):

        account = ChartOfAccountRepository.get_by_id(

            db,

            account_id

        )

        if not account:

            raise HTTPException(

                status_code=404,

                detail="Account not found."

            )

        update_data = data.model_dump(

            exclude_unset=True

        )

        for key, value in update_data.items():

            setattr(

                account,

                key,

                value

            )

        return ChartOfAccountRepository.update(

            db,

            account

        )

    # =====================================================
    # Delete Account
    # =====================================================

    @staticmethod
    def delete_account(

        db: Session,

        account_id: int

    ):

        account = ChartOfAccountRepository.get_by_id(

            db,

            account_id

        )

        if not account:

            raise HTTPException(

                status_code=404,

                detail="Account not found."

            )

        return ChartOfAccountRepository.delete(

            db,

            account

        )

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return ChartOfAccountRepository.dashboard(db)

    # =====================================================
    # Seed Default Accounts
    # =====================================================

    @staticmethod
    def seed_accounts(
        db: Session
    ):

        ChartOfAccountRepository.seed_default_accounts(db)

        return {

            "success": True,

            "message": "Default Chart of Accounts created successfully."

        }