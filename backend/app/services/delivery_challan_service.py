from decimal import Decimal

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.models.delivery_challan import DeliveryChallan
from app.models.delivery_challan_item import DeliveryChallanItem

from app.repositories.delivery_challan_repository import (
    DeliveryChallanRepository
)

from app.repositories.sales_order_repository import (
    SalesOrderRepository
)

from app.repositories.product_repository import (
    ProductRepository
)

from app.repositories.customer_repository import (
    CustomerRepository
)

from app.repositories.warehouse_repository import (
    WarehouseRepository
)

from app.schemas.delivery_challan import (
    DeliveryChallanCreate
)

from app.utils.delivery_challan_number import (
    DeliveryChallanNumberGenerator
)


class DeliveryChallanService:

    # =====================================================
    # Create Delivery Challan
    # =====================================================

    @staticmethod
    def create_delivery_challan(
        db: Session,
        data: DeliveryChallanCreate,
        current_user
    ):

        try:

            # =================================================
            # Validate Sales Order
            # =================================================

            sales_order = SalesOrderRepository.get_by_id(
                db,
                data.sales_order_id
            )

            if not sales_order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sales Order not found."
                )

            if sales_order.status == "CANCELLED":
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Cannot create Delivery Challan "
                        "for cancelled Sales Order."
                    )
                )

            if sales_order.status not in [
                "CONFIRMED",
                "PARTIALLY_DELIVERED"
            ]:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Cannot create Delivery Challan "
                        f"for Sales Order in "
                        f"'{sales_order.status}' status."
                    )
                )

            # =================================================
            # Validate Customer
            # =================================================

            customer = CustomerRepository.get_by_id(
                db,
                data.customer_id
            )

            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found."
                )

            if not customer.is_active:
                raise HTTPException(
                    status_code=400,
                    detail="Customer is inactive."
                )

            if sales_order.customer_id != customer.id:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Customer does not belong "
                        "to this Sales Order."
                    )
                )

            # =================================================
            # Validate Warehouse
            # =================================================

            warehouse = WarehouseRepository.get_by_id(
                db,
                data.warehouse_id
            )

            if not warehouse:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Warehouse not found."
                )

            if not warehouse.is_active:
                raise HTTPException(
                    status_code=400,
                    detail="Warehouse is inactive."
                )

            if sales_order.warehouse_id != warehouse.id:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Warehouse does not belong "
                        "to this Sales Order."
                    )
                )

            # =================================================
            # Generate Delivery Challan Number
            # =================================================

            last_dc = (
                DeliveryChallanRepository
                .last_delivery_challan(db)
            )

            if last_dc:

                dc_number = (
                    DeliveryChallanNumberGenerator.generate(
                        last_dc.id + 1
                    )
                )

            else:

                dc_number = (
                    DeliveryChallanNumberGenerator.generate(1)
                )

            # =================================================
            # Create Delivery Challan
            # =================================================

            delivery_challan = DeliveryChallan(
                dc_number=dc_number,
                sales_order_id=data.sales_order_id,
                customer_id=data.customer_id,
                warehouse_id=data.warehouse_id,
                delivery_date=data.delivery_date,
                status="DRAFT",
                remarks=data.remarks,
                created_by=current_user.id,
                updated_by=current_user.id
            )

            items = []

            # =================================================
            # Validate Duplicate Items
            # =================================================

            product_ids = [
                item.product_id
                for item in data.items
            ]

            sales_order_item_ids = [
                item.sales_order_item_id
                for item in data.items
            ]

            if len(sales_order_item_ids) != len(
                set(sales_order_item_ids)
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Duplicate Sales Order Items "
                        "are not allowed."
                    )
                )

            if len(product_ids) != len(
                set(product_ids)
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Duplicate products are not allowed."
                )

            # =================================================
            # Get Sales Order Items
            # =================================================

            sales_order_items = (
                SalesOrderRepository.get_items(
                    db,
                    sales_order.id
                )
            )

            sales_order_item_map = {
                item.id: item
                for item in sales_order_items
            }

            # =================================================
            # Validate Delivery Quantities
            # =================================================

            for delivered_item in data.items:

                order_item = sales_order_item_map.get(
                    delivered_item.sales_order_item_id
                )

                if not order_item:
                    raise HTTPException(
                        status_code=404,
                        detail=(
                            f"Sales Order Item "
                            f"{delivered_item.sales_order_item_id} "
                            f"not found."
                        )
                    )

                # =============================================
                # Product must match order item
                # =============================================

                if (
                    order_item.product_id
                    != delivered_item.product_id
                ):
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Product does not belong "
                            "to the selected Sales Order Item."
                        )
                    )

                # =============================================
                # Calculate pending quantity
                # =============================================

                pending_qty = (
                    order_item.quantity
                    - order_item.delivered_quantity
                )

                if delivered_item.delivered_quantity <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Delivered quantity must be "
                            "greater than zero."
                        )
                    )

                if (
                    delivered_item.delivered_quantity
                    > pending_qty
                ):
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Delivered quantity exceeds "
                            f"pending quantity for "
                            f"{order_item.product_name}"
                        )
                    )

            # =================================================
            # Process Delivery Items
            #
            # IMPORTANT:
            #
            # Inventory stock is NOT changed here.
            #
            # There is no:
            #
            # current_stock
            # reserved_stock
            # available_stock
            #
            # There is also NO SALES_OUT inventory
            # transaction here.
            #
            # Stock is updated only when the Sales Order
            # is successfully committed.
            # =================================================

            for item in data.items:

                # =============================================
                # Product validation
                # =============================================

                product = ProductRepository.get_by_id(
                    db,
                    item.product_id
                )

                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail="Product not found."
                    )

                prod_status = getattr(
                    product,
                    "status",
                    None
                )

                if (
                    not prod_status
                    or str(prod_status).upper()
                    != "ACTIVE"
                ):
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"{product.product_name} "
                            f"is inactive."
                        )
                    )

                # =============================================
                # Get Sales Order Item
                # =============================================

                order_item = sales_order_item_map.get(
                    item.sales_order_item_id
                )

                if not order_item:
                    raise HTTPException(
                        status_code=404,
                        detail=(
                            f"Sales Order Item "
                            f"{item.sales_order_item_id} "
                            f"not found."
                        )
                    )

                # =============================================
                # Selling Price
                # =============================================

                selling_price = (
                    order_item.selling_price
                )

                # =============================================
                # Create Delivery Challan Item
                # =============================================

                dc_item = DeliveryChallanItem(
                    sales_order_item_id=(
                        item.sales_order_item_id
                    ),

                    product_id=item.product_id,

                    delivered_quantity=(
                        item.delivered_quantity
                    ),

                    selling_price=selling_price,

                    product_name=product.product_name,

                    sku=product.sku,

                    model_no=product.model_no,

                    remarks=item.remarks
                )

                items.append(dc_item)

            # =================================================
            # Create Delivery Challan
            # =================================================

            delivery_challan = (
                DeliveryChallanRepository.create(
                    db,
                    delivery_challan,
                    items
                )
            )

            # =================================================
            # Update Sales Order Items
            #
            # Delivery tracking only.
            #
            # Inventory stock is NOT modified.
            # =================================================

            for delivered_item in data.items:

                order_item = sales_order_item_map.get(
                    delivered_item.sales_order_item_id
                )

                if not order_item:
                    raise HTTPException(
                        status_code=404,
                        detail=(
                            f"Sales Order Item "
                            f"{delivered_item.sales_order_item_id} "
                            f"not found."
                        )
                    )

                # =============================================
                # Calculate pending quantity
                # =============================================

                pending_qty = (
                    order_item.quantity
                    - order_item.delivered_quantity
                )

                if (
                    delivered_item.delivered_quantity
                    > pending_qty
                ):
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Delivered quantity exceeds "
                            f"pending quantity for "
                            f"{order_item.product_name}"
                        )
                    )

                # =============================================
                # Update delivered quantity
                # =============================================

                order_item.delivered_quantity += (
                    delivered_item.delivered_quantity
                )

                # =============================================
                # Update pending quantity
                # =============================================

                order_item.pending_quantity = (
                    order_item.quantity
                    - order_item.delivered_quantity
                )

            # =================================================
            # Update Sales Order Status
            # =================================================

            all_delivered = all(
                item.pending_quantity == 0
                for item in sales_order_items
            )

            any_delivered = any(
                item.delivered_quantity > 0
                for item in sales_order_items
            )

            if all_delivered:

                sales_order.status = "DELIVERED"

            elif any_delivered:

                sales_order.status = "PARTIALLY_DELIVERED"

            else:

                sales_order.status = "CONFIRMED"

            # =================================================
            # Update Delivery Challan Status
            # =================================================

            delivery_challan.status = (
                sales_order.status
            )

            DeliveryChallanRepository.update(
                db,
                delivery_challan
            )

            # =================================================
            # Commit
            # =================================================

            db.commit()

            db.refresh(
                delivery_challan
            )

            return delivery_challan

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Delivery Challan Creation Failed : "
                    f"{str(e)}"
                )
            )

    # =====================================================
    # Get Delivery Challans
    # =====================================================

    @staticmethod
    def get_delivery_challans(
        db: Session,
        search=None,
        sales_order_id=None,
        customer_id=None,
        warehouse_id=None,
        status=None,
        page=1,
        page_size=10
    ):

        skip = (
            (page - 1)
            * page_size
        )

        return DeliveryChallanRepository.get_all(
            db=db,
            search=search,
            sales_order_id=sales_order_id,
            customer_id=customer_id,
            warehouse_id=warehouse_id,
            status=status,
            skip=skip,
            limit=page_size
        )

    # =====================================================
    # Get Delivery Challan
    # =====================================================

    @staticmethod
    def get_delivery_challan(
        db: Session,
        delivery_challan_id: int
    ):

        delivery_challan = (
            DeliveryChallanRepository.get_by_id(
                db,
                delivery_challan_id
            )
        )

        if not delivery_challan:

            raise HTTPException(
                status_code=404,
                detail="Delivery Challan not found."
            )

        return delivery_challan

    # =====================================================
    # Update Delivery Challan
    # =====================================================

    @staticmethod
    def update_delivery_challan(
        db: Session,
        delivery_challan_id: int,
        data,
        current_user
    ):

        delivery_challan = (
            DeliveryChallanRepository.get_by_id(
                db,
                delivery_challan_id
            )
        )

        if not delivery_challan:

            raise HTTPException(
                status_code=404,
                detail="Delivery Challan not found."
            )

        if delivery_challan.status != "DRAFT":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only draft Delivery Challans "
                    "can be updated."
                )
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():

            setattr(
                delivery_challan,
                key,
                value
            )

        delivery_challan.updated_by = (
            current_user.id
        )

        DeliveryChallanRepository.update(
            db,
            delivery_challan
        )

        db.commit()

        db.refresh(
            delivery_challan
        )

        return delivery_challan

    # =====================================================
    # Delete Delivery Challan
    # =====================================================

    @staticmethod
    def delete_delivery_challan(
        db: Session,
        delivery_challan_id: int
    ):

        delivery_challan = (
            DeliveryChallanRepository.get_by_id(
                db,
                delivery_challan_id
            )
        )

        if not delivery_challan:

            raise HTTPException(
                status_code=404,
                detail="Delivery Challan not found."
            )

        if delivery_challan.status != "DRAFT":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only draft Delivery Challans "
                    "can be deleted."
                )
            )

        DeliveryChallanRepository.delete(
            db,
            delivery_challan
        )

        db.commit()

        return {
            "success": True,
            "message": (
                "Delivery Challan cancelled successfully."
            )
        }

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return DeliveryChallanRepository.dashboard(
            db
        )