import {
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

import SalesService from "../services/SalesService";

const SalesContext = createContext();

export const SalesProvider = ({ children }) => {

    // =====================================================
    // Master Data States
    // =====================================================

    const [customers, setCustomers] = useState([]);
    const [products, setProducts] = useState([]);
    const [warehouses, setWarehouses] = useState([]);

    // =====================================================
    // Sales States
    // =====================================================

    const [salesOrders, setSalesOrders] = useState([]);
    const [dashboard, setDashboard] = useState({});
    const [loading, setLoading] = useState(false);

    const [drawerOpen, setDrawerOpen] = useState(false);
    const [drawerMode, setDrawerMode] = useState("create");
    const [selectedSale, setSelectedSale] = useState(null);

    // =====================================================
    // Filters
    // =====================================================

    const [search, setSearch] = useState("");
    const [customer_id, setCustomerId] = useState("");
    const [warehouse_id, setWarehouseId] = useState("");
    const [date_from, setDateFrom] = useState("");
    const [date_to, setDateTo] = useState("");
    const [payment_status, setPaymentStatus] = useState("");
    // Product / Item filter
    const [product_id, setProductId] = useState("");
    const [page, setPage] = useState(1);

    // =====================================================
    // Pagination
    // =====================================================
    // NEW: Rows per page can be changed from the Sales Table.
    // Existing default remains 10.
    const [page_size, setPageSize] = useState(10);

    const filters = {
        search,
        customer_id,
        warehouse_id,
        payment_status,
        product_id,
        date_from,
        date_to,
        page,
        page_size,
    };

    // =====================================================
    // Set Filters
    // =====================================================

    const setFilters = (newFilters) => {

        if (newFilters.search !== undefined)
            setSearch(newFilters.search);

        if (newFilters.customer_id !== undefined)
            setCustomerId(newFilters.customer_id);

        if (newFilters.warehouse_id !== undefined)
            setWarehouseId(newFilters.warehouse_id);

        if (newFilters.date_from !== undefined)
            setDateFrom(newFilters.date_from);

        if (newFilters.date_to !== undefined)
            setDateTo(newFilters.date_to);

        if (newFilters.payment_status !== undefined)
            setPaymentStatus(newFilters.payment_status);

        if (newFilters.product_id !== undefined)
            setProductId(newFilters.product_id);

        if (newFilters.page !== undefined)
            setPage(newFilters.page);

        // NEW: Rows per page
        if (newFilters.page_size !== undefined) {
            const newPageSize = Number(newFilters.page_size) || 10;

            setPageSize(newPageSize);

            // Changing page size should always start from page 1.
            if (newFilters.page === undefined) {
                setPage(1);
            }
        }
    };

    // =====================================================
    // Update Filter
    // =====================================================

    const updateFilter = (field, value) => {

        switch (field) {

            case "search":
                setSearch(value);
                break;

            case "customer_id":
                setCustomerId(value);
                break;

            case "warehouse_id":
                setWarehouseId(value);
                break;

            case "date_from":
                setDateFrom(value);
                break;

            case "date_to":
                setDateTo(value);
                break;

            case "payment_status":
                setPaymentStatus(value);
                break;

            case "product_id":
                setProductId(value);
                break;

            case "page":
                setPage(value);
                break;

            // NEW: Rows per page
            case "page_size": {
                const newPageSize = Number(value) || 10;

                setPageSize(newPageSize);

                // Start from first page whenever page size changes.
                setPage(1);
                break;
            }

            default:
                break;
        }

        if (field !== "page") {
            setPage(1);
        }
    };

    // =========================================
    // Pending Orders Card Click
    // =========================================
    const handlePendingCardClick = () => {

        const today = new Date();

        const year = today.getFullYear();

        const month = String(
            today.getMonth() + 1
        ).padStart(2, "0");

        const day = String(
            today.getDate()
        ).padStart(2, "0");

        // First day of current month
        const dateFrom = `${year}-${month}-01`;

        // Today
        const dateTo = `${year}-${month}-${day}`;

        setFilters({
            ...filters,

            search: "",

            customer_id: "",

            warehouse_id: "",

            payment_status: "PENDING",

            date_from: dateFrom,

            date_to: dateTo,

            page: 1,
        });
    };

    // =====================================================
    // Sales Form State
    // =====================================================

    const getToday = () => {

        return new Date()
            .toISOString()
            .split("T")[0];

    };

    const getDueDate = (orderDate) => {
        if (!orderDate) {
            return "";
        }

        const date = new Date(orderDate + "T00:00:00");

        date.setDate(date.getDate() + 20);

        return date
            .toISOString()
            .split("T")[0];
    };

    const createEmptyItem = () => ({
        product_id: "",
        quantity: 1,
        selling_price: 0,
        discount_percentage: 0,
        gst_percentage: 18,

        // =================================================
        // Serial Numbers
        // =================================================

        serial_numbers: [],

        remarks: "",
        total: 0,
        _warehouse_stock: 0,
    });

    const createEmptySale = () => {
        const today = getToday();

        return {
            customer_id: "",
            warehouse_id: "",

            // Sales Reference / Reference By
            reference: "",

            // Sales Date
            order_date: today,

            // Due Date = Sales Date + 20 Days
            due_date: getDueDate(today),

            // Expected Delivery Date
            expected_delivery_date: "",

            remarks: "",

            // Payment
            payment_status: "PENDING",
            payment_method: "",
            payment_reference: "",
            paid_amount: 0,

            items: [
                createEmptyItem()
            ],
        };
    };

    const [sale, setSale] = useState(
        createEmptySale()
    );

    // =====================================================
    // Reset Sales Form
    // =====================================================

    const resetSale = () => {

        // A new sale must never retain the ID of a previous sale.
        setSale(
            createEmptySale()
        );

    };

    // =====================================================
    // Drawer Functions
    // =====================================================

    const openCreateDrawer = () => {

        resetSale();

        setDrawerMode("create");
        setSelectedSale(null);
        setDrawerOpen(true);
    };

    // =====================================================
    // Open Edit Drawer
    // =====================================================

    const openEditDrawer = (saleData) => {

        setDrawerMode("edit");

        setSelectedSale(saleData);

        setSale({

            // IMPORTANT:
            // Keep the existing Sales Order ID in the editable form state.
            // This guarantees that an edit can never be treated as a new sale.
            id:
                saleData.id,

            customer_id:
                saleData.customer_id,

            warehouse_id:
                saleData.warehouse_id,

            reference:
                saleData.reference ||
                saleData.reference_by ||
                saleData.reference_name ||
                "",

            order_date:
                saleData.order_date,

            due_date:
                saleData.due_date || getDueDate(saleData.order_date),

            expected_delivery_date:
                saleData.expected_delivery_date || "",

            remarks:
                saleData.remarks || "",

            payment_status:
                saleData.payment_status || "PENDING",

            payment_method:
                saleData.payment_method || "",

            payment_reference:
                saleData.payment_reference || "",

            paid_amount:
                saleData.paid_amount || 0,

            items:
                saleData.items || [],
        });

        setDrawerOpen(true);
    };

    // =====================================================
    // Open View Drawer
    // =====================================================

    const openViewDrawer = (saleData) => {

        setDrawerMode("view");

        setSelectedSale(saleData);

        setSale({

            id:
                saleData.id,

            customer_id:
                saleData.customer_id,

            warehouse_id:
                saleData.warehouse_id,

            reference:
                saleData.reference ||
                saleData.reference_by ||
                saleData.reference_name ||
                "",

            order_date:
                saleData.order_date,

            due_date:
                saleData.due_date || getDueDate(saleData.order_date),

            expected_delivery_date:
                saleData.expected_delivery_date || "",

            remarks:
                saleData.remarks || "",

            payment_status:
                saleData.payment_status || "PENDING",

            payment_method:
                saleData.payment_method || "",

            payment_reference:
                saleData.payment_reference || "",

            paid_amount:
                saleData.paid_amount || 0,

            items:
                saleData.items || [],
        });

        setDrawerOpen(true);
    };

    // =====================================================
    // Close Drawer
    // =====================================================

    const closeDrawer = () => {

        setDrawerOpen(false);

    };

    // =====================================================
    // Load Customers
    // =====================================================

    const loadCustomers = async () => {

        try {

            const response =
                await SalesService.getCustomers();

            console.log(
                "CUSTOMERS API RESPONSE:",
                response
            );

            let customerList = [];

            if (Array.isArray(response)) {

                customerList = response;

            } else if (
                Array.isArray(response?.data)
            ) {

                customerList = response.data;

            } else if (
                Array.isArray(response?.items)
            ) {

                customerList = response.items;

            } else if (
                Array.isArray(response?.customers)
            ) {

                customerList =
                    response.customers;
            }

            setCustomers(customerList);

        } catch (error) {

            console.error(
                "Failed to load customers:",
                error
            );

            setCustomers([]);
        }
    };

    // =====================================================
    // Load Products
    // =====================================================

    const loadProducts = async () => {

        try {

            const data =
                await SalesService.getProducts();

            if (Array.isArray(data)) {

                setProducts(data);

            } else if (
                Array.isArray(data?.items)
            ) {

                setProducts(data.items);

            } else if (
                Array.isArray(data?.products)
            ) {

                setProducts(data.products);

            } else {

                setProducts([]);
            }

        } catch (error) {

            console.error(
                "Failed to load products:",
                error
            );

            setProducts([]);
        }
    };

    // =====================================================
    // Load Warehouses
    // =====================================================

    const loadWarehouses = async () => {

        try {

            const response =
                await SalesService.getWarehouses();

            console.log(
                "WAREHOUSE API:",
                response
            );

            if (Array.isArray(response)) {

                setWarehouses(response);

            } else if (
                Array.isArray(response?.items)
            ) {

                setWarehouses(
                    response.items
                );

            } else if (
                Array.isArray(response?.data)
            ) {

                setWarehouses(
                    response.data
                );

            } else {

                setWarehouses([]);
            }

        } catch (error) {

            console.error(
                "Failed to load warehouses:",
                error
            );

            setWarehouses([]);
        }
    };

    // =====================================================
    // Load Sales Orders
    // =====================================================

    const loadSalesOrders = async () => {

        try {

            setLoading(true);

            const params = {
                page,
                // NEW: Use the selected rows-per-page value.
                page_size,
            };

            // Search:
            // Order number
            // Customer name
            // Customer code

            if (search?.trim()) {

                params.search =
                    search.trim();
            }

            // Customer

            if (customer_id) {

                params.customer_id =
                    Number(customer_id);
            }

            // Warehouse

            if (warehouse_id) {

                params.warehouse_id =
                    Number(warehouse_id);
            }

            // Payment Status
            if (payment_status) {
                params.payment_status =
                    payment_status;
            }

            // Item / Product
            // The backend should receive the selected product id
            // as product_id. This filters sales orders containing
            // that product.
            if (product_id) {
                params.product_id = Number(product_id);
            }

            // From date

            if (date_from) {

                params.date_from =
                    date_from;
            }

            // To date

            if (date_to) {

                params.date_to =
                    date_to;
            }

            console.log(
                "Loading Sales Orders:",
                params
            );

            const data =
                await SalesService.getSalesOrders(
                    params
                );

            console.log(
                "Sales Orders API Response:",
                data
            );

            if (Array.isArray(data)) {

                setSalesOrders(data);

            } else if (
                Array.isArray(
                    data?.sales_orders
                )
            ) {

                setSalesOrders(
                    data.sales_orders
                );

            } else if (
                Array.isArray(data?.items)
            ) {

                setSalesOrders(
                    data.items
                );

            } else {

                setSalesOrders([]);
            }

        } catch (error) {

            console.error(
                "Failed to load sales orders:",
                error
            );

            console.error(
                "Status:",
                error.response?.status
            );

            console.error(
                "Response:",
                error.response?.data
            );

            setSalesOrders([]);

        } finally {

            setLoading(false);
        }
    };

    // =====================================================
    // Load Dashboard
    // =====================================================

    const loadDashboard = async () => {

        try {

            console.log(
                "Loading Sales Dashboard..."
            );

            const data =
                await SalesService.getDashboard();

            console.log(
                "SALES DASHBOARD RESPONSE:",
                data
            );

            if (data) {

                setDashboard({

                    // Existing backend fields
                    total_sales_orders:
                        Number(
                            data.total_sales_orders || 0
                        ),

                    draft_sales_orders:
                        Number(
                            data.draft_sales_orders || 0
                        ),

                    confirmed_sales_orders:
                        Number(
                            data.confirmed_sales_orders || 0
                        ),

                    delivered_sales_orders:
                        Number(
                            data.delivered_sales_orders || 0
                        ),

                    cancelled_sales_orders:
                        Number(
                            data.cancelled_sales_orders || 0
                        ),

                    sales_value:
                        Number(
                            data.sales_value || 0
                        ),

                    // New dashboard fields
                    todays_sales:
                        Number(
                            data.todays_sales ?? 0
                        ),

                    todays_orders:
                        Number(
                            data.todays_orders ?? 0
                        ),

                    todays_sales_count:
                        Number(
                            data.todays_sales_count ?? 0
                        ),

                    pending_orders:
                        Number(
                            data.pending_orders ?? 0
                        ),

                    unpaid_invoices:
                        Number(
                            data.unpaid_invoices ?? 0
                        ),

                    pending_payment_amount:
                        Number(
                            data.pending_payment_amount ?? 0
                        ),

                    pending_deliveries:
                        Number(
                            data.pending_deliveries ?? 0
                        ),

                    monthly_revenue:
                        Number(
                            data.monthly_revenue ?? 0
                        ),
                });

            } else {

                setDashboard({});
            }

        } catch (error) {

            console.error(
                "SALES DASHBOARD API ERROR:",
                error
            );

            console.error(
                "Status:",
                error.response?.status
            );

            console.error(
                "Response:",
                error.response?.data
            );

            setDashboard({});
        }
    };

    // =====================================================
    // Load Dashboard + Sales Orders
    // =====================================================

    useEffect(() => {

        loadSalesOrders();

        // Dashboard is independent of filters.
        // It should not reload every time the
        // search/date filter changes.

        // eslint-disable-next-line react-hooks/exhaustive-deps

    }, [
        search,
        customer_id,
        warehouse_id,
        payment_status,
        product_id,
        date_from,
        date_to,
        page,
        page_size,
    ]);

    // =====================================================
    // Initial Load
    // =====================================================

    useEffect(() => {

        loadCustomers();
        loadProducts();
        loadWarehouses();
        loadDashboard();

        // Sales orders are loaded by the
        // filter useEffect above.

        // eslint-disable-next-line react-hooks/exhaustive-deps

    }, []);

    // =====================================================
    // Update Sale Field
    // =====================================================

    const updateField = async (
        field,
        value
    ) => {

        // =================================================
        // Sales Date Changed
        // =================================================

        if (field === "order_date") {

            setSale((prev) => ({
                ...prev,

                // Update Sales Date
                order_date: value,

                // Automatically calculate:
                // Sales Date + 20 Days
                due_date: getDueDate(value),
            }));

            return;
        }


        // =================================================
        // Normal Field Update
        // =================================================

        setSale((prev) => ({
            ...prev,
            [field]: value,
        }));

        // =================================================
        // Warehouse Changed
        // =================================================

        if (
            field === "warehouse_id" &&
            value
        ) {

            const currentItems =
                sale.items;

            currentItems.forEach(
                async (item, index) => {

                    if (!item.product_id) {
                        return;
                    }

                    try {

                        const stock =
                            await SalesService
                                .getCurrentStock(
                                    item.product_id,
                                    value
                                );

                        setSale((prev) => {

                            const newItems =
                                [...prev.items];

                            if (
                                newItems[index]
                            ) {

                                newItems[index] = {

                                    ...newItems[index],

                                    _warehouse_stock:
                                        stock,
                                };
                            }

                            return {

                                ...prev,

                                items:
                                    newItems,
                            };
                        });

                    } catch (error) {

                        console.error(
                            "Failed to fetch stock:",
                            error
                        );
                    }
                }
            );
        }
    };

    // =====================================================
    // Add Item
    // =====================================================

    const addItem = () => {

        setSale((prev) => ({

            ...prev,

            items: [
                ...prev.items,
                createEmptyItem(),
            ],

        }));
    };

    // =====================================================
    // Remove Item
    // =====================================================

    const removeItem = (index) => {

        setSale((prev) => {

            const items =
                [...prev.items];

            items.splice(index, 1);

            return {
                ...prev,
                items,
            };
        });
    };

    // =====================================================
    // Update Item
    // =====================================================

    const updateItem = async (
        index,
        field,
        value
    ) => {

        let updatedItem;

        setSale((prev) => {

            const items =
                [...prev.items];

            updatedItem = {
                ...items[index],
                [field]: value,
            };

            // =================================================
            // Calculate Item Total
            // =================================================

            const quantity =
                Number(
                    updatedItem.quantity
                ) || 0;

            const selling_price =
                Number(
                    updatedItem.selling_price
                ) || 0;

            const discount_percentage =
                Number(
                    updatedItem.discount_percentage
                ) || 0;

            const gst_percentage =
                Number(
                    updatedItem.gst_percentage
                ) || 0;

            const amount =
                quantity *
                selling_price;

            const discount =
                amount *
                (
                    discount_percentage /
                    100
                );

            const taxable =
                amount -
                discount;

            const gst =
                taxable *
                (
                    gst_percentage /
                    100
                );

            updatedItem.total =
                taxable + gst;

            items[index] =
                updatedItem;

            return {
                ...prev,
                items,
            };
        });

        // =================================================
        // Product Changed
        // =================================================

        if (
            field === "product_id" &&
            value &&
            sale.warehouse_id
        ) {

            try {

                const stock =
                    await SalesService
                        .getCurrentStock(
                            value,
                            sale.warehouse_id
                        );

                setSale((prev) => {

                    const newItems =
                        [...prev.items];

                    if (
                        newItems[index]
                    ) {

                        newItems[index] = {

                            ...newItems[index],

                            _warehouse_stock:
                                stock,
                        };
                    }

                    return {

                        ...prev,

                        items:
                            newItems,
                    };
                });

            } catch (error) {

                console.error(
                    "Failed to fetch stock:",
                    error
                );
            }
        }
    };

    // =====================================================
    // Calculate Grand Total
    // =====================================================
    //
    // IMPORTANT:
    // Do NOT depend on item.total here. The form can display the
    // correct total while item.total is still 0 in the context
    // state. Calculate the same amount directly from the raw
    // item values so payment validation and the API payload use
    // the real invoice total.
    //

    const grandTotal =
        sale.items.reduce(
            (sum, item) => {

                const quantity =
                    Number(
                        item.quantity
                    ) || 0;

                const sellingPrice =
                    Number(
                        item.selling_price
                    ) || 0;

                const discountPercentage =
                    Number(
                        item.discount_percentage
                    ) || 0;

                const gstPercentage =
                    Number(
                        item.gst_percentage
                    ) || 0;

                const amount =
                    quantity *
                    sellingPrice;

                const discountAmount =
                    amount *
                    (
                        discountPercentage /
                        100
                    );

                const taxableAmount =
                    amount -
                    discountAmount;

                const gstAmount =
                    taxableAmount *
                    (
                        gstPercentage /
                        100
                    );

                const itemTotal =
                    taxableAmount +
                    gstAmount;

                return sum + itemTotal;
            },
            0
        );

    // =====================================================
    // Normalize Payment Status
    // =====================================================

    const getNormalizedPaymentStatus = () => {

        return String(
            sale.payment_status ||
            "PENDING"
        )
            .trim()
            .toUpperCase()
            .replace(/\s+/g, "_");
    };

    // =====================================================
    // Calculate Paid Amount
    // =====================================================
    //
    // Fully received payments must always equal the
    // grand total. The backend validates this rule.
    //
    // PENDING payments = 0
    // Fully received payments = grand total
    // Partial payments = entered paid amount
    //
    // =====================================================

    const validatePayment = () => {

        const paymentStatus =
            getNormalizedPaymentStatus();

        const paidAmount =
            getPaidAmountForPayload();

        const total =
            Number(
                Number(grandTotal || 0).toFixed(2)
            );

        const partialPaymentStatuses = [
            "PARTIALLY_RECEIVED_BY_HAND",
            "PARTIALLY_RECEIVED_TO_ACCOUNT",
        ];

        const fullPaymentStatuses = [
            "RECEIVED_BY_HAND",
            "RECEIVED_TO_ACCOUNT",
        ];

        if (
            partialPaymentStatuses.includes(
                paymentStatus
            ) &&
            paidAmount <= 0
        ) {
            alert(
                "For a partially received payment, the paid amount must be greater than 0."
            );
            return false;
        }

        if (
            partialPaymentStatuses.includes(
                paymentStatus
            ) &&
            paidAmount >= total
        ) {
            alert(
                "For a partially received payment, the paid amount must be less than the grand total."
            );
            return false;
        }

        if (
            fullPaymentStatuses.includes(
                paymentStatus
            ) &&
            Number(
                paidAmount.toFixed(2)
            ) !==
                Number(
                    total.toFixed(2)
                )
        ) {
            alert(
                "For a fully received payment, the paid amount must equal the grand total."
            );
            return false;
        }

        return true;
    };

    const getPaidAmountForPayload = () => {

        const paymentStatus =
            getNormalizedPaymentStatus();

        const fullPaymentStatuses = [
            "RECEIVED_BY_HAND",
            "RECEIVED_TO_ACCOUNT",
        ];

        const partialPaymentStatuses = [
            "PARTIALLY_RECEIVED_BY_HAND",
            "PARTIALLY_RECEIVED_TO_ACCOUNT",
        ];

        // Fully received payment: paid amount MUST equal grand total.
        if (
            fullPaymentStatuses.includes(
                paymentStatus
            )
        ) {
            return Number(
                Number(grandTotal || 0).toFixed(2)
            );
        }

        // Pending payment: paid amount MUST be zero.
        if (
            paymentStatus === "PENDING"
        ) {
            return 0;
        }

        // Partially received payment: use the amount entered by the user.
        // This fixes the previous bug where partial statuses were falling
        // through to zero even when the form contained ₹1000, etc.
        if (
            partialPaymentStatuses.includes(
                paymentStatus
            )
        ) {
            return Number(
                Number(sale.paid_amount || 0).toFixed(2)
            );
        }

        // Safe fallback for any future payment status.
        return Number(
            Number(sale.paid_amount || 0).toFixed(2)
        );
    };

    // =====================================================
    // Save Sale
    // =====================================================

    const saveSale = async () => {

        try {

            if (!validatePayment()) {
                return null;
            }

            // =================================================
            // IMPORTANT:
            // Decide CREATE vs UPDATE using BOTH drawerMode and
            // selectedSale.id.
            //
            // This prevents an existing sale from accidentally
            // being sent to POST /sales-orders/.
            // =================================================

            const existingSalesOrderId =
                selectedSale?.id ??
                sale?.id ??
                null;

            if (
                drawerMode === "edit" ||
                existingSalesOrderId !== null
            ) {

                if (
                    existingSalesOrderId === null ||
                    existingSalesOrderId === undefined ||
                    existingSalesOrderId === ""
                ) {
                    throw new Error(
                        "Sales Order ID is missing. Cannot update the existing sale."
                    );
                }

                console.log(
                    "========== UPDATE EXISTING SALE =========="
                );

                console.log(
                    "Sales Order ID:",
                    existingSalesOrderId
                );

                const response =
                    await updateSale(
                        existingSalesOrderId
                    );

                return response;
            }

            // =====================================================
            // Get only selected products
            // =====================================================

            const validItems = sale.items.filter(
                (item) =>
                    item.product_id !== null &&
                    item.product_id !== undefined &&
                    item.product_id !== "" &&
                    Number(item.product_id) > 0
            );

            // =====================================================
            // Make sure at least one product is selected
            // =====================================================

            if (validItems.length === 0) {
                alert("Please select at least one product.");
                return;
            }

            // =====================================================
            // Prevent duplicate products
            // =====================================================

            const productIds = validItems.map(
                (item) => Number(item.product_id)
            );

            const uniqueProductIds = new Set(productIds);

            if (uniqueProductIds.size !== productIds.length) {
                alert(
                    "Duplicate products are not allowed in a Sales Order. Please select each product only once."
                );

                return;
            }

            // =================================================
            // Create Payload
            // =================================================

            const payload = {
                customer_id: Number(sale.customer_id),
            
                warehouse_id: Number(sale.warehouse_id),

                // Sales Reference / Reference By
                reference: String(
                    sale.reference ??
                    sale.reference_by ??
                    sale.reference_name ??
                    ""
                ).trim() || null,
            
                order_date: sale.order_date,
            
                due_date:
                    sale.due_date || null,
            
                expected_delivery_date:
                    sale.expected_delivery_date || null,
            
                remarks:
                    sale.remarks || "",
            
                payment_status:
                    sale.payment_status || "PENDING",
            
                payment_method:
                    sale.payment_method || null,
            
                payment_reference:
                    sale.payment_reference || null,
            
                paid_amount:
                    getPaidAmountForPayload(),
            
                items: validItems.map(
                    (item) => ({
                        product_id:
                            Number(item.product_id),
            
                        quantity:
                            Number(item.quantity),
            
                        selling_price:
                            Number(item.selling_price || 0),
            
                        discount_percentage:
                            Number(
                                item.discount_percentage || 0
                            ),
            
                        gst_percentage:
                            Number(
                                item.gst_percentage || 18
                            ),
            
                        serial_numbers:
                            Array.isArray(
                                item.serial_numbers
                            )
                                ? item.serial_numbers
                                    .map((serial) =>
                                        String(serial).trim()
                                    )
                                    .filter(Boolean)
                                : [],
            
                        remarks:
                            item.remarks || "",
                    })
                ),
            };

            console.log(
                "CREATE SALES ORDER PAYMENT STATUS:",
                getNormalizedPaymentStatus()
            );

            console.log(
                "CREATE SALES ORDER PAID AMOUNT:",
                payload.paid_amount
            );

            console.log(
                "CREATE SALES ORDER PAYLOAD:",
                payload
            );

            // =================================================
            // SAFETY:
            // If an existing ID appears here, this is not a new
            // sale. Refuse to POST a duplicate sales order.
            // =================================================

            if (
                sale?.id !== undefined &&
                sale?.id !== null &&
                sale?.id !== ""
            ) {
                throw new Error(
                    "An existing Sales Order ID was found while creating a sale. Please use Update Sale instead."
                );
            }

            // =================================================
            // API
            // =================================================

            const response =
                await SalesService.createSale(
                    payload
                );

            // Notify InventoryContext that stock may have changed.
            // This runs only after the backend successfully creates the sale.
            window.dispatchEvent(
                new Event("erp:inventory-refresh")
            );

            // =================================================
            // Refresh Sales Orders
            // =================================================

            await loadSalesOrders();

            // =================================================
            // Refresh Dashboard
            // =================================================

            await loadDashboard();

            // =================================================
            // Close
            // =================================================

            closeDrawer();

            resetSale();

            alert(
                "Sale Saved Successfully"
            );

            // Return the created sales order response.
            // SalesForm uses this response to get the
            // newly-created sales order ID and then calls
            // the PDF endpoint. The backend PDF endpoint
            // stores the generated PDF in PostgreSQL and
            // returns the same PDF for local download.

            return response;

        } catch (error) {

            console.error(
                "SAVE SALES ORDER ERROR:",
                error
            );

            console.error(
                "STATUS:",
                error.response?.status
            );

            console.error(
                "RESPONSE:",
                error.response?.data
            );

            alert(
                error.response?.data?.detail ||
                "Failed to Save Sale"
            );

            return null;
        }
    };

    // =====================================================
    // Update Sale
    // =====================================================

    const updateSale = async (
        salesOrderIdOverride = null
    ) => {

        try {

            if (!validatePayment()) {
                return null;
            }

            // =================================================
            // Always use the actual existing Sales Order ID.
            // =================================================

            const salesOrderId =
                salesOrderIdOverride ??
                selectedSale?.id ??
                sale?.id ??
                null;

            if (
                salesOrderId === null ||
                salesOrderId === undefined ||
                salesOrderId === ""
            ) {
                throw new Error(
                    "Sales Order ID is missing. Cannot update the existing sale."
                );
            }

            // =================================================
            // Validate customer and warehouse
            // =================================================

            if (
                !sale.customer_id ||
                !sale.warehouse_id
            ) {
                alert(
                    "Please select customer and warehouse."
                );
                return null;
            }

            // =================================================
            // Get selected products
            // =================================================

            const validItems = (
                Array.isArray(sale.items)
                    ? sale.items
                    : []
            ).filter(
                (item) =>
                    item.product_id !== null &&
                    item.product_id !== undefined &&
                    item.product_id !== "" &&
                    Number(item.product_id) > 0
            );

            if (validItems.length === 0) {
                alert(
                    "Please select at least one product."
                );
                return null;
            }

            // =================================================
            // Validate quantities
            // =================================================

            for (const item of validItems) {

                const quantity =
                    Number(item.quantity);

                if (
                    !Number.isInteger(quantity) ||
                    quantity <= 0
                ) {
                    alert(
                        "Each product quantity must be a whole number greater than 0."
                    );
                    return null;
                }
            }

            // =================================================
            // Prevent duplicate products
            // =================================================

            const productIds =
                validItems.map(
                    (item) =>
                        Number(item.product_id)
                );

            const uniqueProductIds =
                new Set(productIds);

            if (
                uniqueProductIds.size !==
                productIds.length
            ) {
                alert(
                    "Duplicate products are not allowed in a Sales Order. Please select each product only once."
                );
                return null;
            }

            // =================================================
            // Build complete update payload
            // =================================================

            const payload = {

                customer_id:
                    Number(
                        sale.customer_id
                    ),

                warehouse_id:
                    Number(
                        sale.warehouse_id
                    ),

                // Sales Reference / Reference By
                reference:
                    String(
                        sale.reference ??
                        sale.reference_by ??
                        sale.reference_name ??
                        ""
                    ).trim() || null,

                order_date:
                    sale.order_date,

                due_date:
                    sale.due_date || null,

                expected_delivery_date:
                    sale.expected_delivery_date ||
                    null,

                remarks:
                    sale.remarks || "",

                payment_status:
                    sale.payment_status ||
                    "PENDING",

                payment_method:
                    sale.payment_method ||
                    null,

                payment_reference:
                    sale.payment_reference ||
                    null,

                paid_amount:
                    getPaidAmountForPayload(),

                // IMPORTANT:
                // Send the products and quantities during
                // Update Sale so the backend can reconcile
                // inventory correctly.

                items: validItems.map(
                    (item) => ({

                        product_id:
                            Number(
                                item.product_id
                            ),

                        quantity:
                            Number(
                                item.quantity
                            ),

                        selling_price:
                            Number(
                                item.selling_price || 0
                            ),

                        discount_percentage:
                            Number(
                                item.discount_percentage ||
                                0
                            ),

                        gst_percentage:
                            Number(
                                item.gst_percentage ||
                                18
                            ),

                        serial_numbers:
                            Array.isArray(
                                item.serial_numbers
                            )
                                ? item.serial_numbers
                                    .map(
                                        (serial) =>
                                            String(
                                                serial
                                            ).trim()
                                    )
                                    .filter(Boolean)
                                : [],

                        remarks:
                            item.remarks || "",
                    })
                ),
            };

            console.log(
                "UPDATE SALES ORDER PAYMENT STATUS:",
                getNormalizedPaymentStatus()
            );

            console.log(
                "UPDATE SALES ORDER PAID AMOUNT:",
                payload.paid_amount
            );

            console.log(
                "UPDATE SALES ORDER PAYLOAD:",
                payload
            );

            console.log(
                "UPDATE SALES ORDER ID:",
                salesOrderId
            );

            // =================================================
            // IMPORTANT:
            // Existing sale MUST use PUT /sales-orders/{id}.
            // Never call createSale() from this path.
            // =================================================

            const response =
                await SalesService.updateSale(
                    salesOrderId,
                    payload
                );

            // Notify InventoryContext that stock may have changed.
            // This runs only after the backend successfully updates the sale.
            window.dispatchEvent(
                new Event("erp:inventory-refresh")
            );

            console.log(
                "UPDATE SALES ORDER RESPONSE:",
                response
            );

            // =================================================
            // Refresh table
            // =================================================

            await loadSalesOrders();

            // =================================================
            // Refresh dashboard
            // =================================================

            await loadDashboard();

            // =================================================
            // Close drawer
            // =================================================

            closeDrawer();

            resetSale();

            alert(
                "Sale Updated Successfully"
            );

            return response;

        } catch (error) {

            console.error(
                "UPDATE SALES ORDER ERROR:",
                error
            );

            console.error(
                "STATUS:",
                error.response?.status
            );

            console.error(
                "RESPONSE:",
                error.response?.data
            );

            alert(
                error.response?.data?.detail ||
                "Failed to Update Sale"
            );

            return null;
        }
    };

    // =====================================================
    // Delete / Cancel Sale
    // =====================================================

    const deleteSale = async (
        saleId
    ) => {

        const confirmDelete =
            window.confirm(
                "Are you sure you want to cancel this sales order?"
            );

        if (!confirmDelete) {
            return;
        }

        try {

            await SalesService.deleteSale(
                saleId
            );

            // Refresh table
            await loadSalesOrders();

            // Refresh dashboard
            await loadDashboard();

            alert(
                "Sales Order Cancelled Successfully"
            );

        } catch (error) {

            console.error(
                "DELETE SALES ORDER ERROR:",
                error
            );

            alert(
                error.response?.data?.detail ||
                "Failed to Cancel Sales Order"
            );
        }
    };

    // =====================================================
    // Export Sales
    // =====================================================

    const exportSales = async () => {

        try {

            const blob =
                await SalesService
                    .exportSalesOrders(
                        filters
                    );

            const url =
                window.URL
                    .createObjectURL(blob);

            const link =
                document.createElement(
                    "a"
                );

            link.href = url;

            link.download =
                "sales_orders.xlsx";

            document.body.appendChild(
                link
            );

            link.click();

            link.remove();

            window.URL.revokeObjectURL(
                url
            );

        } catch (error) {

            console.error(
                "EXPORT SALES ERROR:",
                error
            );

            alert(
                "Failed to export sales orders."
            );
        }
    };

    // =====================================================
    // Context
    // =====================================================

    return (

        <SalesContext.Provider
            value={{

                // =================================================
                // Dashboard
                // =================================================

                dashboard,

                loadDashboard,

                // =================================================
                // Sales
                // =================================================

                salesOrders,

                loading,

                // =================================================
                // Filters
                // =================================================

                filters,

                setFilters,

                updateFilter,

                handlePendingCardClick,

                // =================================================
                // Loaders
                // =================================================

                loadSalesOrders,

                // =================================================
                // Drawer
                // =================================================

                drawerOpen,

                drawerMode,

                selectedSale,

                openCreateDrawer,

                openEditDrawer,

                openViewDrawer,

                closeDrawer,

                // =================================================
                // Sale
                // =================================================

                sale,

                saveSale,

                updateSale,

                deleteSale,

                updateField,

                addItem,

                removeItem,

                updateItem,

                // =================================================
                // Master Data
                // =================================================

                customers,

                warehouses,

                products,

                // =================================================
                // Totals
                // =================================================

                grandTotal,

                // =================================================
                // Export
                // =================================================

                exportSales,

                // =================================================
                // Individual Filters
                // =================================================

                setSearch,

                setCustomerId,

                setWarehouseId,

                setDateFrom,

                setDateTo,

                setPaymentStatus,

                setProductId,

                // =================================================
                // Pagination
                // =================================================

                page_size,
                setPageSize,
            }}
        >

            {children}

        </SalesContext.Provider>
    );
};

export const useSales = () =>
    useContext(SalesContext);