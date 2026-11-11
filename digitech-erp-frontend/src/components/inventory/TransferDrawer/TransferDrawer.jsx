import "./TransferDrawer.css";

import { useEffect, useState } from "react";
import { X } from "lucide-react";
import Select from "react-select";

import { useInventory } from "../../../context/InventoryContext";
import { useWarehouses } from "../../../context/WarehouseContext";
import { useProducts } from "../../../context/ProductContext";

const TransferDrawer = () => {
    const {
        transferDrawer,
        closeTransferDrawer,
        transferStock,
        inventory,
        selectedTransfer,
        getCurrentInventoryStock,
    } = useInventory();

    const {
        warehouses = [],
    } = useWarehouses();

    const {
        products = [],
    } = useProducts();

    // ==========================================
    // Form
    // ==========================================

    const [form, setForm] = useState({
        product_id: "",
        from_warehouse_id: "",
        to_warehouse_id: "",
        reference_by: "",
        quantity: "",
        remarks: "",
    });

    // ==========================================
    // Available Stock
    // ==========================================

    const [availableStock, setAvailableStock] = useState(0);

    const [stockLoading, setStockLoading] = useState(false);

    // ==========================================
    // Initialize From Selected Transfer
    // ==========================================

    useEffect(() => {
        if (!transferDrawer) {
            return;
        }

        if (!selectedTransfer) {
            return;
        }

        setForm((prev) => ({
            ...prev,

            product_id:
                selectedTransfer.product_id ??
                "",

            from_warehouse_id:
                selectedTransfer.warehouse_id ??
                "",

            to_warehouse_id:
                "",

            reference_by:
                selectedTransfer.reference_by ??
                "",

            quantity: "",

            remarks:
                selectedTransfer.remarks ??
                "",
        }));

        // ==========================================
        // Get Stock Directly From Selected Transfer
        // ==========================================

        const rowStock = Number(
            selectedTransfer.available ??
            selectedTransfer.available_stock ??
            selectedTransfer.quantity ??
            0
        );

        setAvailableStock(rowStock);

    }, [
        transferDrawer,
        selectedTransfer,
    ]);

    // ==========================================
    // Get Accurate Stock When Product + Warehouse
    // Are Selected
    // ==========================================

    useEffect(() => {
        if (!transferDrawer) {
            return;
        }

        if (!form.product_id) {
            setAvailableStock(0);
            return;
        }

        if (!form.from_warehouse_id) {
            setAvailableStock(0);
            return;
        }

        const loadStock = async () => {
            try {
                setStockLoading(true);

                const response =
                    await getCurrentInventoryStock(
                        Number(form.product_id),
                        Number(form.from_warehouse_id)
                    );

                /*
                 * Backend may return:
                 *
                 * { stock: 36 }
                 *
                 * or
                 *
                 * { available: 36 }
                 *
                 * or
                 *
                 * { available_stock: 36 }
                 */

                const stock = Number(
                    response?.available ??
                    response?.available_stock ??
                    response?.stock ??
                    0
                );

                /*
                 * Only replace the selected-row value
                 * when the API actually gives a value.
                 */

                if (stock >= 0) {
                    setAvailableStock(stock);
                }

            } catch (error) {
                console.error(
                    "Failed to load transfer stock:",
                    error
                );

                /*
                 * Keep the stock already obtained from
                 * selectedTransfer instead of forcing 0.
                 */

            } finally {
                setStockLoading(false);
            }
        };

        loadStock();

    }, [
        transferDrawer,
        form.product_id,
        form.from_warehouse_id,
        getCurrentInventoryStock,
    ]);

    // ==========================================
    // Input Change
    // ==========================================

    const handleChange = (e) => {
        const {
            name,
            value,
        } = e.target;

        setForm((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    // ==========================================
    // Product Change
    // ==========================================

    const handleProductChange = (selected) => {
        setForm((prev) => ({
            ...prev,

            product_id:
                selected
                    ? selected.value
                    : "",

            from_warehouse_id: "",

            quantity: "",
        }));

        setAvailableStock(0);
    };

    // ==========================================
    // From Warehouse Change
    // ==========================================

    const handleFromWarehouseChange = (selected) => {
        setForm((prev) => ({
            ...prev,

            from_warehouse_id:
                selected
                    ? selected.value
                    : "",

            quantity: "",
        }));
    };

    // ==========================================
    // To Warehouse Change
    // ==========================================

    const handleToWarehouseChange = (selected) => {
        setForm((prev) => ({
            ...prev,

            to_warehouse_id:
                selected
                    ? selected.value
                    : "",
        }));
    };

    // ==========================================
    // Transfer
    // ==========================================

    const handleTransfer = async () => {

        if (!form.product_id) {
            alert("Select Product");
            return;
        }

        if (!form.from_warehouse_id) {
            alert("Select From Warehouse");
            return;
        }

        if (!form.to_warehouse_id) {
            alert("Select To Warehouse");
            return;
        }

        if (
            Number(form.from_warehouse_id) ===
            Number(form.to_warehouse_id)
        ) {
            alert(
                "From and To Warehouse cannot be the same."
            );
            return;
        }

        const quantity = Number(form.quantity);

        if (!quantity || quantity <= 0) {
            alert("Enter valid quantity.");
            return;
        }

        if (quantity > availableStock) {
            alert(
                `Insufficient Available Stock. Available stock: ${availableStock}`
            );
            return;
        }

        try {

            await transferStock({

                product_id:
                    Number(form.product_id),

                from_warehouse_id:
                    Number(form.from_warehouse_id),

                to_warehouse_id:
                    Number(form.to_warehouse_id),

                reference_by:
                    form.reference_by?.trim() || null,

                quantity,

                remarks:
                    form.remarks,
            });

            setForm({
                product_id: "",
                from_warehouse_id: "",
                to_warehouse_id: "",
                reference_by: "",
                quantity: "",
                remarks: "",
            });

            setAvailableStock(0);

        } catch (error) {

            console.error(
                "STOCK TRANSFER ERROR:",
                error
            );
        }
    };

    // ==========================================
    // Drawer
    // ==========================================

    if (!transferDrawer) {
        return null;
    }

    // ==========================================
    // Options
    // ==========================================

    const productOptions = products.map(
        (product) => ({
            value: product.id,
            label: product.product_name,
        })
    );

    const warehouseOptions = warehouses.map(
        (warehouse) => ({
            value: warehouse.id,
            label: warehouse.warehouse_name,
        })
    );

    // ==========================================
    // Select Styles
    // ==========================================

    const selectStyles = {

        control: (base) => ({
            ...base,

            minHeight: 42,

            borderRadius: 8,

            borderColor: "#d1d5db",

            boxShadow: "none",

            "&:hover": {
                borderColor: "#3b82f6",
            },
        }),

        menuPortal: (base) => ({
            ...base,

            zIndex: 9999,
        }),
    };

    // ==========================================
    // Render
    // ==========================================

    return (

        <div className="transfer-overlay">

            <div className="transfer-drawer">

                {/* ==================================
                    Header
                ================================== */}

                <div className="transfer-header">

                    <h2>
                        Stock Transfer
                    </h2>

                    <button
                        type="button"
                        onClick={closeTransferDrawer}
                    >
                        <X size={20} />
                    </button>

                </div>

                {/* ==================================
                    Body
                ================================== */}

                <div className="transfer-body">

                    {/* ==================================
                        Product
                    ================================== */}

                    <div className="form-group">

                        <label>
                            Product
                        </label>

                        <Select
                            styles={selectStyles}

                            options={productOptions}

                            placeholder="Search Product..."

                            isClearable

                            menuPortalTarget={
                                document.body
                            }

                            value={
                                productOptions.find(
                                    (option) =>
                                        Number(
                                            option.value
                                        ) ===
                                        Number(
                                            form.product_id
                                        )
                                ) || null
                            }

                            onChange={
                                handleProductChange
                            }
                        />

                    </div>

                    {/* ==================================
                        From Warehouse
                    ================================== */}

                    <div className="form-group">

                        <label>
                            From Warehouse
                        </label>

                        <Select
                            styles={selectStyles}

                            options={warehouseOptions}

                            placeholder="Select Warehouse"

                            isClearable

                            menuPortalTarget={
                                document.body
                            }

                            value={
                                warehouseOptions.find(
                                    (option) =>
                                        Number(
                                            option.value
                                        ) ===
                                        Number(
                                            form.from_warehouse_id
                                        )
                                ) || null
                            }

                            onChange={
                                handleFromWarehouseChange
                            }
                        />

                    </div>

                    {/* ==================================
                        To Warehouse
                    ================================== */}

                    <div className="form-group">

                        <label>
                            To Warehouse
                        </label>

                        <Select
                            styles={selectStyles}

                            options={warehouseOptions}

                            placeholder="Select Warehouse"

                            isClearable

                            menuPortalTarget={
                                document.body
                            }

                            value={
                                warehouseOptions.find(
                                    (option) =>
                                        Number(
                                            option.value
                                        ) ===
                                        Number(
                                            form.to_warehouse_id
                                        )
                                ) || null
                            }

                            onChange={
                                handleToWarehouseChange
                            }
                        />

                    </div>

                    {/* ==================================
                        Reference By
                    ================================== */}

                    <div className="form-group">

                        <label>
                            Reference By
                        </label>

                        <input
                            type="text"
                            name="reference_by"
                            value={
                                form.reference_by
                            }
                            onChange={
                                handleChange
                            }
                            placeholder="Enter Reference..."
                        />

                    </div>

                    {/* ==================================
                        Available Stock
                    ================================== */}

                    <div className="stock-info">

                        <strong>
                            Available Stock :
                        </strong>

                        {stockLoading ? (
                            <span>
                                {" "}
                                Loading...
                            </span>
                        ) : (
                            <span>
                                {" "}
                                {availableStock}
                            </span>
                        )}

                    </div>

                    {/* ==================================
                        Quantity
                    ================================== */}

                    <div className="form-group">

                        <label>
                            Quantity
                        </label>

                        <input
                            type="number"

                            name="quantity"

                            value={
                                form.quantity
                            }

                            onChange={
                                handleChange
                            }

                            placeholder="Transfer Quantity"

                            min="1"

                            max={
                                availableStock > 0
                                    ? availableStock
                                    : undefined
                            }
                        />

                    </div>

                    {/* ==================================
                        Remarks
                    ================================== */}

                    <div className="form-group">

                        <label>
                            Remarks
                        </label>

                        <textarea
                            rows={4}

                            name="remarks"

                            value={
                                form.remarks
                            }

                            onChange={
                                handleChange
                            }
                        />

                    </div>

                    {/* ==================================
                        Footer
                    ================================== */}

                    <div className="transfer-footer">

                        <button
                            type="button"

                            className="btn-cancel"

                            onClick={
                                closeTransferDrawer
                            }
                        >
                            Cancel
                        </button>

                        <button
                            type="button"

                            className="btn-transfer"

                            onClick={
                                handleTransfer
                            }

                            disabled={
                                stockLoading ||
                                availableStock <= 0
                            }
                        >
                            Transfer Stock
                        </button>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default TransferDrawer;