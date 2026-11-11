import "./PurchaseDetails.css";

const PurchaseDetails = ({ purchase }) => {

    if (!purchase) return null;

    return (

        <div className="purchase-details">

            <div className="detail-row">

                <span>PO Number</span>

                <strong>{purchase.po_number}</strong>

            </div>

            <div className="detail-row">

                <span>Supplier</span>

                <strong>{purchase.supplier_name}</strong>

            </div>

            <div className="detail-row">

                <span>Warehouse</span>

                <strong>{purchase.warehouse_name}</strong>

            </div>

            <div className="detail-row">

                <span>Date</span>

                <strong>{purchase.po_date}</strong>

            </div>

            <div className="detail-row">

                <span>Status</span>

                <strong>{purchase.status}</strong>

            </div>

            <div className="detail-row">

                <span>Total</span>

                <strong>

                    ₹ {Number(
                        purchase.grand_total
                    ).toLocaleString()}

                </strong>

            </div>

        </div>

    );

};

export default PurchaseDetails;