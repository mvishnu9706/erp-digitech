import "./ProductInventoryDrawer.css";
import { useEffect, useState } from "react";
import { 
    X, 
    Package, 
    ShoppingCart, 
    FileText, 
    PackagePlus, 
    IndianRupee 
} from "lucide-react";
import { useForm } from "react-hook-form";
import Select from "react-select";
import { toast } from "react-toastify";

import { useProducts } from "../../../context/ProductContext";
import { useWarehouses } from "../../../context/WarehouseContext";
import { useInventory } from "../../../context/InventoryContext"; 

const ProductInventoryDrawer = () => {
    const {
        inventoryDrawerOpen,
        inventoryProduct,
        closeInventoryDrawer,
    } = useProducts();

    const { warehouses } = useWarehouses();
    const { createNewInventory, checkInventory } = useInventory(); // Assuming InventoryContext is globally wrapped

    const [alreadyExists, setAlreadyExists] = useState(false);

    const {
        register,
        handleSubmit,
        reset,
        watch,
        setValue,
        formState: { errors, isSubmitting },
    } = useForm({
        defaultValues: {
            warehouse_id: "",
            rack_location: "",
            current_stock: 0,
            reserved_stock: 0,
            last_purchase_price: 0,
            last_purchase_date: "",
            remarks: "",
        },
    });

    const currentStock = watch("current_stock") || 0;
    const reservedStock = watch("reserved_stock") || 0;
    const availableStock = Number(currentStock) - Number(reservedStock);

    // Auto-fill defaults when opened
    useEffect(() => {
        if (inventoryDrawerOpen && inventoryProduct) {
            setAlreadyExists(false); // Reset check state
            reset({
                warehouse_id: "",
                rack_location: "",
                current_stock: 0,
                reserved_stock: 0,
                // Default to product's cost price if available
                last_purchase_price: inventoryProduct.cost_price || 0,
                // Default to today's date
                last_purchase_date: new Date().toISOString().split("T")[0],
                remarks: "",
            });
        } else {
            reset();
            setAlreadyExists(false);
        }
    }, [inventoryDrawerOpen, inventoryProduct, reset]);

    const onSubmit = async (data) => {
        try {
            // Attach the fixed product ID to the payload
            const payload = {
                ...data,
                product_id: inventoryProduct.id,
            };
            
            await createNewInventory(payload);
            closeInventoryDrawer();
        } catch (error) {
            console.error("Failed to add inventory:", error);
        }
    };

    if (!inventoryDrawerOpen) {
        return null;
    }

    // ==========================================
    // React-Select Options & Styles
    // ==========================================
    const warehouseOptions = warehouses.map((w) => ({
        value: w.id,
        label: w.warehouse_name,
    }));

    const selectStyles = {
        control: (base) => ({
            ...base,
            minHeight: 42,
            borderRadius: 8,
            borderColor: "#d6dbe4",
            boxShadow: "none",
        }),
    };

    // Status Preview helper
    const renderStatusBadge = () => {
        if (availableStock <= 0) return <span className="status-badge error">🔴 OUT OF STOCK</span>;
        if (availableStock <= 5) return <span className="status-badge warning">🟠 LOW STOCK</span>;
        return <span className="status-badge success">🟢 IN STOCK</span>;
    };

    return (
        <div className="drawer-overlay">
            <div className="inventory-drawer">
                
                {/* ============================ */}
                {/* Header */}
                {/* ============================ */}
                <div className="drawer-header">
                    <h2>
                        <PackagePlus size={28} />
                        Add To Inventory
                    </h2>
                    <button type="button" onClick={closeInventoryDrawer}>
                        <X size={22} />
                    </button>
                </div>

                <form onSubmit={handleSubmit(onSubmit)}>
                    <div className="drawer-body">
                        
                        {/* ================================= */}
                        {/* Inventory Information */}
                        {/* ================================= */}
                        <div className="form-section">
                            <h3><Package size={20} /> Inventory Information</h3>
                            <div className="form-grid">
                                
                                {/* Fixed Product Info */}
                                <div className="form-group span-2">
                                    <label>Selected Product</label>
                                    <div className="product-preview" style={{ marginTop: 0 }}>
                                        <img 
                                            src={inventoryProduct?.image_url || "https://placehold.co/60x60/e2e8f0/64748b?text=No+Img"} 
                                            alt="product" 
                                        />
                                        <div className="product-preview-details">
                                            <h4>{inventoryProduct?.product_name}</h4>
                                            <p>
                                                SKU : {inventoryProduct?.sku || "N/A"} | 
                                                Category : {inventoryProduct?.category?.name || "N/A"} | 
                                                Brand : {inventoryProduct?.brand?.name || "N/A"}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* Warehouse */}
                                <div className="form-group">
                                    <label>Warehouse *</label>
                                    <Select
                                        styles={selectStyles}
                                        options={warehouseOptions}
                                        placeholder="Select Warehouse"
                                        autoFocus
                                        value={warehouseOptions.find(o => o.value === watch("warehouse_id")) || null}
                                        onChange={async (selected) => {
                                            if (!selected) {
                                                setValue("warehouse_id", "", { shouldValidate: true });
                                                setAlreadyExists(false);
                                                return;
                                            }

                                            const warehouseId = selected.value;
                                            setValue("warehouse_id", warehouseId, { shouldValidate: true });

                                            try {
                                                const result = await checkInventory(
                                                    inventoryProduct.id,
                                                    warehouseId
                                                );
                                                setAlreadyExists(result.exists);
                                            } catch (error) {
                                                console.error("Inventory check failed", error);
                                            }
                                        }}
                                    />
                                    {/* Hidden input to register with react-hook-form */}
                                    <input 
                                        type="hidden" 
                                        {...register("warehouse_id", { required: "Warehouse is required" })} 
                                    />
                                    <span className="error">{errors.warehouse_id?.message}</span>
                                </div>

                                {/* Rack Location */}
                                <div className="form-group">
                                    <label>Rack Location (Optional)</label>
                                    <input
                                        type="text"
                                        placeholder="Ex : A-01 (Optional)"
                                        {...register("rack_location")}
                                    />
                                    <span className="error">{errors.rack_location?.message}</span>
                                </div>

                                {/* Current Stock */}
                                <div className="form-group">
                                    <label>Current Stock *</label>
                                    <input
                                        type="number"
                                        min="0"
                                        {...register("current_stock", {
                                            valueAsNumber: true,
                                            required: "Current Stock is required",
                                            min: { value: 0, message: "Cannot be negative" },
                                        })}
                                    />
                                    <span className="error">{errors.current_stock?.message}</span>
                                </div>

                                {/* Reserved Stock */}
                                <div className="form-group">
                                    <label>Reserved Stock</label>
                                    <input
                                        type="number"
                                        min="0"
                                        {...register("reserved_stock", {
                                            valueAsNumber: true,
                                            min: { value: 0, message: "Cannot be negative" },
                                        })}
                                    />
                                    <span className="error">{errors.reserved_stock?.message}</span>
                                </div>

                                {/* Available Stock (Read Only) */}
                                <div className="form-group">
                                    <label>Available Stock</label>
                                    <div className="view-value highlight">
                                        {availableStock}
                                    </div>
                                </div>

                                {/* Status Preview */}
                                <div className="form-group">
                                    <label>Status Preview</label>
                                    <div className="view-value no-border">
                                        {renderStatusBadge()}
                                    </div>
                                </div>

                            </div>
                        </div>

                        {/* ================================= */}
                        {/* Purchase Information */}
                        {/* ================================= */}
                        <div className="form-section">
                            <h3><ShoppingCart size={20} /> Purchase Information</h3>
                            <div className="form-grid">
                                
                                {/* Purchase Price */}
                                <div className="form-group">
                                    <label>Purchase Price</label>
                                    <div className="input-with-icon">
                                        <IndianRupee size={16} className="input-icon" />
                                        <input
                                            type="number"
                                            step="0.01"
                                            min="0"
                                            style={{ paddingLeft: "32px" }}
                                            {...register("last_purchase_price", { valueAsNumber: true })}
                                        />
                                    </div>
                                </div>

                                {/* Purchase Date */}
                                <div className="form-group">
                                    <label>Purchase Date</label>
                                    <input
                                        type="date"
                                        {...register("last_purchase_date")}
                                    />
                                </div>
                            </div>
                        </div>

                        {/* ================================= */}
                        {/* Remarks */}
                        {/* ================================= */}
                        <div className="form-section">
                            <h3><FileText size={20} /> Remarks</h3>
                            <div className="form-group">
                                <textarea
                                    rows={4}
                                    placeholder="Enter Remarks"
                                    {...register("remarks")}
                                />
                            </div>
                        </div>
                    </div>

                    {/* ================================= */}
                    {/* Warning Message */}
                    {/* ================================= */}
                    {alreadyExists && (
                        <div className="warning-box" style={{ padding: "12px 24px", color: "#b91c1c", backgroundColor: "#fef2f2", borderTop: "1px solid #fecaca", fontWeight: "600", fontSize: "14px" }}>
                            ⚠ Product already exists in this warehouse.
                        </div>
                    )}

                    {/* ================================= */}
                    {/* Footer */}
                    {/* ================================= */}
                    <div className="drawer-footer">
                        <button
                            type="button"
                            className="btn-cancel"
                            onClick={closeInventoryDrawer}
                        >
                            ✖ Cancel
                        </button>
                        
                        <button
                            type="submit"
                            className="btn-save"
                            disabled={isSubmitting || alreadyExists}
                        >
                            {isSubmitting ? "💾 Saving..." : "💾 Add to Inventory"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ProductInventoryDrawer;