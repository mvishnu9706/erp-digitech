from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.goods_receipt import GoodsReceipt
from app.models.goods_receipt_item import GoodsReceiptItem


class GoodsReceiptRepository:

    # =====================================================
    # Create Goods Receipt
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        goods_receipt: GoodsReceipt,
        items: list[GoodsReceiptItem]
    ):

        db.add(goods_receipt)

        db.flush()

        for item in items:

            item.goods_receipt_id = goods_receipt.id

            db.add(item)

        return goods_receipt

    # =====================================================
    # Get All
    # =====================================================

    @staticmethod
    def get_all(
        db: Session,
        search: str = None,
        supplier_id: int = None,
        warehouse_id: int = None,
        skip: int = 0,
        limit: int = 10
    ):

        query = db.query(GoodsReceipt)

        if search:

            query = query.filter(

                GoodsReceipt.grn_number.ilike(
                    f"%{search}%"
                )

            )

        if supplier_id:

            query = query.filter(
                GoodsReceipt.supplier_id == supplier_id
            )

        if warehouse_id:

            query = query.filter(
                GoodsReceipt.warehouse_id == warehouse_id
            )

        return (

            query

            .order_by(GoodsReceipt.id.desc())

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
        goods_receipt_id: int
    ):

        return (

            db.query(GoodsReceipt)

            .filter(
                GoodsReceipt.id == goods_receipt_id
            )

            .first()

        )

    # =====================================================
    # Get Items
    # =====================================================

    @staticmethod
    def get_items(
        db: Session,
        goods_receipt_id: int
    ):

        return (

            db.query(GoodsReceiptItem)

            .filter(
                GoodsReceiptItem.goods_receipt_id == goods_receipt_id
            )

            .all()

        )

    # =====================================================
    # Last Goods Receipt
    # =====================================================

    @staticmethod
    def last_goods_receipt(
        db: Session
    ):

        return (

            db.query(GoodsReceipt)

            .order_by(
                GoodsReceipt.id.desc()
            )

            .first()

        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        goods_receipt: GoodsReceipt
    ):

        db.flush()

        db.refresh(goods_receipt)

        return goods_receipt

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        goods_receipt: GoodsReceipt
    ):

        db.delete(goods_receipt)

        db.flush()

        return True

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return {

            "total_goods_receipts":

                db.query(GoodsReceipt).count(),

            "total_received_value":

                db.query(

                    func.coalesce(

                        func.sum(
                            GoodsReceipt.grand_total
                        ),

                        0

                    )

                ).scalar()

        }