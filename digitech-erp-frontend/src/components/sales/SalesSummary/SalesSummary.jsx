import "./SalesSummary.css";

import { IndianRupee } from "lucide-react";

import { useSales } from "../../../context/SalesContext";

const SalesSummary = () => {

    const {
        sale,
    } = useSales();

    //----------------------------------------
    // Safety
    //----------------------------------------

    const items = Array.isArray(sale?.items)
        ? sale.items
        : [];

    //----------------------------------------
    // Subtotal
    //----------------------------------------

    const subtotal = items.reduce(
        (sum, item) => {

            const quantity =
                Number(item.quantity) || 0;

            const price =
                Number(item.selling_price) || 0;

            return (
                sum +
                quantity * price
            );
        },
        0
    );

    //----------------------------------------
    // Discount
    //----------------------------------------

    const discount = items.reduce(
        (sum, item) => {

            const quantity =
                Number(item.quantity) || 0;

            const price =
                Number(item.selling_price) || 0;

            const discountPercentage =
                Number(
                    item.discount_percentage
                ) || 0;

            const amount =
                quantity * price;

            const itemDiscount =
                amount *
                (discountPercentage / 100);

            return (
                sum +
                itemDiscount
            );
        },
        0
    );

    //----------------------------------------
    // Taxable Amount
    //----------------------------------------

    const taxableAmount =
        subtotal - discount;

    //----------------------------------------
    // GST
    //----------------------------------------

    const gst = items.reduce(
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

            const itemDiscount =
                amount *
                (discountPercentage / 100);

            const taxable =
                amount - itemDiscount;

            const itemGst =
                taxable *
                (gstPercentage / 100);

            return (
                sum +
                itemGst
            );
        },
        0
    );

    //----------------------------------------
    // Grand Total
    //----------------------------------------

    const grandTotal =
        taxableAmount + gst;

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

    return (
        <div className="sales-summary">

            {/* =================================
                Summary Header
            ================================= */}

            <div className="sales-summary-header">

                <div className="sales-summary-title">

                    <div className="sales-summary-icon">

                        <IndianRupee size={18} />

                    </div>

                    <div>

                        <h3>
                            Order Summary
                        </h3>

                        <p>
                            Sales order total
                        </p>

                    </div>

                </div>

            </div>


            {/* =================================
                Summary Values
            ================================= */}

            <div className="sales-summary-content">

                {/* Subtotal */}

                <div className="sales-summary-row">

                    <span>
                        Subtotal
                    </span>

                    <strong>
                        {formatCurrency(
                            subtotal
                        )}
                    </strong>

                </div>


                {/* Discount */}

                <div className="sales-summary-row discount">

                    <span>
                        Discount
                    </span>

                    <strong>
                        - {formatCurrency(
                            discount
                        )}
                    </strong>

                </div>


                {/* Taxable Amount */}

                <div className="sales-summary-row">

                    <span>
                        Taxable Amount
                    </span>

                    <strong>
                        {formatCurrency(
                            taxableAmount
                        )}
                    </strong>

                </div>


                {/* GST */}

                <div className="sales-summary-row">

                    <span>
                        GST
                    </span>

                    <strong>
                        {formatCurrency(
                            gst
                        )}
                    </strong>

                </div>


                {/* Divider */}

                <div className="sales-summary-divider" />


                {/* Grand Total */}

                <div className="sales-summary-grand-total">

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

        </div>
    );
};

export default SalesSummary;