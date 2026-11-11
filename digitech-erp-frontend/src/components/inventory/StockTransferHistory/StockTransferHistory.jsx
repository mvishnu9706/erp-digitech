import "./StockTransferHistory.css";

import {
    X,
    Search,
    RotateCcw,
    CalendarDays,
    ArrowRightLeft,
    Eye,
    Download,
} from "lucide-react";

import { useEffect, useState } from "react";

import * as XLSX from "xlsx";

import { getStockTransferHistory } from "../../../services/inventoryService";

import { useWarehouses } from "../../../context/WarehouseContext";

import { useProducts } from "../../../context/ProductContext";


const StockTransferHistory = () => {

    // =====================================================
    // Drawer
    // =====================================================

    const [open, setOpen] = useState(false);


    // =====================================================
    // Warehouses / Products
    // =====================================================

    const {
        warehouses = [],
    } = useWarehouses();

    const {
        products = [],
    } = useProducts();


    // =====================================================
    // History
    // =====================================================

    const [history, setHistory] = useState([]);

    const [loading, setLoading] = useState(false);

    const [totalTransfers, setTotalTransfers] = useState(0);


    // =====================================================
    // Filters
    // =====================================================

    const [filters, setFilters] = useState({

        search: "",

        from_date: "",

        to_date: "",

        product_id: "",

        from_warehouse_id: "",

        to_warehouse_id: "",

        reference_by: "",

        activity: "",

    });


    // =====================================================
    // Pagination
    // =====================================================

    const [page, setPage] = useState(1);

    const pageSize = 10;


    // =====================================================
    // Open History
    // =====================================================

    useEffect(() => {

        const handleOpenHistory = () => {

            setOpen(true);

        };


        window.addEventListener(
            "openTransferHistory",
            handleOpenHistory
        );


        return () => {

            window.removeEventListener(
                "openTransferHistory",
                handleOpenHistory
            );

        };

    }, []);


    // =====================================================
    // Load History
    // =====================================================

    const loadHistory = async () => {

        try {

            setLoading(true);


            const params = {

                page,

                page_size: pageSize,

                search:
                    filters.search ||
                    undefined,

                from_date:
                    filters.from_date ||
                    undefined,

                to_date:
                    filters.to_date ||
                    undefined,

                product_id:
                    filters.product_id
                        ? Number(filters.product_id)
                        : undefined,

                from_warehouse_id:
                    filters.from_warehouse_id
                        ? Number(filters.from_warehouse_id)
                        : undefined,

                to_warehouse_id:
                    filters.to_warehouse_id
                        ? Number(filters.to_warehouse_id)
                        : undefined,

                reference_by:
                    filters.reference_by ||
                    undefined,

                activity:
                    filters.activity ||
                    undefined,

            };


            const response =
                await getStockTransferHistory(
                    params
                );


            const data =
                response?.data || {};


            setHistory(
                data.items || []
            );


            setTotalTransfers(
                data.total || 0
            );


        } catch (error) {

            console.error(
                "Failed to load stock transfer history:",
                error
            );


            setHistory([]);

            setTotalTransfers(0);

        } finally {

            setLoading(false);

        }

    };


    // =====================================================
    // Load When Drawer Opens / Filters Change
    // =====================================================

    useEffect(() => {

        if (!open) {
            return;
        }


        loadHistory();

    }, [
        open,
        page,
        filters.search,
        filters.from_date,
        filters.to_date,
        filters.product_id,
        filters.from_warehouse_id,
        filters.to_warehouse_id,
        filters.reference_by,
        filters.activity,
    ]);


    // =====================================================
    // Filter Change
    // =====================================================

    const handleFilterChange = (
        name,
        value
    ) => {

        setFilters(
            (previous) => ({
                ...previous,
                [name]: value,
            })
        );


        setPage(1);

    };


    // =====================================================
    // Reset
    // =====================================================

    const handleReset = () => {

        setFilters({

            search: "",

            from_date: "",

            to_date: "",

            product_id: "",

            from_warehouse_id: "",

            to_warehouse_id: "",

            reference_by: "",

            activity: "",

        });


        setPage(1);

    };


    // =====================================================
    // Close
    // =====================================================

    const handleClose = () => {

        setOpen(false);

    };


    // =====================================================
    // Export Excel
    // =====================================================

    const handleExportExcel = () => {

        if (
            !history ||
            history.length === 0
        ) {

            alert(
                "There is no stock transfer history to export."
            );

            return;

        }


        // -------------------------------------------------
        // Excel Data
        // -------------------------------------------------

        const excelData =
            history.map(
                (item, index) => ({

                    "S.No":
                        (
                            page - 1
                        ) *
                            pageSize +
                        index +
                        1,

                    "Date & Time":
                        item.created_at ||
                        "",

                    "Transfer No.":
                        item.transaction_number ||
                        "",

                    "Item":
                        item.product_name ||
                        item.product?.product_name ||
                        "",

                    "From Warehouse":
                        item.from_warehouse ||
                        "",

                    "To Warehouse":
                        item.to_warehouse ||
                        "",

                    "Quantity":
                        item.quantity ??
                        "",

                    "Reference By":
                        item.reference_by ||
                        "",

                    "Activity":
                        item.activity ||
                        "Created",

                    "Created By":
                        item.created_by_name ||
                        item.created_by ||
                        "",

                    "Remarks":
                        item.remarks ||
                        "",

                })
            );


        // -------------------------------------------------
        // Worksheet
        // -------------------------------------------------

        const worksheet =
            XLSX.utils.json_to_sheet(
                excelData
            );


        // -------------------------------------------------
        // Column Widths
        // -------------------------------------------------

        worksheet["!cols"] = [

            {
                wch: 8,
            },

            {
                wch: 22,
            },

            {
                wch: 25,
            },

            {
                wch: 30,
            },

            {
                wch: 25,
            },

            {
                wch: 25,
            },

            {
                wch: 12,
            },

            {
                wch: 22,
            },

            {
                wch: 15,
            },

            {
                wch: 20,
            },

            {
                wch: 40,
            },

        ];


        // -------------------------------------------------
        // Workbook
        // -------------------------------------------------

        const workbook =
            XLSX.utils.book_new();


        XLSX.utils.book_append_sheet(
            workbook,
            worksheet,
            "Transfer History"
        );


        // -------------------------------------------------
        // File Name
        // -------------------------------------------------

        const today =
            new Date();


        const year =
            today.getFullYear();


        const month =
            String(
                today.getMonth() + 1
            ).padStart(
                2,
                "0"
            );


        const day =
            String(
                today.getDate()
            ).padStart(
                2,
                "0"
            );


        const fileName =
            `Stock_Transfer_History_${year}${month}${day}.xlsx`;


        // -------------------------------------------------
        // Download
        // -------------------------------------------------

        XLSX.writeFile(
            workbook,
            fileName
        );

    };


    // =====================================================
    // View Transfer
    // =====================================================

    const handleView = (
        item
    ) => {

        console.log(
            "View Stock Transfer:",
            item
        );

    };


    // =====================================================
    // Calculate Total Pages
    // =====================================================

    const totalPages =
        Math.max(
            1,
            Math.ceil(
                totalTransfers /
                pageSize
            )
        );


    // =====================================================
    // Drawer
    // =====================================================

    if (!open) {

        return null;

    }


    return (

        <div className="stock-history-overlay">

            <div className="stock-history-drawer">


                {/* =================================================
                    Header
                ================================================= */}

                <div className="stock-history-header">

                    <div className="stock-history-title">

                        <div className="stock-history-title-icon">

                            <ArrowRightLeft
                                size={20}
                            />

                        </div>


                        <div>

                            <h2>
                                Stock Transfer History
                            </h2>

                            <p>
                                View and filter all stock
                                transfer activities.
                            </p>

                        </div>

                    </div>


                    <button
                        type="button"
                        className="stock-history-close"
                        onClick={handleClose}
                    >

                        <X size={22} />

                    </button>

                </div>


                {/* =================================================
                    Filters
                ================================================= */}

                <div className="stock-history-filters">


                    {/* Search */}

                    <div className="stock-history-search">

                        <Search
                            size={18}
                        />

                        <input
                            type="text"
                            placeholder="Search transfer no, item, reference..."
                            value={
                                filters.search
                            }
                            onChange={(e) =>
                                handleFilterChange(
                                    "search",
                                    e.target.value
                                )
                            }
                        />

                    </div>


                    {/* From Date */}

                    <div className="stock-history-filter-group">

                        <label>
                            From Date
                        </label>

                        <div className="stock-history-date-input">

                            <input
                                type="date"
                                value={
                                    filters.from_date
                                }
                                onChange={(e) =>
                                    handleFilterChange(
                                        "from_date",
                                        e.target.value
                                    )
                                }
                            />

                            <CalendarDays
                                size={16}
                            />

                        </div>

                    </div>


                    {/* To Date */}

                    <div className="stock-history-filter-group">

                        <label>
                            To Date
                        </label>

                        <div className="stock-history-date-input">

                            <input
                                type="date"
                                value={
                                    filters.to_date
                                }
                                onChange={(e) =>
                                    handleFilterChange(
                                        "to_date",
                                        e.target.value
                                    )
                                }
                            />

                            <CalendarDays
                                size={16}
                            />

                        </div>

                    </div>


                    {/* Product */}

                    <div className="stock-history-filter-group">

                        <label>
                            Item
                        </label>

                        <select
                            value={
                                filters.product_id
                            }
                            onChange={(e) =>
                                handleFilterChange(
                                    "product_id",
                                    e.target.value
                                )
                            }
                        >

                            <option value="">
                                All Items
                            </option>

                            {products.map(
                                (product) => (

                                    <option
                                        key={
                                            product.id
                                        }
                                        value={
                                            product.id
                                        }
                                    >

                                        {
                                            product.product_name
                                        }

                                    </option>

                                )
                            )}

                        </select>

                    </div>


                    {/* From Warehouse */}

                    <div className="stock-history-filter-group">

                        <label>
                            From Warehouse
                        </label>

                        <select
                            value={
                                filters.from_warehouse_id
                            }
                            onChange={(e) =>
                                handleFilterChange(
                                    "from_warehouse_id",
                                    e.target.value
                                )
                            }
                        >

                            <option value="">
                                All Warehouses
                            </option>

                            {warehouses.map(
                                (warehouse) => (

                                    <option
                                        key={
                                            warehouse.id
                                        }
                                        value={
                                            warehouse.id
                                        }
                                    >

                                        {
                                            warehouse.warehouse_name
                                        }

                                    </option>

                                )
                            )}

                        </select>

                    </div>


                    {/* To Warehouse */}

                    <div className="stock-history-filter-group">

                        <label>
                            To Warehouse
                        </label>

                        <select
                            value={
                                filters.to_warehouse_id
                            }
                            onChange={(e) =>
                                handleFilterChange(
                                    "to_warehouse_id",
                                    e.target.value
                                )
                            }
                        >

                            <option value="">
                                All Warehouses
                            </option>

                            {warehouses.map(
                                (warehouse) => (

                                    <option
                                        key={
                                            warehouse.id
                                        }
                                        value={
                                            warehouse.id
                                        }
                                    >

                                        {
                                            warehouse.warehouse_name
                                        }

                                    </option>

                                )
                            )}

                        </select>

                    </div>


                    {/* Reference By */}

                    <div className="stock-history-filter-group">

                        <label>
                            Reference By
                        </label>

                        <input
                            type="text"
                            placeholder="Reference person..."
                            value={
                                filters.reference_by
                            }
                            onChange={(e) =>
                                handleFilterChange(
                                    "reference_by",
                                    e.target.value
                                )
                            }
                        />

                    </div>


                    {/* Activity */}

                    <div className="stock-history-filter-group">

                        <label>
                            Activity
                        </label>

                        <select
                            value={
                                filters.activity
                            }
                            onChange={(e) =>
                                handleFilterChange(
                                    "activity",
                                    e.target.value
                                )
                            }
                        >

                            <option value="">
                                All Activities
                            </option>

                            <option value="CREATED">
                                Created
                            </option>

                            <option value="UPDATED">
                                Updated
                            </option>

                            <option value="DELETED">
                                Deleted
                            </option>

                        </select>

                    </div>


                    {/* Reset */}

                    <button
                        type="button"
                        className="stock-history-reset"
                        onClick={
                            handleReset
                        }
                    >

                        <RotateCcw
                            size={17}
                        />

                        Reset

                    </button>


                    {/* Export */}

                    <button
                        type="button"
                        className="stock-history-export"
                        onClick={
                            handleExportExcel
                        }
                    >

                        <Download
                            size={17}
                        />

                        Export Excel

                    </button>

                </div>


                {/* =================================================
                    Summary
                ================================================= */}

                <div className="stock-history-summary">

                    <div>

                        <span>
                            Total Transfers
                        </span>

                        <strong>
                            {
                                totalTransfers
                            }
                        </strong>

                    </div>


                    <div>

                        <span>
                            Current Page
                        </span>

                        <strong>
                            {page}
                        </strong>

                    </div>

                </div>


                {/* =================================================
                    Table
                ================================================= */}

                <div className="stock-history-table-wrapper">

                    <table className="stock-history-table">

                        <thead>

                            <tr>

                                <th>
                                    Date & Time
                                </th>

                                <th>
                                    Transfer No.
                                </th>

                                <th>
                                    Item
                                </th>

                                <th>
                                    From Warehouse
                                </th>

                                <th>
                                    To Warehouse
                                </th>

                                <th>
                                    Quantity
                                </th>

                                <th>
                                    Reference By
                                </th>

                                <th>
                                    Activity
                                </th>

                                <th>
                                    Created By
                                </th>

                                <th>
                                    Remarks
                                </th>

                                <th>
                                    Actions
                                </th>

                            </tr>

                        </thead>


                        <tbody>

                            {loading ? (

                                <tr>

                                    <td
                                        colSpan="11"
                                        className="stock-history-empty"
                                    >

                                        Loading Stock
                                        Transfer History...

                                    </td>

                                </tr>

                            ) : history.length === 0 ? (

                                <tr>

                                    <td
                                        colSpan="11"
                                        className="stock-history-empty"
                                    >

                                        <div className="stock-history-empty-content">

                                            <ArrowRightLeft
                                                size={34}
                                            />

                                            <h3>
                                                No Stock Transfer History
                                            </h3>

                                            <p>
                                                Stock transfer records
                                                will appear here after
                                                a transfer is completed.
                                            </p>

                                        </div>

                                    </td>

                                </tr>

                            ) : (

                                history.map(
                                    (item) => (

                                        <tr
                                            key={
                                                item.id
                                            }
                                        >

                                            <td>
                                                {
                                                    item.created_at ||
                                                    "-"
                                                }
                                            </td>


                                            <td>

                                                <span className="transfer-number">

                                                    {
                                                        item.transaction_number ||
                                                        "-"
                                                    }

                                                </span>

                                            </td>


                                            <td>
                                                {
                                                    item.product_name ||
                                                    item.product?.product_name ||
                                                    "-"
                                                }
                                            </td>


                                            <td>
                                                {
                                                    item.from_warehouse ||
                                                    "-"
                                                }
                                            </td>


                                            <td>
                                                {
                                                    item.to_warehouse ||
                                                    "-"
                                                }
                                            </td>


                                            <td>

                                                <strong>
                                                    {
                                                        item.quantity ??
                                                        "-"
                                                    }
                                                </strong>

                                            </td>


                                            <td>
                                                {
                                                    item.reference_by ||
                                                    "-"
                                                }
                                            </td>


                                            <td>

                                                <span
                                                    className={
                                                        `activity-badge ${
                                                            (
                                                                item.activity ||
                                                                "CREATED"
                                                            ).toLowerCase()
                                                        }`
                                                    }
                                                >

                                                    {
                                                        item.activity ||
                                                        "Created"
                                                    }

                                                </span>

                                            </td>


                                            <td>
                                                {
                                                    item.created_by_name ||
                                                    item.created_by ||
                                                    "-"
                                                }
                                            </td>


                                            <td>
                                                {
                                                    item.remarks ||
                                                    "-"
                                                }
                                            </td>


                                            <td>

                                                <button
                                                    type="button"
                                                    className="history-view-btn"
                                                    onClick={() =>
                                                        handleView(
                                                            item
                                                        )
                                                    }
                                                    title="View Transfer"
                                                >

                                                    <Eye
                                                        size={17}
                                                    />

                                                </button>

                                            </td>

                                        </tr>

                                    )
                                )

                            )}

                        </tbody>

                    </table>

                </div>


                {/* =================================================
                    Footer
                ================================================= */}

                <div className="stock-history-footer">

                    <div className="stock-history-footer-info">

                        Showing{" "}

                        <strong>
                            {
                                history.length
                            }
                        </strong>{" "}

                        of{" "}

                        <strong>
                            {
                                totalTransfers
                            }
                        </strong>{" "}

                        transfer records

                    </div>


                    <div className="stock-history-pagination">

                        <button
                            type="button"
                            disabled={
                                page <= 1 ||
                                loading
                            }
                            onClick={() =>
                                setPage(
                                    (previous) =>
                                        Math.max(
                                            1,
                                            previous - 1
                                        )
                                )
                            }
                        >

                            Previous

                        </button>


                        <span>
                            Page {page} of {totalPages}
                        </span>


                        <button
                            type="button"
                            disabled={
                                page >=
                                    totalPages ||
                                loading
                            }
                            onClick={() =>
                                setPage(
                                    (previous) =>
                                        previous + 1
                                )
                            }
                        >

                            Next

                        </button>

                    </div>

                </div>

            </div>

        </div>

    );

};


export default StockTransferHistory;