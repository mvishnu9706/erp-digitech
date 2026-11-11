from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.purchase_invoice import PurchaseInvoice
from app.models.purchase_invoice_item import PurchaseInvoiceItem

from app.repositories.purchase_invoice_repository import (
    PurchaseInvoiceRepository
)

from app.repositories.purchase_order_repository import (
    PurchaseOrderRepository
)

from app.repositories.goods_receipt_repository import (
    GoodsReceiptRepository
)

from app.repositories.supplier_repository import (
    SupplierRepository
)

from app.repositories.warehouse_repository import (
    WarehouseRepository
)

from app.repositories.product_repository import product_repository

from app.schemas.purchase_invoice import (
    PurchaseInvoiceCreate
)

from app.utils.purchase_invoice_number import (
    PurchaseInvoiceNumberGenerator
)


class PurchaseInvoiceService:

    # =====================================================
    # Create Purchase Invoice
    # =====================================================

    @staticmethod
    def create_purchase_invoice(
        db: Session,
        data: PurchaseInvoiceCreate,
        current_user
    ):

        try:

            # =====================================================
            # Validate Purchase Order
            # =====================================================

            purchase_order = PurchaseOrderRepository.get_by_id(
                db,
                data.purchase_order_id
            )
            
            if not purchase_order:
                raise HTTPException(
                    status_code=404,
                    detail="Purchase Order not found."
                )

            # =====================================================
            # Validate Goods Receipt
            # =====================================================

            if data.goods_receipt_id:
                goods_receipt = GoodsReceiptRepository.get_by_id(
                    db,
                    data.goods_receipt_id
                )

                if not goods_receipt:

                    raise HTTPException(
                        status_code=404,
                        detail="Goods Receipt not found."
                    )

            # =====================================================
            # Validate Supplier
            # =====================================================

            supplier = SupplierRepository.get_by_id(
                db,
                data.supplier_id
            )

            if not supplier:

                raise HTTPException(
                    status_code=404,
                    detail="Supplier not found."
                )
                
            if not supplier.is_active:
                raise HTTPException(
                    status_code=400,
                    detail="Supplier is inactive."
                )

            # =====================================================
            # Validate Warehouse
            # =====================================================

            warehouse = WarehouseRepository.get_by_id(
                db,
                data.warehouse_id
            )

            if not warehouse:

                raise HTTPException(
                    status_code=404,
                    detail="Warehouse not found."
                )
                
            if not warehouse.is_active:
                raise HTTPException(
                    status_code=400,
                    detail="Warehouse is inactive."
                )

            # =====================================================
            # Generate Invoice Number
            # =====================================================

            last_invoice = PurchaseInvoiceRepository.last_invoice(
                db
            )

            if last_invoice:

                invoice_number = PurchaseInvoiceNumberGenerator.generate(
                    last_invoice.id + 1
                )

            else:

                invoice_number = PurchaseInvoiceNumberGenerator.generate(
                    1
                )

            # =====================================================
            # Totals
            # =====================================================

            subtotal = Decimal("0")

            discount_total = Decimal("0")

            gst_total = Decimal("0")

            grand_total = Decimal("0")

            # =====================================================
            # Duplicate Product Validation
            # =====================================================

            product_ids = [item.product_id for item in data.items]
            
            if len(product_ids) != len(set(product_ids)):
                raise HTTPException(
                    status_code=400,
                    detail="Duplicate products are not allowed."
                )

            # =====================================================
            # Invoice Header
            # =====================================================

            purchase_invoice = PurchaseInvoice(

                invoice_number=invoice_number,

                purchase_order_id=data.purchase_order_id,

                goods_receipt_id=data.goods_receipt_id,

                supplier_id=data.supplier_id,

                warehouse_id=data.warehouse_id,

                invoice_date=data.invoice_date,

                due_date=data.due_date,

                status="UNPAID",

                subtotal=0,

                discount_amount=0,

                gst_amount=0,

                other_charges=0,

                grand_total=0,

                paid_amount=0,

                balance_amount=0,

                remarks=data.remarks,

                created_by=current_user.id,

                updated_by=current_user.id

            )

            items = []

            # =====================================================
            # Process Invoice Items
            # =====================================================

            for item in data.items:
                
                # Validate Product
                product = product_repository.get_by_id(
                    db,
                    item.product_id
                )
                
                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product {item.product_id} not found."
                    )
                    
                if product.status != "Active":
                    raise HTTPException(
                        status_code=400,
                        detail=f"{product.product_name} is inactive."
                    )
                    
                # Validate Quantities and Pricing
                if item.quantity <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Quantity must be greater than zero."
                    )
                    
                if item.purchase_price <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Purchase price must be greater than zero."
                    )

                line_subtotal = (

                    Decimal(item.quantity)

                    * item.purchase_price

                )

                discount_amount = (

                    line_subtotal

                    * item.discount_percentage

                    / Decimal("100")

                )

                taxable_amount = (

                    line_subtotal

                    - discount_amount

                )

                gst_amount = (

                    taxable_amount

                    * item.gst_percentage

                    / Decimal("100")

                )

                line_total = (

                    taxable_amount

                    + gst_amount

                )

                subtotal += line_subtotal

                discount_total += discount_amount

                gst_total += gst_amount

                grand_total += line_total

                invoice_item = PurchaseInvoiceItem(

                    product_id=item.product_id,
                    
                    warehouse_id=item.warehouse_id,
                    
                    unit_id=item.unit_id,

                    quantity=item.quantity,

                    purchase_price=item.purchase_price,

                    discount_percentage=item.discount_percentage,

                    discount_amount=discount_amount,

                    gst_percentage=item.gst_percentage,

                    gst_amount=gst_amount,

                    line_total=line_total,

                    product_name=product.product_name,

                    sku=product.sku,

                    model_no=product.model_no,
                    
                    hsn_code=item.hsn_code,
                    
                    serial_number=item.serial_number,

                    remarks=item.remarks

                )

                items.append(invoice_item)
                
            # =====================================================
            # Update Invoice Totals
            # =====================================================

            purchase_invoice.subtotal = subtotal

            purchase_invoice.discount_amount = discount_total

            purchase_invoice.gst_amount = gst_total

            purchase_invoice.grand_total = grand_total

            purchase_invoice.balance_amount = grand_total

            # =====================================================
            # Save Purchase Invoice
            # =====================================================

            purchase_invoice = PurchaseInvoiceRepository.create(

                db,

                purchase_invoice,

                items

            )

            # =====================================================
            # Update Supplier Outstanding
            # =====================================================

            supplier.current_balance += grand_total
            
            db.add(supplier)

            # =====================================================
            # Commit
            # =====================================================

            db.commit()

            db.refresh(purchase_invoice)

            return purchase_invoice

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(

                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=f"Purchase Invoice Creation Failed : {str(e)}"

            )
            
    # =====================================================
    # Get Purchase Invoices
    # =====================================================

    @staticmethod
    def get_purchase_invoices(

        db: Session,

        search=None,

        supplier_id=None,

        warehouse_id=None,

        status=None,

        page=1,

        page_size=10

    ):

        skip = (page - 1) * page_size

        return PurchaseInvoiceRepository.get_all(

            db=db,

            search=search,

            supplier_id=supplier_id,

            warehouse_id=warehouse_id,

            status=status,

            skip=skip,

            limit=page_size

        )
        
    # =====================================================
    # Get Purchase Invoice
    # =====================================================

    @staticmethod
    def get_purchase_invoice(

        db: Session,

        purchase_invoice_id: int

    ):

        invoice = PurchaseInvoiceRepository.get_by_id(

            db,

            purchase_invoice_id

        )

        if not invoice:

            raise HTTPException(

                status_code=404,

                detail="Purchase Invoice not found."

            )
            
        invoice.items = PurchaseInvoiceRepository.get_items(
            db,
            purchase_invoice_id
        )

        return invoice
        
    # =====================================================
    # Update Purchase Invoice
    # =====================================================

    @staticmethod
    def update_purchase_invoice(

        db: Session,

        purchase_invoice_id: int,

        data,

        current_user

    ):

        invoice = PurchaseInvoiceRepository.get_by_id(

            db,

            purchase_invoice_id

        )

        if not invoice:

            raise HTTPException(

                status_code=404,

                detail="Purchase Invoice not found."

            )
            
        if invoice.status == "CANCELLED":
            
            raise HTTPException(
                status_code=400,
                detail="Cancelled Purchase Invoice cannot be modified."
            )

        update_data = data.model_dump(

            exclude_unset=True

        )

        for key, value in update_data.items():

            setattr(

                invoice,

                key,

                value

            )

        invoice.updated_by = current_user.id

        PurchaseInvoiceRepository.update(

            db,

            invoice

        )

        db.commit()

        db.refresh(invoice)

        return invoice
        
    # =====================================================
    # Delete Purchase Invoice
    # =====================================================

    @staticmethod
    def delete_purchase_invoice(

        db: Session,

        purchase_invoice_id: int

    ):

        invoice = PurchaseInvoiceRepository.get_by_id(

            db,

            purchase_invoice_id

        )

        if not invoice:

            raise HTTPException(

                status_code=404,

                detail="Purchase Invoice not found."

            )
            
        if invoice.status == "CANCELLED":
            
            raise HTTPException(
                status_code=400,
                detail="Purchase Invoice is already cancelled."
            )
            
        supplier = SupplierRepository.get_by_id(
            db,
            invoice.supplier_id
        )
        
        if supplier:
            supplier.current_balance -= invoice.balance_amount
            db.add(supplier)

        PurchaseInvoiceRepository.delete(

            db,

            invoice

        )

        db.commit()

        return {

            "success": True,

            "message": "Purchase Invoice deleted successfully."

        }
        
    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return PurchaseInvoiceRepository.dashboard(db)    