import "./ServiceTable.css";

import {
    Eye,
    Pencil,
    Ban,
    UserRoundPlus,
} from "lucide-react";


const ServiceTable = ({
    services = [],
    onView,
    onEdit,
    onDelete,
    onAssignEngineer,
}) => {


    // =====================================================
    // STATUS LABEL
    // =====================================================

    const getStatusLabel = (status) => {
        const normalizedStatus = String(status || "")
            .trim()
            .toUpperCase();

        switch (normalizedStatus) {
            case "OPEN":
                return "Open";

            case "REQUESTED":
                return "Requested";

            case "ASSIGNED":
                return "Assigned";

            case "CONFIRMED":
                return "Confirmed";

            case "IN_PROGRESS":
                return "In Progress";

            case "ON_HOLD":
                return "On Hold";

            case "PARTS_PENDING":
                return "Parts Pending";

            case "WAITING_FOR_PARTS":
                return "Waiting For Parts";

            case "COMPLETED":
                return "Completed";

            case "CLOSED":
                return "Closed";

            case "PENDING":
                return "Pending";

            case "CANCELLED":
                return "Cancelled";

            case "REJECTED":
                return "Rejected";

            default:
                return status || "-";
        }
    };


    // =====================================================
    // PRIORITY LABEL
    // =====================================================

    const getPriorityLabel = (priority) => {

        switch (priority) {

            case "LOW":
                return "Low";

            case "MEDIUM":
                return "Medium";

            case "NORMAL":
                return "Normal";

            case "HIGH":
                return "High";

            case "URGENT":
                return "Urgent";

            default:
                return priority || "-";
        }
    };


    // =====================================================
    // CUSTOMER NAME
    // =====================================================

    const getCustomerName = (service) => {

        return (
            service.customer_name ||
            service.customer?.customer_name ||
            service.customer?.name ||
            service.customer_details?.customer_name ||
            service.customer_details?.name ||
            "-"
        );
    };


    // =====================================================
    // PRODUCT NAME
    // =====================================================

    const getProductName = (service) => {

        return (
            service.product_name ||
            service.product?.product_name ||
            service.product?.name ||
            service.product_details?.product_name ||
            service.product_details?.name ||
            service.machine_number ||
            service.machine?.machine_number ||
            "-"
        );
    };


    // =====================================================
    // TECHNICIAN / ENGINEER NAME
    // =====================================================

    const getTechnicianName = (service) => {

        return (
            service.engineer_name ||
            service.technician ||
            service.engineer?.full_name ||
            service.engineer?.name ||
            service.assigned_engineer?.full_name ||
            service.assigned_engineer?.name ||
            service.engineer_details?.full_name ||
            service.engineer_details?.name ||
            "-"
        );
    };


    // =====================================================
    // ISSUE
    // =====================================================

    const getIssue = (service) => {

        return (
            service.issue ||
            service.complaint ||
            service.problem_description ||
            service.subject ||
            "-"
        );
    };


    // =====================================================
    // DATE
    // =====================================================

    const getServiceDate = (service) => {

        return (
            service.service_date ||
            service.reported_date ||
            service.created_at?.split("T")[0] ||
            "-"
        );
    };


    // =====================================================
    // MATERIAL USED
    // =====================================================

    const getMaterialUsed = (service) => {

        return (
            service.material_used ??
            service.materialUsed ??
            service.material ??
            service.material_details?.name ??
            "-"
        );
    };


    // =====================================================
    // SERVICE COST + PAYMENT STATUS
    // =====================================================

    const getPaymentStatus = (service) => {

        const value =
            service?.payment_status ||
            service?.payment?.status ||
            service?.payment?.payment_status ||
            "";

        const normalized =
            String(value)
                .trim()
                .toUpperCase();

        if (!normalized) {
            return {
                value: "PENDING",
                label: "Pending",
            };
        }

        const labels = {
            PENDING: "Pending",
            RECEIVED: "Received",
            RECEIVED_BY_HAND: "Received by Hand",
            RECEIVED_TO_HAND: "Received by Hand",
            RECEIVED_TO_ACCOUNT: "Received to Account",
            PARTIALLY_RECEIVED_BY_HAND:
                "Partially Received by Hand",
            PARTIALLY_RECEIVED_TO_ACCOUNT:
                "Partially Received to Account",
        };

        return {
            value: normalized,
            label:
                labels[normalized] ||
                normalized.replace(/_/g, " "),
        };
    };


    const PaymentBadge = ({ service }) => {

        const payment =
            getPaymentStatus(service);

        const isReceived =
            payment.value === "RECEIVED" ||
            payment.value === "RECEIVED_BY_HAND" ||
            payment.value === "RECEIVED_TO_HAND" ||
            payment.value === "RECEIVED_TO_ACCOUNT";

        const isPartial =
            payment.value === "PARTIALLY_RECEIVED_BY_HAND" ||
            payment.value === "PARTIALLY_RECEIVED_TO_ACCOUNT";

        const badgeStyle = {
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            whiteSpace: "nowrap",
            padding: "5px 9px",
            borderRadius: "7px",
            fontSize: "10px",
            fontWeight: 700,
            lineHeight: 1.2,
            border: "1px solid",
            background: isPartial
                ? "#fff7ed"
                : isReceived
                    ? "#ecfdf5"
                    : "#f8fafc",
            color: isPartial
                ? "#c2410c"
                : isReceived
                    ? "#047857"
                    : "#475569",
            borderColor: isPartial
                ? "#fed7aa"
                : isReceived
                    ? "#a7f3d0"
                    : "#cbd5e1",
        };

        return (
            <span
                className={`engineer-payment-badge engineer-payment-${payment.value.toLowerCase()}`}
                style={badgeStyle}
            >
                {payment.label}
            </span>
        );
    };


    const PaymentCell = ({ service }) => {

        const value =
            service?.service_cost ??
            service?.serviceCost;

        let amount = "-";

        if (
            value !== null &&
            value !== undefined &&
            value !== ""
        ) {
            const numericAmount = Number(value);

            if (!Number.isNaN(numericAmount)) {
                amount =
                    numericAmount.toLocaleString(
                        "en-IN",
                        {
                            minimumFractionDigits: 0,
                            maximumFractionDigits: 2,
                        }
                    );
            }
        }

        return (
            <div
                className="engineer-payment-cell"
                style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    gap: "5px",
                    minWidth: "105px",
                }}
            >
                <strong
                    className="engineer-payment-amount"
                    style={{
                        fontSize: "12px",
                        fontWeight: 800,
                        color: "#0f172a",
                        whiteSpace: "nowrap",
                    }}
                >
                    ₹ {amount}
                </strong>

                <PaymentBadge service={service} />
            </div>
        );
    };


    // =====================================================
    // CHECK ENGINEER ASSIGNED
    // =====================================================

    const hasEngineer = (service) => {

        return Boolean(
            service.assigned_engineer_id ||
            service.engineer_id ||
            service.engineer_name ||
            service.technician ||
            service.engineer ||
            service.assigned_engineer
        );
    };


    // =====================================================
    // RENDER
    // =====================================================

    return (

        <div className="service-table-wrapper">

            <table className="service-data-table">

                {/* =================================================
                    TABLE HEADER
                ================================================: */}

                <thead>

                    <tr>

                        <th>
                            #
                        </th>

                        <th>
                            Ticket
                        </th>

                        <th>
                            Customer
                        </th>

                        <th>
                            Product
                        </th>

                        <th>
                            Issue
                        </th>

                        <th>
                            Technician
                        </th>

                        <th>
                            Priority
                        </th>

                        <th>
                            Status
                        </th>

                        <th>
                            Date
                        </th>

                        <th>
                            Material Used
                        </th>

                        <th>
                            Service Cost
                        </th>

                        <th>
                            Actions
                        </th>

                    </tr>

                </thead>


                {/* =================================================
                    TABLE BODY
                ================================================: */}

                <tbody>

                    {services.length === 0 ? (

                        <tr>

                            <td
                                colSpan="12"
                                className="service-table-empty"
                            >

                                No service records found.

                            </td>

                        </tr>

                    ) : (

                        services.map(
                            (service, index) => (

                                <tr
                                    key={
                                        service.id ??
                                        service.ticket_number ??
                                        index
                                    }
                                >

                                    {/* =================================
                                        #
                                    ================================= */}

                                    <td>
                                        {index + 1}
                                    </td>


                                    {/* =================================
                                        TICKET
                                    ================================= */}

                                    <td>

                                        <strong
                                            className="service-ticket-number"
                                        >

                                            {
                                                service.ticket_number ||
                                                "-"
                                            }

                                        </strong>

                                    </td>


                                    {/* =================================
                                        CUSTOMER
                                    ================================= */}

                                    <td>

                                        <span
                                            className="service-customer"
                                        >

                                            {
                                                getCustomerName(
                                                    service
                                                )
                                            }

                                        </span>

                                    </td>


                                    {/* =================================
                                        PRODUCT
                                    ================================= */}

                                    <td>

                                        {
                                            getProductName(
                                                service
                                            )
                                        }

                                    </td>


                                    {/* =================================
                                        ISSUE
                                    ================================= */}

                                    <td>

                                        <span
                                            className="service-issue"
                                        >

                                            {
                                                getIssue(
                                                    service
                                                )
                                            }

                                        </span>

                                    </td>


                                    {/* =================================
                                        TECHNICIAN
                                    ================================= */}

                                    <td>

                                        {
                                            getTechnicianName(
                                                service
                                            )
                                        }

                                    </td>


                                    {/* =================================
                                        PRIORITY
                                    ================================= */}

                                    <td>

                                        <span
                                            className={
                                                `service-priority ${
                                                    (
                                                        service.priority ||
                                                        ""
                                                    ).toLowerCase()
                                                }`
                                            }
                                        >

                                            {
                                                getPriorityLabel(
                                                    service.priority
                                                )
                                            }

                                        </span>

                                    </td>


                                    {/* =================================
                                        STATUS
                                    ================================= */}

                                    <td>

                                        <span
                                            className={
                                                `service-status-badge ${
                                                    (
                                                        service.status ||
                                                        ""
                                                    ).toLowerCase()
                                                }`
                                            }
                                        >

                                            {
                                                getStatusLabel(
                                                    service.status
                                                )
                                            }

                                        </span>

                                    </td>


                                    {/* =================================
                                        DATE
                                    ================================= */}

                                    <td>

                                        {
                                            getServiceDate(
                                                service
                                            )
                                        }

                                    </td>


                                    {/* =================================
                                        MATERIAL USED
                                    ================================= */}

                                    <td>

                                        <span
                                            className="service-material"
                                            title={String(
                                                getMaterialUsed(service)
                                            )}
                                        >

                                            {
                                                getMaterialUsed(
                                                    service
                                                )
                                            }

                                        </span>

                                    </td>
                                    {/* =================================
                                        SERVICE COST + PAYMENT STATUS
                                    ================================= */}

                                    <td>
                                        <PaymentCell
                                            service={service}
                                        />
                                    </td>


                                    {/* =================================
                                        ACTIONS
                                    ================================= */}

                                    <td>

                                        <div
                                            className="service-table-actions"
                                        >


                                            {/* =================================
                                                VIEW
                                            ================================= */}

                                            <button
                                                type="button"
                                                className="service-table-action view"
                                                title="View Service"
                                                onClick={() =>
                                                    onView?.(
                                                        service
                                                    )
                                                }
                                            >

                                                <Eye
                                                    size={16}
                                                />

                                            </button>


                                            {/* =================================
                                                ASSIGN ENGINEER
                                            ================================= */}

                                            <div
                                                className="service-engineer-action"
                                            >

                                                <button
                                                    type="button"
                                                    className="service-table-action assign"
                                                    aria-label={
                                                        hasEngineer(service)
                                                            ? "Change Engineer"
                                                            : "Assign Engineer"
                                                    }
                                                    onClick={() =>
                                                        onAssignEngineer?.(
                                                            service
                                                        )
                                                    }
                                                >

                                                    <UserRoundPlus
                                                        size={16}
                                                    />

                                                </button>


                                                {/* =================================
                                                    HOVER TOOLTIP
                                                ================================= */}

                                                <span
                                                    className="service-engineer-tooltip"
                                                >

                                                    {
                                                        hasEngineer(service)
                                                            ? "Change Engineer"
                                                            : "Assign Engineer"
                                                    }

                                                </span>

                                            </div>


                                            {/* =================================
                                                EDIT
                                            ================================= */}

                                            <button
                                                type="button"
                                                className="service-table-action edit"
                                                title="Edit Service"
                                                onClick={() =>
                                                    onEdit?.(
                                                        service
                                                    )
                                                }
                                            >

                                                <Pencil
                                                    size={16}
                                                />

                                            </button>


                                            {/* =================================
                                                CANCEL SERVICE / DELETE ICON
                                            ================================= */}

                                            {String(
                                                service.status ||
                                                ""
                                            ).toUpperCase() ===
                                                "CANCELLED" ? (

                                                <button
                                                    type="button"
                                                    className="service-table-action delete"
                                                    title="Service Cancelled"
                                                    disabled
                                                >

                                                    <Ban
                                                        size={16}
                                                    />

                                                </button>

                                            ) : (

                                                <button
                                                    type="button"
                                                    className="service-table-action delete"
                                                    title="Service Cancelled"
                                                    onClick={() =>
                                                        onDelete?.(
                                                            service
                                                        )
                                                    }
                                                >

                                                    <Ban
                                                        size={16}
                                                    />

                                                </button>

                                            )}


                                        </div>

                                    </td>

                                </tr>

                            )
                        )

                    )}

                </tbody>

            </table>

        </div>

    );

};

export default ServiceTable;