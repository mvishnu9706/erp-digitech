import "./SalesTable.css";

import {
    Eye,
    FileDown,
    Pencil,
    Trash2,
    ChevronLeft,
    ChevronRight,
    ChevronsLeft,
    ChevronsRight,
} from "lucide-react";

import { useEffect, useMemo, useState } from "react";

import { useSales } from "../../../context/SalesContext";
import SalesService from "../../../services/SalesService";


const SalesTable = () => {

    const {
        salesOrders,
        customers,
        warehouses,
        openViewDrawer,
        openEditDrawer,
        deleteSale,

        // Existing pagination/filter support
        filters,
        updateFilter,
    } = useSales();


    // =====================================================
    // Pagination State
    // =====================================================

    // Keep the selected page size in sync with the value used
    // by SalesContext/API.
    const pageSize =
        Number(filters?.page_size) || 10;

    const currentPage =
        Number(filters?.page) || 1;


    // =====================================================
    // IMPORTANT
    // =====================================================
    //
    // Your current SalesContext loads 10 records from API.
    //
    // Therefore:
    // - 10 works directly
    // - 25 / 50 require SalesContext to send page_size
    //
    // This component keeps the UI ready for that update.
    //
    // =====================================================


    // =====================================================
    // Customer Name
    // =====================================================

    const getCustomerName = (sale) => {

        if (!sale) {
            return "-";
        }


        if (
            sale.customer_name &&
            String(
                sale.customer_name
            ).trim() !== ""
        ) {

            return sale.customer_name;

        }


        const customer =
            customers?.find(
                (item) =>
                    Number(item.id) ===
                    Number(sale.customer_id)
            );


        return (
            customer?.name ||
            customer?.customer_name ||
            customer?.full_name ||
            customer?.company_name ||
            (
                sale.customer_id
                    ? `Customer #${sale.customer_id}`
                    : "-"
            )
        );

    };


    // =====================================================
    // Warehouse Name
    // =====================================================

    const getWarehouseName = (sale) => {

        if (!sale) {
            return "-";
        }


        if (
            sale.warehouse_name &&
            String(
                sale.warehouse_name
            ).trim() !== ""
        ) {

            return sale.warehouse_name;

        }


        const warehouse =
            warehouses?.find(
                (item) =>
                    Number(item.id) ===
                    Number(sale.warehouse_id)
            );


        return (
            warehouse?.name ||
            warehouse?.warehouse_name ||
            warehouse?.code ||
            (
                sale.warehouse_id
                    ? `Warehouse #${sale.warehouse_id}`
                    : "-"
            )
        );

    };


    // =====================================================
    // Reference By
    // =====================================================

    const getReferenceBy = (sale) => {

        if (!sale) {
            return "-";
        }


        const directReference =
            sale.reference_by ??
            sale.reference ??
            sale.reference_name ??
            sale.referred_by ??
            sale.reference_by_name ??
            sale.referenceBy ??
            sale.referenceName ??
            sale.referredBy ??
            sale.referred_by_name;


        if (
            directReference !== null &&
            directReference !== undefined &&
            typeof directReference !== "object" &&
            String(
                directReference
            ).trim() !== ""
        ) {

            return String(
                directReference
            ).trim();

        }


        if (
            sale.reference_by &&
            typeof sale.reference_by === "object"
        ) {

            return (
                sale.reference_by.name ||
                sale.reference_by.full_name ||
                sale.reference_by.customer_name ||
                sale.reference_by.reference_name ||
                sale.reference_by.label ||
                "-"
            );

        }


        if (
            sale.reference &&
            typeof sale.reference === "object"
        ) {

            return (
                sale.reference.name ||
                sale.reference.full_name ||
                sale.reference.customer_name ||
                sale.reference.reference_name ||
                sale.reference.label ||
                "-"
            );

        }


        if (
            sale.reference_person &&
            typeof sale.reference_person === "object"
        ) {

            return (
                sale.reference_person.name ||
                sale.reference_person.full_name ||
                sale.reference_person.customer_name ||
                "-"
            );

        }


        return "-";

    };


    // =====================================================
    // Currency
    // =====================================================

    const formatCurrency = (value) => {

        return `₹${Number(
            value || 0
        ).toLocaleString(
            "en-IN",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            }
        )}`;

    };


    // =====================================================
    // Date
    // =====================================================

    const formatDate = (date) => {

        if (!date) {
            return "-";
        }


        const parsedDate =
            new Date(date);


        if (
            Number.isNaN(
                parsedDate.getTime()
            )
        ) {

            return "-";

        }


        return parsedDate.toLocaleDateString(
            "en-IN",
            {
                day: "2-digit",
                month: "short",
                year: "numeric",
            }
        );

    };


    // =====================================================
    // Payment Status Class
    // =====================================================

    const getPaymentStatusClass = (status) => {

        switch (
            String(
                status || ""
            ).toUpperCase()
        ) {

            case "PENDING":
                return "pending";

            case "RECEIVED":
            case "RECEIVED_TO_ACCOUNT":
            case "PAID":
                return "received-account";

            case "RECEIVED_BY_HAND":
                return "received-hand";

            case "PARTIAL":
            case "PARTIALLY_RECEIVED_BY_HAND":
            case "PARTIALLY_RECEIVED_TO_ACCOUNT":
                return "partial";

            default:
                return "default";

        }

    };


    // =====================================================
    // Payment Status Label
    // =====================================================

    const getPaymentStatusLabel = (status) => {

        switch (
            String(
                status || ""
            ).toUpperCase()
        ) {

            case "PENDING":
                return "Pending";

            case "RECEIVED":
                return "Received";

            case "RECEIVED_BY_HAND":
                return "Received by Hand";

            case "RECEIVED_TO_ACCOUNT":
                return "Received to Account";

            case "PARTIAL":
            case "PARTIALLY_RECEIVED_BY_HAND":
            case "PARTIALLY_RECEIVED_TO_ACCOUNT":
                return "Partially Paid";

            case "PAID":
                return "Paid";

            default:
                return "Pending";

        }

    };


    // =====================================================
    // Download PDF
    // =====================================================

    const handleDownloadPdf = async (sale) => {

        if (!sale?.id) {

            alert(
                "Sales order ID is missing."
            );

            return;

        }


        try {

            console.log(
                "Downloading Sales Order PDF:",
                sale.id
            );


            const orderNumber =
                sale.so_number ||
                sale.sales_order_number ||
                sale.invoice_number ||
                `SO-${sale.id}`;


            const result =
                await SalesService.downloadSalesOrderPdf(
                    sale.id,
                    orderNumber
                );


            if (result === true) {

                console.log(
                    "Sales Order PDF downloaded successfully:",
                    orderNumber
                );

                return;

            }


            if (!result) {

                throw new Error(
                    "PDF file was not returned by the server."
                );

            }

        } catch (error) {

            console.error(
                "DOWNLOAD SALES ORDER PDF ERROR:",
                error
            );


            console.error(
                "STATUS:",
                error?.response?.status
            );


            console.error(
                "RESPONSE:",
                error?.response?.data
            );


            let errorMessage =
                "Failed to download sales order PDF.";


            if (
                error?.response?.data?.detail
            ) {

                errorMessage =
                    error.response.data.detail;

            } else if (
                error?.response?.data?.message
            ) {

                errorMessage =
                    error.response.data.message;

            } else if (
                error?.message
            ) {

                errorMessage =
                    error.message;

            }


            alert(
                errorMessage
            );

        }

    };


    // =====================================================
    // Pagination
    // =====================================================

    const handlePageSizeChange = (event) => {

        const newSize =
            Number(
                event.target.value
            );


        // Change the API page size and reset to page 1.
        if (typeof updateFilter === "function") {

            updateFilter(
                "page_size",
                newSize
            );

            updateFilter(
                "page",
                1
            );

        }

    };


    // =====================================================
    // Go To Page
    // =====================================================

    const goToPage = (newPage) => {

        if (
            newPage < 1
        ) {

            return;

        }


        if (
            typeof updateFilter === "function"
        ) {

            updateFilter(
                "page",
                newPage
            );

        }

    };


    // =====================================================
    // Pagination Calculation
    // =====================================================
    //
    // Until SalesContext sends total count,
    // we calculate whether another page exists
    // from the number of records returned.
    //
    // =====================================================

    const hasNextPage =
        Array.isArray(
            salesOrders
        ) &&
        salesOrders.length >=
            pageSize;


    const hasPreviousPage =
        currentPage > 1;


    // =====================================================
    // Page Number Display
    // =====================================================

    const pageNumbers =
        useMemo(() => {

            const pages = [];


            const start =
                Math.max(
                    1,
                    currentPage - 2
                );


            const end =
                currentPage + 2;


            for (
                let i = start;
                i <= end;
                i++
            ) {

                pages.push(i);

            }


            return pages;

        }, [
            currentPage
        ]);


    // =====================================================
    // Reset Page When Sales Data Becomes Empty
    // =====================================================

    useEffect(() => {

        if (
            currentPage > 1 &&
            Array.isArray(
                salesOrders
            ) &&
            salesOrders.length === 0
        ) {

            goToPage(
                currentPage - 1
            );

        }

    }, [
        salesOrders,
        currentPage
    ]);


    // =====================================================
    // Pagination Component
    // =====================================================

    const Pagination = () => {

        return (

            <div className="sales-pagination">

                {/* LEFT SIDE */}

                <div className="sales-pagination-left">

                    <span className="sales-pagination-label">
                        Rows per page
                    </span>


                    <select
                        className="sales-page-size"
                        value={pageSize}
                        onChange={
                            handlePageSizeChange
                        }
                        aria-label="Rows per page"
                    >

                        <option value={10}>
                            10
                        </option>

                        <option value={25}>
                            25
                        </option>

                        <option value={50}>
                            50
                        </option>

                    </select>

                </div>


                {/* CENTER */}

                <div className="sales-pagination-center">

                    {/* First */}

                    <button
                        type="button"
                        className="sales-page-button"
                        disabled={
                            !hasPreviousPage
                        }
                        onClick={() =>
                            goToPage(1)
                        }
                        title="First Page"
                    >

                        <ChevronsLeft
                            size={16}
                        />

                    </button>


                    {/* Previous */}

                    <button
                        type="button"
                        className="sales-page-button"
                        disabled={
                            !hasPreviousPage
                        }
                        onClick={() =>
                            goToPage(
                                currentPage - 1
                            )
                        }
                        title="Previous Page"
                    >

                        <ChevronLeft
                            size={16}
                        />

                    </button>


                    {/* Page Numbers */}

                    {pageNumbers.map(
                        (pageNumber) => {

                            const isCurrent =
                                pageNumber ===
                                currentPage;


                            return (

                                <button
                                    key={
                                        pageNumber
                                    }
                                    type="button"
                                    className={`sales-page-number ${
                                        isCurrent
                                            ? "active"
                                            : ""
                                    }`}
                                    onClick={() =>
                                        goToPage(
                                            pageNumber
                                        )
                                    }
                                >

                                    {
                                        pageNumber
                                    }

                                </button>

                            );

                        }
                    )}


                    {/* Next */}

                    <button
                        type="button"
                        className="sales-page-button"
                        disabled={
                            !hasNextPage
                        }
                        onClick={() =>
                            goToPage(
                                currentPage + 1
                            )
                        }
                        title="Next Page"
                    >

                        <ChevronRight
                            size={16}
                        />

                    </button>


                    {/* Last */}

                    <button
                        type="button"
                        className="sales-page-button"
                        disabled={
                            !hasNextPage
                        }
                        onClick={() =>
                            goToPage(
                                currentPage + 1
                            )
                        }
                        title="Last Page"
                    >

                        <ChevronsRight
                            size={16}
                        />

                    </button>

                </div>


                {/* RIGHT SIDE */}

                <div className="sales-pagination-right">

                    Page{" "}

                    <strong>
                        {currentPage}
                    </strong>

                </div>

            </div>

        );

    };


    // =====================================================
    // Empty State
    // =====================================================

    if (
        !salesOrders?.length
    ) {

        return (

            <div className="sales-table-wrapper">

                <div className="sales-empty-state">

                    <div className="sales-empty-icon">
                        🛒
                    </div>


                    <h3>
                        No Sales Orders Found
                    </h3>


                    <p>
                        There are no sales orders
                        matching your filters.
                    </p>

                </div>

            </div>

        );

    }


    // =====================================================
    // Table
    // =====================================================

    return (

        <div className="sales-table-wrapper">

            {/* =====================================================
                PAGINATION - MOVED TO TOP
            ===================================================== */}

            <Pagination />


            {/* =====================================================
                SALES TABLE
            ===================================================== */}

            <div className="sales-table-scroll">

                <table className="sales-table">

                    <thead>

                        <tr>

                            <th>
                                Order No.
                            </th>

                            <th>
                                Customer
                            </th>

                            <th>
                                Reference By
                            </th>

                            <th>
                                Warehouse
                            </th>

                            <th>
                                Date
                            </th>

                            <th>
                                Items
                            </th>

                            <th>
                                Payment
                            </th>

                            <th>
                                Actions
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        {salesOrders.map(
                            (sale) => {

                                const paymentStatusStr =
                                    String(
                                        sale.payment_status || ""
                                    ).toUpperCase();


                                const isPartial =
                                    paymentStatusStr ===
                                        "PARTIAL" ||
                                    paymentStatusStr ===
                                        "PARTIALLY_RECEIVED_BY_HAND" ||
                                    paymentStatusStr ===
                                        "PARTIALLY_RECEIVED_TO_ACCOUNT";


                                return (

                                    <tr
                                        key={
                                            sale.id
                                        }
                                    >

                                        {/* =================================
                                            ORDER NUMBER
                                        ================================= */}

                                        <td>

                                            <span className="sales-order-number">

                                                {sale.so_number ||
                                                    sale.sales_order_number ||
                                                    sale.invoice_number ||
                                                    `SO-${sale.id}`}

                                            </span>

                                        </td>


                                        {/* =================================
                                            CUSTOMER
                                        ================================= */}

                                        <td>

                                            <div className="sales-customer">

                                                <span className="sales-customer-name">

                                                    {getCustomerName(
                                                        sale
                                                    )}

                                                </span>


                                                {sale.customer_phone && (

                                                    <span className="sales-customer-phone">

                                                        {sale.customer_phone}

                                                    </span>

                                                )}

                                            </div>

                                        </td>


                                        {/* =================================
                                            REFERENCE BY
                                        ================================= */}

                                        <td>

                                            <span className="sales-reference-by">

                                                {getReferenceBy(
                                                    sale
                                                )}

                                            </span>

                                        </td>


                                        {/* =================================
                                            WAREHOUSE
                                        ================================= */}

                                        <td>

                                            <span className="sales-warehouse-name">

                                                {getWarehouseName(
                                                    sale
                                                )}

                                            </span>

                                        </td>


                                        {/* =================================
                                            DATE
                                        ================================= */}

                                        <td>

                                            <span className="sales-date">

                                                {formatDate(
                                                    sale.order_date
                                                )}

                                            </span>

                                        </td>


                                        {/* =================================
                                            ITEMS
                                        ================================= */}

                                        <td>

                                            <div className="sales-items">

                                                {sale.items?.length > 0 ? (

                                                    sale.items.map(
                                                        (
                                                            item,
                                                            index
                                                        ) => {

                                                            const productName =
                                                                item.product_name ||
                                                                item.product?.name ||
                                                                item.name ||
                                                                `Product #${item.product_id}`;


                                                            const quantity =
                                                                Number(
                                                                    item.quantity || 0
                                                                );


                                                            return (

                                                                <div
                                                                    className="sales-item-row"
                                                                    key={
                                                                        item.id ||
                                                                        index
                                                                    }
                                                                >

                                                                    <span className="sales-item-name">

                                                                        {productName}

                                                                    </span>


                                                                    <span className="sales-item-quantity">

                                                                        × {quantity}

                                                                    </span>

                                                                </div>

                                                            );

                                                        }
                                                    )

                                                ) : (

                                                    <span className="sales-item-count">

                                                        {sale.item_count || 0}

                                                    </span>

                                                )}

                                            </div>

                                        </td>


                                        {/* =================================
                                            PAYMENT
                                        ================================= */}

                                        <td>

                                            <div
                                                style={{
                                                    display:
                                                        "flex",
                                                    flexDirection:
                                                        "column",
                                                    gap:
                                                        "4px",
                                                    alignItems:
                                                        "flex-start",
                                                }}
                                            >

                                                <span
                                                    className={`sales-status-badge sales-payment-status ${getPaymentStatusClass(
                                                        sale.payment_status
                                                    )}`}
                                                >

                                                    {getPaymentStatusLabel(
                                                        sale.payment_status
                                                    )}

                                                </span>


                                                {isPartial &&
                                                    Number(
                                                        sale.paid_amount || 0
                                                    ) > 0 && (

                                                        <span
                                                            style={{
                                                                fontSize:
                                                                    "0.85em",
                                                                color:
                                                                    "#64748b",
                                                                fontWeight:
                                                                    600,
                                                                paddingLeft:
                                                                    "2px",
                                                            }}
                                                        >

                                                            {formatCurrency(
                                                                sale.paid_amount
                                                            )}

                                                        </span>

                                                    )}

                                            </div>

                                        </td>


                                        {/* =================================
                                            ACTIONS
                                        ================================= */}

                                        <td>

                                            <div className="sales-actions">

                                                {/* View */}

                                                <button
                                                    type="button"
                                                    className="sales-action view"
                                                    title="View Sale"
                                                    aria-label="View Sale"
                                                    onClick={() =>
                                                        openViewDrawer(
                                                            sale
                                                        )
                                                    }
                                                >

                                                    <Eye
                                                        size={15}
                                                        strokeWidth={2}
                                                    />

                                                </button>


                                                {/* PDF */}

                                                <button
                                                    type="button"
                                                    className="sales-action pdf"
                                                    title="Download PDF"
                                                    aria-label="Download PDF"
                                                    onClick={() =>
                                                        handleDownloadPdf(
                                                            sale
                                                        )
                                                    }
                                                >

                                                    <FileDown
                                                        size={15}
                                                        strokeWidth={2}
                                                    />

                                                </button>


                                                {/* Edit */}

                                                <button
                                                    type="button"
                                                    className="sales-action edit"
                                                    title="Edit Sale"
                                                    aria-label="Edit Sale"
                                                    onClick={() =>
                                                        openEditDrawer(
                                                            sale
                                                        )
                                                    }
                                                >

                                                    <Pencil
                                                        size={15}
                                                        strokeWidth={2}
                                                    />

                                                </button>


                                                {/* Delete */}

                                                <button
                                                    type="button"
                                                    className="sales-action delete"
                                                    title="Delete / Cancel Sale"
                                                    aria-label="Delete / Cancel Sale"
                                                    onClick={() =>
                                                        deleteSale(
                                                            sale.id
                                                        )
                                                    }
                                                >

                                                    <Trash2
                                                        size={15}
                                                        strokeWidth={2}
                                                    />

                                                </button>

                                            </div>

                                        </td>

                                    </tr>

                                );

                            }
                        )}

                    </tbody>

                </table>

            </div>

        </div>

    );

};


export default SalesTable;