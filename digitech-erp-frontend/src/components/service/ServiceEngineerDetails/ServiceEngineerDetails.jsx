import React, { useMemo } from "react";

import {
    CalendarDays,
    CheckCircle2,
    Clock3,
    IndianRupee,
    Package,
    UserRound,
    Wrench,
} from "lucide-react";

import "./ServiceEngineerDetails.css";

/* =========================================================
   HELPERS
   ========================================================= */

const normalize = (value) =>
    String(value ?? "")
        .trim()
        .toLowerCase();

/* =========================================================
   ENGINEER NAME
   ========================================================= */

const getEngineerName = (service) => {
    const name =
        service?.technician ||
        service?.engineer_name ||
        service?.engineer?.full_name ||
        service?.engineer?.name ||
        service?.engineer?.username ||
        service?.assigned_engineer?.full_name ||
        service?.assigned_engineer?.name ||
        service?.assigned_engineer?.username ||
        "";

    return String(name).trim();
};

/* =========================================================
   ENGINEER ID
   ========================================================= */

const getEngineerId = (service) => {
    return (
        service?.engineer_id ??
        service?.assigned_engineer_id ??
        service?.engineer?.id ??
        service?.assigned_engineer?.id ??
        null
    );
};

/* =========================================================
   SERVICE DATE
   ========================================================= */

const getServiceDate = (service) => {
    return (
        service?.completed_date ||
        service?.completion_date ||
        service?.completed_at ||
        service?.completion_at ||
        service?.service_date ||
        service?.serviceDate ||
        service?.date ||
        service?.created_at ||
        service?.createdAt ||
        null
    );
};

/* =========================================================
   DATE ONLY
   ========================================================= */

const dateOnly = (value) => {
    if (!value) {
        return "";
    }

    const text = String(value).trim();

    /*
     * Handle ISO date directly.
     * Example:
     * 2026-09-05
     * 2026-09-05T10:30:00
     */
    const isoMatch = text.match(
        /^(\d{4}-\d{2}-\d{2})/
    );

    if (isoMatch) {
        return isoMatch[1];
    }

    /*
     * Handle DD-MM-YYYY
     */
    const dmyMatch = text.match(
        /^(\d{2})-(\d{2})-(\d{4})$/
    );

    if (dmyMatch) {
        return `${dmyMatch[3]}-${dmyMatch[2]}-${dmyMatch[1]}`;
    }

    /*
     * Handle DD/MM/YYYY
     */
    const slashMatch = text.match(
        /^(\d{2})\/(\d{2})\/(\d{4})$/
    );

    if (slashMatch) {
        return `${slashMatch[3]}-${slashMatch[2]}-${slashMatch[1]}`;
    }

    const parsed = new Date(value);

    if (Number.isNaN(parsed.getTime())) {
        return "";
    }

    const year = parsed.getFullYear();

    const month = String(
        parsed.getMonth() + 1
    ).padStart(2, "0");

    const day = String(
        parsed.getDate()
    ).padStart(2, "0");

    return `${year}-${month}-${day}`;
};

/* =========================================================
   FORMAT DATE
   ========================================================= */

const formatDate = (value) => {
    const normalized = dateOnly(value);

    if (!normalized) {
        return "-";
    }

    const [year, month, day] =
        normalized.split("-");

    return `${day}-${month}-${year}`;
};

/* =========================================================
   CUSTOMER
   ========================================================= */

const getCustomerName = (service) => {
    return (
        service?.customer_name ||
        service?.customer?.customer_name ||
        service?.customer?.name ||
        service?.customer?.full_name ||
        service?.customerName ||
        "-"
    );
};

/* =========================================================
   CUSTOMER PHONE
   ========================================================= */

const getCustomerPhone = (service) => {
    return (
        service?.phone ||
        service?.mobile ||
        service?.customer_phone ||
        service?.customer?.phone ||
        service?.customer?.mobile ||
        service?.customer?.mobile_number ||
        "-"
    );
};

/* =========================================================
   PRODUCT / MACHINE
   ========================================================= */

const getProductName = (service) => {
    return (
        service?.product_name ||
        service?.product?.name ||
        service?.product?.product_name ||
        service?.machine_name ||
        service?.machine?.name ||
        service?.machine?.machine_name ||
        service?.machine?.model_name ||
        service?.productName ||
        "-"
    );
};

/* =========================================================
   TICKET NUMBER
   ========================================================= */

const getTicketNumber = (service) => {
    return (
        service?.ticket_number ||
        service?.ticket_no ||
        service?.ticket ||
        service?.service_ticket_number ||
        service?.service_ticket_no ||
        service?.ticketNumber ||
        service?.reference_number ||
        `#${service?.id ?? "-"}`
    );
};

/* =========================================================
   ISSUE
   ========================================================= */

const getIssue = (service) => {
    return (
        service?.issue ||
        service?.problem_description ||
        service?.complaint ||
        service?.complaint_description ||
        service?.description ||
        service?.problem ||
        "-"
    );
};

/* =========================================================
   MATERIAL
   ========================================================= */

const getMaterial = (service) => {
    const value =
        service?.material_used ??
        service?.materials_used ??
        service?.materialUsed ??
        service?.materialsUsed ??
        service?.material ??
        "";

    if (
        value === null ||
        value === undefined ||
        String(value).trim() === ""
    ) {
        return "-";
    }

    return value;
};

/* =========================================================
   SERVICE COST
   ========================================================= */

const getCost = (service) => {
    const value =
        service?.service_cost ??
        service?.serviceCost ??
        service?.total_amount ??
        service?.totalAmount ??
        service?.cost ??
        service?.amount ??
        0;

    /*
     * Remove currency symbols and commas.
     * Example:
     * ₹3,500 -> 3500
     */
    const cleaned = String(value)
        .replace(/[₹,\s]/g, "");

    const numeric = Number(cleaned);

    return Number.isFinite(numeric)
        ? numeric
        : 0;
};

/* =========================================================
   PAYMENT STATUS
   ========================================================= */

const getPaymentStatus = (service) => {
    const value =
        service?.payment_status ??
        service?.paymentStatus ??
        service?.payment ??
        service?.payment_state ??
        "Pending";

    const text = String(value).trim();

    if (!text) {
        return "Pending";
    }

    return text
        .toLowerCase()
        .replace(
            /^./,
            (char) => char.toUpperCase()
        );
};

/* =========================================================
   SERVICE STATUS
   ========================================================= */

const getStatus = (service) => {
    return normalize(
        service?.status ||
        service?.service_status ||
        service?.serviceStatus ||
        ""
    );
};

/* =========================================================
   COMPLETED STATUS
   ========================================================= */

const isCompleted = (service) => {
    const status = getStatus(service);

    /*
     * Accept all common completed values.
     */
    return (
        status === "completed" ||
        status === "closed" ||
        status === "complete" ||
        status === "service completed" ||
        status === "service_completed"
    );
};

/* =========================================================
   CURRENCY
   ========================================================= */

const formatCurrency = (value) => {
    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 2,
        }
    ).format(Number(value) || 0);
};

/* =========================================================
   COMPONENT
   ========================================================= */

const ServiceEngineerDetails = ({
    services = [],
    selectedEngineer = "",
    dateFrom = "",
    dateTo = "",
    search = "",
}) => {
    /* =====================================================
       FILTER SERVICES
       ===================================================== */

    const filteredServices = useMemo(() => {
        const searchValue =
            normalize(search);

        const selectedEngineerValue =
            normalize(selectedEngineer);

        return (services || []).filter(
            (service) => {
                /* =========================================
                   ENGINEER FILTER
                   ========================================= */

                if (
                    selectedEngineerValue &&
                    selectedEngineerValue !== "all" &&
                    selectedEngineerValue !==
                        "all engineers"
                ) {
                    const engineerName =
                        normalize(
                            getEngineerName(
                                service
                            )
                        );

                    const engineerId =
                        String(
                            getEngineerId(
                                service
                            ) ?? ""
                        ).trim();

                    /*
                     * Match by engineer name.
                     */
                    const nameMatches =
                        engineerName ===
                        selectedEngineerValue;

                    /*
                     * Also support selecting an ID
                     * from the dropdown.
                     */
                    const idMatches =
                        engineerId !== "" &&
                        engineerId ===
                            String(
                                selectedEngineer
                            ).trim();

                    /*
                     * Support values such as:
                     * name:Arjun Kumar
                     * id:5
                     */
                    const selectedWithoutPrefix =
                        selectedEngineerValue
                            .replace(
                                /^name:/,
                                ""
                            )
                            .replace(
                                /^id:/,
                                ""
                            )
                            .trim();

                    const prefixNameMatches =
                        engineerName ===
                        normalize(
                            selectedWithoutPrefix
                        );

                    const prefixIdMatches =
                        engineerId ===
                        selectedWithoutPrefix;

                    if (
                        !nameMatches &&
                        !idMatches &&
                        !prefixNameMatches &&
                        !prefixIdMatches
                    ) {
                        return false;
                    }
                }

                /* =========================================
                   DATE FILTER
                   ========================================= */

                const serviceDate =
                    dateOnly(
                        getServiceDate(
                            service
                        )
                    );

                if (
                    dateFrom &&
                    serviceDate &&
                    serviceDate < dateFrom
                ) {
                    return false;
                }

                if (
                    dateTo &&
                    serviceDate &&
                    serviceDate > dateTo
                ) {
                    return false;
                }

                /*
                 * If a date filter is selected but
                 * service has no valid date, don't show it.
                 */
                if (
                    (dateFrom || dateTo) &&
                    !serviceDate
                ) {
                    return false;
                }

                /* =========================================
                   SEARCH FILTER
                   ========================================= */

                if (searchValue) {
                    const haystack = [
                        getTicketNumber(
                            service
                        ),
                        getCustomerName(
                            service
                        ),
                        getCustomerPhone(
                            service
                        ),
                        getProductName(
                            service
                        ),
                        getIssue(service),
                        getEngineerName(
                            service
                        ),
                        getMaterial(
                            service
                        ),
                        getPaymentStatus(
                            service
                        ),
                        getCost(service),
                    ]
                        .join(" ")
                        .toLowerCase();

                    if (
                        !haystack.includes(
                            searchValue
                        )
                    ) {
                        return false;
                    }
                }

                return true;
            }
        );
    }, [
        services,
        selectedEngineer,
        dateFrom,
        dateTo,
        search,
    ]);

    /* =====================================================
       COMPLETED SERVICES ONLY
       ===================================================== */

    const completedServices = useMemo(
        () => {
            return filteredServices.filter(
                (service) =>
                    isCompleted(service)
            );
        },
        [filteredServices]
    );

    /* =====================================================
       TOTAL COST
       ===================================================== */

    const totalCost = useMemo(
        () => {
            return completedServices.reduce(
                (total, service) => {
                    return (
                        total +
                        getCost(service)
                    );
                },
                0
            );
        },
        [completedServices]
    );

    /* =====================================================
       PAYMENT TOTALS
       ===================================================== */

    const receivedAmount = useMemo(
        () => {
            return completedServices.reduce(
                (total, service) => {
                    const payment =
                        normalize(
                            getPaymentStatus(
                                service
                            )
                        );

                    if (
                        payment ===
                            "received" ||
                        payment ===
                            "paid" ||
                        payment ===
                            "completed"
                    ) {
                        return (
                            total +
                            getCost(service)
                        );
                    }

                    return total;
                },
                0
            );
        },
        [completedServices]
    );

    const pendingAmount = useMemo(
        () => {
            return Math.max(
                totalCost -
                    receivedAmount,
                0
            );
        },
        [
            totalCost,
            receivedAmount,
        ]
    );

    /* =====================================================
       PAYMENT COUNTS
       ===================================================== */

    const receivedCount = useMemo(
        () => {
            return completedServices.filter(
                (service) => {
                    const payment =
                        normalize(
                            getPaymentStatus(
                                service
                            )
                        );

                    return (
                        payment ===
                            "received" ||
                        payment ===
                            "paid" ||
                        payment ===
                            "completed"
                    );
                }
            ).length;
        },
        [completedServices]
    );

    const pendingCount = useMemo(
        () => {
            return completedServices.filter(
                (service) => {
                    const payment =
                        normalize(
                            getPaymentStatus(
                                service
                            )
                        );

                    return (
                        payment ===
                            "pending" ||
                        payment ===
                            "unpaid"
                    );
                }
            ).length;
        },
        [completedServices]
    );

    /* =====================================================
       MATERIAL COUNT
       ===================================================== */

    const materialsUsed = useMemo(
        () => {
            return completedServices.filter(
                (service) => {
                    const material =
                        normalize(
                            getMaterial(
                                service
                            )
                        );

                    return (
                        material &&
                        material !== "-" &&
                        material !== "no" &&
                        material !== "none" &&
                        material !== "n/a"
                    );
                }
            ).length;
        },
        [completedServices]
    );

    /* =====================================================
       SERVICE DAYS
       ===================================================== */

    const serviceDays = useMemo(
        () => {
            const dates =
                completedServices
                    .map((service) =>
                        dateOnly(
                            getServiceDate(
                                service
                            )
                        )
                    )
                    .filter(Boolean);

            return new Set(dates).size;
        },
        [completedServices]
    );

    /* =====================================================
       ENGINEER NAME
       ===================================================== */

    const engineerName =
        selectedEngineer &&
        normalize(selectedEngineer) !==
            "all" &&
        normalize(selectedEngineer) !==
            "all engineers"
            ? selectedEngineer
            : getEngineerName(
                  filteredServices[0]
              ) ||
              "All Engineers";

    /* =====================================================
       DATE PERIOD TEXT
       ===================================================== */

    const periodText =
        dateFrom || dateTo
            ? `${formatDate(
                  dateFrom
              )} - ${formatDate(
                  dateTo
              )}`
            : "All available dates";

    /* =====================================================
       RENDER
       ===================================================== */

    return (
        <section className="service-engineer-details">

            {/* =================================================
               HEADER
            ================================================= */}

            <div className="service-engineer-details-header">

                <div>

                    <div className="service-engineer-details-eyebrow">
                        ENGINEER DETAILS
                    </div>

                    <h3>
                        {engineerName}
                    </h3>

                    <p>
                        Completed service
                        performance,
                        service details,
                        cost and payment
                        information.
                    </p>

                </div>

                <div className="service-engineer-details-period">

                    <CalendarDays
                        size={16}
                    />

                    <span>
                        {periodText}
                    </span>

                </div>

            </div>

            {/* =================================================
               SUMMARY
            ================================================= */}

            <div className="service-engineer-summary-grid">

                {/* TOTAL SERVICES */}

                <div className="service-engineer-summary-card">

                    <div className="service-engineer-summary-icon">

                        <Wrench
                            size={18}
                        />

                    </div>

                    <div>

                        <span>
                            Total Services
                        </span>

                        <strong>
                            {
                                filteredServices.length
                            }
                        </strong>

                    </div>

                </div>

                {/* COMPLETED */}

                <div className="service-engineer-summary-card">

                    <div className="service-engineer-summary-icon completed">

                        <CheckCircle2
                            size={18}
                        />

                    </div>

                    <div>

                        <span>
                            Completed
                        </span>

                        <strong>
                            {
                                completedServices.length
                            }
                        </strong>

                    </div>

                </div>

                {/* TOTAL COST */}

                <div className="service-engineer-summary-card">

                    <div className="service-engineer-summary-icon cost">

                        <IndianRupee
                            size={18}
                        />

                    </div>

                    <div>

                        <span>
                            Completed Service Cost
                        </span>

                        <strong>
                            {formatCurrency(
                                totalCost
                            )}
                        </strong>

                    </div>

                </div>

                {/* SERVICE DAYS */}

                <div className="service-engineer-summary-card">

                    <div className="service-engineer-summary-icon days">

                        <Clock3
                            size={18}
                        />

                    </div>

                    <div>

                        <span>
                            Service Days
                        </span>

                        <strong>
                            {serviceDays}
                        </strong>

                    </div>

                </div>

                {/* MATERIAL */}

                <div className="service-engineer-summary-card">

                    <div className="service-engineer-summary-icon material">

                        <Package
                            size={18}
                        />

                    </div>

                    <div>

                        <span>
                            Services With Material
                        </span>

                        <strong>
                            {materialsUsed}
                        </strong>

                    </div>

                </div>

            </div>

            {/* =================================================
               PAYMENT SUMMARY
            ================================================= */}

            <div className="service-engineer-payment-summary">

                <div className="service-engineer-payment-box">

                    <span>
                        Received
                    </span>

                    <strong>
                        {formatCurrency(
                            receivedAmount
                        )}
                    </strong>

                    <small>
                        {
                            receivedCount
                        } services
                    </small>

                </div>

                <div className="service-engineer-payment-box">

                    <span>
                        Pending
                    </span>

                    <strong>
                        {formatCurrency(
                            pendingAmount
                        )}
                    </strong>

                    <small>
                        {
                            pendingCount
                        } services
                    </small>

                </div>

                <div className="service-engineer-payment-box total">

                    <span>
                        Total Service Value
                    </span>

                    <strong>
                        {formatCurrency(
                            totalCost
                        )}
                    </strong>

                    <small>
                        {
                            completedServices.length
                        } completed services
                    </small>

                </div>

            </div>

            {/* =================================================
               COMPLETED SERVICES
            ================================================= */}

            <div className="service-engineer-completed-section">

                <div className="service-engineer-section-title">

                    <div>

                        <h3>
                            Completed Services
                        </h3>

                        <p>
                            {
                                completedServices.length
                            } completed service
                            {completedServices.length ===
                            1
                                ? ""
                                : "s"} for the
                            selected engineer.
                        </p>

                    </div>

                    <span className="service-engineer-count">
                        {
                            completedServices.length
                        }
                    </span>

                </div>

                {/* =================================================
                   NO DATA
                ================================================= */}

                {completedServices.length ===
                0 ? (
                    <div className="service-engineer-empty">

                        <CheckCircle2
                            size={32}
                        />

                        <strong>
                            No completed
                            services found
                        </strong>

                        <span>
                            Select an engineer
                            with completed
                            services or change
                            the date range.
                        </span>

                    </div>
                ) : (

                    /* =================================================
                       TABLE
                    ================================================= */

                    <div className="service-engineer-completed-table-wrap">

                        <table className="service-engineer-completed-table">

                            <thead>

                                <tr>

                                    <th>
                                        #
                                    </th>

                                    <th>
                                        Ticket
                                    </th>

                                    <th>
                                        Engineer
                                    </th>

                                    <th>
                                        Customer
                                    </th>

                                    <th>
                                        Product / Machine
                                    </th>

                                    <th>
                                        Issue
                                    </th>

                                    <th>
                                        Completed Date
                                    </th>

                                    <th>
                                        Material Used
                                    </th>

                                    <th>
                                        Service Cost
                                    </th>

                                    <th>
                                        Payment
                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                {completedServices.map(
                                    (
                                        service,
                                        index
                                    ) => {

                                        const paymentStatus =
                                            getPaymentStatus(
                                                service
                                            );

                                        const paymentClass =
                                            normalize(
                                                paymentStatus
                                            );

                                        return (
                                            <tr
                                                key={
                                                    service?.id ??
                                                    `${getTicketNumber(
                                                        service
                                                    )}-${index}`
                                                }
                                            >

                                                {/* # */}

                                                <td>
                                                    {index +
                                                        1}
                                                </td>

                                                {/* TICKET */}

                                                <td>

                                                    <strong className="service-engineer-ticket">

                                                        {
                                                            getTicketNumber(
                                                                service
                                                            )
                                                        }

                                                    </strong>

                                                </td>

                                                {/* ENGINEER */}

                                                <td>

                                                    <div className="service-engineer-name-cell">

                                                        <UserRound
                                                            size={
                                                                15
                                                            }
                                                        />

                                                        <span>
                                                            {
                                                                getEngineerName(
                                                                    service
                                                                ) ||
                                                                "-"
                                                            }
                                                        </span>

                                                    </div>

                                                </td>

                                                {/* CUSTOMER */}

                                                <td>

                                                    <div className="service-engineer-customer-cell">

                                                        <strong>
                                                            {
                                                                getCustomerName(
                                                                    service
                                                                )
                                                            }
                                                        </strong>

                                                        {getCustomerPhone(
                                                            service
                                                        ) !==
                                                            "-" && (
                                                            <small>
                                                                {
                                                                    getCustomerPhone(
                                                                        service
                                                                    )
                                                                }
                                                            </small>
                                                        )}

                                                    </div>

                                                </td>

                                                {/* MACHINE */}

                                                <td>

                                                    {
                                                        getProductName(
                                                            service
                                                        )
                                                    }

                                                </td>

                                                {/* ISSUE */}

                                                <td>

                                                    <span className="service-engineer-issue">

                                                        {
                                                            getIssue(
                                                                service
                                                            )
                                                        }

                                                    </span>

                                                </td>

                                                {/* DATE */}

                                                <td>

                                                    <strong>
                                                        {formatDate(
                                                            getServiceDate(
                                                                service
                                                            )
                                                        )}
                                                    </strong>

                                                </td>

                                                {/* MATERIAL */}

                                                <td>

                                                    {
                                                        getMaterial(
                                                            service
                                                        )
                                                    }

                                                </td>

                                                {/* COST */}

                                                <td>

                                                    <strong className="service-engineer-cost">

                                                        {formatCurrency(
                                                            getCost(
                                                                service
                                                            )
                                                        )}

                                                    </strong>

                                                </td>

                                                {/* PAYMENT */}

                                                <td>

                                                    <span
                                                        className={`service-engineer-payment ${
                                                            paymentClass ===
                                                                "received" ||
                                                            paymentClass ===
                                                                "paid" ||
                                                            paymentClass ===
                                                                "completed"
                                                                ? "received"
                                                                : paymentClass ===
                                                                    "pending" ||
                                                                  paymentClass ===
                                                                    "unpaid"
                                                                    ? "pending"
                                                                    : ""
                                                        }`}
                                                    >

                                                        {
                                                            paymentStatus
                                                        }

                                                    </span>

                                                </td>

                                            </tr>
                                        );
                                    }
                                )}

                            </tbody>

                            {/* =================================================
                               TABLE TOTAL
                            ================================================= */}

                            <tfoot>

                                <tr>

                                    <td
                                        colSpan={
                                            8
                                        }
                                        className="service-engineer-total-label"
                                    >
                                        Total Completed
                                        Service Cost
                                    </td>

                                    <td className="service-engineer-total-cost">

                                        {formatCurrency(
                                            totalCost
                                        )}

                                    </td>

                                    <td>
                                        {
                                            completedServices.length
                                        } Services
                                    </td>

                                </tr>

                            </tfoot>

                        </table>

                    </div>
                )}

            </div>

        </section>
    );
};

export default ServiceEngineerDetails;