import "./SalesForm.css";

import { useState } from "react";

import {
    Warehouse,
    Save,
    FileDown,
    MapPin,
    CreditCard,
} from "lucide-react";

import { useSales } from "../../../context/SalesContext";

import SalesService from "../../../services/SalesService";

import SalesItemsTable from "../SalesItemsTable/SalesItemsTable";

import SalesSummary from "../SalesSummary/SalesSummary";

import SearchableCustomer from "../SearchableCustomer/SearchableCustomer";


const SalesForm = () => {

    const [isSaving, setIsSaving] =
        useState(false);


    const {
        sale,
        drawerMode,
        selectedSale,
        customers,
        warehouses,
        updateField,
        saveSale,
        updateSale,
        deleteSale,
        grandTotal,
    } = useSales();


    // =====================================================
    // EDIT MODE
    // =====================================================

    const isEdit =
        drawerMode === "edit";


    // =====================================================
    // SELECTED CUSTOMER
    // =====================================================

    const selectedCustomer =
        customers.find(
            (customer) =>
                String(customer.id) ===
                String(sale?.customer_id)
        );


    // =====================================================
    // CUSTOMER CHANGE
    // =====================================================

    const handleCustomerChange = (
        customerId
    ) => {

        updateField(
            "customer_id",
            customerId
        );
    };


    // =====================================================
    // DUE DATE
    // =====================================================

    const getDueDate = () => {

        if (!sale?.order_date) {
            return "";
        }


        // -------------------------------------------------
        // Existing due date
        // -------------------------------------------------

        if (
            sale.expected_delivery_date
        ) {

            return sale.expected_delivery_date;
        }


        // -------------------------------------------------
        // Default due date = 20 days
        // -------------------------------------------------

        const date =
            new Date(
                `${sale.order_date}T00:00:00`
            );


        date.setDate(
            date.getDate() + 20
        );


        return date
            .toISOString()
            .split("T")[0];
    };


    // =====================================================
    // DUE DATE CHANGE
    // =====================================================

    const handleDueDateChange = (
        event
    ) => {

        updateField(
            "expected_delivery_date",
            event.target.value
        );
    };


    // =====================================================
    // CUSTOMER BILLING ADDRESS
    // =====================================================

    const renderCustomerAddress = () => {

        if (!selectedCustomer) {

            return (
                <span>
                    Select a customer to view billing address
                </span>
            );
        }


        return (
            <>
                {selectedCustomer.billing_address && (
                    <>
                        {selectedCustomer.billing_address}
                        <br />
                    </>
                )}


                {selectedCustomer.city && (
                    <>
                        {selectedCustomer.city}
                        <br />
                    </>
                )}


                {(selectedCustomer.state ||
                    selectedCustomer.pincode) && (

                    <>
                        {selectedCustomer.state || ""}

                        {selectedCustomer.state &&
                            selectedCustomer.pincode
                            ? " - "
                            : ""}

                        {selectedCustomer.pincode || ""}

                        <br />
                    </>
                )}


                {selectedCustomer.country && (
                    <>
                        {selectedCustomer.country}
                    </>
                )}


                {selectedCustomer.phone && (

                    <div className="customer-phone">

                        <span>
                            Contact No.:
                        </span>

                        <strong>
                            {selectedCustomer.phone}
                        </strong>

                    </div>
                )}

            </>
        );
    };


    // =====================================================
    // INVOICE NUMBER
    // =====================================================

    const invoiceNumber =
        sale?.so_number ||
        sale?.sales_order_number ||
        sale?.invoice_number ||
        "Auto Generated";


    // =====================================================
    // SALES DATE
    // =====================================================

    const salesDate =
        sale?.order_date || "";


    // =====================================================
    // DUE DATE
    // =====================================================

    const dueDate =
        getDueDate();


    // =====================================================
    // SALES ORDER ID
    // =====================================================

    const getSalesOrderId = (
        response
    ) => {

        if (!response) {
            return null;
        }


        // Direct ID

        if (
            response.id !== undefined &&
            response.id !== null
        ) {

            return response.id;
        }


        // Sales order ID

        if (
            response.sales_order_id !== undefined &&
            response.sales_order_id !== null
        ) {

            return response.sales_order_id;
        }


        // Sale ID

        if (
            response.sale_id !== undefined &&
            response.sale_id !== null
        ) {

            return response.sale_id;
        }


        // Nested data

        if (
            response.data &&
            response.data.id !== undefined &&
            response.data.id !== null
        ) {

            return response.data.id;
        }


        if (
            response.data &&
            response.data.sales_order_id !== undefined &&
            response.data.sales_order_id !== null
        ) {

            return response.data.sales_order_id;
        }


        if (
            response.data &&
            response.data.sale_id !== undefined &&
            response.data.sale_id !== null
        ) {

            return response.data.sale_id;
        }


        // Nested sale

        if (
            response.sale &&
            response.sale.id !== undefined &&
            response.sale.id !== null
        ) {

            return response.sale.id;
        }


        // Nested sales order

        if (
            response.sales_order &&
            response.sales_order.id !== undefined &&
            response.sales_order.id !== null
        ) {

            return response.sales_order.id;
        }


        return null;
    };


    // =====================================================
    // SALES ORDER NUMBER
    // =====================================================

    const getSalesOrderNumber = (
        response
    ) => {

        if (!response) {

            return (
                invoiceNumber !==
                "Auto Generated"

                    ? invoiceNumber

                    : null
            );
        }


        return (

            response.so_number ||

            response.sales_order_number ||

            response.invoice_number ||

            response.data?.so_number ||

            response.data?.sales_order_number ||

            response.data?.invoice_number ||

            response.sale?.so_number ||

            response.sale?.sales_order_number ||

            response.sale?.invoice_number ||

            response.sales_order?.so_number ||

            response.sales_order?.sales_order_number ||

            response.sales_order?.invoice_number ||

            (
                invoiceNumber !==
                "Auto Generated"

                    ? invoiceNumber

                    : null
            )
        );
    };


    // =====================================================
    // RESOLVE SALES ORDER ID
    // =====================================================

    const resolveSalesOrderId = (
        response
    ) => {

        // Existing sale in edit mode
        if (
            isEdit &&
            selectedSale?.id !== undefined &&
            selectedSale?.id !== null &&
            selectedSale?.id !== ""
        ) {
            return selectedSale.id;
        }

        if (
            isEdit &&
            sale?.id !== undefined &&
            sale?.id !== null &&
            sale?.id !== ""
        ) {
            return sale.id;
        }

        // New sale: get ID returned by backend
        return getSalesOrderId(response);
    };


    // =====================================================
    // RESOLVE SALES ORDER NUMBER
    // =====================================================

    const resolveSalesOrderNumber = (
        response,
        salesOrderId
    ) => {

        return (
            getSalesOrderNumber(response) ||
            sale?.so_number ||
            `Sales-Invoice-${salesOrderId}`
        );
    };


    // =====================================================
    // GENERATE + STORE PDF
    // =====================================================
    //
    // Generates the PDF through the backend.
    //
    // The backend stores the generated PDF in the database.
    //
    // IMPORTANT:
    // This does NOT download the PDF.
    //
    // Used by:
    // Save Sale
    //
    // =====================================================

    const generateAndStorePdf = async (
        response
    ) => {

        const salesOrderId =
            resolveSalesOrderId(response);

        if (!salesOrderId) {

            console.error(
                "Unable to find Sales Order ID.",
                response
            );

            throw new Error(
                "Sale was saved successfully, but the Sales Order ID was not returned by the server. PDF could not be generated."
            );
        }

        await SalesService.generateSalesOrderPdf(
            salesOrderId
        );

        return salesOrderId;
    };


    // =====================================================
    // GENERATE + STORE + DOWNLOAD PDF
    // =====================================================
    //
    // Generates the PDF.
    // Backend stores it in the database.
    // Browser downloads the same PDF.
    //
    // Used by:
    // Save as PDF
    //
    // =====================================================

    const generateStoreAndDownloadPdf = async (
        response
    ) => {

        const salesOrderId =
            resolveSalesOrderId(response);

        if (!salesOrderId) {

            console.error(
                "Unable to find Sales Order ID.",
                response
            );

            throw new Error(
                "Sale was saved successfully, but the Sales Order ID was not returned by the server. PDF could not be generated."
            );
        }

        const soNumber =
            resolveSalesOrderNumber(
                response,
                salesOrderId
            );

        await SalesService.downloadSalesOrderPdf(
            salesOrderId,
            soNumber
        );

        return salesOrderId;
    };


    // =====================================================
    // SAVE SALE
    // =====================================================
    //
    // Save Sale:
    //
    // 1. Save/update sale in database
    // 2. Generate PDF
    // 3. Store PDF in database
    // 4. DO NOT download PDF
    //
    // =====================================================

    const handleSaveSale = async () => {

        if (isSaving) {
            return;
        }

        setIsSaving(true);

        try {

            // =================================================
            // IMPORTANT:
            // Existing sales must call updateSale() directly.
            // This prevents an edited sale from accidentally
            // reaching POST /sales-orders/.
            // =================================================

            let response;

            if (isEdit) {

                const salesOrderId =
                    selectedSale?.id ??
                    sale?.id ??
                    null;

                if (
                    salesOrderId === null ||
                    salesOrderId === undefined ||
                    salesOrderId === ""
                ) {
                    throw new Error(
                        "Sales Order ID is missing. Cannot update this sale."
                    );
                }

                console.log(
                    "========== SALES FORM UPDATE =========="
                );

                console.log(
                    "Sales Order ID:",
                    salesOrderId
                );

                response =
                    await updateSale(
                        salesOrderId
                    );

            } else {

                console.log(
                    "========== SALES FORM CREATE =========="
                );

                response =
                    await saveSale();
            }

            if (!response) {
                return;
            }

            await generateAndStorePdf(
                response
            );

        } catch (error) {

            console.error(
                "SAVE SALE / PDF ERROR:",
                error
            );

            if (
                error?.message &&
                !error?.response
            ) {

                alert(
                    error.message
                );
            }

        } finally {

            setIsSaving(false);
        }
    };


    // =====================================================
    // SAVE AS PDF
    // =====================================================
    //
    // Save as PDF:
    //
    // 1. Save/update sale in database
    // 2. Generate PDF
    // 3. Store PDF in database
    // 4. Download PDF to local computer
    //
    // =====================================================

    const handleSaveAsPdf = async () => {

        if (isSaving) {
            return;
        }

        setIsSaving(true);

        try {

            // =================================================
            // IMPORTANT:
            // Existing sales must call updateSale() directly.
            // =================================================

            let response;

            if (isEdit) {

                const salesOrderId =
                    selectedSale?.id ??
                    sale?.id ??
                    null;

                if (
                    salesOrderId === null ||
                    salesOrderId === undefined ||
                    salesOrderId === ""
                ) {
                    throw new Error(
                        "Sales Order ID is missing. Cannot update this sale."
                    );
                }

                console.log(
                    "========== SALES FORM UPDATE + PDF =========="
                );

                console.log(
                    "Sales Order ID:",
                    salesOrderId
                );

                response =
                    await updateSale(
                        salesOrderId
                    );

            } else {

                console.log(
                    "========== SALES FORM CREATE + PDF =========="
                );

                response =
                    await saveSale();
            }

            if (!response) {
                return;
            }

            await generateStoreAndDownloadPdf(
                response
            );

        } catch (error) {

            console.error(
                "SAVE AS PDF ERROR:",
                error
            );

            if (
                error?.message &&
                !error?.response
            ) {

                alert(
                    error.message
                );
            }

        } finally {

            setIsSaving(false);
        }
    };


    // =====================================================
    // CANCEL SALE
    // =====================================================
    //
    // Cancels/deletes an existing saved sale.
    //
    // No PDF is generated.
    // No PDF is downloaded.
    //
    // =====================================================

    const handleCancelSale = async () => {

        if (isSaving) {
            return;
        }

        const salesOrderId =
            sale?.id;

        if (
            salesOrderId === undefined ||
            salesOrderId === null ||
            salesOrderId === ""
        ) {

            alert(
                "There is no saved sales order to cancel."
            );

            return;
        }

        const confirmed =
            window.confirm(
                "Are you sure you want to cancel this sale?"
            );

        if (!confirmed) {
            return;
        }

        setIsSaving(true);

        try {

            await deleteSale(
                salesOrderId
            );

        } catch (error) {

            console.error(
                "CANCEL SALE ERROR:",
                error
            );

            if (
                error?.message &&
                !error?.response
            ) {

                alert(
                    error.message
                );
            }

        } finally {

            setIsSaving(false);
        }
    };


    // =====================================================
    // RENDER
    // =====================================================

    return (

        <div className="sales-form">


            {/* =================================================
                HEADER
            ================================================= */}

            <div className="sales-form-header">

                <div>

                    <h2>
                        Sales Invoice Information
                    </h2>

                    <p>
                        Enter customer and invoice details
                    </p>

                </div>

            </div>


            {/* =================================================
                TOP COMBINED SECTION
            ================================================= */}

            <div className="sales-top-section">


                {/* =================================================
                    LEFT SIDE
                ================================================= */}

                <div className="sales-top-left">


                    {/* =================================================
                        CUSTOMER / WAREHOUSE / BILLING / PAYMENT
                    ================================================= */}

                    <div className="sales-fields-grid">


                        {/* =========================================
                            CUSTOMER
                        ========================================= */}

                        <div className="sales-form-field">

                            <label>
                                Customer
                                <span>*</span>
                            </label>


                            <SearchableCustomer
                                customers={
                                    customers
                                }

                                value={
                                    sale?.customer_id
                                }

                                onChange={
                                    handleCustomerChange
                                }
                            />

                        </div>


                        {/* =========================================
                            WAREHOUSE
                        ========================================= */}

                        <div className="sales-form-field">

                            <label>
                                Warehouse
                                <span>*</span>
                            </label>


                            <div className="sales-select-wrapper">

                                <Warehouse
                                    size={15}
                                />


                                <select
                                    value={
                                        sale?.warehouse_id ||
                                        ""
                                    }

                                    onChange={
                                        (event) =>
                                            updateField(
                                                "warehouse_id",
                                                event.target.value
                                            )
                                    }
                                >

                                    <option value="">
                                        Select Warehouse
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
                                                    warehouse.warehouse_name ||
                                                    warehouse.name ||
                                                    warehouse.code
                                                }

                                            </option>
                                        )
                                    )}

                                </select>

                            </div>

                        </div>


                        {/* =========================================
                            BILLING NAME
                        ========================================= */}

                        <div className="sales-form-field">

                            <label>
                                Billing Name
                            </label>


                            <input
                                className="sales-text-input"

                                type="text"

                                placeholder="Billing Name"

                                value={
                                    selectedCustomer?.customer_name ||
                                    ""
                                }

                                readOnly
                            />

                        </div>


                        {/* =========================================
                            PAYMENT STATUS
                        ========================================= */}

                        <div className="sales-form-field">

                            <label>
                                Payment Status
                            </label>


                            <div className="sales-select-wrapper">

                                <CreditCard
                                    size={15}
                                />


                                <select
                                    value={
                                        sale?.payment_status ||
                                        "PENDING"
                                    }

                                    onChange={
                                        (event) => {

                                            const paymentStatus =
                                                event.target.value;

                                            updateField(
                                                "payment_status",
                                                paymentStatus
                                            );

                                            // =================================================
                                            // PAYMENT AMOUNT SYNCHRONIZATION
                                            // =================================================
                                            //
                                            // Fully received:
                                            // paid amount must equal the Grand Total.
                                            //
                                            // Pending:
                                            // paid amount must be 0.
                                            //
                                            // Partial:
                                            // keep the amount entered by the user.
                                            // =================================================

                                            if (
                                                paymentStatus ===
                                                    "RECEIVED_BY_HAND" ||
                                                paymentStatus ===
                                                    "RECEIVED_TO_ACCOUNT"
                                            ) {

                                                updateField(
                                                    "paid_amount",
                                                    Number(
                                                        Number(
                                                            grandTotal || 0
                                                        ).toFixed(2)
                                                    )
                                                );

                                            } else if (
                                                paymentStatus ===
                                                    "PENDING"
                                            ) {

                                                updateField(
                                                    "paid_amount",
                                                    0
                                                );

                                            }

                                        }
                                    }
                                >

                                    <option value="PENDING">
                                        Pending
                                    </option>


                                    <option value="RECEIVED_BY_HAND">
                                        Received by Hand
                                    </option>


                                    <option value="PARTIALLY_RECEIVED_BY_HAND">
                                        Partially Received by Hand
                                    </option>


                                    <option value="RECEIVED_TO_ACCOUNT">
                                        Received to Account
                                    </option>


                                    <option value="PARTIALLY_RECEIVED_TO_ACCOUNT">
                                        Partially Received to Account
                                    </option>

                                </select>

                            </div>

                        </div>


                        {/* =========================================
                            PARTIAL PAYMENT AMOUNT
                        ========================================= */}
                        {(
                            sale?.payment_status ===
                                "PARTIALLY_RECEIVED_BY_HAND" ||

                            sale?.payment_status ===
                                "PARTIALLY_RECEIVED_TO_ACCOUNT"
                        ) && (

                            <div className="sales-form-field">

                                <label>
                                    Partially Received Amount
                                    <span>*</span>
                                </label>


                                <div
                                    className="sales-select-wrapper"
                                >

                                    <span
                                        style={{
                                            fontSize: "14px",
                                            fontWeight: 600,
                                            color: "#64748b",
                                        }}
                                    >
                                        ₹
                                    </span>


                                    <input
                                        type="number"

                                        min="0"

                                        step="0.01"

                                        placeholder="Enter received amount"

                                        value={
                                            sale?.paid_amount ??
                                            ""
                                        }

                                        onChange={
                                            (event) => {

                                                const value =
                                                    event.target.value;


                                                updateField(
                                                    "paid_amount",
                                                    value === ""
                                                        ? ""
                                                        : Number(value)
                                                );
                                            }
                                        }
                                    />

                                </div>

                            </div>

                        )}

                    </div>


                    {/* =================================================
                        CUSTOMER BILLING ADDRESS
                    ================================================= */}

                    {selectedCustomer && (

                        <div className="customer-address-card">


                            <div className="customer-address-title">

                                <MapPin
                                    size={14}
                                />

                                <span>
                                    Billing Address
                                </span>

                            </div>


                            <div className="customer-address-content">

                                <div className="customer-address-text">

                                    {renderCustomerAddress()}

                                </div>

                            </div>

                        </div>
                    )}

                </div>


                {/* =================================================
                    RIGHT SIDE - INVOICE INFORMATION
                ================================================= */}

                <div className="sales-top-right">

                    <div className="invoice-meta-card">


                        {/* =========================================
                            INVOICE NUMBER
                        ========================================= */}

                        <div className="invoice-meta-row">

                            <span>
                                Invoice Number
                            </span>


                            <strong>
                                {invoiceNumber}
                            </strong>

                        </div>


                        {/* =========================================
                            REFERENCE
                        ========================================= */}

                        <div className="invoice-meta-row">

                            <span>
                                Reference
                            </span>


                            <input
                                type="text"

                                value={
                                    sale?.reference ||
                                    ""
                                }

                                placeholder="Enter reference"

                                onChange={
                                    (event) =>
                                        updateField(
                                            "reference",
                                            event.target.value
                                        )
                                }
                            />

                        </div>


                        {/* =========================================
                            SALES DATE
                        ========================================= */}

                        <div className="invoice-meta-row">

                            <span>
                                Sales Date
                            </span>


                            <input
                                type="date"

                                value={
                                    salesDate
                                }

                                onChange={
                                    (event) =>
                                        updateField(
                                            "order_date",
                                            event.target.value
                                        )
                                }
                            />

                        </div>


                        {/* =========================================
                            PLACE OF SUPPLY
                        ========================================= */}

                        <div className="invoice-meta-row">

                            <span>
                                Place of Supply
                            </span>


                            <strong>
                                29-Karnataka
                            </strong>

                        </div>


                        {/* =========================================
                            DUE DATE
                        ========================================= */}

                        <div className="invoice-meta-row">

                            <span>
                                Due Date
                            </span>


                            <input
                                type="date"

                                value={
                                    dueDate
                                }

                                onChange={
                                    handleDueDateChange
                                }
                            />

                        </div>

                    </div>

                </div>

            </div>


            {/* =================================================
                PRODUCTS
            ================================================= */}

            <section className="sales-products-section">


                <div className="sales-section-heading">

                    <div>

                        <h3>
                            Products
                        </h3>

                        <p>
                            Select products, quantities and serial numbers
                        </p>

                    </div>

                </div>


                <div className="sales-products-table-wrapper">

                    <SalesItemsTable />

                </div>

            </section>


            {/* =================================================
                ORDER SUMMARY
            ================================================= */}

            <div className="sales-summary-section">

                <SalesSummary />

            </div>


            {/* =================================================
                REMARKS
            ================================================= */}

            <section className="sales-remarks-section">

                <div className="sales-form-field">

                    <label>
                        Remarks
                    </label>


                    <textarea
                        rows="3"

                        placeholder="Enter any additional remarks..."

                        value={
                            sale?.remarks ||
                            ""
                        }

                        onChange={
                            (event) =>
                                updateField(
                                    "remarks",
                                    event.target.value
                                )
                        }
                    />

                </div>

            </section>


            {/* =================================================
                FOOTER
            ================================================= */}

            <div className="sales-form-footer">

                {/* =============================================
                    CANCEL SALE
                ============================================= */}

                {isEdit && (

                    <button
                        type="button"
                        className="sales-cancel-button"
                        onClick={handleCancelSale}
                        disabled={isSaving}
                    >

                        {isSaving
                            ? "Cancelling..."
                            : "Cancel Sale"}

                    </button>

                )}


                {/* =============================================
                    SAVE AS PDF
                ============================================= */}

                <button
                    type="button"
                    className="sales-pdf-button"
                    onClick={handleSaveAsPdf}
                    disabled={isSaving}
                >

                    <FileDown
                        size={17}
                    />

                    {isSaving
                        ? "Saving..."
                        : "Save as PDF"}

                </button>


                {/* =============================================
                    SAVE SALE
                ============================================= */}

                <button
                    type="button"
                    className="sales-save-button"
                    onClick={handleSaveSale}
                    disabled={isSaving}
                >

                    <Save
                        size={17}
                    />

                    {isSaving
                        ? "Saving..."
                        : isEdit
                            ? "Update Sale"
                            : "Save Sale"}

                </button>

            </div>

        </div>
    );
};


export default SalesForm;