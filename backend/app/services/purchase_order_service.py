from datetime import date
from io import BytesIO
from decimal import Decimal

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy.orm import Session

from app.models.goods_receipt import GoodsReceipt
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.schemas.purchase_order import PurchaseOrderItemResponse
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.repositories.supplier_repository import SupplierRepository
from app.repositories.warehouse_repository import WarehouseRepository

from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderResponse,
    PurchaseOrderItemResponse,
    PurchaseOrderListResponse,
    PurchaseDashboardResponse,
)

from app.utils.purchase_order_number import (
    PurchaseOrderNumberGenerator,
)


class PurchaseOrderService:

    # =====================================================
    # Create Purchase Order
    # =====================================================

    @staticmethod
    def create_purchase_order(
        db: Session,
        data: PurchaseOrderCreate,
        current_user,
    ):

        try:

            # ==========================================
            # Validate Supplier
            # ==========================================

            supplier = SupplierRepository.get_by_id(
                db,
                data.supplier_id,
            )

            if not supplier:
                raise HTTPException(
                    status_code=404,
                    detail="Supplier not found.",
                )

            if not supplier.is_active:
                raise HTTPException(
                    status_code=400,
                    detail="Supplier is inactive.",
                )

            # ==========================================
            # Validate Warehouse
            # ==========================================

            warehouse = WarehouseRepository.get_by_id(
                db,
                data.warehouse_id,
            )

            if not warehouse:
                raise HTTPException(
                    status_code=404,
                    detail="Warehouse not found.",
                )

            if not warehouse.is_active:
                raise HTTPException(
                    status_code=400,
                    detail="Warehouse is inactive.",
                )

            # ==========================================
            # Generate PO Number
            # ==========================================

            # Continue from the highest existing PO sequence
            # instead of using the database ID.
            last_sequence = (
                PurchaseOrderRepository.get_last_po_sequence(
                    db
                )
            )

            next_sequence = last_sequence + 1

            po_number = (
                PurchaseOrderNumberGenerator.generate(
                    data.po_date,
                    next_sequence
                )
            )

            # ==========================================
            # Calculate Totals
            # ==========================================

            purchase_items = []

            subtotal = Decimal("0")
            discount_amount = Decimal("0")
            gst_amount = Decimal("0")

            for item in data.items:

                product = ProductRepository.get_by_id(
                    db,
                    item.product_id,
                )

                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product {item.product_id} not found.",
                    )

                amount = (
                    Decimal(item.quantity)
                    * Decimal(item.purchase_price)
                )

                discount = (
                    amount
                    * Decimal(item.discount_percentage)
                    / Decimal("100")
                )

                taxable = amount - discount

                gst = (
                    taxable
                    * Decimal(item.gst_percentage)
                    / Decimal("100")
                )

                line_total = taxable + gst

                subtotal += amount
                discount_amount += discount
                gst_amount += gst

                purchase_items.append(

                    PurchaseOrderItem(

                        product_id=product.id,
                        product_name=product.product_name,
                        sku=product.sku,

                        warehouse_id=data.warehouse_id,
                        warehouse_name=warehouse.warehouse_name,

                        unit_id=product.unit_id,

                        # FIXED
                        unit_name=(
                            product.unit.name
                            if product.unit
                            else ""
                        ),

                        quantity=item.quantity,

                        received_quantity=item.quantity,
                        pending_quantity=0,

                        purchase_price=item.purchase_price,

                        discount_percentage=item.discount_percentage,
                        discount_amount=discount,

                        gst_percentage=item.gst_percentage,
                        gst_amount=gst,

                        line_total=line_total,

                        remarks=item.remarks,
                    )
                )

            # ==========================================
            # Purchase Header
            # ==========================================

            purchase_order = PurchaseOrder(

                po_number=po_number,

                supplier_id=data.supplier_id,
                warehouse_id=data.warehouse_id,

                po_date=data.po_date,

                reference_number=data.reference_number,

                remarks=data.remarks,

                subtotal=subtotal,
                discount_amount=discount_amount,
                gst_amount=gst_amount,

                other_charges=Decimal("0"),

                grand_total=(
                    subtotal
                    - discount_amount
                    + gst_amount
                ),

                created_by=current_user.id,
            )

            # ==========================================
            # Save Purchase
            # ==========================================

            purchase_order = PurchaseOrderRepository.create(
                db=db,
                purchase_order=purchase_order,
                items=purchase_items,
            )

            # ==========================================
            # Update Inventory
            # ==========================================

            for item in purchase_items:

                InventoryRepository.increase_stock(
                    db=db,
                    product_id=item.product_id,
                    warehouse_id=item.warehouse_id,
                    quantity=item.quantity,
                    purchase_price=item.purchase_price,
                    purchase_date=purchase_order.po_date,
                    user_id=current_user.id,
                )

            # ==========================================
            # Commit
            # ==========================================

            db.commit()

            db.refresh(purchase_order)

            purchase_order.items = (
                PurchaseOrderRepository.get_items(
                    db,
                    purchase_order.id,
                )
            )

            purchase_order.supplier_name = (
                purchase_order.supplier.company_name
                if purchase_order.supplier
                else None
            )

            purchase_order.warehouse_name = (
                purchase_order.warehouse.warehouse_name
                if purchase_order.warehouse
                else None
            )

            return purchase_order

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:

            import traceback

            traceback.print_exc()

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    # =====================================================
    # Get Purchase Orders
    # =====================================================

    @staticmethod
    def get_purchase_orders(
        db: Session,
        search=None,
        supplier_id=None,
        warehouse_id=None,
        date_from=None,
        date_to=None,
        page=1,
        page_size=10,
    ):

        skip = (page - 1) * page_size

        total_records, purchases = (
            PurchaseOrderRepository.get_all(
                db=db,
                search=search,
                supplier_id=supplier_id,
                warehouse_id=warehouse_id,
                date_from=date_from,
                date_to=date_to,
                skip=skip,
                limit=page_size,
            )
        )

        response = []

        for po in purchases:

            items = []

            for item in po.items:

                items.append(

                    PurchaseOrderItemResponse(

                        id=item.id,

                        purchase_order_id=item.purchase_order_id,

                        product_id=item.product_id,
                        warehouse_id=item.warehouse_id,
                        unit_id=item.unit_id,

                        quantity=item.quantity,

                        received_quantity=item.received_quantity,
                        pending_quantity=item.pending_quantity,

                        purchase_price=item.purchase_price,

                        discount_percentage=item.discount_percentage,
                        discount_amount=item.discount_amount,

                        gst_percentage=item.gst_percentage,
                        gst_amount=item.gst_amount,

                        line_total=item.line_total,

                        remarks=item.remarks,

                        product_name=item.product_name,
                        sku=item.sku,

                        hsn_code=getattr(
                            item,
                            "hsn_code",
                            None
                        ),

                        serial_number=getattr(
                            item,
                            "serial_number",
                            None
                        ),

                        model_no=(
                            item.product.model_no
                            if item.product
                            else None
                        ),

                        created_at=item.created_at,
                        updated_at=item.updated_at,
                    )
                )

            response.append(

                PurchaseOrderResponse(

                    id=po.id,

                    po_number=po.po_number,

                    supplier_id=po.supplier_id,
                    warehouse_id=po.warehouse_id,

                    supplier_name=(
                        po.supplier.company_name
                        if po.supplier
                        else None
                    ),

                    warehouse_name=(
                        po.warehouse.warehouse_name
                        if po.warehouse
                        else None
                    ),

                    po_date=po.po_date,

                    reference_number=po.reference_number,

                    remarks=po.remarks,

                    subtotal=po.subtotal,
                    discount_amount=po.discount_amount,
                    gst_amount=po.gst_amount,
                    other_charges=po.other_charges,
                    grand_total=po.grand_total,

                    created_by=po.created_by,
                    updated_by=po.updated_by,

                    created_at=po.created_at,
                    updated_at=po.updated_at,

                    items=items,
                )
            )

        return PurchaseOrderListResponse(

            total_records=total_records,

            page=page,

            page_size=page_size,

            purchase_orders=response,
        )

    # =====================================================
    # Get Purchase Order
    # =====================================================

    @staticmethod
    def get_purchase_order(
        db: Session,
        purchase_order_id: int,
    ):

        po = PurchaseOrderRepository.get_by_id(
            db,
            purchase_order_id,
        )

        if not po:
            raise HTTPException(
                status_code=404,
                detail="Purchase Order not found.",
            )

        items = []

        for item in po.items:

            items.append(

                PurchaseOrderItemResponse(

                    id=item.id,

                    purchase_order_id=item.purchase_order_id,

                    product_id=item.product_id,
                    warehouse_id=item.warehouse_id,
                    unit_id=item.unit_id,

                    quantity=item.quantity,

                    received_quantity=item.received_quantity,
                    pending_quantity=item.pending_quantity,

                    purchase_price=item.purchase_price,

                    discount_percentage=item.discount_percentage,
                    discount_amount=item.discount_amount,

                    gst_percentage=item.gst_percentage,
                    gst_amount=item.gst_amount,

                    line_total=item.line_total,

                    remarks=item.remarks,

                    product_name=item.product_name,
                    sku=item.sku,

                    model_no=(
                        item.product.model_no
                        if item.product
                        else None
                    ),

                    hsn_code=getattr(
                        item,
                        "hsn_code",
                        None
                    ),

                    serial_number=getattr(
                        item,
                        "serial_number",
                        None
                    ),

                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )

        return PurchaseOrderResponse(

            id=po.id,

            po_number=po.po_number,

            supplier_id=po.supplier_id,
            warehouse_id=po.warehouse_id,

            supplier_name=(
                po.supplier.company_name
                if po.supplier
                else None
            ),

            warehouse_name=(
                po.warehouse.warehouse_name
                if po.warehouse
                else None
            ),

            po_date=po.po_date,

            reference_number=po.reference_number,

            remarks=po.remarks,

            subtotal=po.subtotal,
            discount_amount=po.discount_amount,
            gst_amount=po.gst_amount,
            other_charges=po.other_charges,
            grand_total=po.grand_total,

            created_by=po.created_by,
            updated_by=po.updated_by,

            created_at=po.created_at,
            updated_at=po.updated_at,

            items=items,
        )

    # =====================================================
    # Update Purchase Order
    # =====================================================

    @staticmethod
    def update_purchase_order(
        db: Session,
        purchase_order_id: int,
        data: PurchaseOrderUpdate,
        current_user,
    ):

        purchase_order = PurchaseOrderRepository.get_by_id(
            db,
            purchase_order_id,
        )

        if not purchase_order:
            raise HTTPException(
                status_code=404,
                detail="Purchase Order not found.",
            )

        # ==========================================
        # Supplier
        # ==========================================

        if data.supplier_id is not None:

            supplier = SupplierRepository.get_by_id(
                db,
                data.supplier_id,
            )

            if not supplier:
                raise HTTPException(
                    status_code=404,
                    detail="Supplier not found.",
                )

            purchase_order.supplier_id = data.supplier_id

        # ==========================================
        # Warehouse
        # ==========================================

        if data.warehouse_id is not None:

            warehouse = WarehouseRepository.get_by_id(
                db,
                data.warehouse_id,
            )

            if not warehouse:
                raise HTTPException(
                    status_code=404,
                    detail="Warehouse not found.",
                )

            purchase_order.warehouse_id = data.warehouse_id

        # ==========================================
        # Update Fields
        # ==========================================

        if data.po_date is not None:
            purchase_order.po_date = data.po_date

        if data.reference_number is not None:
            purchase_order.reference_number = data.reference_number

        if data.remarks is not None:
            purchase_order.remarks = data.remarks

        purchase_order.updated_by = current_user.id

        purchase_order = PurchaseOrderRepository.update(
            db,
            purchase_order,
        )

        db.commit()

        db.refresh(purchase_order)

        purchase_order.items = PurchaseOrderRepository.get_items(
            db,
            purchase_order.id,
        )

        purchase_order.supplier_name = (
            purchase_order.supplier.company_name
            if purchase_order.supplier
            else None
        )

        purchase_order.warehouse_name = (
            purchase_order.warehouse.warehouse_name
            if purchase_order.warehouse
            else None
        )

        return purchase_order

    # =====================================================
    # Delete Purchase Order
    # =====================================================

    @staticmethod
    def delete_purchase_order(
        db: Session,
        purchase_order_id: int,
    ):

        purchase_order = PurchaseOrderRepository.get_by_id(
            db,
            purchase_order_id,
        )

        if not purchase_order:
            raise HTTPException(
                status_code=404,
                detail="Purchase Order not found.",
            )

        PurchaseOrderRepository.delete(
            db,
            purchase_order,
        )

        db.commit()

        return {
            "success": True,
            "message": "Purchase Order deleted successfully.",
        }

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session,
    ):

        dashboard = PurchaseOrderRepository.dashboard(db)

        return PurchaseDashboardResponse(

            total_purchases=dashboard["total_purchases"],

            today_entries=dashboard["today_entries"],

            today_purchases=dashboard["today_purchases"],

            month_entries=dashboard["month_entries"],

            month_purchases=dashboard["month_purchases"],

            total_purchase_value=dashboard["total_purchase_value"],

            today_entry_value=dashboard["today_entry_value"],

            today_purchase_value=dashboard["today_purchase_value"],
        )

    # =====================================================
    # Export Purchase Orders
    # =====================================================

    @staticmethod
    def export_purchase_orders(
        db,
        search=None,
        supplier_id=None,
        warehouse_id=None,
        date_from=None,
        date_to=None,
    ):

        total, purchases = PurchaseOrderRepository.get_all(
            db=db,
            search=search,
            supplier_id=supplier_id,
            warehouse_id=warehouse_id,
            date_from=date_from,
            date_to=date_to,
            skip=0,
            limit=100000,
        )

        wb = Workbook()
        ws = wb.active
        ws.title = "Purchase Orders"

        ws.append([
            "PO Number",
            "Supplier",
            "Warehouse",
            "Purchase Date",
            "Created On",
            "Subtotal",
            "GST",
            "Discount",
            "Grand Total",
            "Remarks",
        ])

        for po in purchases:
            ws.append([
                po.po_number,
                po.supplier.company_name if po.supplier else "",
                po.warehouse.warehouse_name if po.warehouse else "",
                po.po_date.strftime("%d-%m-%Y"),
                po.created_at.strftime("%d-%m-%Y"),
                float(po.subtotal),
                float(po.gst_amount),
                float(po.discount_amount),
                float(po.grand_total),
                po.remarks or "",
            ])

        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)

        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition":
                "attachment; filename=purchase_orders.xlsx"
            },
        )