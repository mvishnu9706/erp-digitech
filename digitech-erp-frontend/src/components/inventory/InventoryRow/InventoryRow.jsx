import {
    Eye,
    Pencil,
    Trash2,
} from "lucide-react";

import { useInventory } from "../../../context/InventoryContext";

const InventoryRow = ({ item, index }) => {

    const {
        page,
        size,
        openViewDrawer,
        openEditDrawer,
        removeInventory,
    } = useInventory();

    const getStatusClass = (status) => {

        switch (status) {

            case "IN_STOCK":
                return "status success";

            case "LOW_STOCK":
                return "status warning";

            case "OUT_OF_STOCK":
                return "status danger";

            default:
                return "status";
        }

    };

    return (

        <tr>

            {/* # */}
            <td>
                {((page - 1) * size) + index + 1}
            </td>

            {/* Product */}
            <td>

                <div className="product-cell">

                    <div className="product-name">
                        {item.product?.product_name}
                    </div>

                    <div className="product-sku">
                        {item.product?.sku}
                    </div>

                </div>

            </td>

            {/* Warehouse */}
            <td>
                {item.warehouse?.warehouse_name}
            </td>

            {/* Rack */}
            <td>
                {item.rack_location || "-"}
            </td>

            {/* Available Stock
                Backend field = stock
            */}
            <td>
                {item.stock ?? 0}
            </td>

            {/* Purchase Price */}
            <td>
                ₹ {Number(
                    item.last_purchase_price || 0
                ).toLocaleString()}
            </td>

            {/* Status */}
            <td>

                <span
                    className={getStatusClass(
                        item.stock_status
                    )}
                >

                    {
                        item.stock_status
                            ?.replaceAll("_", " ")
                    }

                </span>

            </td>

            {/* Actions */}
            <td>

                <div className="action-buttons">

                    <button
                        className="btn-view"
                        onClick={() =>
                            openViewDrawer(item)
                        }
                    >
                        <Eye size={18} />
                    </button>

                    <button
                        className="btn-edit"
                        onClick={() =>
                            openEditDrawer(item)
                        }
                    >
                        <Pencil size={18} />
                    </button>

                    <button
                        className="btn-delete"
                        onClick={() =>
                            removeInventory(item.id)
                        }
                    >
                        <Trash2 size={18} />
                    </button>

                </div>

            </td>

        </tr>

    );

};

export default InventoryRow;