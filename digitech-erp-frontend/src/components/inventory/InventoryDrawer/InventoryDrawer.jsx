import "./InventoryDrawer.css";

import { useEffect, useState } from "react";

import {
    X,
    Package,
    ShoppingCart,
    FileText,
    Package2,
    IndianRupee,
} from "lucide-react";

import { useForm } from "react-hook-form";
import Select from "react-select";

import { useInventory } from "../../../context/InventoryContext";
import { useProducts } from "../../../context/ProductContext";
import { useWarehouses } from "../../../context/WarehouseContext";
import {
    checkInventoryExists,
    getInventoryStock,
} from "../../../services/inventoryService";


const InventoryDrawer = () => {

    const {
        drawerOpen,
        drawerMode,
        selectedInventory,
        closeDrawer,
        createNewInventory,
        editInventory,
    } = useInventory();


    const { products } = useProducts();

    const { warehouses } = useWarehouses();

    const [existingInventory, setExistingInventory] = useState(null);
    const [checkingInventory, setCheckingInventory] = useState(false);


    const isView = drawerMode === "view";

    const isEdit = drawerMode === "edit";

    const isAdd = drawerMode === "add";


    const {
        register,
        handleSubmit,
        reset,
        watch,
        setValue,
        formState: {
            errors,
            isSubmitting,
        },
    } = useForm({

        defaultValues: {

            product_id: "",

            warehouse_id: "",

            rack_location: "",

            // ==========================================
            // Only one stock field
            // ==========================================

            stock: 0,

            last_purchase_price: 0,

            last_purchase_date: "",

            remarks: "",
        },

    });


    // =====================================================
    // Watch Stock
    // =====================================================

    const stock = watch("stock") || 0;

    const watchedProductId = watch("product_id");
    const watchedWarehouseId = watch("warehouse_id");

    // =====================================================
    // Local Date Helper
    // =====================================================

    const getTodayDate = () => {
        const today = new Date();

        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, "0");
        const day = String(today.getDate()).padStart(2, "0");

        return `${year}-${month}-${day}`;
    };


    // =====================================================
    // Reset Form
    // =====================================================

    useEffect(() => {

        if (selectedInventory) {

            setExistingInventory(
                selectedInventory.id
                    ? { id: selectedInventory.id }
                    : null
            );

            reset({
                product_id:
                    selectedInventory.product?.id || "",

                warehouse_id:
                    selectedInventory.warehouse?.id || "",

                rack_location:
                    selectedInventory.rack_location || "",

                stock:
                    selectedInventory.stock || 0,

                last_purchase_price:
                    selectedInventory.last_purchase_price || 0,

                last_purchase_date:
                    selectedInventory.last_purchase_date || "",

                remarks:
                    selectedInventory.remarks || "",
            });

        } else {

            setExistingInventory(null);

            reset({
                product_id: "",
                warehouse_id: "",
                rack_location: "",
                stock: 0,
                last_purchase_price: 0,
                last_purchase_date: getTodayDate(),
                remarks: "",
            });

        }

    }, [
        selectedInventory,
        reset,
        drawerOpen,
    ]);


    // =====================================================
    // Load Existing Stock For Product + Warehouse
    // =====================================================

    useEffect(() => {

        if (!isAdd) {
            return;
        }

        if (!watchedProductId || !watchedWarehouseId) {
            setExistingInventory(null);
            setCheckingInventory(false);

            setValue("stock", 0, {
                shouldValidate: true,
                shouldDirty: false,
            });

            return;
        }

        let cancelled = false;

        const loadExistingInventory = async () => {

            try {
                setCheckingInventory(true);

                const productId = Number(watchedProductId);
                const warehouseId = Number(watchedWarehouseId);

                // First find whether Product + Warehouse already exists.
                const checkResponse =
                    await checkInventoryExists(
                        productId,
                        warehouseId
                    );

                const checkResult = checkResponse?.data || {};

                console.log(
                    "Inventory check response:",
                    checkResult
                );

                if (cancelled) {
                    return;
                }

                if (
                    checkResult.exists === true &&
                    checkResult.inventory_id
                ) {

                    const inventoryId = Number(
                        checkResult.inventory_id
                    );

                    setExistingInventory({
                        id: inventoryId,
                    });

                    // The /inventory/check endpoint intentionally returns
                    // the ID, not the stock. Get the actual stock separately.
                    const stockResponse =
                        await getInventoryStock(
                            productId,
                            warehouseId
                        );

                    const stockResult =
                        stockResponse?.data || {};

                    const currentStock = Number(
                        stockResult.stock ?? 0
                    );

                    console.log(
                        "Current inventory stock:",
                        currentStock
                    );

                    if (cancelled) {
                        return;
                    }

                    setValue(
                        "stock",
                        currentStock,
                        {
                            shouldValidate: true,
                            shouldDirty: false,
                        }
                    );

                    // Use today's date for an inventory update.
                    setValue(
                        "last_purchase_date",
                        getTodayDate()
                    );

                } else {

                    setExistingInventory(null);

                    setValue(
                        "stock",
                        0,
                        {
                            shouldValidate: true,
                            shouldDirty: false,
                        }
                    );

                    setValue(
                        "last_purchase_date",
                        getTodayDate()
                    );
                }

            } catch (error) {

                console.error(
                    "Failed to load current inventory stock:",
                    error
                );

                if (!cancelled) {
                    setExistingInventory(null);

                    setValue(
                        "stock",
                        0,
                        {
                            shouldValidate: true,
                        }
                    );
                }

            } finally {

                if (!cancelled) {
                    setCheckingInventory(false);
                }
            }
        };

        loadExistingInventory();

        return () => {
            cancelled = true;
        };

    }, [
        isAdd,
        watchedProductId,
        watchedWarehouseId,
        setValue,
    ]);


    // =====================================================
    // Submit
    // =====================================================

    const onSubmit = async (data) => {

        try {

            const payload = {
                product_id: Number(data.product_id),
                warehouse_id: Number(data.warehouse_id),
                rack_location: data.rack_location,
                stock: Number(data.stock),
                last_purchase_price:
                    Number(data.last_purchase_price || 0),
                last_purchase_date:
                    data.last_purchase_date || getTodayDate(),
                remarks: data.remarks || "",
            };

            // ---------------------------------------------
            // Edit an existing inventory record
            // ---------------------------------------------
            if (isEdit) {

                await editInventory(
                    selectedInventory.id,
                    {
                        rack_location: payload.rack_location,
                        stock: payload.stock,
                        last_purchase_price:
                            payload.last_purchase_price,
                        last_purchase_date:
                            payload.last_purchase_date,
                        remarks: payload.remarks,
                    }
                );

                return;
            }

            // ---------------------------------------------
            // Add mode + existing Product/Warehouse
            // Update instead of POSTing a duplicate.
            // ---------------------------------------------
            if (existingInventory?.id) {

                await editInventory(
                    existingInventory.id,
                    {
                        rack_location: payload.rack_location,
                        stock: payload.stock,
                        last_purchase_price:
                            payload.last_purchase_price,
                        last_purchase_date:
                            payload.last_purchase_date,
                        remarks: payload.remarks,
                    }
                );

                return;
            }

            // ---------------------------------------------
            // New Product/Warehouse combination
            // Create a new inventory record.
            // ---------------------------------------------
            await createNewInventory(payload);

        } catch (error) {

            console.error(
                "Inventory save failed:",
                error
            );
        }
    };


    // =====================================================
    // Drawer Visibility
    // =====================================================

    if (!drawerOpen) {

        return null;

    }


    // =====================================================
    // Product Options
    // =====================================================

    const productOptions = products.map(
        (product) => ({

            value: product.id,

            label: product.product_name,

            sku: product.sku,

            category:
                product.category?.name ||
                "Uncategorized",

            brand:
                product.brand?.name ||
                "No Brand",

            image:
                product.image_url ||
                "https://placehold.co/60x60/e2e8f0/64748b?text=No+Img",

        })
    );


    // =====================================================
    // Warehouse Options
    // =====================================================

    const warehouseOptions = warehouses.map(
        (warehouse) => ({

            value: warehouse.id,

            label:
                warehouse.warehouse_name,

        })
    );


    // =====================================================
    // Select Styles
    // =====================================================

    const selectStyles = {

        control: (base) => ({

            ...base,

            minHeight: 42,

            borderRadius: 8,

            borderColor: "#d6dbe4",

            boxShadow: "none",

        }),

    };


    // =====================================================
    // Selected Product
    // =====================================================

    const selectedProductDetails =
        productOptions.find(
            (product) =>
                product.value === watchedProductId
        );


    // =====================================================
    // Date Formatting
    // =====================================================

    const formatDate = (dateString) => {

        if (!dateString) {

            return "N/A";

        }

        return new Date(
            dateString
        ).toLocaleDateString(
            "en-GB",
            {
                day: "2-digit",
                month: "short",
                year: "numeric",
            }
        );

    };


    // =====================================================
    // Status Badge
    // =====================================================

    const renderStatusBadge = () => {

        const currentStock =
            isView
                ? Number(
                    selectedInventory?.stock || 0
                )
                : Number(stock || 0);


        if (currentStock <= 0) {

            return (
                <span className="status-badge error">
                    🔴 OUT OF STOCK
                </span>
            );

        }


        if (currentStock <= 5) {

            return (
                <span className="status-badge warning">
                    🟠 LOW STOCK
                </span>
            );

        }


        return (
            <span className="status-badge success">
                🟢 IN STOCK
            </span>
        );

    };


    return (

        <div className="drawer-overlay">

            <div className="inventory-drawer">


                {/* =================================================
                    Header
                ================================================= */}

                <div className="drawer-header">

                    <h2>

                        <Package2 size={28} />

                        {
                            isAdd
                                ? " Add Inventory"
                                : isEdit
                                    ? " Edit Inventory"
                                    : " View Inventory"
                        }

                    </h2>


                    <button
                        type="button"
                        onClick={closeDrawer}
                    >

                        <X size={22} />

                    </button>

                </div>


                {/* =================================================
                    Form
                ================================================= */}

                <form
                    onSubmit={handleSubmit(onSubmit)}
                >

                    <div className="drawer-body">


                        {/* =================================================
                            Inventory Information
                        ================================================= */}

                        <div className="form-section">

                            <h3>

                                <Package size={20} />

                                Inventory Information

                            </h3>


                            <div className="form-grid">


                                {/* =================================================
                                    Product
                                ================================================= */}

                                <div className="form-group span-2">

                                    <label>
                                        Product *
                                    </label>


                                    {isView ? (

                                        <div className="view-value">

                                            {
                                                selectedInventory
                                                    ?.product
                                                    ?.product_name
                                                || "N/A"
                                            }

                                        </div>

                                    ) : (

                                        <Select
                                            classNamePrefix="select"

                                            styles={
                                                selectStyles
                                            }

                                            options={
                                                productOptions
                                            }

                                            placeholder={
                                                "Search Product..."
                                            }

                                            isClearable

                                            autoFocus

                                            value={
                                                productOptions.find(
                                                    (option) =>
                                                        option.value ===
                                                        watchedProductId
                                                ) || null
                                            }

                                            onChange={(
                                                selected
                                            ) => {

                                                setValue(
                                                    "product_id",
                                                    selected
                                                        ? selected.value
                                                        : "",
                                                    {
                                                        shouldValidate:
                                                            true,
                                                    }
                                                );

                                            }}

                                        />

                                    )}


                                    <span className="error">

                                        {
                                            errors
                                                .product_id
                                                ?.message
                                        }

                                    </span>


                                    {/* =================================================
                                        Product Preview
                                    ================================================= */}

                                    {
                                        (
                                            selectedProductDetails
                                            || isView
                                        ) && (

                                            <div className="product-preview">

                                                <img
                                                    src={
                                                        isView
                                                            ? (
                                                                selectedInventory
                                                                    ?.product
                                                                    ?.image_url
                                                                ||
                                                                "https://placehold.co/60x60/e2e8f0/64748b?text=No+Img"
                                                            )
                                                            : selectedProductDetails
                                                                ?.image
                                                    }
                                                    alt="product"
                                                />


                                                <div className="product-preview-details">

                                                    <h4>

                                                        {
                                                            isView
                                                                ? selectedInventory
                                                                    ?.product
                                                                    ?.product_name
                                                                : selectedProductDetails
                                                                    ?.label
                                                        }

                                                    </h4>


                                                    <p>

                                                        SKU :{" "}

                                                        {
                                                            isView
                                                                ? selectedInventory
                                                                    ?.product
                                                                    ?.sku
                                                                : selectedProductDetails
                                                                    ?.sku
                                                        }

                                                        {" | "}

                                                        Category :{" "}

                                                        {
                                                            isView
                                                                ? selectedInventory
                                                                    ?.product
                                                                    ?.category
                                                                    ?.name
                                                                : selectedProductDetails
                                                                    ?.category
                                                        }

                                                        {" | "}

                                                        Brand :{" "}

                                                        {
                                                            isView
                                                                ? selectedInventory
                                                                    ?.product
                                                                    ?.brand
                                                                    ?.name
                                                                : selectedProductDetails
                                                                    ?.brand
                                                        }

                                                    </p>

                                                </div>

                                            </div>

                                        )
                                    }

                                </div>


                                {/* =================================================
                                    Warehouse
                                ================================================= */}

                                <div className="form-group">

                                    <label>
                                        Warehouse *
                                    </label>


                                    {isView ? (

                                        <div className="view-value">

                                            {
                                                selectedInventory
                                                    ?.warehouse
                                                    ?.warehouse_name
                                                || "N/A"
                                            }

                                        </div>

                                    ) : (

                                        <Select
                                            classNamePrefix="select"

                                            styles={
                                                selectStyles
                                            }

                                            options={
                                                warehouseOptions
                                            }

                                            placeholder={
                                                "Select Warehouse"
                                            }

                                            value={
                                                warehouseOptions.find(
                                                    (option) =>
                                                        option.value ===
                                                        watch(
                                                            "warehouse_id"
                                                        )
                                                ) || null
                                            }

                                            onChange={(
                                                selected
                                            ) => {

                                                setValue(
                                                    "warehouse_id",
                                                    selected
                                                        ? selected.value
                                                        : "",
                                                    {
                                                        shouldValidate:
                                                            true,
                                                    }
                                                );

                                            }}

                                        />

                                    )}


                                    <span className="error">

                                        {
                                            errors
                                                .warehouse_id
                                                ?.message
                                        }

                                    </span>

                                </div>


                                {/* =================================================
                                    Rack Location
                                ================================================= */}

                                <div className="form-group">

                                    <label>
                                        Rack Location *
                                    </label>


                                    {isView ? (

                                        <div className="view-value">

                                            {
                                                selectedInventory
                                                    ?.rack_location
                                                || "N/A"
                                            }

                                        </div>

                                    ) : (

                                        <input
                                            type="text"
                                            placeholder="Ex : A-01"
                                            {...register(
                                                "rack_location",
                                                {
                                                    required:
                                                        "Rack Location is required",
                                                }
                                            )}
                                        />

                                    )}


                                    <span className="error">

                                        {
                                            errors
                                                .rack_location
                                                ?.message
                                        }

                                    </span>

                                </div>


                                {/* =================================================
                                    AVAILABLE STOCK
                                    =================================================
                                    This is the ONLY stock field.
                                    Backend field = stock.
                                    ================================================= */}

                                <div className="form-group">

                                    <label>
                                        Available Stock *
                                    </label>


                                    {isView ? (

                                        <div className="view-value highlight">

                                            {
                                                selectedInventory
                                                    ?.stock ?? 0
                                            }

                                        </div>

                                    ) : (

                                        <input

                                            type="number"

                                            min="0"

                                            {...register(
                                                "stock",
                                                {
                                                    valueAsNumber:
                                                        true,

                                                    required:
                                                        "Available Stock is required",

                                                    min: {
                                                        value: 0,

                                                        message:
                                                            "Cannot be negative",
                                                    },

                                                }
                                            )}

                                        />

                                    )}


                                    <span className="error">

                                        {
                                            errors
                                                .stock
                                                ?.message
                                        }

                                    </span>

                                </div>


                                {/* =================================================
                                    Stock Status
                                ================================================= */}

                                {isView && (

                                    <div className="form-group">

                                        <label>
                                            Stock Status
                                        </label>


                                        <div className="view-value no-border">

                                            {
                                                renderStatusBadge()
                                            }

                                        </div>

                                    </div>

                                )}

                            </div>

                        </div>


                        {/* =================================================
                            Purchase Information
                        ================================================= */}

                        <div className="form-section">

                            <h3>

                                <ShoppingCart size={20} />

                                Purchase Information

                            </h3>


                            <div className="form-grid">


                                {/* Purchase Price */}

                                <div className="form-group">

                                    <label>
                                        Purchase Price
                                    </label>


                                    {isView ? (

                                        <div className="view-value">

                                            <IndianRupee
                                                size={16}
                                                className="text-muted"
                                            />

                                            {
                                                Number(
                                                    selectedInventory
                                                        ?.last_purchase_price
                                                    || 0
                                                ).toLocaleString(
                                                    "en-IN"
                                                )
                                            }

                                        </div>

                                    ) : (

                                        <div className="input-with-icon">

                                            <IndianRupee
                                                size={16}
                                                className="input-icon"
                                            />

                                            <input
                                                type="number"
                                                step="0.01"
                                                min="0"
                                                style={{
                                                    paddingLeft:
                                                        "32px",
                                                }}
                                                {...register(
                                                    "last_purchase_price",
                                                    {
                                                        valueAsNumber:
                                                            true,
                                                    }
                                                )}
                                            />

                                        </div>

                                    )}

                                </div>


                                {/* Purchase Date */}

                                <div className="form-group">

                                    <label>
                                        Purchase Date
                                    </label>


                                    {isView ? (

                                        <div className="view-value">

                                            {
                                                formatDate(
                                                    selectedInventory
                                                        ?.last_purchase_date
                                                )
                                            }

                                        </div>

                                    ) : (

                                        <input
                                            type="date"
                                            {...register(
                                                "last_purchase_date"
                                            )}
                                        />

                                    )}

                                </div>

                            </div>

                        </div>


                        {/* =================================================
                            Remarks
                        ================================================= */}

                        <div className="form-section">

                            <h3>

                                <FileText size={20} />

                                Remarks

                            </h3>


                            <div className="form-group">

                                {isView ? (

                                    <div
                                        className="view-value"
                                        style={{
                                            minHeight:
                                                "90px",

                                            alignItems:
                                                "flex-start",
                                        }}
                                    >

                                        {
                                            selectedInventory
                                                ?.remarks
                                            || "No remarks"
                                        }

                                    </div>

                                ) : (

                                    <textarea
                                        rows={4}
                                        placeholder="Enter Remarks"
                                        {...register(
                                            "remarks"
                                        )}
                                    />

                                )}

                            </div>

                        </div>

                    </div>


                    {/* =================================================
                        Footer
                    ================================================= */}

                    <div className="drawer-footer">

                        <button
                            type="button"
                            className="btn-cancel"
                            onClick={closeDrawer}
                        >
                            ✖ Cancel
                        </button>


                        {!isView && (

                            <button
                                type="submit"
                                className="btn-save"
                                disabled={isSubmitting}
                            >

                                {
                                    isSubmitting
                                        ? "💾 Saving..."
                                        : isEdit
                                            ? "💾 Update Inventory"
                                            : existingInventory?.id
                                                ? "💾 Update Inventory"
                                                : "💾 Add Inventory"
                                }

                            </button>

                        )}

                    </div>

                </form>

            </div>

        </div>

    );

};


export default InventoryDrawer;