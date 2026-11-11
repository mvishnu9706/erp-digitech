import "./PurchaseSummary.css";
import { usePurchase } from "../../../context/PurchaseContext";

const PurchaseSummary = () => {

    const { purchase } = usePurchase();

    const subtotal = purchase.items.reduce(
        (sum, item) =>
            sum +
            Number(item.quantity || 0) *
            Number(item.purchase_price || 0),
        0
    );

    const discount = purchase.items.reduce(
        (sum, item) =>
            sum +
            (
                Number(item.quantity || 0) *
                Number(item.purchase_price || 0) *
                Number(item.discount_percentage || 0)
            ) / 100,
        0
    );

    const taxable = subtotal - discount;

    const gst = purchase.items.reduce(
        (sum, item) => {

            const amount =
                Number(item.quantity || 0) *
                Number(item.purchase_price || 0);

            const disc =
                amount *
                Number(item.discount_percentage || 0) /
                100;

            return (
                sum +
                (
                    (amount - disc) *
                    Number(item.gst_percentage || 0)
                ) / 100
            );

        },
        0
    );

    const grandTotal = taxable + gst;

    return (

        <div className="purchase-summary-card">

            <h3>

                Purchase Summary

            </h3>

            <div className="summary-row">

                <span>Total Items</span>

                <strong>

                    {purchase.items.length}

                </strong>

            </div>

            <div className="summary-row">

                <span>Subtotal</span>

                <strong>

                    ₹ {subtotal.toLocaleString()}

                </strong>

            </div>

            <div className="summary-row">

                <span>Discount</span>

                <strong>

                    ₹ {discount.toLocaleString()}

                </strong>

            </div>

            <div className="summary-row">

                <span>GST</span>

                <strong>

                    ₹ {gst.toLocaleString()}

                </strong>

            </div>

            <hr />

            <div className="summary-row grand-total">

                <span>

                    Grand Total

                </span>

                <strong>

                    ₹ {grandTotal.toLocaleString()}

                </strong>

            </div>

        </div>

    );

};

export default PurchaseSummary;