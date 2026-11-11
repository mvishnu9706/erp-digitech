from sqlalchemy import func, or_, String
from sqlalchemy.orm import Session, selectinload, joinedload

from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.supplier import Supplier
from app.models.warehouse import Warehouse


class PurchaseOrderRepository:

    # =====================================================
    # Create Purchase Order
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        purchase_order: PurchaseOrder,
        items: list[PurchaseOrderItem]
    ):

        # Save Header
        db.add(purchase_order)
        db.flush()

        # Save Items
        for item in items:
            item.purchase_order_id = purchase_order.id
            db.add(item)

        db.flush()
        db.refresh(purchase_order)

        # IMPORTANT:
        # No commit here.
        # Service layer will commit.

        return purchase_order


    # =====================================================
    # Get All Purchase Orders
    # =====================================================

    @staticmethod
    def get_all(
        db: Session,
        search: str = None,
        supplier_id: int = None,
        warehouse_id: int = None,
        date_from=None,
        date_to=None,
        skip: int = 0,
        limit: int = 10
    ):

        query = (
            db.query(PurchaseOrder)
            .options(
                joinedload(PurchaseOrder.supplier),
                joinedload(PurchaseOrder.warehouse),
                joinedload(PurchaseOrder.items),
            )
            .filter(
                PurchaseOrder.is_active == True
            )
        )

        # -----------------------------------------
        # Search
        # -----------------------------------------

        if search:

            query = (
                query
                .join(
                    Supplier,
                    PurchaseOrder.supplier_id == Supplier.id
                )
                .join(
                    Warehouse,
                    PurchaseOrder.warehouse_id == Warehouse.id
                )
                .filter(
                    or_(
                        PurchaseOrder.po_number.ilike(
                            f"%{search}%"
                        ),
                        PurchaseOrder.reference_number.ilike(
                            f"%{search}%"
                        ),
                        Supplier.company_name.ilike(
                            f"%{search}%"
                        ),
                        Warehouse.warehouse_name.ilike(
                            f"%{search}%"
                        ),
                    )
                )
            )

        # -----------------------------------------
        # Supplier
        # -----------------------------------------

        if supplier_id:

            query = query.filter(
                PurchaseOrder.supplier_id == supplier_id
            )

        # -----------------------------------------
        # Warehouse
        # -----------------------------------------

        if warehouse_id:

            query = query.filter(
                PurchaseOrder.warehouse_id == warehouse_id
            )

        # -----------------------------------------
        # Date Filters
        # -----------------------------------------

        if date_from:

            query = query.filter(
                PurchaseOrder.po_date >= date_from
            )

        if date_to:

            query = query.filter(
                PurchaseOrder.po_date <= date_to
            )

        total_records = query.count()

        purchases = (
            query
            .order_by(
                PurchaseOrder.po_date.desc(),
                PurchaseOrder.created_at.desc(),
                PurchaseOrder.id.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        return total_records, purchases


    # =====================================================
    # Get Purchase Order By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        purchase_order_id: int
    ):

        return (
            db.query(PurchaseOrder)
            .options(
                selectinload(PurchaseOrder.items)
            )
            .filter(
                PurchaseOrder.id == purchase_order_id
            )
            .first()
        )


    # =====================================================
    # Get Purchase Order Items
    # =====================================================

    @staticmethod
    def get_items(
        db: Session,
        purchase_order_id: int
    ):

        return (
            db.query(PurchaseOrderItem)
            .filter(
                PurchaseOrderItem.purchase_order_id
                == purchase_order_id
            )
            .all()
        )


    # =====================================================
    # Last Purchase Order
    # =====================================================

    @staticmethod
    def last_purchase_order(
        db: Session
    ):

        return (
            db.query(PurchaseOrder)
            .order_by(
                PurchaseOrder.id.desc()
            )
            .first()
        )


    # =====================================================
    # Get Last PO Sequence Number
    # =====================================================

    @staticmethod
    def get_last_po_sequence(
        db: Session
    ):

        purchase_orders = (
            db.query(
                PurchaseOrder.po_number
            )
            .filter(
                PurchaseOrder.po_number.isnot(None)
            )
            .all()
        )

        highest_number = 0

        for row in purchase_orders:

            po_number = row[0]

            if not po_number:
                continue

            try:

                sequence = int(
                    po_number.rsplit("-", 1)[1]
                )

                if sequence > highest_number:
                    highest_number = sequence

            except (
                ValueError,
                IndexError
            ):
                continue

        return highest_number


    # =====================================================
    # Update Purchase Order
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        purchase_order: PurchaseOrder
    ):

        # Service will commit
        db.flush()
        db.refresh(purchase_order)

        return purchase_order


    # =====================================================
    # Soft Delete Purchase Order
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        purchase_order: PurchaseOrder
    ):

        purchase_order.status = "CANCELLED"
        purchase_order.is_active = False

        db.flush()
        db.refresh(purchase_order)

        return purchase_order


    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        # ------------------------------------
        # Total Purchases
        # ------------------------------------

        total_purchases = (
            db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.is_active == True
            )
            .count()
        )

        # ------------------------------------
        # Today's Entries (Created Today)
        # ------------------------------------

        today_entries = (
            db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.is_active == True,
                func.date(
                    PurchaseOrder.created_at
                ) == func.current_date()
            )
            .count()
        )

        # ------------------------------------
        # Today's Purchases (PO Date)
        # ------------------------------------

        today_purchases = (
            db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.is_active == True,
                PurchaseOrder.po_date
                == func.current_date()
            )
            .count()
        )

        # ------------------------------------
        # This Month Entries
        # ------------------------------------

        month_entries = (
            db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.is_active == True,
                func.extract(
                    "year",
                    PurchaseOrder.created_at
                )
                == func.extract(
                    "year",
                    func.now()
                ),
                func.extract(
                    "month",
                    PurchaseOrder.created_at
                )
                == func.extract(
                    "month",
                    func.now()
                )
            )
            .count()
        )

        # ------------------------------------
        # This Month Purchases
        # ------------------------------------

        month_purchases = (
            db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.is_active == True,
                func.extract(
                    "year",
                    PurchaseOrder.po_date
                )
                == func.extract(
                    "year",
                    func.now()
                ),
                func.extract(
                    "month",
                    PurchaseOrder.po_date
                )
                == func.extract(
                    "month",
                    func.now()
                )
            )
            .count()
        )

        # ------------------------------------
        # Total Purchase Value
        # ------------------------------------

        total_purchase_value = (
            db.query(
                func.coalesce(
                    func.sum(
                        PurchaseOrder.grand_total
                    ),
                    0
                )
            )
            .filter(
                PurchaseOrder.is_active == True
            )
            .scalar()
        )

        # ------------------------------------
        # Today's Entry Value
        # ------------------------------------

        today_entry_value = (
            db.query(
                func.coalesce(
                    func.sum(
                        PurchaseOrder.grand_total
                    ),
                    0
                )
            )
            .filter(
                PurchaseOrder.is_active == True,
                func.date(
                    PurchaseOrder.created_at
                ) == func.current_date()
            )
            .scalar()
        )

        # ------------------------------------
        # Today's Purchase Value
        # ------------------------------------

        today_purchase_value = (
            db.query(
                func.coalesce(
                    func.sum(
                        PurchaseOrder.grand_total
                    ),
                    0
                )
            )
            .filter(
                PurchaseOrder.is_active == True,
                PurchaseOrder.po_date
                == func.current_date()
            )
            .scalar()
        )

        return {
            "total_purchases":
                total_purchases,

            "today_entries":
                today_entries,

            "today_purchases":
                today_purchases,

            "month_entries":
                month_entries,

            "month_purchases":
                month_purchases,

            "total_purchase_value":
                total_purchase_value,

            "today_entry_value":
                today_entry_value,

            "today_purchase_value":
                today_purchase_value,
        }