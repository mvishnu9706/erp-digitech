import React, { useState } from "react";
import {
    Eye,
    CheckCircle2,
    XCircle,
    Clock3,
    MapPin,
    Pencil,
    X,
    Phone,
    Mail,
    Building2,
} from "lucide-react";

import "./EngineerTable.css";

/* =====================================================
   HELPERS
===================================================== */

const normalizeStatus = (service) => {
    return String(service?.status || "").toUpperCase();
};

const getCustomerName = (service) => {
    return (
        service?.customer_name ||
        service?.customer?.customer_name ||
        service?.customer?.name ||
        "-"
    );
};

const getCustomerAddress = (service) => {
    return (
        service?.customer?.address ||
        service?.customer_address ||
        service?.address ||
        "-"
    );
};

const getMachineName = (service) => {
    return (
        service?.machine?.machine_number ||
        service?.machine_number ||
        service?.machine?.machine_name ||
        service?.product?.name ||
        service?.product_name ||
        "-"
    );
};

const getSerialNumber = (service) => {
    return (
        service?.machine?.serial_number ||
        service?.serial_number ||
        service?.machine?.serial_no ||
        "-"
    );
};

const getIssue = (service) => {
    return (
        service?.complaint ||
        service?.issue ||
        service?.problem_description ||
        service?.description ||
        "-"
    );
};

const getEngineerName = (service) => {
    return (
        service?.engineer?.full_name ||
        service?.engineer?.name ||
        service?.engineer?.username ||
        service?.engineer_name ||
        "-"
    );
};

const getPriority = (service) => {
    return (
        service?.priority ||
        "NORMAL"
    );
};

const getDate = (service) => {
    const value =
        service?.created_at ||
        service?.request_date ||
        service?.created_date ||
        service?.assigned_at;

    if (!value) {
        return "-";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "-";
    }

    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
};

/* =====================================================
   STATUS
===================================================== */

const StatusBadge = ({ status }) => {

    const normalized = String(
        status || ""
    ).toUpperCase();

    let label = normalized || "-";

    if (normalized === "IN_PROGRESS") {
        label = "In Progress";
    } else if (normalized === "ASSIGNED") {
        label = "Assigned";
    } else if (normalized === "COMPLETED") {
        label = "Completed";
    } else if (normalized === "CANCELLED") {
        label = "Cancelled";
    } else if (normalized === "CONFIRMED") {
        label = "Confirmed";
    } else if (normalized === "ON_HOLD") {
        label = "On Hold";
    } else if (normalized === "PARTS_PENDING") {
        label = "Parts Pending";
    } else if (normalized === "CLOSED") {
        label = "Closed";
    }

    return (
        <span
            className={`engineer-status-badge engineer-status-${normalized.toLowerCase()}`}
        >
            {label}
        </span>
    );
};

/* =====================================================
   PRIORITY
===================================================== */

const PriorityBadge = ({ priority }) => {

    const value = String(
        priority || "NORMAL"
    ).toUpperCase();

    return (
        <span
            className={`engineer-priority-badge engineer-priority-${value.toLowerCase()}`}
        >
            {value}
        </span>
    );
};

/* =====================================================
   TABLE
===================================================== */

const EngineerTable = ({
    services = [],
    loading = false,

    onAccept,
    onReject,
    onComplete,

    acceptingId = null,
    rejectingId = null,
    completingId = null,

    onView,
    onUpdate,
}) => {

    /* =================================================
       UPDATE FORM
    ================================================= */

    const [updateService, setUpdateService] = useState(null);
    const [viewService, setViewService] = useState(null);

    const [updateForm, setUpdateForm] = useState({
        service_date: "",
        materials_used: "",
        service_cost: "",
        payment_status: "PENDING",
    });

    const openUpdateForm = (service) => {
        const rawDate =
            service?.service_date ||
            service?.completed_date ||
            service?.created_at ||
            service?.request_date ||
            "";

        let formattedDate = "";

        if (rawDate) {
            const parsedDate = new Date(rawDate);
            if (!Number.isNaN(parsedDate.getTime())) {
                formattedDate = parsedDate.toISOString().slice(0, 10);
            }
        }

        setUpdateService(service);

        setUpdateForm({
            service_date: formattedDate,
            materials_used:
                service?.materials_used ||
                service?.materials ||
                "",
            service_cost:
                service?.service_cost ??
                service?.cost ??
                "",
            payment_status:
                String(
                    service?.payment_status || "PENDING"
                ).toUpperCase(),
        });
    };

    const closeUpdateForm = () => {
        setUpdateService(null);

        setUpdateForm({
            service_date: "",
            materials_used: "",
            service_cost: "",
            payment_status: "PENDING",
        });
    };

    const handleUpdateFormChange = (event) => {
        const { name, value } = event.target;

        setUpdateForm((previous) => ({
            ...previous,
            [name]: value,
        }));
    };

    const handleUpdateSubmit = (event) => {
        event.preventDefault();

        if (!updateService) {
            return;
        }

        /*
         * Send both the service and the form data to the parent.
         * The parent component can call your existing API here.
         */
        if (typeof onUpdate === "function") {
            onUpdate(updateService, updateForm);
        }

        closeUpdateForm();
    };

    /* =================================================
       VIEW
    ================================================= */

    const handleView = (service) => {
        // Open the details drawer directly in this table component.
        setViewService(service);
    };

    const closeView = () => setViewService(null);

    const firstValue = (...values) =>
        values.find((value) => value !== undefined && value !== null && String(value).trim() !== "") || "-";

    const getCustomerPhone = (service) => firstValue(
        service?.customer?.mobile_number,
        service?.customer?.phone_number,
        service?.customer?.mobile,
        service?.customer?.phone,
        service?.customer_mobile,
        service?.customer_phone,
        service?.mobile_number,
        service?.phone_number,
        service?.mobile,
        service?.phone
    );

    const getCustomerEmail = (service) => firstValue(
        service?.customer?.email,
        service?.customer?.email_address,
        service?.customer_email,
        service?.email,
        service?.email_address
    );

    const getCustomerField = (service, ...keys) => firstValue(
        ...keys.flatMap((key) => [service?.customer?.[key], service?.[key]])
    );

    /* =================================================
       UPDATE
    ================================================= */

    const handleUpdate = (service) => {
        openUpdateForm(service);
    };

    /* =================================================
       ACCEPT
    ================================================= */

    const handleAccept = (service) => {

        if (
            typeof onAccept === "function"
        ) {
            onAccept(service);
        }
    };

    /* =================================================
       REJECT
    ================================================= */

    const handleReject = (service) => {

        if (
            typeof onReject === "function"
        ) {
            onReject(service);
        }
    };

    /* =================================================
       COMPLETE
    ================================================= */

    const handleComplete = (service) => {

        if (
            typeof onComplete === "function"
        ) {
            onComplete(service);
        }
    };

    /* =================================================
       LOADING
    ================================================= */

    if (loading) {

        return (
            <div className="engineer-table-wrapper">

                <div className="engineer-table-loading">

                    <div className="engineer-table-loading-spinner" />

                    <span>
                        Loading service requests...
                    </span>

                </div>

            </div>
        );
    }

    /* =================================================
       EMPTY
    ================================================= */

    if (!services.length) {

        return (
            <div className="engineer-table-wrapper">

                <div className="engineer-table-empty">

                    <div className="engineer-table-empty-icon">
                        <Clock3 size={25} />
                    </div>

                    <strong>
                        No service requests
                    </strong>

                    <span>
                        Assigned service requests
                        will appear here.
                    </span>

                </div>

            </div>
        );
    }

    /* =================================================
       RENDER
    ================================================= */

    return (
        <div className="engineer-table-wrapper">

            <div className="engineer-table-scroll">

                <table className="engineer-service-table">

                    <thead>
                        <tr>

                            <th className="engineer-col-number">
                                #
                            </th>

                            <th className="engineer-col-ticket">
                                Ticket
                            </th>

                            <th className="engineer-col-customer">
                                Customer
                            </th>

                            <th className="engineer-col-machine">
                                Product / Machine
                            </th>

                            <th className="engineer-col-issue">
                                Issue
                            </th>

                            <th className="engineer-col-technician">
                                Technician
                            </th>

                            <th className="engineer-col-priority">
                                Priority
                            </th>

                            <th className="engineer-col-status">
                                Status
                            </th>

                            <th className="engineer-col-date">
                                Date
                            </th>

                            <th className="engineer-col-actions">
                                Actions
                            </th>

                        </tr>
                    </thead>

                    <tbody>

                        {services.map(
                            (service, index) => {

                                const status =
                                    normalizeStatus(
                                        service
                                    );

                                const isAssigned =
                                    status ===
                                    "ASSIGNED";

                                const isInProgress =
                                    status ===
                                    "IN_PROGRESS";

                                const isCompleted =
                                    status ===
                                    "COMPLETED";

                                const isClosed =
                                    status ===
                                    "CLOSED";

                                const customerName =
                                    getCustomerName(
                                        service
                                    );

                                const customerAddress =
                                    getCustomerAddress(
                                        service
                                    );

                                const machineName =
                                    getMachineName(
                                        service
                                    );

                                const serialNumber =
                                    getSerialNumber(
                                        service
                                    );

                                return (
                                    <tr
                                        key={
                                            service?.id ||
                                            service?.ticket_number ||
                                            index
                                        }
                                    >

                                        {/* =================================
                                            NUMBER
                                        ================================= */}

                                        <td className="engineer-number-cell">
                                            {index + 1}
                                        </td>

                                        {/* =================================
                                            TICKET
                                        ================================= */}

                                        <td>

                                            <div className="engineer-ticket-cell">

                                                <strong>
                                                    {
                                                        service?.ticket_number ||
                                                        `#${service?.id || "-"}`
                                                    }
                                                </strong>

                                            </div>

                                        </td>

                                        {/* =================================
                                            CUSTOMER
                                        ================================= */}

                                        <td>

                                            <div className="engineer-customer-cell">

                                                <strong>
                                                    {
                                                        customerName
                                                    }
                                                </strong>

                                                <div className="engineer-address">

                                                    <MapPin
                                                        size={
                                                            11
                                                        }
                                                    />

                                                    <span>
                                                        {
                                                            customerAddress
                                                        }
                                                    </span>

                                                </div>

                                            </div>

                                        </td>

                                        {/* =================================
                                            MACHINE
                                        ================================= */}

                                        <td>

                                            <div className="engineer-machine-cell">

                                                <strong>
                                                    {
                                                        machineName
                                                    }
                                                </strong>

                                                {serialNumber !==
                                                    "-" && (
                                                    <span>
                                                        Serial:{" "}
                                                        {
                                                            serialNumber
                                                        }
                                                    </span>
                                                )}

                                            </div>

                                        </td>

                                        {/* =================================
                                            ISSUE
                                        ================================= */}

                                        <td>

                                            <div className="engineer-issue-cell">

                                                {
                                                    getIssue(
                                                        service
                                                    )
                                                }

                                            </div>

                                        </td>

                                        {/* =================================
                                            TECHNICIAN
                                        ================================= */}

                                        <td>

                                            <div className="engineer-technician-cell">

                                                {
                                                    getEngineerName(
                                                        service
                                                    )
                                                }

                                            </div>

                                        </td>

                                        {/* =================================
                                            PRIORITY
                                        ================================= */}

                                        <td>

                                            <PriorityBadge
                                                priority={
                                                    getPriority(
                                                        service
                                                    )
                                                }
                                            />

                                        </td>

                                        {/* =================================
                                            STATUS
                                        ================================= */}

                                        <td>

                                            <StatusBadge
                                                status={
                                                    status
                                                }
                                            />

                                        </td>

                                        {/* =================================
                                            DATE
                                        ================================= */}

                                        <td>

                                            <div className="engineer-date-cell">

                                                <Clock3
                                                    size={
                                                        13
                                                    }
                                                />

                                                <span>
                                                    {
                                                        getDate(
                                                            service
                                                        )
                                                    }
                                                </span>

                                            </div>

                                        </td>

                                        {/* =================================
                                            ACTIONS
                                        ================================= */}

                                        <td>

                                            <div className="engineer-actions-cell">

                                                {/* VIEW */}

                                                <button
                                                    type="button"
                                                    className="engineer-view-button"
                                                    onClick={() =>
                                                        handleView(
                                                            service
                                                        )
                                                    }
                                                >

                                                    <Eye
                                                        size={
                                                            14
                                                        }
                                                    />

                                                    <span>
                                                        View
                                                    </span>

                                                </button>

                                                {/* =================================
                                                    ASSIGNED
                                                    SHOW ACCEPT + REJECT
                                                ================================= */}

                                                {isAssigned && (
                                                    <>
                                                        <button
                                                            type="button"
                                                            className="engineer-accept-button"
                                                            onClick={() =>
                                                                handleAccept(
                                                                    service
                                                                )
                                                            }
                                                            disabled={
                                                                acceptingId ===
                                                                service?.id
                                                            }
                                                        >

                                                            <CheckCircle2
                                                                size={
                                                                    14
                                                                }
                                                            />

                                                            <span>
                                                                {acceptingId ===
                                                                service?.id
                                                                    ? "Accepting..."
                                                                    : "Accept"}
                                                            </span>

                                                        </button>

                                                        <button
                                                            type="button"
                                                            className="engineer-reject-button"
                                                            onClick={() =>
                                                                handleReject(
                                                                    service
                                                                )
                                                            }
                                                            disabled={
                                                                rejectingId ===
                                                                service?.id
                                                            }
                                                        >

                                                            <XCircle
                                                                size={
                                                                    14
                                                                }
                                                            />

                                                            <span>
                                                                {rejectingId ===
                                                                service?.id
                                                                    ? "Rejecting..."
                                                                    : "Reject"}
                                                            </span>

                                                        </button>
                                                    </>
                                                )}

                                                {/* =================================
                                                    IN PROGRESS
                                                    SHOW COMPLETE
                                                ================================= */}

                                                {isInProgress && (
                                                    <button
                                                        type="button"
                                                        className="engineer-complete-action-button"
                                                        onClick={() =>
                                                            handleComplete(
                                                                service
                                                            )
                                                        }
                                                        disabled={
                                                            completingId ===
                                                            service?.id
                                                        }
                                                    >

                                                        <CheckCircle2
                                                            size={
                                                                14
                                                            }
                                                        />

                                                        <span>
                                                            {completingId ===
                                                            service?.id
                                                                ? "Completing..."
                                                                : "Complete"}
                                                        </span>

                                                    </button>
                                                )}

                                                {/* =================================
                                                    COMPLETED
                                                    SHOW COMPLETED BUTTON
                                                ================================= */}

                                                {isCompleted && (
                                                    <button
                                                        type="button"
                                                        className="engineer-completed-action-button"
                                                        disabled
                                                    >

                                                        <CheckCircle2
                                                            size={
                                                                14
                                                            }
                                                        />

                                                        <span>
                                                            Completed
                                                        </span>

                                                    </button>
                                                )}

                                                {/* =================================
                                                    UPDATE
                                                    SHOW UPDATE BUTTON
                                                ================================= */}

                                                <button
                                                    type="button"
                                                    className="engineer-update-action-button"
                                                    onClick={() =>
                                                        handleUpdate(
                                                            service
                                                        )
                                                    }
                                                >

                                                    <Pencil
                                                        size={
                                                            14
                                                        }
                                                    />

                                                    <span>
                                                        Update
                                                    </span>

                                                </button>

                                                {/* =================================
                                                    CLOSED
                                                ================================= */}

                                                {isClosed && (
                                                    <button
                                                        type="button"
                                                        className="engineer-closed-action-button"
                                                        disabled
                                                    >

                                                        <CheckCircle2
                                                            size={
                                                                14
                                                            }
                                                        />

                                                        <span>
                                                            Closed
                                                        </span>

                                                    </button>
                                                )}

                                            </div>

                                        </td>

                                    </tr>
                                );
                            }
                        )}

                    </tbody>

                </table>

            </div>

            {/* =====================================================
                CUSTOMER / SERVICE DETAILS POPUP MODAL
            ===================================================== */}
            {viewService && (
                <div
                    className="engineer-view-overlay"
                    role="presentation"
                    onMouseDown={(event) => {
                        if (event.target === event.currentTarget) closeView();
                    }}
                    style={{
                        position: "fixed", inset: 0, zIndex: 1200,
                        background: "rgba(15, 23, 42, 0.62)",
                        display: "flex", justifyContent: "center", alignItems: "center",
                        padding: "20px", boxSizing: "border-box", backdropFilter: "blur(3px)"
                    }}
                >
                    <aside
                        className="engineer-view-drawer"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="engineer-view-title"
                        style={{
                            width: "min(760px, 100%)", maxHeight: "min(88vh, 900px)", overflowY: "auto",
                            background: "#fff", boxShadow: "0 24px 80px rgba(15,23,42,.30)",
                            borderRadius: "18px", border: "1px solid rgba(226,232,240,.9)",
                            padding: "26px", boxSizing: "border-box", color: "#172033"
                        }}
                    >
                        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16, borderBottom: "1px solid #e2e8f0", paddingBottom: 18, marginBottom: 18 }}>
                            <div>
                                <div style={{ color: "#2563eb", fontSize: 12, fontWeight: 800, letterSpacing: 1 }}>CUSTOMER DETAILS</div>
                                <h2 id="engineer-view-title" style={{ margin: "6px 0", fontSize: 23 }}>{getCustomerName(viewService)}</h2>
                                <div style={{ color: "#64748b", fontSize: 13 }}>{viewService?.ticket_number || `Ticket #${viewService?.id || "-"}`}</div>
                            </div>
                            <button type="button" onClick={closeView} aria-label="Close customer details" style={{ border: "1px solid #cbd5e1", background: "#fff", borderRadius: 9, padding: 8, cursor: "pointer" }}><X size={19} /></button>
                        </div>

                        <section style={{ marginBottom: 22 }}>
                            <h3 style={{ fontSize: 15, margin: "0 0 12px", color: "#0f172a" }}>Contact information</h3>
                            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 250px), 1fr))", gap: 10 }}>
                                <div style={{ padding: 12, border: "1px solid #e2e8f0", borderRadius: 10 }}>
                                    <div style={{ color: "#64748b", fontSize: 12, marginBottom: 5 }}>Customer / Company name</div>
                                    <strong>{getCustomerName(viewService)}</strong>
                                </div>
                                <div style={{ padding: 12, border: "1px solid #e2e8f0", borderRadius: 10 }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: 7, color: "#64748b", fontSize: 12, marginBottom: 5 }}><Phone size={13} /> Mobile number</div>
                                    <strong>{getCustomerPhone(viewService)}</strong>
                                </div>
                                <div style={{ padding: 12, border: "1px solid #e2e8f0", borderRadius: 10 }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: 7, color: "#64748b", fontSize: 12, marginBottom: 5 }}><Mail size={13} /> Email address</div>
                                    <strong style={{ overflowWrap: "anywhere" }}>{getCustomerEmail(viewService)}</strong>
                                </div>
                                <div style={{ padding: 12, border: "1px solid #e2e8f0", borderRadius: 10 }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: 7, color: "#64748b", fontSize: 12, marginBottom: 5 }}><MapPin size={13} /> Full address</div>
                                    <strong style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>{firstValue(viewService?.customer?.full_address, viewService?.customer?.address, viewService?.customer_address, viewService?.address)}</strong>
                                    <div style={{ marginTop: 6, color: "#475569", fontSize: 13 }}>
                                        {[getCustomerField(viewService, "city"), getCustomerField(viewService, "state"), getCustomerField(viewService, "pincode", "postal_code", "zip_code"), getCustomerField(viewService, "country")].filter((v) => v !== "-").join(", ") || "-"}
                                    </div>
                                </div>
                                <div style={{ padding: 12, border: "1px solid #e2e8f0", borderRadius: 10 }}>
                                    <div style={{ color: "#64748b", fontSize: 12, marginBottom: 5 }}>GSTIN</div>
                                    <strong>{getCustomerField(viewService, "gstin", "gst_number", "gst_no")}</strong>
                                </div>
                            </div>
                        </section>

                        <section style={{ marginBottom: 22 }}>
                            <h3 style={{ fontSize: 15, margin: "0 0 12px", color: "#0f172a" }}>Machine details</h3>
                            <div style={{ padding: 14, background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 10, display: "grid", gap: 10 }}>
                                <div><div style={{ color: "#64748b", fontSize: 12 }}>Product / Machine</div><strong>{getMachineName(viewService)}</strong></div>
                                <div><div style={{ color: "#64748b", fontSize: 12 }}>Serial number</div><strong>{getSerialNumber(viewService)}</strong></div>
                            </div>
                        </section>

                        <section style={{ marginBottom: 22 }}>
                            <h3 style={{ fontSize: 15, margin: "0 0 12px", color: "#0f172a" }}>Service request</h3>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                                <div style={{ padding: 12, background: "#f8fafc", borderRadius: 9 }}><div style={{ color: "#64748b", fontSize: 12 }}>Status</div><strong>{viewService?.status || "-"}</strong></div>
                                <div style={{ padding: 12, background: "#f8fafc", borderRadius: 9 }}><div style={{ color: "#64748b", fontSize: 12 }}>Priority</div><strong>{getPriority(viewService)}</strong></div>
                                <div style={{ padding: 12, background: "#f8fafc", borderRadius: 9 }}><div style={{ color: "#64748b", fontSize: 12 }}>Technician</div><strong>{getEngineerName(viewService)}</strong></div>
                                <div style={{ padding: 12, background: "#f8fafc", borderRadius: 9 }}><div style={{ color: "#64748b", fontSize: 12 }}>Date</div><strong>{getDate(viewService)}</strong></div>
                            </div>
                            <div style={{ marginTop: 10, padding: 12, border: "1px solid #e2e8f0", borderRadius: 10 }}><div style={{ color: "#64748b", fontSize: 12, marginBottom: 5 }}>Issue / Complaint</div><div style={{ whiteSpace: "pre-wrap" }}>{getIssue(viewService)}</div></div>
                        </section>

                        <button type="button" onClick={closeView} style={{ width: "100%", padding: "11px 16px", border: 0, borderRadius: 9, background: "#1d4ed8", color: "#fff", fontWeight: 700, cursor: "pointer" }}>Close details</button>
                    </aside>
                </div>
            )}

            {/* =====================================================
                UPDATE SERVICE DRAWER
            ===================================================== */}

            {updateService && (
                <div
                    className="engineer-update-overlay"
                    onMouseDown={(event) => {
                        if (event.target === event.currentTarget) {
                            closeUpdateForm();
                        }
                    }}
                >
                    <div
                        className="engineer-update-drawer engineer-update-popup"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="engineer-update-title"
                    >

                        <div className="engineer-update-drawer-header">

                            <div>
                                <span className="engineer-update-eyebrow">
                                    SERVICE UPDATE
                                </span>

                                <h2 id="engineer-update-title">
                                    Update Service
                                </h2>

                                <p>
                                    {updateService?.ticket_number ||
                                        `#${updateService?.id || "-"}`}
                                </p>
                            </div>

                            <button
                                type="button"
                                className="engineer-update-close-button"
                                onClick={closeUpdateForm}
                                aria-label="Close update form"
                            >
                                <XCircle size={20} />
                            </button>

                        </div>

                        <form
                            className="engineer-update-form"
                            onSubmit={handleUpdateSubmit}
                        >

                            <div className="engineer-update-field">
                                <label htmlFor="service_date">
                                    Service Date
                                </label>

                                <input
                                    id="service_date"
                                    name="service_date"
                                    type="date"
                                    value={updateForm.service_date}
                                    onChange={handleUpdateFormChange}
                                    required
                                />
                            </div>

                            <div className="engineer-update-field">
                                <label htmlFor="materials_used">
                                    Materials Used
                                </label>

                                <textarea
                                    id="materials_used"
                                    name="materials_used"
                                    rows="4"
                                    value={updateForm.materials_used}
                                    onChange={handleUpdateFormChange}
                                    placeholder="Enter materials used during service"
                                />
                            </div>

                            <div className="engineer-update-field">
                                <label htmlFor="service_cost">
                                    Service Cost
                                </label>

                                <div className="engineer-cost-input">
                                    <span>₹</span>

                                    <input
                                        id="service_cost"
                                        name="service_cost"
                                        type="number"
                                        min="0"
                                        step="0.01"
                                        value={updateForm.service_cost}
                                        onChange={handleUpdateFormChange}
                                        placeholder="0.00"
                                    />
                                </div>
                            </div>

                            <div className="engineer-update-field">
                                <label htmlFor="payment_status">
                                    Payment Status
                                </label>

                                <select
                                    id="payment_status"
                                    name="payment_status"
                                    value={updateForm.payment_status}
                                    onChange={handleUpdateFormChange}
                                >
                                    <option value="PENDING">
                                        Pending
                                    </option>

                                    <option value="RECEIVED">
                                        Received
                                    </option>
                                </select>
                            </div>

                            <div className="engineer-update-actions">

                                <button
                                    type="button"
                                    className="engineer-update-cancel-button"
                                    onClick={closeUpdateForm}
                                >
                                    Cancel
                                </button>

                                <button
                                    type="submit"
                                    className="engineer-update-save-button"
                                >
                                    <CheckCircle2 size={15} />
                                    Save Update
                                </button>

                            </div>

                        </form>

                    </div>
                </div>
            )}

        </div>
    );
};

export default EngineerTable;