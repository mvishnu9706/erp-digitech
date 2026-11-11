import "./ServiceDetails.css";

import {
    X,
    Wrench,
    User,
    Package,
    CalendarDays,
    Phone,
    Mail,
    MapPin,
    UserCog,
    IndianRupee,
    FileText,
    Gauge,
} from "lucide-react";


const ServiceDetails = ({
    open = false,
    service = null,
    onClose,
}) => {

    if (!open || !service) {
        return null;
    }


    // =====================================================
    // Helpers
    // =====================================================

    const getStatusLabel = (status) => {

        switch (status) {

            case "OPEN":
                return "Open";

            case "IN_PROGRESS":
                return "In Progress";

            case "WAITING_FOR_PARTS":
                return "Waiting For Parts";

            case "COMPLETED":
                return "Completed";

            case "PENDING":
                return "Pending";

            case "CANCELLED":
                return "Cancelled";

            default:
                return status || "-";

        }

    };


    const getPriorityLabel = (priority) => {

        switch (priority) {

            case "LOW":
                return "Low";

            case "NORMAL":
                return "Normal";

            case "MEDIUM":
                return "Medium";

            case "HIGH":
                return "High";

            case "URGENT":
                return "Urgent";

            default:
                return priority || "-";

        }

    };


    const formatAmount = (amount) => {

        return `₹ ${Number(
            amount || 0
        ).toLocaleString("en-IN")}`;

    };


    return (

        <div className="service-details-overlay">


            {/* =================================================
                PANEL
            ================================================= */}

            <div className="service-details-panel">


                {/* =================================================
                    HEADER
                ================================================= */}

                <div className="service-details-header">

                    <div className="service-details-heading">

                        <div className="service-details-icon">

                            <Wrench size={21} />

                        </div>


                        <div>

                            <h2>
                                Service Details
                            </h2>

                            <p>
                                {
                                    service.ticket_number ||
                                    "Service Ticket"
                                }
                            </p>

                        </div>

                    </div>


                    <button
                        type="button"
                        className="service-details-close"
                        onClick={onClose}
                    >

                        <X size={20} />

                    </button>

                </div>


                {/* =================================================
                    CONTENT
                ================================================= */}

                <div className="service-details-content">


                    {/* =================================================
                        STATUS SECTION
                    ================================================= */}

                    <div className="service-details-status-row">

                        <div>

                            <span className="service-details-label">
                                Ticket
                            </span>

                            <strong>
                                {
                                    service.ticket_number ||
                                    "-"
                                }
                            </strong>

                        </div>


                        <div className="service-details-status-group">

                            <span
                                className={
                                    `service-details-status ${
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


                            <span
                                className={
                                    `service-details-priority ${
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

                        </div>

                    </div>


                    {/* =================================================
                        CUSTOMER
                    ================================================= */}

                    <div className="service-details-section">

                        <div className="service-details-section-title">

                            <User size={17} />

                            <h3>
                                Customer Information
                            </h3>

                        </div>


                        <div className="service-details-grid">


                            <div className="service-detail-item">

                                <span>
                                    Customer
                                </span>

                                <strong>
                                    {
                                        service.customer ||
                                        "-"
                                    }
                                </strong>

                            </div>


                            <div className="service-detail-item">

                                <span>
                                    Phone
                                </span>

                                <strong>

                                    {service.phone ? (

                                        <span className="service-detail-inline">

                                            <Phone size={14} />

                                            {service.phone}

                                        </span>

                                    ) : (
                                        "-"
                                    )}

                                </strong>

                            </div>


                            <div className="service-detail-item">

                                <span>
                                    Email
                                </span>

                                <strong>

                                    {service.email ? (

                                        <span className="service-detail-inline">

                                            <Mail size={14} />

                                            {service.email}

                                        </span>

                                    ) : (
                                        "-"
                                    )}

                                </strong>

                            </div>


                            <div className="service-detail-item full">

                                <span>
                                    Address
                                </span>

                                <strong>

                                    {service.address ? (

                                        <span className="service-detail-inline">

                                            <MapPin size={14} />

                                            {service.address}

                                        </span>

                                    ) : (
                                        "-"
                                    )}

                                </strong>

                            </div>

                        </div>

                    </div>


                    {/* =================================================
                        PRODUCT
                    ================================================= */}

                    <div className="service-details-section">

                        <div className="service-details-section-title">

                            <Package size={17} />

                            <h3>
                                Product & Issue
                            </h3>

                        </div>


                        <div className="service-details-grid">


                            <div className="service-detail-item">

                                <span>
                                    Product
                                </span>

                                <strong>
                                    {
                                        service.product ||
                                        "-"
                                    }
                                </strong>

                            </div>


                            <div className="service-detail-item">

                                <span>
                                    Service Date
                                </span>

                                <strong>

                                    <span className="service-detail-inline">

                                        <CalendarDays size={14} />

                                        {
                                            service.service_date ||
                                            "-"
                                        }

                                    </span>

                                </strong>

                            </div>


                            <div className="service-detail-item full">

                                <span>
                                    Issue
                                </span>

                                <strong>
                                    {
                                        service.issue ||
                                        "-"
                                    }
                                </strong>

                            </div>


                            <div className="service-detail-item full">

                                <span>
                                    Description
                                </span>

                                <div className="service-detail-description">

                                    <FileText size={15} />

                                    <span>
                                        {
                                            service.description ||
                                            "No description provided."
                                        }
                                    </span>

                                </div>

                            </div>

                        </div>

                    </div>


                    {/* =================================================
                        MACHINE METER READING
                    ================================================= */}

                    <div className="service-details-section">
                        <div className="service-details-section-title">
                            <Gauge size={17} />
                            <h3>Machine Meter Reading</h3>
                        </div>

                        <div className="service-details-grid">
                            <div className="service-detail-item">
                                <span>Reading submitted with request</span>
                                <strong>
                                    {(() => {
                                        const reading =
                                            service.meter_reading ??
                                            service.current_meter_reading ??
                                            service.currentMeterReading;

                                        return reading !== null && reading !== undefined && reading !== ""
                                            ? Number(reading).toLocaleString("en-IN")
                                            : "Not provided";
                                    })()}
                                </strong>
                            </div>
                        </div>
                    </div>


                    {/* =================================================
                        ASSIGNMENT
                    ================================================= */}

                    <div className="service-details-section">

                        <div className="service-details-section-title">

                            <UserCog size={17} />

                            <h3>
                                Assignment
                            </h3>

                        </div>


                        <div className="service-details-grid">


                            <div className="service-detail-item">

                                <span>
                                    Technician
                                </span>

                                <strong>
                                    {
                                        service.technician ||
                                        "-"
                                    }
                                </strong>

                            </div>


                            <div className="service-detail-item">

                                <span>
                                    Priority
                                </span>

                                <strong>

                                    <span
                                        className={
                                            `service-details-priority ${
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

                                </strong>

                            </div>

                        </div>

                    </div>


                    {/* =================================================
                        AMOUNT
                    ================================================= */}

                    <div className="service-details-amount">

                        <div className="service-details-amount-icon">

                            <IndianRupee size={20} />

                        </div>


                        <div>

                            <span>
                                Service Amount
                            </span>

                            <strong>
                                {
                                    formatAmount(
                                        service.total_amount
                                    )
                                }
                            </strong>

                        </div>

                    </div>


                </div>


                {/* =================================================
                    FOOTER
                ================================================= */}

                <div className="service-details-footer">

                    <button
                        type="button"
                        onClick={onClose}
                    >
                        Close
                    </button>

                </div>


            </div>

        </div>

    );

};


export default ServiceDetails;