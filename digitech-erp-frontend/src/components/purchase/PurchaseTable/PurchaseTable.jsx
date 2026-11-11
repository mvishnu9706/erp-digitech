import "./PurchaseTable.css";

import {
    Eye, Pencil, Trash2,
} from "lucide-react";

import { usePurchase } from "../../../context/PurchaseContext";

const PurchaseTable = () => {

    const {
        purchaseOrders,
        loading,
        openViewDrawer,
        openEditDrawer,
        deletePurchase,
    } = usePurchase();

    if (loading) {
        return (
            <div className="purchase-loading">
                Loading Purchase Orders...
            </div>
        );
    }

    return (
        <div className="purchase-table-container">
            <table className="purchase-table">
                <thead>
                    <tr>
                        <th>PO Number</th>
                        <th>Supplier</th>
                        <th>Warehouse</th>
                        <th>Purchase Date</th>
                        <th>Created On</th>
                        <th>Total</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {
                        purchaseOrders.length === 0 ? (
                            <tr>
                                <td
                                    colSpan="7"
                                    className="empty-row"
                                >
                                    No Purchase Orders Found
                                </td>
                            </tr>
                        ) : (
                            purchaseOrders.map((purchase) => (
                                <tr key={purchase.id}>
                                    <td>
                                        {purchase.po_number || "-"}
                                    </td>
                                    <td>
                                        {purchase.supplier_name || "-"}
                                    </td>
                                    <td>
                                        {purchase.warehouse_name || "-"}
                                    </td>
                                    <td>
                                        {purchase.po_date
                                            ? new Date(purchase.po_date).toLocaleDateString()
                                            : "-"}
                                    </td>
                                    <td>
                                        {purchase.created_at
                                            ? new Date(purchase.created_at).toLocaleDateString()
                                            : "-"}
                                    </td>
                                    <td>
                                        ₹ {Number(purchase.grand_total || 0).toLocaleString()}
                                    </td>
                                    <td>
                                        <div className="purchase-actions">
                                            <button
                                                className="view-btn"
                                                onClick={() => openViewDrawer(purchase)}
                                            >
                                                <Eye size={16} />
                                            </button>
                                            <button
                                                className="edit-btn"
                                                onClick={() => openEditDrawer(purchase)}
                                            >
                                                <Pencil size={16} />
                                            </button>
                                            <button
                                                className="delete-btn"
                                                onClick={() => {
                                                    if (window.confirm("Delete this Purchase Order?")) {
                                                        deletePurchase(purchase.id);
                                                    }
                                                }}>
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )
                    }
                </tbody>
            </table>
        </div>
    );
};

export default PurchaseTable;