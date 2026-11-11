import "./SalesDetails.css";

import {
    User,
    Warehouse,
    CalendarDays,
    FileText,
    Package,
} from "lucide-react";

import { useSales } from "../../../context/SalesContext";

const SalesDetails = () => {

    const {
        sale,
        customers,
        warehouses,
    } = useSales();

    //----------------------------------------
    // Customer
    //----------------------------------------

    const customer = customers.find(
        (item) =>
            Number(item.id) ===
            Number(sale.customer_id)
    );

    const customerName =
        customer?.name ||
        customer?.customer_name ||
        customer?.full_name ||
        sale.customer_name ||
        "-";

    //----------------------------------------
    // Warehouse
    //----------------------------------------

    const warehouse = warehouses.find(
        (item) =>
            Number(item.id) ===
            Number(sale.warehouse_id)
    );

    const warehouseName =
        warehouse?.name ||
        warehouse?.warehouse_name ||
        sale.warehouse_name ||
        "-";

    //----------------------------------------
    // Currency
    //----------------------------------------

    const formatCurrency = (value) => {

        return `₹${Number(value || 0).toLocaleString(
            "en-IN",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            }
        )}`;
    };

    //----------------------------------------
    // Date
    //----------------------------------------

    const formatDate = (date) => {

        if (!date) {
            return "-";
        }

        return new Date(date).toLocaleDateString(
            "en-IN",
            {
                day: "2-digit",
                month: "short",
                year: "numeric",
            }
        );
    };

    //----------------------------------------
    // Item Total
    //----------------------------------------

    const getItemTotal = (item) => {

        if (item.total !== undefined) {
            return Number(item.total) || 0;
        }

        const quantity =
            Number(item.quantity) || 0;

        const price =
            Number(item.selling_price) || 0;

        const discount =
            Number(
                item.discount_percentage
            ) || 0;

        const gst =
            Number(
                item.gst_percentage
            ) || 0;

        const amount =
            quantity * price;

        const discountAmount =
            amount * (discount / 100);

        const taxable =
            amount - discountAmount;

        return (
            taxable +
            taxable * (gst / 100)
        );
    };

    //----------------------------------------
    // Totals
    //----------------------------------------

    const subtotal = sale.items.reduce(
        (sum, item) => {

            const quantity =
                Number(item.quantity) || 0;

            const price =
                Number(item.selling_price) || 0;

            return sum + quantity * price;
        },
        0
    );

    const discount = sale.items.reduce(
        (sum, item) => {

            const quantity =
                Number(item.quantity) || 0;

            const price =
                Number(item.selling_price) || 0;

            const percentage =
                Number(
                    item.discount_percentage
                ) || 0;

            return (
                sum +
                quantity *
                    price *
                    (percentage / 100)
            );
        },
        0
    );

    const gst = sale.items.reduce(
        (sum, item) => {

            const quantity =
                Number(item.quantity) || 0;

            const price =
                Number(item.selling_price) || 0;

            const discountPercentage =
                Number(
                    item.discount_percentage
                ) || 0;

            const gstPercentage =
                Number(
                    item.gst_percentage
                ) || 0;

            const amount =
                quantity * price;

            const discountAmount =
                amount *
                (discountPercentage / 100);

            const taxable =
                amount - discountAmount;

            return (
                sum +
                taxable *
                    (gstPercentage / 100)
            );
        },
        0
    );

    const grandTotal =
        sale.items.reduce(
            (sum, item) =>
                sum + getItemTotal(item),
            0
        );

    return (
        <div className="sales-details">

            {/* =================================
                Order Information
            ================================= */}

            <div className="sales-details-card">

                <div className="sales-details-card-header">

                    <div>
                        <h3>
                            Sales Order Information
                        </h3>

                        <p>
                            Sales order details
                        </p>
                    </div>

                    <span className="sales-details-order-number">
                        {sale.order_number ||
                            sale.sales_order_number ||
                            sale.reference_number ||
                            "-"}
                    </span>

                </div>


                <div className="sales-details-info-grid">

                    {/* Customer */}

                    <div className="sales-detail-info">

                        <div className="sales-detail-icon">
                            <User size={17} />
                        </div>

                        <div>
                            <span>
                                Customer
                            </span>

                            <strong>
                                {customerName}
                            </strong>
                        </div>

                    </div>


                    {/* Warehouse */}

                    <div className="sales-detail-info">

                        <div className="sales-detail-icon">
                            <Warehouse size={17} />
                        </div>

                        <div>
                            <span>
                                Warehouse
                            </span>

                            <strong>
                                {warehouseName}
                            </strong>
                        </div>

                    </div>


                    {/* Date */}

                    <div className="sales-detail-info">

                        <div className="sales-detail-icon">
                            <CalendarDays size={17} />
                        </div>

                        <div>
                            <span>
                                Sales Date
                            </span>

                            <strong>
                                {formatDate(
                                    sale.sale_date
                                )}
                            </strong>
                        </div>

                    </div>


                    {/* Invoice */}

                    <div className="sales-detail-info">

                        <div className="sales-detail-icon">
                            <FileText size={17} />
                        </div>

                        <div>
                            <span>
                                Invoice / Reference
                            </span>

                            <strong>
                                {sale.invoice_no ||
                                    "-"}
                            </strong>
                        </div>

                    </div>

                </div>

            </div>


            {/* =================================
                Products
            ================================= */}

            <div className="sales-details-card">

                <div className="sales-details-card-header">

                    <div>
                        <h3>
                            Products
                        </h3>

                        <p>
                            Products included in this order
                        </p>
                    </div>

                </div>


                <div className="sales-details-items-scroll">

                    <table className="sales-details-items">

                        <thead>

                            <tr>

                                <th>
                                    #
                                </th>

                                <th>
                                    Product
                                </th>

                                <th>
                                    Qty
                                </th>

                                <th>
                                    Selling Price
                                </th>

                                <th>
                                    Discount
                                </th>

                                <th>
                                    GST
                                </th>

                                <th>
                                    Total
                                </th>

                            </tr>

                        </thead>

                        <tbody>

                            {sale.items.map(
                                (item, index) => (

                                    <tr
                                        key={index}
                                    >

                                        <td>
                                            {index + 1}
                                        </td>

                                        <td>

                                            <div className="sales-detail-product">

                                                <Package
                                                    size={16}
                                                />

                                                <span>
                                                    {item.product_name ||
                                                        item.name ||
                                                        `Product #${item.product_id}`}
                                                </span>

                                            </div>

                                        </td>

                                        <td>
                                            {item.quantity}
                                        </td>

                                        <td>
                                            {formatCurrency(
                                                item.selling_price
                                            )}
                                        </td>

                                        <td>
                                            {item.discount_percentage ??
                                                0}%
                                        </td>

                                        <td>
                                            {item.gst_percentage ??
                                                18}%
                                        </td>

                                        <td>

                                            <strong>
                                                {formatCurrency(
                                                    getItemTotal(
                                                        item
                                                    )
                                                )}
                                            </strong>

                                        </td>

                                    </tr>

                                )
                            )}

                        </tbody>

                    </table>

                </div>

            </div>


            {/* =================================
                Summary
            ================================= */}

            <div className="sales-details-summary">

                <div className="sales-details-summary-row">

                    <span>
                        Subtotal
                    </span>

                    <strong>
                        {formatCurrency(
                            subtotal
                        )}
                    </strong>

                </div>


                <div className="sales-details-summary-row discount">

                    <span>
                        Discount
                    </span>

                    <strong>
                        - {formatCurrency(
                            discount
                        )}
                    </strong>

                </div>


                <div className="sales-details-summary-row">

                    <span>
                        GST
                    </span>

                    <strong>
                        {formatCurrency(
                            gst
                        )}
                    </strong>

                </div>


                <div className="sales-details-summary-divider" />


                <div className="sales-details-total">

                    <span>
                        Grand Total
                    </span>

                    <strong>
                        {formatCurrency(
                            grandTotal
                        )}
                    </strong>

                </div>

            </div>


            {/* =================================
                Remarks
            ================================= */}

            {sale.remarks && (

                <div className="sales-details-remarks">

                    <h3>
                        Remarks
                    </h3>

                    <p>
                        {sale.remarks}
                    </p>

                </div>

            )}

        </div>
    );
};

export default SalesDetails;