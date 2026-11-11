from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.chart_of_account import ChartOfAccount


class ChartOfAccountRepository:

    # =====================================================
    # Create
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        account: ChartOfAccount
    ):

        db.add(account)

        db.commit()

        db.refresh(account)

        return account

    # =====================================================
    # Get All
    # =====================================================

    @staticmethod
    def get_all(

        db: Session,

        search: str = None,

        account_type: str = None,

        is_active: bool = None,

        skip: int = 0,

        limit: int = 10

    ):

        query = db.query(ChartOfAccount)

        # ------------------------------------
        # Search
        # ------------------------------------

        if search:

            query = query.filter(

                or_(

                    ChartOfAccount.account_code.ilike(
                        f"%{search}%"
                    ),

                    ChartOfAccount.account_name.ilike(
                        f"%{search}%"
                    )

                )

            )

        # ------------------------------------
        # Filters
        # ------------------------------------

        if account_type:

            query = query.filter(

                ChartOfAccount.account_type == account_type

            )

        if is_active is not None:

            query = query.filter(

                ChartOfAccount.is_active == is_active

            )

        return (

            query

            .order_by(
                ChartOfAccount.account_code
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # Get By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        account_id: int
    ):

        return (

            db.query(ChartOfAccount)

            .filter(
                ChartOfAccount.id == account_id
            )

            .first()

        )

    # =====================================================
    # Get By Code
    # =====================================================

    @staticmethod
    def get_by_code(
        db: Session,
        account_code: str
    ):

        return (

            db.query(ChartOfAccount)

            .filter(
                ChartOfAccount.account_code == account_code
            )

            .first()

        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        account: ChartOfAccount
    ):

        db.commit()

        db.refresh(account)

        return account

    # =====================================================
    # Soft Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        account: ChartOfAccount
    ):

        account.is_active = False

        db.commit()

        db.refresh(account)

        return account

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return {

            "total_accounts":

                db.query(
                    ChartOfAccount
                ).count(),

            "asset_accounts":

                db.query(
                    ChartOfAccount
                )
                .filter(
                    ChartOfAccount.account_type == "ASSET"
                )
                .count(),

            "liability_accounts":

                db.query(
                    ChartOfAccount
                )
                .filter(
                    ChartOfAccount.account_type == "LIABILITY"
                )
                .count(),

            "equity_accounts":

                db.query(
                    ChartOfAccount
                )
                .filter(
                    ChartOfAccount.account_type == "EQUITY"
                )
                .count(),

            "income_accounts":

                db.query(
                    ChartOfAccount
                )
                .filter(
                    ChartOfAccount.account_type == "INCOME"
                )
                .count(),

            "expense_accounts":

                db.query(
                    ChartOfAccount
                )
                .filter(
                    ChartOfAccount.account_type == "EXPENSE"
                )
                .count()

        }

    # =====================================================
    # Seed Default Accounts
    # =====================================================

    @staticmethod
    def seed_default_accounts(
        db: Session
    ):

        if db.query(ChartOfAccount).count() > 0:
            return

        accounts = [

            ("1000", "Assets", "ASSET", "DEBIT"),
            ("1100", "Cash", "ASSET", "DEBIT"),
            ("1200", "Bank", "ASSET", "DEBIT"),
            ("1300", "Inventory", "ASSET", "DEBIT"),
            ("1400", "Accounts Receivable", "ASSET", "DEBIT"),
            ("1500", "GST Input", "ASSET", "DEBIT"),

            ("2000", "Liabilities", "LIABILITY", "CREDIT"),
            ("2100", "Accounts Payable", "LIABILITY", "CREDIT"),
            ("2200", "GST Output", "LIABILITY", "CREDIT"),

            ("3000", "Capital", "EQUITY", "CREDIT"),

            ("4000", "Sales Revenue", "INCOME", "CREDIT"),

            ("5000", "Purchase Expense", "EXPENSE", "DEBIT"),
            ("5100", "Salary Expense", "EXPENSE", "DEBIT"),
            ("5200", "Rent Expense", "EXPENSE", "DEBIT"),
            ("5300", "Electricity Expense", "EXPENSE", "DEBIT")

        ]

        for code, name, account_type, nature in accounts:

            db.add(

                ChartOfAccount(

                    account_code=code,

                    account_name=name,

                    account_type=account_type,

                    account_nature=nature,

                    is_active=True

                )

            )

        db.commit()