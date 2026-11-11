import "./SalesItemsTable.css";

import {
    Package,
    Trash2,
    Plus,
    ChevronDown,
    List,
    X,
} from "lucide-react";

import {
    useEffect,
    useRef,
    useState,
} from "react";

import { createPortal } from "react-dom";

import { useSales } from "../../../context/SalesContext";

import SalesService from "../../../services/SalesService";


const SalesItemsTable = () => {

    const {
        sale,
        products,
        updateField,
    } = useSales();


    // =====================================================
    // STATE
    // =====================================================

    const [openProductRow, setOpenProductRow] =
        useState(null);

    const [productSearch, setProductSearch] =
        useState("");

    const searchRef =
        useRef(null);

    const dropdownRef =
        useRef(null);

    const [dropdownPosition, setDropdownPosition] =
        useState({
            top: 0,
            left: 0,
            width: 360,
        });


    // =====================================================
    // SERIAL NUMBER MODAL
    // =====================================================

    const [serialModalRow, setSerialModalRow] =
        useState(null);

    const [serialDraft, setSerialDraft] =
        useState([]);


    // =====================================================
    // ITEMS
    // =====================================================

    const items =
        Array.isArray(sale?.items)
            ? sale.items
            : [];


    // =====================================================
    // PRODUCTS
    // =====================================================

    const availableProducts =
        Array.isArray(products)
            ? products
            : [];


    // =====================================================
    // CURRENT WAREHOUSE
    // =====================================================

    const selectedWarehouseId =
        sale?.warehouse_id
            ? Number(sale.warehouse_id)
            : null;


    // =====================================================
    // DROPDOWN POSITION
    // =====================================================

    const updateDropdownPosition = () => {

        if (!searchRef.current) {
            return;
        }

        const rect =
            searchRef.current.getBoundingClientRect();

        const availableWidth =
            window.innerWidth -
            rect.left -
            20;

        setDropdownPosition({
            top: rect.bottom + 6,
            left: rect.left,
            width: Math.min(
                Math.max(
                    rect.width,
                    360
                ),
                Math.max(
                    availableWidth,
                    280
                )
            ),
        });
    };


    // =====================================================
    // CLOSE DROPDOWN WHEN CLICKING OUTSIDE
    // =====================================================

    useEffect(() => {

        const handleClickOutside = (event) => {

            const clickedInsideSearch =
                searchRef.current &&
                searchRef.current.contains(
                    event.target
                );

            const clickedInsideDropdown =
                dropdownRef.current &&
                dropdownRef.current.contains(
                    event.target
                );

            if (
                !clickedInsideSearch &&
                !clickedInsideDropdown
            ) {
                setOpenProductRow(null);
                setProductSearch("");
            }
        };

        document.addEventListener(
            "mousedown",
            handleClickOutside
        );

        return () => {

            document.removeEventListener(
                "mousedown",
                handleClickOutside
            );
        };

    }, []);


    // =====================================================
    // DROPDOWN POSITION TRACKING
    // =====================================================

    useEffect(() => {

        if (
            openProductRow === null
        ) {
            return;
        }

        const updatePosition = () => {
            updateDropdownPosition();
        };

        updatePosition();

        window.addEventListener(
            "resize",
            updatePosition
        );

        window.addEventListener(
            "scroll",
            updatePosition,
            true
        );

        return () => {

            window.removeEventListener(
                "resize",
                updatePosition
            );

            window.removeEventListener(
                "scroll",
                updatePosition,
                true
            );
        };

    }, [openProductRow]);


    // =====================================================
    // PRODUCT NAME
    // =====================================================

    const getProductName = (product) => {

        if (!product) {
            return "";
        }

        return (
            product.product_name ||
            product.name ||
            product.productName ||
            "Unnamed Product"
        );
    };


    // =====================================================
    // PRODUCT SKU
    // =====================================================

    const getProductSku = (product) => {

        if (!product) {
            return "";
        }

        return (
            product.sku ||
            product.product_code ||
            product.code ||
            ""
        );
    };


    // =====================================================
    // PRODUCT MODEL
    // =====================================================

    const getProductModel = (product) => {

        if (!product) {
            return "";
        }

        return (
            product.model_no ||
            product.model_number ||
            product.model ||
            ""
        );
    };


    // =====================================================
    // PRODUCT UNIT
    // =====================================================

    const getProductUnit = (product) => {

        if (!product) {
            return "-";
        }

        if (product.unit?.name) {
            return product.unit.name;
        }

        if (product.unit?.short_name) {
            return product.unit.short_name;
        }

        return (
            product.unit_name ||
            product.uom_name ||
            product.uom ||
            "-"
        );
    };


    // =====================================================
    // PRODUCT HSN / SAC
    // =====================================================

    const getProductHSN = (product) => {

        if (!product) {
            return "";
        }

        return (
            product.hsn_code ||
            product.hsn ||
            product.sac_code ||
            product.sac ||
            ""
        );
    };


    // =====================================================
    // PRODUCT PRICE
    // =====================================================

    const getProductPrice = (product) => {

        if (!product) {
            return 0;
        }

        return Number(
            product.retail_price ??
            product.dtp_price ??
            product.selling_price ??
            product.sale_price ??
            product.price ??
            product.sellingPrice ??
            0
        );
    };


    // =====================================================
    // PRODUCT GST
    // =====================================================

    const getProductGST = (product) => {

        if (!product) {
            return 18;
        }

        return Number(
            product.gst_percentage ??
            product.gst_rate ??
            product.gst ??
            18
        );
    };


    // =====================================================
    // PRODUCT STOCK
    // =====================================================
    //
    // IMPORTANT
    //
    // Priority:
    //
    // 1. _warehouse_stock
    //    -> value fetched from:
    //       /inventory/stock
    //
    // 2. Product inventory for selected warehouse
    //
    // 3. Product-level stock fallback
    //
    // IMPORTANT:
    //
    // If _warehouse_stock is 0, it MUST return 0.
    //
    // We must NOT fall through to another stock value.
    //
    // =====================================================

    const getProductStock = (
        product,
        warehouseId = selectedWarehouseId,
        itemStock = null
    ) => {

        // -------------------------------------------------
        // 1. Item-level warehouse stock
        // -------------------------------------------------
        //
        // ZERO IS A VALID STOCK VALUE.
        //
        // -------------------------------------------------

        if (
            itemStock !== null &&
            itemStock !== undefined &&
            itemStock !== ""
        ) {

            const stock =
                Number(itemStock);

            if (
                Number.isFinite(stock)
            ) {
                return Math.max(
                    stock,
                    0
                );
            }
        }


        // -------------------------------------------------
        // Product not available
        // -------------------------------------------------

        if (!product) {
            return 0;
        }


        const selectedWarehouse =
            Number(warehouseId);


        // -------------------------------------------------
        // 2. Product Inventory
        // -------------------------------------------------

        if (
            Array.isArray(
                product.inventory
            )
        ) {

            const warehouseInventory =
                product.inventory.find(
                    (inventory) =>
                        Number(
                            inventory.warehouse_id
                        ) ===
                        selectedWarehouse
                );

            if (
                warehouseInventory
            ) {

                return Math.max(
                    Number(
                        warehouseInventory.stock ??
                        0
                    ),
                    0
                );
            }
        }


        // -------------------------------------------------
        // 3. Product-level fallback
        // -------------------------------------------------

        return Math.max(
            Number(
                product.stock ??
                product.quantity ??
                0
            ),
            0
        );
    };


    // =====================================================
    // FIND PRODUCT
    // =====================================================

    const findProduct = (productId) => {

        return availableProducts.find(
            (product) =>
                Number(product.id) ===
                Number(productId)
        );
    };


    // =====================================================
    // FILTER PRODUCTS
    // =====================================================

    const getFilteredProducts = () => {

        const search =
            productSearch
                .trim()
                .toLowerCase();

        if (!search) {
            return availableProducts;
        }

        return availableProducts.filter(
            (product) => {

                const name =
                    getProductName(product)
                        .toLowerCase();

                const sku =
                    getProductSku(product)
                        .toLowerCase();

                const model =
                    getProductModel(product)
                        .toLowerCase();

                const hsn =
                    getProductHSN(product)
                        .toLowerCase();

                return (
                    name.includes(search) ||
                    sku.includes(search) ||
                    model.includes(search) ||
                    hsn.includes(search)
                );
            }
        );
    };


    // =====================================================
    // ADD ITEM
    // =====================================================

    const addItem = () => {

        const newItem = {

            product_id: "",

            quantity: 1,

            delivered_quantity: 0,

            pending_quantity: 1,

            selling_price: 0,

            discount_percentage: 0,

            discount_amount: 0,

            gst_percentage: 18,

            gst_amount: 0,

            line_total: 0,

            product_name: "",

            sku: "",

            model_no: "",

            hsn_code: "",

            serial_numbers: [],

            description: "",

            remarks: "",

            // -------------------------------------------------
            // Actual warehouse stock
            // This will be populated by SalesContext.
            // -------------------------------------------------

            _warehouse_stock: 0,
        };

        updateField(
            "items",
            [
                ...items,
                newItem,
            ]
        );
    };


    // =====================================================
    // REMOVE ITEM
    // =====================================================

    const removeItem = (index) => {

        const updatedItems =
            items.filter(
                (_, itemIndex) =>
                    itemIndex !== index
            );

        updateField(
            "items",
            updatedItems
        );
    };


    // =====================================================
    // SELECT PRODUCT
    // =====================================================

    const selectProduct = async (
        index,
        product
    ) => {

        const quantity =
            Number(
                items[index]?.quantity ||
                1
            );

        const sellingPrice =
            getProductPrice(product);

        const gstPercentage =
            getProductGST(product);

        // -------------------------------------------------
        // FETCH ACTUAL WAREHOUSE STOCK FROM API
        // -------------------------------------------------
        let stock = 0;
        
        if (product?.id && selectedWarehouseId) {
            try {
                stock = await SalesService.getCurrentStock(
                    Number(product.id),
                    Number(selectedWarehouseId)
                );
            } catch (error) {
                console.error("Failed to fetch real-time stock:", error);
            }
        }


        const discountPercentage =
            Number(
                items[index]
                    ?.discount_percentage ||
                0
            );

        const baseAmount =
            quantity *
            sellingPrice;

        const discountAmount =
            (
                baseAmount *
                discountPercentage
            ) / 100;

        const taxableAmount =
            baseAmount -
            discountAmount;

        const gstAmount =
            (
                taxableAmount *
                gstPercentage
            ) / 100;

        const lineTotal =
            taxableAmount +
            gstAmount;


        const updatedItem = {

            ...items[index],

            product_id:
                product.id,

            product_name:
                getProductName(
                    product
                ),

            sku:
                getProductSku(
                    product
                ),

            model_no:
                getProductModel(
                    product
                ),

            hsn_code:
                getProductHSN(
                    product
                ),

            quantity,

            delivered_quantity:
                0,

            pending_quantity:
                quantity,

            selling_price:
                sellingPrice,

            discount_percentage:
                discountPercentage,

            discount_amount:
                discountAmount,

            gst_percentage:
                gstPercentage,

            gst_amount:
                gstAmount,

            line_total:
                lineTotal,

            // -------------------------------------------------
            // Keep warehouse stock separately.
            // -------------------------------------------------

            _warehouse_stock:
                stock,
        };


        const updatedItems =
            items.map(
                (item, itemIndex) =>
                    itemIndex === index
                        ? updatedItem
                        : item
            );

        updateField(
            "items",
            updatedItems
        );

        setOpenProductRow(null);

        setProductSearch("");
    };


    // =====================================================
    // RECALCULATE ITEM
    // =====================================================

    const recalculateItem = (
        index,
        changes = {}
    ) => {

        const currentItem =
            items[index];

        if (!currentItem) {
            return;
        }

        const quantity =
            Math.max(
                Number(
                    changes.quantity ??
                    currentItem.quantity ??
                    1
                ) || 1,
                1
            );

        const sellingPrice =
            Math.max(
                Number(
                    changes.selling_price ??
                    currentItem.selling_price ??
                    0
                ) || 0,
                0
            );

        const discountPercentage =
            Math.min(
                Math.max(
                    Number(
                        changes.discount_percentage ??
                        currentItem.discount_percentage ??
                        0
                    ) || 0,
                    0
                ),
                100
            );

        const gstPercentage =
            Math.max(
                Number(
                    changes.gst_percentage ??
                    currentItem.gst_percentage ??
                    18
                ) || 0,
                0
            );

        const baseAmount =
            quantity *
            sellingPrice;

        const discountAmount =
            (
                baseAmount *
                discountPercentage
            ) / 100;

        const taxableAmount =
            baseAmount -
            discountAmount;

        const gstAmount =
            (
                taxableAmount *
                gstPercentage
            ) / 100;

        const lineTotal =
            taxableAmount +
            gstAmount;


        const updatedItem = {

            ...currentItem,

            ...changes,

            quantity,

            pending_quantity:
                Math.max(
                    quantity -
                    Number(
                        currentItem.delivered_quantity ||
                        0
                    ),
                    0
                ),

            selling_price:
                sellingPrice,

            discount_percentage:
                discountPercentage,

            discount_amount:
                discountAmount,

            gst_percentage:
                gstPercentage,

            gst_amount:
                gstAmount,

            line_total:
                lineTotal,
        };


        const updatedItems =
            items.map(
                (item, itemIndex) =>
                    itemIndex === index
                        ? updatedItem
                        : item
            );

        updateField(
            "items",
            updatedItems
        );
    };


    // =====================================================
    // QUANTITY
    // =====================================================

    const handleQuantityChange = (
        index,
        value
    ) => {

        const quantity =
            Math.max(
                Number(value) || 1,
                1
            );

        recalculateItem(
            index,
            {
                quantity,
            }
        );
    };


    // =====================================================
    // PRICE
    // =====================================================

    const handlePriceChange = (
        index,
        value
    ) => {

        const price =
            Math.max(
                Number(value) || 0,
                0
            );

        recalculateItem(
            index,
            {
                selling_price:
                    price,
            }
        );
    };


    // =====================================================
    // DISCOUNT
    // =====================================================

    const handleDiscountChange = (
        index,
        value
    ) => {

        const discount =
            Math.min(
                Math.max(
                    Number(value) || 0,
                    0
                ),
                100
            );

        recalculateItem(
            index,
            {
                discount_percentage:
                    discount,
            }
        );
    };


    // =====================================================
    // GST
    // =====================================================

    const handleGSTChange = (
        index,
        value
    ) => {

        const gst =
            Math.max(
                Number(value) || 0,
                0
            );

        recalculateItem(
            index,
            {
                gst_percentage:
                    gst,
            }
        );
    };


    // =====================================================
    // DESCRIPTION
    // =====================================================

    const handleDescriptionChange = (
        index,
        value
    ) => {

        const updatedItems =
            items.map(
                (item, itemIndex) =>
                    itemIndex === index
                        ? {
                            ...item,
                            description:
                                value,
                        }
                        : item
            );

        updateField(
            "items",
            updatedItems
        );
    };


    // =====================================================
    // SERIAL MODAL
    // =====================================================

    const openSerialModal = (
        index
    ) => {

        const existingSerials =
            Array.isArray(
                items[index]
                    ?.serial_numbers
            )
                ? items[index]
                    .serial_numbers
                : [];

        setSerialModalRow(
            index
        );

        setSerialDraft(
            existingSerials.length > 0
                ? [...existingSerials]
                : [""]
        );
    };


    const closeSerialModal = () => {

        setSerialModalRow(
            null
        );

        setSerialDraft([]);
    };


    const updateSerialDraft = (
        serialIndex,
        value
    ) => {

        setSerialDraft(
            (current) =>
                current.map(
                    (
                        serial,
                        index
                    ) =>
                        index === serialIndex
                            ? value
                            : serial
                )
        );
    };


    const addSerialDraft = () => {

        setSerialDraft(
            (current) => [
                ...current,
                "",
            ]
        );
    };


    const removeSerialDraft = (
        serialIndex
    ) => {

        setSerialDraft(
            (current) => {

                const updated =
                    current.filter(
                        (
                            _,
                            index
                        ) =>
                            index !==
                            serialIndex
                    );

                return updated.length > 0
                    ? updated
                    : [""];
            }
        );
    };


    const saveSerialNumbers = () => {

        if (
            serialModalRow ===
            null
        ) {
            return;
        }

        const serialNumbers =
            serialDraft
                .map(
                    (serial) =>
                        serial.trim()
                )
                .filter(Boolean);

        const updatedItems =
            items.map(
                (
                    item,
                    index
                ) =>
                    index ===
                    serialModalRow
                        ? {
                            ...item,
                            serial_numbers:
                                serialNumbers,
                        }
                        : item
            );

        updateField(
            "items",
            updatedItems
        );

        closeSerialModal();
    };


    // =====================================================
    // FILTERED PRODUCTS
    // =====================================================

    const filteredProducts =
        getFilteredProducts();


    // =====================================================
    // RENDER
    // =====================================================

    return (

        <div className="sales-items-table-wrapper">

            {/* =================================================
                TABLE
            ================================================= */}

            <div className="sales-items-table-scroll">

                <table className="sales-items-table">

                    {/* =================================================
                        HEADER
                    ================================================= */}

                    <thead>

                        <tr>

                            <th className="sales-item-number">
                                #
                            </th>

                            <th className="sales-item-product">
                                Item
                            </th>

                            <th className="sales-item-serial">
                                Serial No.
                            </th>

                            <th className="sales-item-description">
                                Description
                            </th>

                            <th className="sales-item-hsn">
                                HSN/SAC
                            </th>

                            <th className="sales-item-unit">
                                Unit
                            </th>

                            <th className="sales-item-qty">
                                Qty
                            </th>

                            <th className="sales-item-price">
                                Price / Unit
                            </th>

                            <th className="sales-item-discount">
                                Discount %
                            </th>

                            <th className="sales-item-gst">
                                GST %
                            </th>

                            <th className="sales-item-total">
                                Amount
                            </th>

                            <th className="sales-item-action">
                                Action
                            </th>

                        </tr>

                    </thead>


                    {/* =================================================
                        BODY
                    ================================================= */}

                    <tbody>

                        {items.length === 0 ? (

                            <tr>

                                <td
                                    colSpan="12"
                                    className="sales-items-empty"
                                >

                                    <div className="sales-items-empty-content">

                                        <Package
                                            size={28}
                                        />

                                        <strong>
                                            No products added
                                        </strong>

                                        <span>
                                            Click Add Product
                                            to add items to
                                            this sales order.
                                        </span>

                                        <button
                                            type="button"
                                            onClick={
                                                addItem
                                            }
                                            className="sales-empty-add-btn"
                                        >

                                            <Plus
                                                size={15}
                                            />

                                            Add Product

                                        </button>

                                    </div>

                                </td>

                            </tr>

                        ) : (

                            items.map(
                                (
                                    item,
                                    index
                                ) => {

                                    const selectedProduct =
                                        findProduct(
                                            item.product_id
                                        );


                                    // -------------------------------------------------
                                    // ACTUAL WAREHOUSE STOCK
                                    // -------------------------------------------------

                                    const stock =
                                        selectedProduct
                                            ? getProductStock(
                                                selectedProduct,
                                                selectedWarehouseId,
                                                item._warehouse_stock
                                            )
                                            : 0;


                                    const quantity =
                                        Number(
                                            item.quantity ||
                                            0
                                        );


                                    const insufficientStock =
                                        selectedProduct &&
                                        quantity >
                                        Number(stock);


                                    const serialCount =
                                        Array.isArray(
                                            item.serial_numbers
                                        )
                                            ? item.serial_numbers
                                                .filter(Boolean)
                                                .length
                                            : 0;


                                    return (

                                        <tr
                                            key={
                                                item.id ||
                                                `${item.product_id}-${index}`
                                            }
                                        >

                                            {/* =================================
                                                NUMBER
                                            ================================= */}

                                            <td>

                                                <span className="sales-item-number-badge">
                                                    {index + 1}
                                                </span>

                                            </td>


                                            {/* =================================
                                                PRODUCT
                                            ================================= */}

                                            <td>

                                                <div
                                                    className="product-search-container"
                                                    ref={
                                                        openProductRow ===
                                                        index
                                                            ? searchRef
                                                            : null
                                                    }
                                                >

                                                    <div
                                                        className={
                                                            `product-search-input ${
                                                                openProductRow ===
                                                                index
                                                                    ? "product-search-input-active"
                                                                    : ""
                                                            }`
                                                        }

                                                        onClick={() => {

                                                            setOpenProductRow(
                                                                openProductRow ===
                                                                index
                                                                    ? null
                                                                    : index
                                                            );

                                                            setProductSearch(
                                                                ""
                                                            );

                                                            setTimeout(
                                                                updateDropdownPosition,
                                                                0
                                                            );
                                                        }}
                                                    >

                                                        <Package
                                                            size={16}
                                                        />

                                                        <input
                                                            type="text"

                                                            value={
                                                                openProductRow ===
                                                                index
                                                                    ? productSearch
                                                                    : selectedProduct
                                                                        ? getProductName(
                                                                            selectedProduct
                                                                        )
                                                                        : ""
                                                            }

                                                            placeholder="Search product, SKU or model..."

                                                            onChange={(event) => {

                                                                setOpenProductRow(
                                                                    index
                                                                );

                                                                setProductSearch(
                                                                    event.target.value
                                                                );

                                                                setTimeout(
                                                                    updateDropdownPosition,
                                                                    0
                                                                );
                                                            }}

                                                            onFocus={() => {

                                                                setOpenProductRow(
                                                                    index
                                                                );

                                                                setTimeout(
                                                                    updateDropdownPosition,
                                                                    0
                                                                );
                                                            }}

                                                            onClick={(event) =>
                                                                event.stopPropagation()
                                                            }
                                                        />

                                                        <ChevronDown
                                                            size={16}
                                                            className={
                                                                openProductRow ===
                                                                index
                                                                    ? "product-chevron-open"
                                                                    : ""
                                                            }
                                                        />

                                                    </div>

                                                </div>


                                                {selectedProduct && (

                                                    <div
                                                        className={
                                                            insufficientStock
                                                                ? "sales-stock-warning"
                                                                : "sales-stock-info"
                                                        }
                                                    >

                                                        Stock: {stock}

                                                        {insufficientStock &&
                                                            " • Insufficient stock"}

                                                    </div>

                                                )}

                                            </td>


                                            {/* =================================
                                                SERIAL NUMBER
                                            ================================= */}

                                            <td className="sales-item-serial-cell">

                                                <button
                                                    type="button"

                                                    className="serial-number-button"

                                                    onClick={() =>
                                                        openSerialModal(
                                                            index
                                                        )
                                                    }

                                                    title="Manage serial numbers"
                                                >

                                                    <List
                                                        size={15}
                                                    />

                                                    {serialCount > 0 && (

                                                        <span className="serial-count">
                                                            {serialCount}
                                                        </span>

                                                    )}

                                                </button>

                                            </td>


                                            {/* =================================
                                                DESCRIPTION
                                            ================================= */}

                                            <td className="sales-item-description-cell">

                                                <input
                                                    type="text"

                                                    className="sales-description-input"

                                                    value={
                                                        item.description ??
                                                        ""
                                                    }

                                                    placeholder="Description"

                                                    onChange={(event) =>
                                                        handleDescriptionChange(
                                                            index,
                                                            event.target.value
                                                        )
                                                    }
                                                />

                                            </td>


                                            {/* =================================
                                                HSN / SAC
                                            ================================= */}

                                            <td>

                                                <input
                                                    type="text"

                                                    className="sales-text-cell-input"

                                                    value={
                                                        item.hsn_code ||
                                                        getProductHSN(
                                                            selectedProduct
                                                        ) ||
                                                        ""
                                                    }

                                                    placeholder="HSN/SAC"

                                                    readOnly
                                                />

                                            </td>


                                            {/* =================================
                                                UNIT
                                            ================================= */}

                                            <td>

                                                <span className="sales-unit-text">

                                                    {
                                                        getProductUnit(
                                                            selectedProduct
                                                        )
                                                    }

                                                </span>

                                            </td>


                                            {/* =================================
                                                QUANTITY
                                            ================================= */}

                                            <td>

                                                <input
                                                    className="sales-number-input"

                                                    type="number"

                                                    min="1"

                                                    value={
                                                        item.quantity ??
                                                        1
                                                    }

                                                    onChange={(event) =>
                                                        handleQuantityChange(
                                                            index,
                                                            event.target.value
                                                        )
                                                    }
                                                />

                                            </td>


                                            {/* =================================
                                                PRICE
                                            ================================= */}

                                            <td>

                                                <input
                                                    className="sales-number-input"

                                                    type="number"

                                                    min="0"

                                                    step="0.01"

                                                    value={
                                                        item.selling_price ??
                                                        0
                                                    }

                                                    onChange={(event) =>
                                                        handlePriceChange(
                                                            index,
                                                            event.target.value
                                                        )
                                                    }
                                                />

                                            </td>


                                            {/* =================================
                                                DISCOUNT
                                            ================================= */}

                                            <td>

                                                <input
                                                    className="sales-number-input"

                                                    type="number"

                                                    min="0"

                                                    max="100"

                                                    step="0.01"

                                                    value={
                                                        item.discount_percentage ??
                                                        0
                                                    }

                                                    onChange={(event) =>
                                                        handleDiscountChange(
                                                            index,
                                                            event.target.value
                                                        )
                                                    }
                                                />

                                            </td>


                                            {/* =================================
                                                GST
                                            ================================= */}

                                            <td>

                                                <input
                                                    className="sales-number-input"

                                                    type="number"

                                                    min="0"

                                                    step="0.01"

                                                    value={
                                                        item.gst_percentage ??
                                                        18
                                                    }

                                                    onChange={(event) =>
                                                        handleGSTChange(
                                                            index,
                                                            event.target.value
                                                        )
                                                    }
                                                />

                                            </td>


                                            {/* =================================
                                                AMOUNT
                                            ================================= */}

                                            <td>

                                                <strong className="sales-line-total">

                                                    ₹
                                                    {Number(
                                                        item.line_total ||
                                                        0
                                                    ).toLocaleString(
                                                        "en-IN",
                                                        {
                                                            minimumFractionDigits: 2,
                                                            maximumFractionDigits: 2,
                                                        }
                                                    )}

                                                </strong>

                                            </td>


                                            {/* =================================
                                                DELETE
                                            ================================= */}

                                            <td>

                                                <button
                                                    type="button"

                                                    className="sales-remove-item-btn"

                                                    onClick={() =>
                                                        removeItem(
                                                            index
                                                        )
                                                    }

                                                    title="Remove product"
                                                >

                                                    <Trash2
                                                        size={16}
                                                    />

                                                </button>

                                            </td>

                                        </tr>
                                    );
                                }
                            )
                        )}

                    </tbody>

                </table>

            </div>


            {/* =================================================
                PRODUCT SEARCH DROPDOWN PORTAL
            ================================================= */}

            {openProductRow !== null &&

                createPortal(

                    <div
                        ref={
                            dropdownRef
                        }

                        className="product-search-dropdown-portal"

                        style={{
                            top:
                                `${dropdownPosition.top}px`,

                            left:
                                `${dropdownPosition.left}px`,

                            width:
                                `${dropdownPosition.width}px`,
                        }}

                        onMouseDown={(event) =>
                            event.stopPropagation()
                        }
                    >

                        {filteredProducts.length === 0 ? (

                            <div className="product-search-empty">

                                <Package
                                    size={24}
                                />

                                <span>
                                    No products found
                                </span>

                                <small>
                                    Try product name,
                                    SKU, model or HSN/SAC
                                </small>

                            </div>

                        ) : (

                            filteredProducts.map(
                                (product) => (

                                    <button
                                        type="button"

                                        key={
                                            product.id
                                        }

                                        className="product-search-option"

                                        onMouseDown={(event) =>
                                            event.preventDefault()
                                        }

                                        onClick={() => {

                                            selectProduct(
                                                openProductRow,
                                                product
                                            );

                                            setOpenProductRow(
                                                null
                                            );

                                            setProductSearch(
                                                ""
                                            );
                                        }}
                                    >

                                        <div className="product-option-icon">

                                            <Package
                                                size={17}
                                            />

                                        </div>


                                        <div className="product-option-content">

                                            <div className="product-option-name">

                                                {
                                                    getProductName(
                                                        product
                                                    )
                                                }

                                            </div>


                                            <div className="product-option-details">

                                                {getProductSku(product) && (

                                                    <span>
                                                        SKU:{" "}
                                                        {
                                                            getProductSku(
                                                                product
                                                            )
                                                        }
                                                    </span>

                                                )}


                                                {getProductModel(product) && (

                                                    <span>
                                                        Model:{" "}
                                                        {
                                                            getProductModel(
                                                                product
                                                            )
                                                        }
                                                    </span>

                                                )}


                                                {getProductHSN(product) && (

                                                    <span>
                                                        HSN/SAC:{" "}
                                                        {
                                                            getProductHSN(
                                                                product
                                                            )
                                                        }
                                                    </span>

                                                )}

                                            </div>

                                        </div>


                                        <div className="product-option-price">

                                            ₹
                                            {Number(
                                                getProductPrice(
                                                    product
                                                )
                                            ).toLocaleString(
                                                "en-IN"
                                            )}

                                        </div>

                                    </button>
                                )
                            )
                        )}

                    </div>,

                    document.body
                )
            }


            {/* =================================================
                SERIAL NUMBER MODAL
            ================================================= */}

            {serialModalRow !== null &&

                createPortal(

                    <div
                        className="serial-modal-backdrop"

                        onMouseDown={
                            closeSerialModal
                        }
                    >

                        <div
                            className="serial-modal"

                            onMouseDown={(event) =>
                                event.stopPropagation()
                            }
                        >

                            {/* HEADER */}

                            <div className="serial-modal-header">

                                <div>

                                    <h3>
                                        Serial Numbers
                                    </h3>

                                    <p>

                                        {items[
                                            serialModalRow
                                        ]

                                            ? getProductName(
                                                findProduct(
                                                    items[
                                                        serialModalRow
                                                    ]?.product_id
                                                )
                                            ) ||
                                            "Selected Product"

                                            : "Selected Product"}

                                    </p>

                                </div>


                                <button
                                    type="button"

                                    className="serial-modal-close"

                                    onClick={
                                        closeSerialModal
                                    }

                                    title="Close"
                                >

                                    <X
                                        size={18}
                                    />

                                </button>

                            </div>


                            {/* BODY */}

                            <div className="serial-modal-body">

                                <div className="serial-modal-label">
                                    Serial Number
                                </div>


                                {serialDraft.map(
                                    (
                                        serial,
                                        serialIndex
                                    ) => (

                                        <div
                                            className="serial-input-row"

                                            key={
                                                serialIndex
                                            }
                                        >

                                            <span className="serial-row-number">

                                                {
                                                    serialIndex +
                                                    1
                                                }

                                            </span>


                                            <input
                                                type="text"

                                                value={
                                                    serial
                                                }

                                                placeholder="Enter serial number"

                                                onChange={(event) =>
                                                    updateSerialDraft(
                                                        serialIndex,
                                                        event.target.value
                                                    )
                                                }

                                                autoFocus={
                                                    serialIndex ===
                                                    0
                                                }
                                            />


                                            <button
                                                type="button"

                                                className="serial-remove-button"

                                                onClick={() =>
                                                    removeSerialDraft(
                                                        serialIndex
                                                    )
                                                }

                                                title="Remove serial number"
                                            >

                                                <X
                                                    size={15}
                                                />

                                            </button>

                                        </div>
                                    )
                                )}


                                <button
                                    type="button"

                                    className="serial-add-button"

                                    onClick={
                                        addSerialDraft
                                    }
                                >

                                    <Plus
                                        size={15}
                                    />

                                    Add Serial Number

                                </button>

                            </div>


                            {/* FOOTER */}

                            <div className="serial-modal-footer">

                                <span className="serial-modal-count">

                                    {
                                        serialDraft.filter(
                                            (serial) =>
                                                serial.trim()
                                        ).length
                                    }

                                    {" "}

                                    serial number

                                    {serialDraft.filter(
                                        (serial) =>
                                            serial.trim()
                                    ).length === 1
                                        ? ""
                                        : "s"}

                                </span>


                                <div className="serial-modal-actions">

                                    <button
                                        type="button"

                                        className="serial-cancel-button"

                                        onClick={
                                            closeSerialModal
                                        }
                                    >
                                        Cancel
                                    </button>


                                    <button
                                        type="button"

                                        className="serial-save-button"

                                        onClick={
                                            saveSerialNumbers
                                        }
                                    >
                                        Save
                                    </button>

                                </div>

                            </div>

                        </div>

                    </div>,

                    document.body
                )
            }


            {/* =================================================
                GLOBAL STOCK WARNING
            ================================================= */}

            {items.some(
                (item) => {

                    const product =
                        findProduct(
                            item.product_id
                        );

                    const stock =
                        product
                            ? getProductStock(
                                product,
                                selectedWarehouseId,
                                item._warehouse_stock
                            )
                            : 0;

                    return (
                        item.product_id &&
                        Number(
                            item.quantity || 0
                        ) >
                        Number(stock)
                    );
                }
            ) && (

                <div className="sales-global-stock-warning">

                    <Package
                        size={17}
                    />

                    <span>
                        One or more products have
                        insufficient available stock.
                    </span>

                </div>
            )}


            {/* =================================================
                ADD PRODUCT
            ================================================= */}

            {items.length > 0 && (

                <button
                    type="button"

                    className="sales-table-add-product"

                    onClick={
                        addItem
                    }
                >

                    <Plus
                        size={16}
                    />

                    Add Product

                </button>
            )}

        </div>
    );
};


export default SalesItemsTable;