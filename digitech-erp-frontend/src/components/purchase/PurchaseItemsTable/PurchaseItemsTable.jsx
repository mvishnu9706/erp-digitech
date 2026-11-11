import "./PurchaseItemsTable.css";
import Select from "react-select";
import { Trash2 } from "lucide-react";
import { usePurchase } from "../../../context/PurchaseContext";

const PurchaseItemsTable = () => {

    const {
        purchase,
        products,
        addItem,
        removeItem,
        updateItem,
        drawerMode,
    } = usePurchase();

    const disabled = drawerMode === "view";

    const productOptions = products.map(product => ({
        value: product.id,
        label: product.product_name,
        product,
    }));

    return (

        <div className="purchase-items-card">

            <table className="purchase-items-table">

                <thead>

                    <tr>

                        <th className="product-col">
                            Product
                        </th>

                        <th className="stock-col">
                            Stock
                        </th>

                        <th className="qty-col">
                            Qty
                        </th>

                        <th className="price-col">
                            Price
                        </th>

                        <th className="gst-col">
                            GST
                        </th>

                        <th className="discount-col">
                            Discount
                        </th>

                        <th className="total-col">
                            Total
                        </th>

                        <th className="action-col">

                        </th>

                    </tr>

                </thead>

                <tbody>

                    {purchase.items.map((item, index) => (

                        <tr key={index}>

                            {/* Product */}

                            <td className="product-cell">

                                <Select

                                    classNamePrefix="product"

                                    className="product-select"

                                    isDisabled={disabled}

                                    placeholder="Search Product..."

                                    isSearchable

                                    options={productOptions}

                                    value={
                                        productOptions.find(
                                            p =>
                                                Number(p.value) ===
                                                Number(item.product_id)
                                        ) || null
                                    }

                                    onChange={(selected) => {

                                        if (!selected) {

                                            updateItem(
                                                index,
                                                "product_id",
                                                ""
                                            );

                                            return;

                                        }

                                        const product = selected.product;

                                        updateItem(
                                            index,
                                            "product_id",
                                            product.id
                                        );

                                        updateItem(
                                            index,
                                            "purchase_price",
                                            product.cost_price
                                        );

                                        updateItem(
                                            index,
                                            "gst_percentage",
                                            product.gst_percentage
                                        );

                                        updateItem(
                                            index,
                                            "warehouse_id",
                                            product.warehouse_id
                                        );

                                        updateItem(
                                            index,
                                            "unit_id",
                                            product.unit_id
                                        );

                                    }}

                                />

                                <div className="product-cell-actions">

                                    <button

                                        className="inline-add-btn"

                                        disabled={disabled}

                                        onClick={addItem}

                                    >

                                        Add Product

                                    </button>

                                </div>

                            </td>

                            {/* Current Stock */}

                            <td className="stock-cell">

                                {item.current_stock || 0}

                            </td>

                            {/* Quantity */}

                            <td>

                                <input

                                    type="number"

                                    min="1"

                                    disabled={disabled}

                                    value={item.quantity}

                                    onChange={(e) =>
                                        updateItem(
                                            index,
                                            "quantity",
                                            e.target.value
                                        )
                                    }

                                />

                            </td>

                            {/* Purchase Price */}

                            <td>

                                <input

                                    type="number"

                                    disabled={disabled}

                                    value={item.purchase_price}

                                    onChange={(e) =>
                                        updateItem(
                                            index,
                                            "purchase_price",
                                            e.target.value
                                        )
                                    }

                                />

                            </td>

                            {/* GST */}

                            <td>

                                <input

                                    type="number"

                                    disabled={disabled}

                                    value={item.gst_percentage}

                                    onChange={(e) =>
                                        updateItem(
                                            index,
                                            "gst_percentage",
                                            e.target.value
                                        )
                                    }

                                />

                            </td>

                            {/* Discount */}

                            <td>

                                <input

                                    type="number"

                                    disabled={disabled}

                                    value={item.discount_percentage}

                                    onChange={(e) =>
                                        updateItem(
                                            index,
                                            "discount_percentage",
                                            e.target.value
                                        )
                                    }

                                />

                            </td>

                            {/* Total */}

                            <td className="total-cell">

                                ₹{" "}

                                {(
                                    Number(item.quantity || 0) *
                                    Number(item.purchase_price || 0)
                                ).toLocaleString()}

                            </td>

                            {/* Delete */}

                            <td>

                                <button

                                    className="remove-item-btn"

                                    disabled={disabled}

                                    onClick={() => {

                                        if (
                                            purchase.items.length > 1
                                        ) {

                                            removeItem(index);

                                        }

                                    }}

                                >

                                    <Trash2 size={16} />

                                </button>

                            </td>

                        </tr>

                    ))}

                </tbody>

            </table>

        </div>

    );

};

export default PurchaseItemsTable;