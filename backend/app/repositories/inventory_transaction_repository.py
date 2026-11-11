from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.inventory_transaction import (
    InventoryTransaction,
)


class InventoryTransactionRepository:

    # =====================================================
    # Create
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        transaction: InventoryTransaction,
    ):

        db.add(transaction)

        return transaction

    # =====================================================
    # Get All
    # =====================================================

    @staticmethod
    def get_all(
        db: Session,
        product_id: int = None,
        warehouse_id: int = None,
        transaction_type: str = None,
        reference_type: str = None,
        reference_by: str = None,
        search: str = None,
        skip: int = 0,
        limit: int = 10,
    ):

        query = db.query(
            InventoryTransaction
        )

        # =================================================
        # Search
        # =================================================

        if search:

            search_value = f"%{search}%"

            query = query.filter(

                or_(

                    InventoryTransaction.transaction_number.ilike(
                        search_value
                    ),

                    InventoryTransaction.reference_by.ilike(
                        search_value
                    ),

                    InventoryTransaction.remarks.ilike(
                        search_value
                    ),

                )

            )

        # =================================================
        # Product
        # =================================================

        if product_id:

            query = query.filter(
                InventoryTransaction.product_id
                == product_id
            )

        # =================================================
        # Warehouse
        # =================================================

        if warehouse_id:

            query = query.filter(

                or_(

                    InventoryTransaction.warehouse_id
                    == warehouse_id,

                    InventoryTransaction.to_warehouse_id
                    == warehouse_id,

                )

            )

        # =================================================
        # Transaction Type
        # =================================================

        if transaction_type:

            query = query.filter(
                InventoryTransaction.transaction_type
                == transaction_type
            )

        # =================================================
        # Reference Type
        # =================================================

        if reference_type:

            query = query.filter(
                InventoryTransaction.reference_type
                == reference_type
            )

        # =================================================
        # Reference By
        # =================================================

        if reference_by:

            query = query.filter(

                InventoryTransaction.reference_by.ilike(
                    f"%{reference_by}%"
                )

            )

        # =================================================
        # Result
        # =================================================

        return (

            query

            .order_by(
                InventoryTransaction.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # Count
    # =====================================================

    @staticmethod
    def count(
        db: Session,
        product_id=None,
        warehouse_id=None,
        transaction_type=None,
        reference_type=None,
        reference_by=None,
        search=None,
    ):

        query = db.query(
            InventoryTransaction
        )

        # =================================================
        # Search
        # =================================================

        if search:

            search_value = f"%{search}%"

            query = query.filter(

                or_(

                    InventoryTransaction.transaction_number.ilike(
                        search_value
                    ),

                    InventoryTransaction.reference_by.ilike(
                        search_value
                    ),

                    InventoryTransaction.remarks.ilike(
                        search_value
                    ),

                )

            )

        # =================================================
        # Product
        # =================================================

        if product_id:

            query = query.filter(
                InventoryTransaction.product_id
                == product_id
            )

        # =================================================
        # Warehouse
        # =================================================

        if warehouse_id:

            query = query.filter(

                or_(

                    InventoryTransaction.warehouse_id
                    == warehouse_id,

                    InventoryTransaction.to_warehouse_id
                    == warehouse_id,

                )

            )

        # =================================================
        # Transaction Type
        # =================================================

        if transaction_type:

            query = query.filter(
                InventoryTransaction.transaction_type
                == transaction_type
            )

        # =================================================
        # Reference Type
        # =================================================

        if reference_type:

            query = query.filter(
                InventoryTransaction.reference_type
                == reference_type
            )

        # =================================================
        # Reference By
        # =================================================

        if reference_by:

            query = query.filter(

                InventoryTransaction.reference_by.ilike(
                    f"%{reference_by}%"
                )

            )

        return query.count()

    # =====================================================
    # Get By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        transaction_id: int,
    ):

        return (

            db.query(
                InventoryTransaction
            )

            .filter(
                InventoryTransaction.id
                == transaction_id
            )

            .first()

        )

    # =====================================================
    # Get By Transaction Number
    # =====================================================

    @staticmethod
    def get_by_transaction_number(
        db: Session,
        transaction_number: str,
    ):

        return (

            db.query(
                InventoryTransaction
            )

            .filter(
                InventoryTransaction.transaction_number
                == transaction_number
            )

            .first()

        )

    # =====================================================
    # Get By Product
    # =====================================================

    @staticmethod
    def get_by_product(
        db: Session,
        product_id: int,
    ):

        return (

            db.query(
                InventoryTransaction
            )

            .filter(
                InventoryTransaction.product_id
                == product_id
            )

            .order_by(
                InventoryTransaction.created_at.desc()
            )

            .all()

        )

    # =====================================================
    # Get By Warehouse
    # =====================================================

    @staticmethod
    def get_by_warehouse(
        db: Session,
        warehouse_id: int,
    ):

        return (

            db.query(
                InventoryTransaction
            )

            .filter(

                or_(

                    InventoryTransaction.warehouse_id
                    == warehouse_id,

                    InventoryTransaction.to_warehouse_id
                    == warehouse_id,

                )

            )

            .order_by(
                InventoryTransaction.created_at.desc()
            )

            .all()

        )

    # =====================================================
    # Stock Transfer History
    # =====================================================
    #
    # ONE database row = ONE stock transfer
    #
    # transaction_type:
    #
    #     TRANSFER
    #
    # warehouse_id:
    #
    #     FROM warehouse
    #
    # to_warehouse_id:
    #
    #     TO warehouse
    #
    # =====================================================

    @staticmethod
    def get_stock_transfer_rows(
        db: Session,
        product_id: Optional[int] = None,
        warehouse_id: Optional[int] = None,
        from_warehouse_id: Optional[int] = None,
        to_warehouse_id: Optional[int] = None,
        reference_by: Optional[str] = None,
        search: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 10,
    ):

        query = db.query(
            InventoryTransaction
        )

        # =================================================
        # Only TRANSFER
        # =================================================

        query = query.filter(

            InventoryTransaction.transaction_type
            == "TRANSFER"

        )

        # =================================================
        # Product
        # =================================================

        if product_id:

            query = query.filter(

                InventoryTransaction.product_id
                == product_id

            )

        # =================================================
        # Any Warehouse
        #
        # Search either:
        #
        # FROM
        # OR
        # TO
        # =================================================

        if warehouse_id:

            query = query.filter(

                or_(

                    InventoryTransaction.warehouse_id
                    == warehouse_id,

                    InventoryTransaction.to_warehouse_id
                    == warehouse_id,

                )

            )

        # =================================================
        # From Warehouse
        # =================================================

        if from_warehouse_id:

            query = query.filter(

                InventoryTransaction.warehouse_id
                == from_warehouse_id

            )

        # =================================================
        # To Warehouse
        # =================================================

        if to_warehouse_id:

            query = query.filter(

                InventoryTransaction.to_warehouse_id
                == to_warehouse_id

            )

        # =================================================
        # Reference By
        # =================================================

        if reference_by:

            query = query.filter(

                InventoryTransaction.reference_by.ilike(
                    f"%{reference_by}%"
                )

            )

        # =================================================
        # Search
        #
        # Searches:
        #
        # - Transfer Number
        # - Reference By
        # - Remarks
        # =================================================

        if search:

            search_value = f"%{search}%"

            query = query.filter(

                or_(

                    InventoryTransaction.transaction_number.ilike(
                        search_value
                    ),

                    InventoryTransaction.reference_by.ilike(
                        search_value
                    ),

                    InventoryTransaction.remarks.ilike(
                        search_value
                    ),

                )

            )

        # =================================================
        # From Date
        # =================================================

        if from_date:

            query = query.filter(

                InventoryTransaction.created_at
                >= from_date

            )

        # =================================================
        # To Date
        # =================================================

        if to_date:

            query = query.filter(

                InventoryTransaction.created_at
                <= to_date

            )

        # =================================================
        # Result
        # =================================================

        return (

            query

            .order_by(
                InventoryTransaction.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # Count Stock Transfer History
    # =====================================================

    @staticmethod
    def count_stock_transfer_rows(
        db: Session,
        product_id: Optional[int] = None,
        warehouse_id: Optional[int] = None,
        from_warehouse_id: Optional[int] = None,
        to_warehouse_id: Optional[int] = None,
        reference_by: Optional[str] = None,
        search: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ):

        query = db.query(
            InventoryTransaction
        )

        # =================================================
        # Only TRANSFER
        # =================================================

        query = query.filter(

            InventoryTransaction.transaction_type
            == "TRANSFER"

        )

        # =================================================
        # Product
        # =================================================

        if product_id:

            query = query.filter(

                InventoryTransaction.product_id
                == product_id

            )

        # =================================================
        # Any Warehouse
        # =================================================

        if warehouse_id:

            query = query.filter(

                or_(

                    InventoryTransaction.warehouse_id
                    == warehouse_id,

                    InventoryTransaction.to_warehouse_id
                    == warehouse_id,

                )

            )

        # =================================================
        # From Warehouse
        # =================================================

        if from_warehouse_id:

            query = query.filter(

                InventoryTransaction.warehouse_id
                == from_warehouse_id

            )

        # =================================================
        # To Warehouse
        # =================================================

        if to_warehouse_id:

            query = query.filter(

                InventoryTransaction.to_warehouse_id
                == to_warehouse_id

            )

        # =================================================
        # Reference By
        # =================================================

        if reference_by:

            query = query.filter(

                InventoryTransaction.reference_by.ilike(
                    f"%{reference_by}%"
                )

            )

        # =================================================
        # Search
        # =================================================

        if search:

            search_value = f"%{search}%"

            query = query.filter(

                or_(

                    InventoryTransaction.transaction_number.ilike(
                        search_value
                    ),

                    InventoryTransaction.reference_by.ilike(
                        search_value
                    ),

                    InventoryTransaction.remarks.ilike(
                        search_value
                    ),

                )

            )

        # =================================================
        # From Date
        # =================================================

        if from_date:

            query = query.filter(

                InventoryTransaction.created_at
                >= from_date

            )

        # =================================================
        # To Date
        # =================================================

        if to_date:

            query = query.filter(

                InventoryTransaction.created_at
                <= to_date

            )

        return query.count()

    # =====================================================
    # Backward Compatible Stock Transfers
    # =====================================================
    #
    # Older service code may call these methods.
    #
    # They now return only TRANSFER records.
    #
    # =====================================================

    @staticmethod
    def get_stock_transfers(
        db: Session,
        product_id: int = None,
        warehouse_id: int = None,
        reference_by: str = None,
        search: str = None,
        skip: int = 0,
        limit: int = 10,
    ):

        query = db.query(
            InventoryTransaction
        )

        # =================================================
        # Only TRANSFER
        # =================================================

        query = query.filter(

            InventoryTransaction.transaction_type
            == "TRANSFER"

        )

        # =================================================
        # Product
        # =================================================

        if product_id:

            query = query.filter(

                InventoryTransaction.product_id
                == product_id

            )

        # =================================================
        # Warehouse
        #
        # Either FROM or TO
        # =================================================

        if warehouse_id:

            query = query.filter(

                or_(

                    InventoryTransaction.warehouse_id
                    == warehouse_id,

                    InventoryTransaction.to_warehouse_id
                    == warehouse_id,

                )

            )

        # =================================================
        # Reference By
        # =================================================

        if reference_by:

            query = query.filter(

                InventoryTransaction.reference_by.ilike(
                    f"%{reference_by}%"
                )

            )

        # =================================================
        # Search
        # =================================================

        if search:

            search_value = f"%{search}%"

            query = query.filter(

                or_(

                    InventoryTransaction.transaction_number.ilike(
                        search_value
                    ),

                    InventoryTransaction.reference_by.ilike(
                        search_value
                    ),

                    InventoryTransaction.remarks.ilike(
                        search_value
                    ),

                )

            )

        # =================================================
        # Result
        # =================================================

        return (

            query

            .order_by(
                InventoryTransaction.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # Count Raw Stock Transfers
    # =====================================================

    @staticmethod
    def count_stock_transfers(
        db: Session,
        product_id: int = None,
        warehouse_id: int = None,
        reference_by: str = None,
        search: str = None,
    ):

        query = db.query(
            InventoryTransaction
        )

        query = query.filter(

            InventoryTransaction.transaction_type
            == "TRANSFER"

        )

        # =================================================
        # Product
        # =================================================

        if product_id:

            query = query.filter(

                InventoryTransaction.product_id
                == product_id

            )

        # =================================================
        # Warehouse
        # =================================================

        if warehouse_id:

            query = query.filter(

                or_(

                    InventoryTransaction.warehouse_id
                    == warehouse_id,

                    InventoryTransaction.to_warehouse_id
                    == warehouse_id,

                )

            )

        # =================================================
        # Reference By
        # =================================================

        if reference_by:

            query = query.filter(

                InventoryTransaction.reference_by.ilike(
                    f"%{reference_by}%"
                )

            )

        # =================================================
        # Search
        # =================================================

        if search:

            search_value = f"%{search}%"

            query = query.filter(

                or_(

                    InventoryTransaction.transaction_number.ilike(
                        search_value
                    ),

                    InventoryTransaction.reference_by.ilike(
                        search_value
                    ),

                    InventoryTransaction.remarks.ilike(
                        search_value
                    ),

                )

            )

        return query.count()

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        transaction: InventoryTransaction,
    ):

        db.commit()

        db.refresh(
            transaction
        )

        return transaction

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        transaction: InventoryTransaction,
    ):

        db.delete(
            transaction
        )

        db.commit()

        return True

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session,
    ):

        # =================================================
        # Total Transactions
        # =================================================

        total_transactions = (

            db.query(
                InventoryTransaction
            )

            .count()

        )

        # =================================================
        # Total Stock In
        #
        # TRANSFER is intentionally NOT included here.
        #
        # Transfer moves existing stock between warehouses;
        # it does not create new stock.
        # =================================================

        total_stock_in = (

            db.query(

                func.coalesce(

                    func.sum(
                        InventoryTransaction.quantity
                    ),

                    Decimal("0"),

                )

            )

            .filter(

                InventoryTransaction.transaction_type.in_(

                    [

                        "GOODS_RECEIPT",

                        "OPENING_STOCK",

                        "SALES_RETURN",

                        "STOCK_ADJUSTMENT_IN",

                    ]

                )

            )

            .scalar()

        )

        # =================================================
        # Total Stock Out
        #
        # TRANSFER is intentionally NOT included here.
        #
        # Transfer does not consume total company stock.
        # =================================================

        total_stock_out = (

            db.query(

                func.coalesce(

                    func.sum(
                        InventoryTransaction.quantity
                    ),

                    Decimal("0"),

                )

            )

            .filter(

                InventoryTransaction.transaction_type.in_(

                    [

                        "SALES_OUT",

                        "SALE",

                        "PURCHASE_RETURN",

                        "STOCK_ADJUSTMENT_OUT",

                    ]

                )

            )

            .scalar()

        )

        # =================================================
        # Total Stock Value
        # =================================================

        total_stock_value = (

            db.query(

                func.coalesce(

                    func.sum(
                        InventoryTransaction.total_cost
                    ),

                    Decimal("0"),

                )

            )

            .scalar()

        )

        # =================================================
        # Return
        # =================================================

        return {

            "total_transactions":
                total_transactions,

            "total_stock_in":
                total_stock_in,

            "total_stock_out":
                total_stock_out,

            "total_stock_value":
                total_stock_value,

        }