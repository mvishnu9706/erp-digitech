from datetime import date

from sqlalchemy import (
    func,
    or_,
)

from sqlalchemy.orm import Session

from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.customer import Customer


class SalesOrderRepository:

    # =====================================================
    # Create Sales Order
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        sales_order: SalesOrder,
        items: list[SalesOrderItem]
    ):

        # -------------------------------------------------
        # Always create a new sales order as PENDING
        # -------------------------------------------------

        sales_order.status = "PENDING"

        # -------------------------------------------------
        # Payment defaults
        # -------------------------------------------------

        if not sales_order.payment_status:
            sales_order.payment_status = "PENDING"

        if sales_order.paid_amount is None:
            sales_order.paid_amount = 0

        # -------------------------------------------------
        # Add Sales Order
        # -------------------------------------------------

        db.add(
            sales_order
        )

        db.flush()

        # -------------------------------------------------
        # Add Items
        # -------------------------------------------------

        for item in items:

            item.sales_order_id = (
                sales_order.id
            )

            db.add(
                item
            )

        db.flush()

        return sales_order

    # =====================================================
    # Get All Sales Orders
    # =====================================================

    @staticmethod
    def get_all(
        db: Session,
        search: str = None,
        customer_id: int = None,
        warehouse_id: int = None,

        # =================================================
        # NEW
        # Item/Product Filter
        # =================================================
        product_id: int = None,

        status: str = None,
        payment_status: str = None,
        date_from=None,
        date_to=None,
        skip: int = 0,
        limit: int = 10
    ):

        # -------------------------------------------------
        # Base Query
        # -------------------------------------------------

        query = (
            db.query(
                SalesOrder
            )
            .join(
                Customer,
                SalesOrder.customer_id ==
                Customer.id
            )
        )

        # =================================================
        # Search
        # =================================================
        #
        # Search supports:
        #
        # - Sales Order Number
        # - Reference By
        # - Customer Name
        # - Customer Code
        #
        # =================================================

        if search:

            search_term = (
                f"%{search.strip()}%"
            )

            query = query.filter(
                or_(
                    SalesOrder.so_number.ilike(
                        search_term
                    ),

                    SalesOrder.reference.ilike(
                        search_term
                    ),

                    Customer.customer_name.ilike(
                        search_term
                    ),

                    Customer.customer_code.ilike(
                        search_term
                    ),
                )
            )

        # =================================================
        # Customer Filter
        # =================================================

        if customer_id:

            query = query.filter(
                SalesOrder.customer_id ==
                customer_id
            )

        # =================================================
        # Warehouse Filter
        # =================================================

        if warehouse_id:

            query = query.filter(
                SalesOrder.warehouse_id ==
                warehouse_id
            )

        # =================================================
        # ITEM / PRODUCT FILTER
        # =================================================
        #
        # This is the new filter.
        #
        # Example:
        #
        # product_id = 5
        #
        # Only sales orders containing product 5
        # will be returned.
        #
        # Using .any() avoids duplicate SalesOrder
        # rows when an order contains multiple items.
        #
        # =================================================

        if product_id:

            query = query.filter(
                SalesOrder.items.any(
                    SalesOrderItem.product_id ==
                    product_id
                )
            )

        # =================================================
        # Sales Order Status Filter
        # =================================================

        if status:

            query = query.filter(
                SalesOrder.status ==
                status
            )

        # =================================================
        # Payment Status Filter
        # =================================================

        if payment_status:

            # -------------------------------------------------
            # Normalize frontend payment-status labels
            # -------------------------------------------------

            payment_status_map = {

                "Pending":
                    "PENDING",

                "Received by Hand":
                    "RECEIVED_BY_HAND",

                "Partially Received by Hand":
                    "PARTIALLY_RECEIVED_BY_HAND",

                "Received to Account":
                    "RECEIVED_TO_ACCOUNT",

                "Partially Received to Account":
                    "PARTIALLY_RECEIVED_TO_ACCOUNT",
            }

            normalized_payment_status = (
                payment_status_map.get(
                    payment_status,
                    payment_status
                )
            )

            query = query.filter(
                SalesOrder.payment_status ==
                normalized_payment_status
            )

        # =================================================
        # From Date
        # =================================================

        if date_from:

            if isinstance(
                date_from,
                str
            ):

                date_from = date.fromisoformat(
                    date_from
                )

            query = query.filter(
                SalesOrder.order_date >=
                date_from
            )

        # =================================================
        # To Date
        # =================================================

        if date_to:

            if isinstance(
                date_to,
                str
            ):

                date_to = date.fromisoformat(
                    date_to
                )

            query = query.filter(
                SalesOrder.order_date <=
                date_to
            )

        # =================================================
        # Final Query
        # =================================================

        return (
            query
            .order_by(
                SalesOrder.id.desc()
            )
            .offset(
                skip
            )
            .limit(
                limit
            )
            .all()
        )

    # =====================================================
    # Get Sales Order By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        sales_order_id: int
    ):

        return (
            db.query(
                SalesOrder
            )
            .filter(
                SalesOrder.id ==
                sales_order_id
            )
            .first()
        )

    # =====================================================
    # Get Sales Order Items
    # =====================================================

    @staticmethod
    def get_items(
        db: Session,
        sales_order_id: int
    ):

        return (
            db.query(
                SalesOrderItem
            )
            .filter(
                SalesOrderItem.sales_order_id ==
                sales_order_id
            )
            .all()
        )

    # =====================================================
    # Last Sales Order
    # =====================================================

    @staticmethod
    def last_sales_order(
        db: Session
    ):

        return (
            db.query(
                SalesOrder
            )
            .order_by(
                SalesOrder.id.desc()
            )
            .first()
        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        sales_order: SalesOrder
    ):

        # -------------------------------------------------
        # Sales Order status remains PENDING
        # -------------------------------------------------

        sales_order.status = "PENDING"

        # -------------------------------------------------
        # Save changes
        # -------------------------------------------------

        db.flush()

        # -------------------------------------------------
        # Refresh object
        # -------------------------------------------------

        db.refresh(
            sales_order
        )

        return sales_order

    # =====================================================
    # Delete Sales Order
    # =====================================================
    #
    # IMPORTANT:
    #
    # We no longer use:
    #
    #     status = "CANCELLED"
    #
    # The sales order is actually deleted.
    #
    # SalesOrder.items has:
    #
    #     cascade="all, delete-orphan"
    #
    # so its items will also be deleted.
    #
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        sales_order: SalesOrder
    ):

        db.delete(
            sales_order
        )

        db.flush()

        return {
            "success": True,
            "message":
                "Sales order deleted successfully."
        }

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):
        # =================================================
        # Current Date
        # =================================================

        today = date.today()

        # =================================================
        # Current Month
        # =================================================

        month_start = today.replace(
            day=1
        )

        # =================================================
        # Total Sales Orders
        # =================================================

        total_sales_orders = (
            db.query(
                SalesOrder
            )
            .count()
        )

        # =================================================
        # Draft Sales Orders
        # =================================================

        draft_sales_orders = (
            db.query(
                SalesOrder
            )
            .filter(
                SalesOrder.status == "DRAFT"
            )
            .count()
        )

        # =================================================
        # Pending Sales Orders
        # =================================================

        pending_orders = (
            db.query(
                SalesOrder
            )
            .filter(
                SalesOrder.status == "PENDING"
            )
            .count()
        )

        # =================================================
        # Confirmed Sales Orders
        # =================================================

        confirmed_sales_orders = (
            db.query(
                SalesOrder
            )
            .filter(
                SalesOrder.status == "CONFIRMED"
            )
            .count()
        )

        # =================================================
        # Delivered Sales Orders
        # =================================================

        delivered_sales_orders = (
            db.query(
                SalesOrder
            )
            .filter(
                SalesOrder.status == "DELIVERED"
            )
            .count()
        )

        # =================================================
        # Cancelled Sales Orders
        # =================================================

        cancelled_sales_orders = (
            db.query(
                SalesOrder
            )
            .filter(
                SalesOrder.status == "CANCELLED"
            )
            .count()
        )

        # =================================================
        # Pending Deliveries
        # =================================================

        pending_deliveries = (
            db.query(
                SalesOrder
            )
            .filter(
                SalesOrder.status.in_(
                    [
                        "PENDING",
                        "CONFIRMED",
                    ]
                )
            )
            .count()
        )

        # =================================================
        # Total Sales Value
        # =================================================

        sales_value = (
            db.query(
                func.coalesce(
                    func.sum(
                        SalesOrder.grand_total
                    ),
                    0
                )
            )
            .scalar()
        )

        # =================================================
        # Today's Orders
        # =================================================

        todays_orders = (
            db.query(
                SalesOrder
            )
            .filter(
                SalesOrder.order_date ==
                today
            )
            .count()
        )

        # =================================================
        # Today's Sales
        # =================================================

        todays_sales = (
            db.query(
                func.coalesce(
                    func.sum(
                        SalesOrder.grand_total
                    ),
                    0
                )
            )
            .filter(
                SalesOrder.order_date ==
                today
            )
            .scalar()
        )

        # =================================================
        # Today's Sales Count
        # =================================================

        todays_sales_count = (
            db.query(
                SalesOrder
            )
            .filter(
                SalesOrder.order_date ==
                today
            )
            .count()
        )

        # =================================================
        # Today's Sales Entries
        #
        # Required by the current FastAPI response schema.
        # =================================================

        todays_sales_entries = (
            todays_orders
        )

        # =================================================
        # Today's Items Sold
        # =================================================

        todays_items_sold = (
            db.query(
                func.coalesce(
                    func.sum(
                        SalesOrderItem.quantity
                    ),
                    0
                )
            )
            .join(
                SalesOrder,
                SalesOrder.id ==
                SalesOrderItem.sales_order_id
            )
            .filter(
                SalesOrder.order_date ==
                today
            )
            .scalar()
        )

        # =================================================
        # Pending Payment Orders
        # =================================================

        unpaid_invoices = (
            db.query(
                SalesOrder
            )
            .filter(
                SalesOrder.payment_status.in_(
                    [
                        "PENDING",
                        "PARTIALLY_RECEIVED_BY_HAND",
                        "PARTIALLY_RECEIVED_TO_ACCOUNT",
                    ]
                )
            )
            .count()
        )

        # =================================================
        # Pending Payment Amount
        # =================================================

        pending_payment_amount = (
            db.query(
                func.coalesce(
                    func.sum(
                        SalesOrder.grand_total -
                        func.coalesce(
                            SalesOrder.paid_amount,
                            0
                        )
                    ),
                    0
                )
            )
            .filter(
                SalesOrder.payment_status.in_(
                    [
                        "PENDING",
                        "PARTIALLY_RECEIVED_BY_HAND",
                        "PARTIALLY_RECEIVED_TO_ACCOUNT",
                    ]
                )
            )
            .scalar()
        )

        # =================================================
        # Monthly Revenue
        # =================================================

        monthly_revenue = (
            db.query(
                func.coalesce(
                    func.sum(
                        SalesOrder.grand_total
                    ),
                    0
                )
            )
            .filter(
                SalesOrder.order_date >=
                month_start
            )
            .scalar()
        )

        # =================================================
        # Return Dashboard
        # =================================================

        return {
            "total_sales_orders":
                int(
                    total_sales_orders or 0
                ),

            "draft_sales_orders":
                int(
                    draft_sales_orders or 0
                ),

            "pending_orders":
                int(
                    pending_orders or 0
                ),

            "confirmed_sales_orders":
                int(
                    confirmed_sales_orders or 0
                ),

            "delivered_sales_orders":
                int(
                    delivered_sales_orders or 0
                ),

            "cancelled_sales_orders":
                int(
                    cancelled_sales_orders or 0
                ),

            "pending_deliveries":
                int(
                    pending_deliveries or 0
                ),

            "sales_value":
                sales_value or 0,

            "todays_sales":
                todays_sales or 0,

            "todays_orders":
                int(
                    todays_orders or 0
                ),

            "todays_sales_entries":
                int(
                    todays_sales_entries or 0
                ),

            "todays_sales_count":
                int(
                    todays_sales_count or 0
                ),

            "todays_items_sold":
                int(
                    todays_items_sold or 0
                ),

            "unpaid_invoices":
                int(
                    unpaid_invoices or 0
                ),

            "pending_payment_amount":
                pending_payment_amount or 0,

            "monthly_revenue":
                monthly_revenue or 0,
        }
