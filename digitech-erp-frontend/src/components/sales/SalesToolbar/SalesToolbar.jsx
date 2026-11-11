import "./SalesToolbar.css";

import {
    Search,
    RotateCcw,
    Download,
    Plus,
} from "lucide-react";

import { useEffect, useState } from "react";

import { useSales } from "../../../context/SalesContext";


const SalesToolbar = () => {

    const {
        filters,
        customers,
        products,
        warehouses,
        updateFilter,
        setFilters,
        openCreateDrawer,
        exportSales,
    } = useSales();


    // =====================================================
    // Local Search
    // =====================================================

    const [localSearch, setLocalSearch] = useState(
        filters?.search || ""
    );


    // =====================================================
    // Customer Dropdown
    // =====================================================

    const [customerSearch, setCustomerSearch] = useState("");

    const [
        customerDropdownOpen,
        setCustomerDropdownOpen
    ] = useState(false);


    // =====================================================
    // Item Dropdown
    // =====================================================

    const [productSearch, setProductSearch] = useState("");

    const [
        productDropdownOpen,
        setProductDropdownOpen
    ] = useState(false);


    // =====================================================
    // Keep Local Search Synchronized
    // =====================================================

    useEffect(() => {

        setLocalSearch(
            filters?.search || ""
        );

    }, [filters?.search]);


    // =====================================================
    // Search
    // =====================================================

    const handleSearch = (e) => {

        const value = e.target.value;

        setLocalSearch(value);

        updateFilter(
            "search",
            value
        );

    };


    // =====================================================
    // Customer
    // =====================================================

    const handleCustomerChange = (e) => {

        updateFilter(
            "customer_id",
            e.target.value
        );

    };


    // =====================================================
    // Filter Customers
    // =====================================================

    const filteredCustomers =
        customers?.filter((customer) => {

            const customerName =
                customer.name ||
                customer.customer_name ||
                customer.full_name ||
                `Customer #${customer.id}`;

            return customerName
                .toLowerCase()
                .includes(
                    customerSearch.toLowerCase()
                );

        });


    // =====================================================
    // Filter Products / Items
    // =====================================================

    const filteredProducts =
        products?.filter((product) => {

            const productName =
                product.name ||
                product.product_name ||
                product.title ||
                `Product #${product.id}`;

            return productName
                .toLowerCase()
                .includes(
                    productSearch.toLowerCase()
                );

        });


    // =====================================================
    // Warehouse
    // =====================================================

    const handleWarehouseChange = (e) => {

        updateFilter(
            "warehouse_id",
            e.target.value
        );

    };


    // =====================================================
    // Item / Product
    // =====================================================

    const handleProductChange = (e) => {

        updateFilter(
            "product_id",
            e.target.value
        );

    };


    // =====================================================
    // Date From
    // =====================================================

    const handleDateFromChange = (e) => {

        updateFilter(
            "date_from",
            e.target.value
        );

    };


    // =====================================================
    // Date To
    // =====================================================

    const handleDateToChange = (e) => {

        updateFilter(
            "date_to",
            e.target.value
        );

    };


    // =====================================================
    // Reset
    // =====================================================

    const handleReset = () => {

        setLocalSearch("");

        setCustomerSearch("");

        setProductSearch("");

        setCustomerDropdownOpen(false);

        setProductDropdownOpen(false);

        setFilters({

            search: "",

            customer_id: "",

            product_id: "",

            warehouse_id: "",

            payment_status: "",

            date_from: "",

            date_to: "",

            page: 1,

        });

    };


    // =====================================================
    // Export
    // =====================================================

    const handleExport = async () => {

        try {

            await exportSales();

        } catch (error) {

            console.error(
                "Sales export failed:",
                error
            );

        }

    };


    // =====================================================
    // Get Selected Product Name
    // =====================================================

    const selectedProduct =
        products?.find(
            (product) =>
                String(product.id) ===
                String(filters?.product_id)
        );


    const selectedProductName =
        selectedProduct?.name ||
        selectedProduct?.product_name ||
        selectedProduct?.title ||
        (
            filters?.product_id
                ? `Product #${filters.product_id}`
                : "All Items"
        );


    // =====================================================
    // Render
    // =====================================================

    return (

        <div className="sales-toolbar">


            {/* =================================================
                Search
            ================================================= */}

            <div className="sales-search-box">

                <Search
                    size={18}
                    className="sales-search-icon"
                />

                <input
                    type="text"
                    placeholder="Search order no, customer..."
                    value={localSearch}
                    onChange={handleSearch}
                />

            </div>


            {/* =================================================
                Filters
            ================================================= */}

            <div className="sales-toolbar-filters">


                {/* =================================================
                    Customer
                ================================================= */}

                <div className="sales-customer-dropdown">

                    {/* Selected Customer */}

                    <div
                        className="sales-customer-select"
                        onClick={() =>
                            setCustomerDropdownOpen(
                                !customerDropdownOpen
                            )
                        }
                    >

                        <span>

                            {filters?.customer_id
                                ? (
                                    customers?.find(
                                        (customer) =>
                                            String(customer.id) ===
                                            String(filters.customer_id)
                                    )
                                )?.name ||

                                customers?.find(
                                    (customer) =>
                                        String(customer.id) ===
                                        String(filters.customer_id)
                                )?.customer_name ||

                                customers?.find(
                                    (customer) =>
                                        String(customer.id) ===
                                        String(filters.customer_id)
                                )?.full_name ||

                                "Customer"

                                : "All Customers"
                            }

                        </span>

                        <span className="sales-customer-arrow">
                            ▼
                        </span>

                    </div>


                    {/* Customer Dropdown */}

                    {customerDropdownOpen && (

                        <div className="sales-customer-menu">


                            {/* Search Customer */}

                            <div className="sales-customer-search">

                                <Search size={16} />

                                <input
                                    type="text"
                                    placeholder="Search customer..."
                                    value={customerSearch}
                                    onChange={(e) =>
                                        setCustomerSearch(
                                            e.target.value
                                        )
                                    }
                                    onClick={(e) =>
                                        e.stopPropagation()
                                    }
                                    autoFocus
                                />

                            </div>


                            {/* All Customers */}

                            <div
                                className="sales-customer-option"
                                onClick={() => {

                                    updateFilter(
                                        "customer_id",
                                        ""
                                    );

                                    setCustomerSearch("");

                                    setCustomerDropdownOpen(
                                        false
                                    );

                                }}
                            >

                                All Customers

                            </div>


                            {/* Customers */}

                            {filteredCustomers?.map(
                                (customer) => {

                                    const customerName =
                                        customer.name ||
                                        customer.customer_name ||
                                        customer.full_name ||
                                        `Customer #${customer.id}`;

                                    return (

                                        <div
                                            key={customer.id}
                                            className="sales-customer-option"
                                            onClick={() => {

                                                updateFilter(
                                                    "customer_id",
                                                    customer.id
                                                );

                                                setCustomerSearch("");

                                                setCustomerDropdownOpen(
                                                    false
                                                );

                                            }}
                                        >

                                            {customerName}

                                        </div>

                                    );

                                }
                            )}


                            {/* No Results */}

                            {filteredCustomers?.length === 0 && (

                                <div className="sales-customer-no-results">

                                    No customers found

                                </div>

                            )}

                        </div>

                    )}

                </div>


                {/* =================================================
                    ITEM FILTER
                ================================================= */}

                <div className="sales-customer-dropdown">


                    {/* Selected Item */}

                    <div
                        className="sales-customer-select"
                        onClick={() =>
                            setProductDropdownOpen(
                                !productDropdownOpen
                            )
                        }
                    >

                        <span>
                            {selectedProductName}
                        </span>

                        <span className="sales-customer-arrow">
                            ▼
                        </span>

                    </div>


                    {/* Item Dropdown */}

                    {productDropdownOpen && (

                        <div className="sales-customer-menu">


                            {/* Search Item */}

                            <div className="sales-customer-search">

                                <Search size={16} />

                                <input
                                    type="text"
                                    placeholder="Search item..."
                                    value={productSearch}
                                    onChange={(e) =>
                                        setProductSearch(
                                            e.target.value
                                        )
                                    }
                                    onClick={(e) =>
                                        e.stopPropagation()
                                    }
                                    autoFocus
                                />

                            </div>


                            {/* All Items */}

                            <div
                                className="sales-customer-option"
                                onClick={() => {

                                    updateFilter(
                                        "product_id",
                                        ""
                                    );

                                    setProductSearch("");

                                    setProductDropdownOpen(
                                        false
                                    );

                                }}
                            >

                                All Items

                            </div>


                            {/* Products */}

                            {filteredProducts?.map(
                                (product) => {

                                    const productName =
                                        product.name ||
                                        product.product_name ||
                                        product.title ||
                                        `Product #${product.id}`;

                                    return (

                                        <div
                                            key={product.id}
                                            className="sales-customer-option"
                                            onClick={() => {

                                                updateFilter(
                                                    "product_id",
                                                    product.id
                                                );

                                                setProductSearch("");

                                                setProductDropdownOpen(
                                                    false
                                                );

                                            }}
                                        >

                                            {productName}

                                        </div>

                                    );

                                }
                            )}


                            {/* No Results */}

                            {filteredProducts?.length === 0 && (

                                <div className="sales-customer-no-results">

                                    No items found

                                </div>

                            )}

                        </div>

                    )}

                </div>


                {/* =================================================
                    Warehouse
                ================================================= */}

                <select
                    value={
                        filters?.warehouse_id || ""
                    }
                    onChange={
                        handleWarehouseChange
                    }
                >

                    <option value="">
                        All Warehouses
                    </option>

                    {warehouses?.map(
                        (warehouse) => (

                            <option
                                key={warehouse.id}
                                value={warehouse.id}
                            >

                                {warehouse.name ||
                                    warehouse.warehouse_name ||
                                    `Warehouse #${warehouse.id}`}

                            </option>

                        )
                    )}

                </select>


                {/* =================================================
                    Payment Status
                ================================================= */}

                <select
                    value={
                        filters?.payment_status || ""
                    }
                    onChange={(e) => {

                        updateFilter(
                            "payment_status",
                            e.target.value
                        );

                    }}
                >

                    {/* All Payments */}
                    <option value="">
                        All Payments
                    </option>


                    {/* Pending */}
                    <option value="PENDING">
                        Pending
                    </option>


                    {/* Received By Hand */}
                    <option value="RECEIVED_BY_HAND">
                        Received by Hand
                    </option>


                    {/* Partially Received By Hand */}
                    <option value="PARTIALLY_RECEIVED_BY_HAND">
                        Partially Received by Hand
                    </option>


                    {/* Received To Account */}
                    <option value="RECEIVED_TO_ACCOUNT">
                        Received to Account
                    </option>


                    {/* Partially Received To Account */}
                    <option value="PARTIALLY_RECEIVED_TO_ACCOUNT">
                        Partially Received to Account
                    </option>

                </select>


                {/* =================================================
                    From Date
                ================================================= */}

                <div className="sales-date-filter">

                    <input
                        type="date"
                        value={
                            filters?.date_from || ""
                        }
                        onChange={
                            handleDateFromChange
                        }
                        aria-label="From date"
                    />

                </div>


                {/* =================================================
                    To Date
                ================================================= */}

                <div className="sales-date-filter">

                    <input
                        type="date"
                        value={
                            filters?.date_to || ""
                        }
                        onChange={
                            handleDateToChange
                        }
                        aria-label="To date"
                    />

                </div>

            </div>


            {/* =================================================
                Actions
            ================================================= */}

            <div className="sales-toolbar-actions">


                {/* Reset */}

                <button
                    type="button"
                    className="sales-reset-btn"
                    onClick={handleReset}
                >

                    <RotateCcw size={17} />

                    Reset

                </button>


                {/* Export */}

                <button
                    type="button"
                    className="sales-export-toolbar-btn"
                    onClick={handleExport}
                >

                    <Download size={17} />

                    Export

                </button>


                {/* New Sale */}

                <button
                    type="button"
                    className="sales-new-btn"
                    onClick={openCreateDrawer}
                >

                    <Plus size={18} />

                    New Sale

                </button>

            </div>


        </div>

    );

};


export default SalesToolbar;