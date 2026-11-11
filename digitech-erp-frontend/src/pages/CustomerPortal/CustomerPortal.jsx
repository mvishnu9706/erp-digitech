import React, {
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
} from "react";

import {
    AlertCircle,
    Bell,
    CheckCircle2,
    ChevronRight,
    FileText,
    ExternalLink,
    Gauge,
    ReceiptText,
    History,
    IndianRupee,
    Loader2,
    LogOut,
    MonitorCog,
    Plus,
    RefreshCw,
    Send,
    Settings2,
    Ticket,
    UserRound,
    Wrench,
    X,
} from "lucide-react";

import { useAuth } from "../../context/AuthContext";
import api from "../../api/axios";
import useNotifications from "../../hooks/useNotifications";

import "./CustomerPortal.css";

// =====================================================
// HELPERS
// =====================================================

const getApiMessage = (
    error,
    fallback = "Something went wrong."
) => {

    const detail =
        error?.response?.data?.detail;

    if (Array.isArray(detail)) {

        return detail
            .map(
                (item) =>
                    typeof item === "string"
                        ? item
                        : item?.msg ||
                          item?.message ||
                          "Invalid value"
            )
            .join(", ");
    }

    if (typeof detail === "string") {
        return detail;
    }

    if (
        typeof error?.response?.data?.message ===
        "string"
    ) {
        return error.response.data.message;
    }

    if (
        typeof error?.message ===
        "string"
    ) {
        return error.message;
    }

    return fallback;
};


const formatDate = (value) => {

    if (!value) {
        return "—";
    }

    const date =
        new Date(value);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return "—";
    }

    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric",
        }
    );
};


const formatCurrency = (value) => {

    if (value === null || value === undefined || value === "") {
        return "—";
    }

    const numericValue = Number(value);

    if (Number.isNaN(numericValue)) {
        return value;
    }

    return `₹ ${numericValue.toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    })}`;
};


const getEngineerName = (request) => {

    return (
        request?.engineer_name ||
        request?.engineer?.full_name ||
        request?.engineer?.name ||
        request?.assigned_engineer?.full_name ||
        request?.assigned_engineer?.name ||
        request?.engineer_details?.full_name ||
        request?.engineer_details?.name ||
        request?.technician ||
        "Not Assigned"
    );
};


const getRequestDate = (request) => {

    return (
        request?.reported_date ||
        request?.reportedDate ||
        request?.request_date ||
        request?.requestDate ||
        request?.created_date ||
        request?.createdDate ||
        request?.created_at ||
        request?.createdAt ||
        request?.date ||
        null
    );
};


const getMachineLabel = (machine) => {

    if (!machine) {
        return "Select machine";
    }

    const machineName =
        machine.machine_name ||
        machine.machineName ||
        machine.name ||
        `Machine #${machine.id}`;

    const serialNumber =
        machine.serial_number ||
        machine.serialNumber;

    return serialNumber
        ? `${machineName} • ${serialNumber}`
        : machineName;
};


const normalizeStatus = (
    status
) => {

    return (
        status ||
        "OPEN"
    )
        .toString()
        .trim()
        .toUpperCase()
        .replace(/\s+/g, "_");
};


const statusLabel = (
    status
) => {

    return normalizeStatus(
        status
    )
        .replaceAll("_", " ")
        .replace(
            /\b\w/g,
            (letter) =>
                letter.toUpperCase()
        );
};


const statusClass = (
    status
) => {

    const normalized =
        normalizeStatus(status);

    if (
        normalized.includes(
            "COMPLETED"
        ) ||
        normalized.includes(
            "CLOSED"
        ) ||
        normalized.includes(
            "RESOLVED"
        )
    ) {

        return "status-success";
    }

    if (
        normalized.includes(
            "IN_PROGRESS"
        ) ||
        normalized.includes(
            "ASSIGNED"
        ) ||
        normalized.includes(
            "VISIT"
        )
    ) {

        return "status-progress";
    }

    if (
        normalized.includes(
            "CANCEL"
        ) ||
        normalized.includes(
            "REJECT"
        )
    ) {

        return "status-danger";
    }

    return "status-open";
};


const formatNotificationTime = (value) => {
    if (!value) return "";

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";

    const diffMs = Date.now() - date.getTime();
    const diffMinutes = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMinutes < 1) return "Just now";
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
};

// =====================================================
// CUSTOMER PORTAL
// =====================================================

const CustomerPortal = () => {

    const {
        user,
        isAuthenticated,
        loading: authLoading,
        logout,
    } = useAuth();

    // =================================================
    // CUSTOMER PORTAL ACCESS
    // =================================================
    // Service and Rental access are independent.
    // The values come from the logged-in CUSTOMER user.
    //
    // Supported backend values:
    //   true / false
    //   1 / 0
    //   "true" / "false"
    // =================================================

    const hasAccess = (value) => {
        if (value === true || value === 1) {
            return true;
        }

        if (typeof value === "string") {
            return value.trim().toLowerCase() === "true" || value.trim() === "1";
        }

        return false;
    };

    const serviceAccess = hasAccess(user?.service_access);
    const rentalAccess = hasAccess(user?.rental_access);

    // =================================================
    // NOTIFICATIONS
    // =================================================

    const {
        notifications,
        unreadCount,
        loading: notificationsLoading,
        refreshNotifications,
        markAsRead,
        markAllAsRead,
    } = useNotifications();

    const [
        notificationsOpen,
        setNotificationsOpen,
    ] = useState(false);

    // =================================================
    // NOTIFICATION OUTSIDE-CLICK REF
    // =================================================

    const notificationRef = useRef(null);


    // =================================================
    // CLOSE NOTIFICATIONS ON OUTSIDE CLICK
    // =================================================

    useEffect(() => {
        const handleOutsideClick = (event) => {
            if (
                notificationRef.current &&
                !notificationRef.current.contains(event.target)
            ) {
                setNotificationsOpen(false);
            }
        };

        document.addEventListener(
            "mousedown",
            handleOutsideClick
        );

        return () => {
            document.removeEventListener(
                "mousedown",
                handleOutsideClick
            );
        };
    }, []);


    // =================================================
    // DATA
    // =================================================

    const [customer, setCustomer] =
        useState(null);

    const [machines, setMachines] =
        useState([]);

    const [serviceRequests, setServiceRequests] =
        useState([]);


    // =================================================
    // UI STATE
    // =================================================

    const [pageLoading, setPageLoading] =
        useState(true);

    const [refreshing, setRefreshing] =
        useState(false);

    const [error, setError] =
        useState("");

    const [activeTab, setActiveTab] =
        useState(() => {
            if (hasAccess(user?.service_access)) return "machines";
            if (hasAccess(user?.rental_access)) return "rental";
            return "none";
        });

    const [requestModalOpen, setRequestModalOpen] =
        useState(false);

    const [selectedRequest, setSelectedRequest] =
        useState(null);

    const [requestMachineId, setRequestMachineId] =
        useState("");

    const [requestComplaint, setRequestComplaint] =
        useState("");

    // Current meter reading entered by the customer when raising a service request.
    const [requestCurrentReading, setRequestCurrentReading] =
        useState("");

    const [requestPriority, setRequestPriority] =
        useState("MEDIUM");

    const [submittingRequest, setSubmittingRequest] =
        useState(false);

    const [requestError, setRequestError] =
        useState("");

    const [requestSuccess, setRequestSuccess] =
        useState("");

    const [requestDetailsOpen, setRequestDetailsOpen] =
        useState(false);

    // =================================================
    // RENTAL BILLING STATE
    // =================================================

    const [rentalMachines, setRentalMachines] =
        useState([]);

    const [rentalBills, setRentalBills] =
        useState([]);

    // Global rental billing month controlled by the admin billing cycle.
    // This is shared by admin and customer portals.
    const [activeRentalBillingMonth, setActiveRentalBillingMonth] =
        useState("");

    // Customer-entered monthly readings are kept per machine.
    // The customer never edits the price; it always comes from the backend.
    const [rentalMeterValues, setRentalMeterValues] =
        useState({});

    const [rentalReadingErrors, setRentalReadingErrors] =
        useState({});

    const [rentalSubmittingMachineId, setRentalSubmittingMachineId] =
        useState(null);

    // Selected rental machine shown in the billing table.
    // The customer can have multiple rental machines but sees
    // one machine's complete billing data at a time.
    const [selectedRentalMachineId, setSelectedRentalMachineId] =
        useState("");


    // =================================================
    // LOAD PORTAL DATA
    // =================================================

    const loadPortalData = useCallback(
        async (
            showPageLoader = true
        ) => {

            try {

                if (showPageLoader) {
                    setPageLoading(true);
                } else {
                    setRefreshing(true);
                }

                setError("");

                // -------------------------------------------------
                // SERVICE DATA
                // -------------------------------------------------
                // Service APIs are called only when Service access
                // is enabled. Rental-only customers never call them.
                // -------------------------------------------------

                let customerResponse = null;
                let machineItems = [];
                let requestItems = [];

                if (serviceAccess) {
                    customerResponse = await api.get("/customer/me");

                    const [machinesResponse, requestsResponse] =
                        await Promise.all([
                            api.get(
                                "/customer/machines",
                                {
                                    params: {
                                        page: 1,
                                        page_size: 100,
                                    },
                                }
                            ),
                            api.get("/customer/service-requests"),
                        ]);

                    machineItems =
                        Array.isArray(machinesResponse?.data?.items)
                            ? machinesResponse.data.items
                            : Array.isArray(machinesResponse?.data)
                                ? machinesResponse.data
                                : [];

                    const requestPayload = requestsResponse?.data;

                    requestItems =
                        Array.isArray(requestPayload)
                            ? requestPayload
                            : Array.isArray(requestPayload?.service_requests)
                                ? requestPayload.service_requests
                                : Array.isArray(requestPayload?.items)
                                    ? requestPayload.items
                                    : Array.isArray(requestPayload?.data)
                                        ? requestPayload.data
                                        : Array.isArray(requestPayload?.data?.service_requests)
                                            ? requestPayload.data.service_requests
                                            : [];
                }

                // -------------------------------------------------
                // RENTAL DATA
                // -------------------------------------------------
                // Rental access is independent from Service access.
                // The backend identifies the customer from the
                // authenticated customer account.
                // -------------------------------------------------

                let rentalMachineItems = [];
                let rentalBillItems = [];

                if (rentalAccess) {
                    const [
                        rentalMachinesResponse,
                        rentalBillsResponse,
                        rentalCycleResponse,
                    ] = await Promise.all([
                        api.get("/rental-bills/my-machines"),
                        api.get("/rental-bills/my"),
                        api.get("/rental-billing-cycle/"),
                    ]);

                    const rentalMachinePayload =
                        rentalMachinesResponse?.data;

                    rentalMachineItems =
                        Array.isArray(rentalMachinePayload)
                            ? rentalMachinePayload
                            : Array.isArray(rentalMachinePayload?.items)
                                ? rentalMachinePayload.items
                                : Array.isArray(rentalMachinePayload?.machines)
                                    ? rentalMachinePayload.machines
                                    : Array.isArray(rentalMachinePayload?.data)
                                        ? rentalMachinePayload.data
                                        : [];

                    const rentalCyclePayload =
                        rentalCycleResponse?.data;

                    if (rentalCyclePayload?.active_billing_month) {
                        setActiveRentalBillingMonth(
                            String(rentalCyclePayload.active_billing_month)
                        );
                    }

                    const rentalBillPayload =
                        rentalBillsResponse?.data;

                    rentalBillItems =
                        Array.isArray(rentalBillPayload)
                            ? rentalBillPayload
                            : Array.isArray(rentalBillPayload?.items)
                                ? rentalBillPayload.items
                                : Array.isArray(rentalBillPayload?.bills)
                                    ? rentalBillPayload.bills
                                    : Array.isArray(rentalBillPayload?.data)
                                        ? rentalBillPayload.data
                                        : [];
                }

                const customerData =
                    customerResponse?.data?.customer ||
                    null;

                setCustomer(customerData);
                setMachines(machineItems);
                setServiceRequests(requestItems);
                setRentalMachines(rentalMachineItems);
                setRentalBills(rentalBillItems);

            }

            catch (err) {

                console.error(
                    "Customer Portal Load Error:",
                    err
                );

                if (err?.response?.status === 401) {
                    setError(
                        "Your login session is not authenticated. Please login again."
                    );
                } else if (err?.response?.status === 403) {
                    // A disabled module is not an error when the other
                    // customer portal module is enabled.
                    if (
                        (!serviceAccess && rentalAccess) ||
                        (serviceAccess && !rentalAccess)
                    ) {
                        setError("");
                    } else if (!serviceAccess && !rentalAccess) {
                        setError("");
                    } else {
                        setError(
                            getApiMessage(
                                err,
                                "Customer portal access is disabled."
                            )
                        );
                    }
                } else {
                    setError(
                        getApiMessage(
                            err,
                            "Unable to load customer portal data."
                        )
                    );
                }

            }

            finally {
                setPageLoading(false);
                setRefreshing(false);
            }

        },
        [serviceAccess, rentalAccess]
    );


    // =================================================
    // KEEP ACTIVE TAB VALID WHEN ACCESS CHANGES
    // =================================================
    // Service only  -> My Machines
    // Rental only   -> Rental
    // Both          -> My Machines
    // Neither       -> No Portal Access
    // =================================================

    useEffect(() => {
        if (serviceAccess && rentalAccess) {
            if (
                activeTab !== "machines" &&
                activeTab !== "requests" &&
                activeTab !== "rental"
            ) {
                setActiveTab("machines");
            }
            return;
        }

        if (serviceAccess && !rentalAccess) {
            if (
                activeTab !== "machines" &&
                activeTab !== "requests"
            ) {
                setActiveTab("machines");
            }
            return;
        }

        if (!serviceAccess && rentalAccess) {
            if (activeTab !== "rental") {
                setActiveTab("rental");
            }
            return;
        }

        if (!serviceAccess && !rentalAccess) {
            if (activeTab !== "none") {
                setActiveTab("none");
            }
        }
    }, [serviceAccess, rentalAccess, activeTab]);


    // =================================================
    // INITIAL LOAD
    // =================================================

    useEffect(
        () => {

            if (
                !authLoading &&
                isAuthenticated
            ) {

                loadPortalData(
                    true
                );
            }

            if (
                !authLoading &&
                !isAuthenticated
            ) {

                setPageLoading(false);
            }

        },
        [
            authLoading,
            isAuthenticated,
            serviceAccess,
            loadPortalData,
        ]
    );


    // =================================================
    // SYNC ACTIVE RENTAL BILLING MONTH
    // =================================================
    // The admin controls the global rental billing cycle.
    // Poll the cycle endpoint so an already-open customer portal
    // automatically moves to the new month after the admin clicks
    // Start New Month. Existing monthly history is preserved.
    // =================================================

    useEffect(() => {
        if (!rentalAccess || !isAuthenticated) {
            return undefined;
        }

        let cancelled = false;

        const syncRentalBillingMonth = async () => {
            try {
                const response = await api.get(
                    "/rental-billing-cycle/"
                );

                const nextMonth =
                    response?.data?.active_billing_month
                        ? String(response.data.active_billing_month)
                        : "";

                if (cancelled || !nextMonth) {
                    return;
                }

                setActiveRentalBillingMonth((previousMonth) => {
                    if (previousMonth && previousMonth !== nextMonth) {
                        // New cycle started by admin. Clear any unsaved
                        // customer input so the new month's box is empty.
                        setRentalMeterValues({});
                        setRentalReadingErrors({});

                        // Refresh machines and all monthly history so the
                        // latest previous reading and existing bills are shown.
                        loadPortalData(false);
                    }

                    return nextMonth;
                });
            } catch (syncError) {
                // Do not interrupt the customer portal if the background
                // billing-cycle check temporarily fails.
                console.warn(
                    "Rental billing cycle sync failed:",
                    syncError
                );
            }
        };

        syncRentalBillingMonth();

        const intervalId = window.setInterval(
            syncRentalBillingMonth,
            10000
        );

        return () => {
            cancelled = true;
            window.clearInterval(intervalId);
        };
    }, [rentalAccess, isAuthenticated, loadPortalData]);


    // =================================================
    // KEEP SELECTED RENTAL MACHINE VALID
    // =================================================

    useEffect(() => {
        if (!rentalMachines.length) {
            setSelectedRentalMachineId("");
            return;
        }

        const selectedStillExists = rentalMachines.some(
            (machine) =>
                String(getRentalMachineId(machine)) ===
                String(selectedRentalMachineId)
        );

        if (!selectedRentalMachineId || !selectedStillExists) {
            setSelectedRentalMachineId(
                String(getRentalMachineId(rentalMachines[0]))
            );
        }
    }, [rentalMachines, selectedRentalMachineId]);

    // Only the selected machine is rendered in the rental billing table.
    const selectedRentalMachine = useMemo(() => {
        if (!rentalMachines.length) return null;

        return (
            rentalMachines.find(
                (machine) =>
                    String(getRentalMachineId(machine)) ===
                    String(selectedRentalMachineId)
            ) || rentalMachines[0]
        );
    }, [rentalMachines, selectedRentalMachineId]);


    // =================================================
    // DERIVED COUNTS
    // =================================================

    const activeMachineCount =
        useMemo(
            () =>
                machines.filter(
                    (machine) => {

                        const status =
                            (
                                machine?.status ||
                                ""
                            )
                                .toString()
                                .toUpperCase();

                        return ![
                            "INACTIVE",
                            "CLOSED",
                            "DECOMMISSIONED",
                        ].includes(
                            status
                        );
                    }
                ).length,
            [machines]
        );


    const openRequestCount =
        useMemo(
            () =>
                serviceRequests.filter(
                    (request) => {

                        const status =
                            normalizeStatus(
                                request?.status
                            );

                        return ![
                            "COMPLETED",
                            "CLOSED",
                            "RESOLVED",
                            "CANCELLED",
                        ].includes(
                            status
                        );
                    }
                ).length,
            [serviceRequests]
        );


    const completedRequestCount =
        useMemo(
            () =>
                serviceRequests.filter(
                    (request) => {

                        const status =
                            normalizeStatus(
                                request?.status
                            );

                        return (
                            status.includes("COMPLETED") ||
                            status.includes("CLOSED") ||
                            status.includes("RESOLVED")
                        );
                    }
                ).length,
            [serviceRequests]
        );


    // =================================================
    // RENTAL BILLING HELPERS
    // =================================================

    const getRentalMachineName = (machine) =>
        machine?.machine_name ||
        machine?.machineName ||
        machine?.name ||
        machine?.machine_number ||
        machine?.machineNumber ||
        "Rental Machine";

    const getRentalSerialNumber = (machine) =>
        machine?.serial_number ||
        machine?.serialNumber ||
        "—";

    // Function declaration is intentionally used here because this helper
    // is referenced by useEffect/useMemo blocks declared earlier in the
    // component. Function declarations are hoisted and avoid the
    // "Cannot access ... before initialization" runtime error.
    function getRentalMachineId(machine) {
        return (
            machine?.id ??
            machine?.machine_id ??
            machine?.machineId ??
            null
        );
    }

    const getRentalCurrentReading = (machine) =>
        machine?.current_meter ??
        machine?.currentMeter ??
        machine?.meter_reading ??
        machine?.meterReading ??
        machine?.current_reading ??
        machine?.currentReading ??
        0;

    // IMPORTANT: Rental Billing uses cost_per_copy.
    const getRentalRate = (machine) =>
        machine?.cost_per_copy ??
        machine?.costPerCopy ??
        machine?.rate_per_copy ??
        machine?.ratePerCopy ??
        0;

    const getCurrentBillingMonth = () => {
        if (activeRentalBillingMonth) {
            return activeRentalBillingMonth;
        }

        const now = new Date();
        const month = String(now.getMonth() + 1).padStart(2, "0");
        return `${now.getFullYear()}-${month}`;
    };

    // Billing date must always belong to the active rental billing month.
    // The admin controls activeRentalBillingMonth through /rental-billing-cycle/.
    // If the active cycle is a future month, use the first day of that month
    // instead of the computer's real/current date. This prevents the backend
    // 422 error: "Billing date must belong to billing month ...".
    const getBillingDate = () => {
        const billingMonth = getCurrentBillingMonth();
        const match = String(billingMonth || "").match(/^(\d{4})-(\d{2})$/);

        if (match) {
            const year = Number(match[1]);
            const month = Number(match[2]);

            if (
                Number.isInteger(year) &&
                Number.isInteger(month) &&
                month >= 1 &&
                month <= 12
            ) {
                // Day 01 is guaranteed to be inside the selected billing month.
                return `${year}-${String(month).padStart(2, "0")}-01`;
            }
        }

        // Safe fallback for an unavailable/invalid cycle value.
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, "0");
        const day = String(now.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
    };

    const getRentalBillMachineId = (bill) =>
        bill?.machine_id ??
        bill?.machineId ??
        null;

    const getRentalBillStatus = (bill) =>
        normalizeStatus(
            bill?.payment_status ||
            bill?.paymentStatus ||
            "PENDING"
        );

    const getCurrentMonthRentalBill = (machineId) => {
        if (!machineId) return null;

        const billingMonth = getCurrentBillingMonth();

        return (
            rentalBills.find(
                (bill) =>
                    Number(getRentalBillMachineId(bill)) ===
                        Number(machineId) &&
                    String(bill?.billing_month || bill?.billingMonth || "") ===
                        billingMonth
            ) || null
        );
    };

    const getRentalBillingMonthLabel = (value) => {
        if (!value) return "—";

        const match = String(value).match(/^(\d{4})-(\d{2})$/);
        if (!match) return String(value);

        const year = Number(match[1]);
        const month = Number(match[2]);

        if (!year || month < 1 || month > 12) {
            return String(value);
        }

        return new Date(year, month - 1, 1).toLocaleDateString(
            "en-IN",
            {
                month: "short",
                year: "numeric",
            }
        );
    };

    const getRentalBillCurrentReading = (bill) =>
        Number(
            bill?.current_meter ??
            bill?.currentMeter ??
            0
        );

    const getRentalBillPreviousReading = (bill) =>
        Number(
            bill?.previous_meter ??
            bill?.previousMeter ??
            0
        );

    const getRentalBillRate = (bill) =>
        Number(
            bill?.cost_per_copy ??
            bill?.costPerCopy ??
            0
        );

    const getRentalBillCopies = (bill) =>
        Number(
            bill?.copies_used ??
            bill?.copiesUsed ??
            0
        );

    const getRentalBillAmount = (bill) =>
        Number(
            bill?.total_amount ??
            bill?.totalAmount ??
            0
        );

    const getRentalMachineHistory = (machineId) => {
        if (!machineId) return [];

        return rentalBills
            .filter(
                (bill) =>
                    Number(getRentalBillMachineId(bill)) ===
                    Number(machineId)
            )
            .sort((a, b) =>
                String(
                    b?.billing_month ||
                    b?.billingMonth ||
                    ""
                ).localeCompare(
                    String(
                        a?.billing_month ||
                        a?.billingMonth ||
                        ""
                    )
                )
            );
    };

    const activeRentalCount = useMemo(
        () =>
            rentalMachines.filter((machine) => {
                const status = normalizeStatus(
                    machine?.status ||
                    machine?.rental_status ||
                    machine?.rentalStatus ||
                    "ACTIVE"
                );

                return ![
                    "INACTIVE",
                    "CANCELLED",
                    "CLOSED",
                    "TERMINATED",
                    "EXPIRED",
                ].includes(status);
            }).length,
        [rentalMachines]
    );

    const pendingRentalReadingCount = useMemo(
        () =>
            rentalMachines.filter((machine) => {
                const bill = getCurrentMonthRentalBill(
                    getRentalMachineId(machine)
                );

                return !bill;
            }).length,
        [rentalMachines, rentalBills]
    );

    const rentalOutstandingAmount = useMemo(
        () =>
            rentalBills.reduce(
                (total, bill) => {
                    const status = getRentalBillStatus(bill);

                    if (
                        [
                            "RECEIVED",
                            "PAID",
                            "CANCELLED",
                            "CLOSED",
                        ].includes(status)
                    ) {
                        return total;
                    }

                    return (
                        total +
                        Number(
                            bill?.outstanding_amount ??
                            bill?.outstandingAmount ??
                            bill?.balance ??
                            0
                        )
                    );
                },
                0
            ),
        [rentalBills]
    );

    const getRentalEnteredReading = (machineId) =>
        rentalMeterValues[String(machineId)] ?? "";

    const getRentalCopiesUsed = (machine) => {
        const machineId = getRentalMachineId(machine);
        const enteredValue = getRentalEnteredReading(machineId);

        if (!machineId || enteredValue === "") return null;

        const previousReading = Number(getRentalCurrentReading(machine));
        const newReading = Number(enteredValue);

        if (!Number.isFinite(previousReading) || !Number.isFinite(newReading)) {
            return null;
        }

        return Math.max(0, newReading - previousReading);
    };

    const getRentalEstimatedAmount = (machine) => {
        const copies = getRentalCopiesUsed(machine);
        const rate = Number(getRentalRate(machine));

        if (copies === null || !Number.isFinite(rate)) return null;

        return copies * rate;
    };

    const handleRentalMeterChange = (machine, event) => {
        const machineId = getRentalMachineId(machine);
        const value = event.target.value;

        if (!machineId) return;

        if (value !== "" && !/^\d+$/.test(value)) return;

        const previousReading = Number(getRentalCurrentReading(machine));
        const newReading = Number(value);
        const key = String(machineId);

        setRentalMeterValues((previous) => ({
            ...previous,
            [key]: value,
        }));

        setRentalReadingErrors((previous) => ({
            ...previous,
            [key]:
                value !== "" && Number.isFinite(previousReading) && newReading < previousReading
                    ? `New reading cannot be less than the last reading (${previousReading.toLocaleString("en-IN")}).`
                    : "",
        }));
    };

    // =================================================
    // SUBMIT RENTAL METER READING
    // =================================================

    const handleSubmitRentalReading = async (machine) => {
        const machineId = getRentalMachineId(machine);
        const key = String(machineId);
        const enteredValue = getRentalEnteredReading(machineId);
        const previousReading = Number(getRentalCurrentReading(machine));
        const newReading = Number(enteredValue);

        if (!machineId) {
            setRentalReadingErrors((previous) => ({
                ...previous,
                [key]: "Unable to identify this rental machine.",
            }));
            return;
        }

        if (enteredValue === "" || !Number.isInteger(newReading)) {
            setRentalReadingErrors((previous) => ({
                ...previous,
                [key]: "Please enter a valid meter reading.",
            }));
            return;
        }

        if (newReading < previousReading) {
            setRentalReadingErrors((previous) => ({
                ...previous,
                [key]: `New reading cannot be less than the last reading (${previousReading.toLocaleString("en-IN")}).`,
            }));
            return;
        }

        if (getCurrentMonthRentalBill(machineId)) {
            setRentalReadingErrors((previous) => ({
                ...previous,
                [key]: `Reading for ${getCurrentBillingMonth()} has already been submitted.`,
            }));
            return;
        }

        try {
            setRentalSubmittingMachineId(machineId);
            setRentalReadingErrors((previous) => ({
                ...previous,
                [key]: "",
            }));

            // Customer submits only the new reading. The backend uses the
            // machine's confirmed meter as the previous reading, calculates
            // copies/amount and updates the machine for the admin portal.
            const billingMonth = getCurrentBillingMonth();
            const billingDate = getBillingDate();

            // IMPORTANT: billingMonth and billingDate are derived from the
            // same active admin-controlled cycle. The backend requires the
            // billing date to be inside the submitted billing month.
            await api.post(
                "/rental-bills/my",
                {
                    machine_id: Number(machineId),
                    billing_month: billingMonth,
                    billing_date: billingDate,
                    current_meter: newReading,
                }
            );

            const [machinesResponse, billsResponse] =
                await Promise.all([
                    api.get("/rental-bills/my-machines"),
                    api.get("/rental-bills/my"),
                ]);

            const machinePayload = machinesResponse?.data;
            const billPayload = billsResponse?.data;

            const updatedMachines =
                Array.isArray(machinePayload)
                    ? machinePayload
                    : Array.isArray(machinePayload?.items)
                        ? machinePayload.items
                        : Array.isArray(machinePayload?.machines)
                            ? machinePayload.machines
                            : Array.isArray(machinePayload?.data)
                                ? machinePayload.data
                                : [];

            const updatedBills =
                Array.isArray(billPayload)
                    ? billPayload
                    : Array.isArray(billPayload?.items)
                        ? billPayload.items
                        : Array.isArray(billPayload?.bills)
                            ? billPayload.bills
                            : Array.isArray(billPayload?.data)
                                ? billPayload.data
                                : [];

            setRentalMachines(updatedMachines);
            setRentalBills(updatedBills);

            setRentalMeterValues((previous) => ({
                ...previous,
                [key]: "",
            }));
        } catch (err) {
            console.error("Submit Rental Reading Error:", err);

            setRentalReadingErrors((previous) => ({
                ...previous,
                [key]: getApiMessage(
                    err,
                    "Unable to submit the rental meter reading."
                ),
            }));
        } finally {
            setRentalSubmittingMachineId(null);
        }
    };

    // =================================================
    // OPEN REQUEST MODAL
    // =================================================

    const openRequestModal = (
        machineId = ""
    ) => {

        setRequestError("");
        setRequestSuccess("");

        setRequestComplaint("");
        setRequestCurrentReading("");

        setRequestPriority(
            "MEDIUM"
        );

        setRequestMachineId(
            machineId
                ? String(machineId)
                : ""
        );

        setRequestModalOpen(
            true
        );
    };


    // =================================================
    // CLOSE REQUEST MODAL
    // =================================================

    const closeRequestModal = () => {

        if (
            submittingRequest
        ) {
            return;
        }

        setRequestModalOpen(
            false
        );

        setRequestError("");
        setRequestSuccess("");
        setRequestComplaint("");
        setRequestCurrentReading("");
        setRequestMachineId("");
        setRequestPriority("MEDIUM");
    };


    // =================================================
    // SUBMIT SERVICE REQUEST
    // =================================================

    const handleSubmitRequest = async (
        event
    ) => {

        event.preventDefault();

        setRequestError("");
        setRequestSuccess("");


        if (!requestMachineId) {

            setRequestError(
                "Please select the machine."
            );

            return;
        }


        if (
            requestCurrentReading === "" ||
            !Number.isInteger(Number(requestCurrentReading)) ||
            Number(requestCurrentReading) < 0
        ) {
            setRequestError(
                "Please enter a valid non-negative current meter reading."
            );
            return;
        }


        if (
            requestComplaint.trim()
                .length < 5
        ) {

            setRequestError(
                "Please describe the complaint in at least 5 characters."
            );

            return;
        }


        try {

            setSubmittingRequest(
                true
            );


            const response =
                await api.post(
                    "/customer/service-requests",
                    {
                        machine_id:
                            Number(
                                requestMachineId
                            ),

                        // Send both supported field names for compatibility.
                        // The backend schema/model stores the value as meter_reading;
                        // current_meter_reading is also accepted by the customer portal schema.
                        meter_reading:
                            Number(requestCurrentReading),

                        current_meter_reading:
                            Number(requestCurrentReading),

                        complaint:
                            requestComplaint.trim(),

                        priority:
                            requestPriority,
                    }
                );


            setRequestSuccess(
                response?.data
                    ?.message ||
                "Service request raised successfully."
            );


            // -------------------------------------------------
            // Refresh service requests.
            // -------------------------------------------------

            const requestsResponse =
                await api.get(
                    "/customer/service-requests"
                );


            const requestPayload = requestsResponse?.data;

            const requestItems =
                Array.isArray(requestPayload)
                    ? requestPayload
                    : Array.isArray(requestPayload?.service_requests)
                        ? requestPayload.service_requests
                        : Array.isArray(requestPayload?.items)
                            ? requestPayload.items
                            : Array.isArray(requestPayload?.data)
                                ? requestPayload.data
                                : Array.isArray(requestPayload?.data?.service_requests)
                                    ? requestPayload.data.service_requests
                                    : [];


            setServiceRequests(
                requestItems
            );


            // -------------------------------------------------
            // Move to service requests tab.
            // -------------------------------------------------

            setActiveTab(
                "requests"
            );


            // -------------------------------------------------
            // Close modal after a short success state.
            // -------------------------------------------------

            setTimeout(
                () => {

                    closeRequestModal();

                },
                700
            );

        }

        catch (err) {

            console.error(
                "Raise Service Request Error:",
                err
            );

            setRequestError(
                getApiMessage(
                    err,
                    "Unable to raise service request."
                )
            );

        }

        finally {

            setSubmittingRequest(
                false
            );
        }
    };


    // =================================================
    // VIEW REQUEST DETAILS
    // =================================================

    const openRequestDetails = (
        request
    ) => {

        setSelectedRequest(
            request
        );

        setRequestDetailsOpen(
            true
        );
    };


    const closeRequestDetails = () => {

        setRequestDetailsOpen(
            false
        );

        setSelectedRequest(
            null
        );
    };


    // =================================================
    // NOTIFICATION CLICK
    // =================================================

    const handleNotificationClick = async (
        notification
    ) => {
        try {
            if (!notification?.is_read) {
                await markAsRead(
                    notification.id
                );
            }
        } catch (error) {
            console.error(
                "Notification read error:",
                error
            );
        }

        setNotificationsOpen(false);

        // Open the related service request
        // inside the customer portal.
        if (
            notification?.reference_type ===
                "SERVICE_TICKET" &&
            notification?.reference_id
        ) {
            setActiveTab("requests");

            // Refresh requests so the latest
            // engineer assignment is visible.
            await loadPortalData(false);
        }
    };


    // =================================================
    // MARK INDIVIDUAL NOTIFICATION AS READ
    // =================================================

    const handleMarkNotificationRead = async (
        event,
        notification
    ) => {
        event.preventDefault();
        event.stopPropagation();

        if (!notification?.id || notification?.is_read) {
            return;
        }

        try {
            await markAsRead(notification.id);
        } catch (error) {
            console.error(
                "Mark notification read error:",
                error
            );
        }
    };


    // =================================================
    // CUSTOMER SESSION STATES
    // =================================================

    if (authLoading) {

        return (
            <div className="customer-portal-state">
                <Loader2
                    size={34}
                    className="customer-portal-spinner"
                />

                <p>
                    Verifying your account...
                </p>
            </div>
        );
    }


    if (!isAuthenticated) {

        return (
            <div className="customer-portal-state error-state">
                <AlertCircle size={34} />

                <h2>
                    Not authenticated
                </h2>

                <p>
                    Please login to access your customer service portal.
                </p>

                <button
                    type="button"
                    onClick={() => {
                        window.location.href =
                            "/login";
                    }}
                >
                    Go to Login
                </button>
            </div>
        );
    }


    // =================================================
    // RENDER
    // =================================================

    return (
        <div className="customer-portal">

            {/* =================================================
                HEADER
            ================================================= */}

            <header className="customer-portal-header">

                <div className="customer-portal-title">

                    <img
                        src="/digitechlogo.png"
                        alt="Digitech Logo"
                        className="customer-portal-logo"
                    />

                    <div className="customer-brand-text">
                        <strong>Digitech</strong>
                        <span>Customer Service Portal</span>
                    </div>

                </div>


                <div className="customer-portal-header-actions">

                    {/* =================================================
                        CUSTOMER NOTIFICATIONS
                    ================================================= */}

                    {(serviceAccess || rentalAccess) && (
                        <div
                            ref={notificationRef}
                            className="portal-notification-wrapper"
                        >

                        <button
                            type="button"
                            className="portal-notification-btn"
                            aria-label="Notifications"
                            title="Notifications"
                            onClick={async () => {
                                const willOpen =
                                    !notificationsOpen;

                                setNotificationsOpen(
                                    willOpen
                                );

                                if (willOpen) {
                                    await refreshNotifications();
                                }
                            }}
                        >
                            <Bell size={20} />

                            {unreadCount > 0 && (
                                <span className="portal-notification-badge">
                                    {unreadCount > 99
                                        ? "99+"
                                        : unreadCount}
                                </span>
                            )}
                        </button>

                        {notificationsOpen && (
                            <div className="portal-notification-dropdown">

                                <div className="portal-notification-header">

                                    <div className="portal-notification-heading">
                                        <strong>
                                            Notifications
                                        </strong>

                                        <span>
                                            {unreadCount > 0
                                                ? `${unreadCount} unread`
                                                : "All caught up"}
                                        </span>
                                    </div>

                                    {unreadCount > 0 && (
                                        <button
                                            type="button"
                                            onClick={async () => {
                                                try {
                                                    await markAllAsRead();
                                                } catch (error) {
                                                    console.error(
                                                        "Mark all read error:",
                                                        error
                                                    );
                                                }
                                            }}
                                        >
                                            Mark all read
                                        </button>
                                    )}

                                </div>

                                <div className="portal-notification-list">

                                    {notificationsLoading &&
                                    notifications.length === 0 ? (
                                        <div className="portal-notification-state">
                                            Loading notifications...
                                        </div>
                                    ) : notifications.length === 0 ? (
                                        <div className="portal-notification-state">
                                            <Bell size={24} />
                                            <span>
                                                No notifications
                                            </span>
                                        </div>
                                    ) : (
                                        notifications.map(
                                            (notification) => (
                                                <div
                                                    key={
                                                        notification.id
                                                    }
                                                    className={
                                                        notification.is_read
                                                            ? "portal-notification-item"
                                                            : "portal-notification-item unread"
                                                    }
                                                >

                                                    <button
                                                        type="button"
                                                        className="portal-notification-item-main"
                                                        onClick={() =>
                                                            handleNotificationClick(
                                                                notification
                                                            )
                                                        }
                                                    >

                                                        <div className="portal-notification-item-icon">
                                                            <Bell
                                                                size={15}
                                                            />
                                                        </div>

                                                        <div className="portal-notification-item-content">

                                                            <strong>
                                                                {
                                                                    notification.title ||
                                                                    "Notification"
                                                                }
                                                            </strong>

                                                            <p>
                                                                {
                                                                    notification.message ||
                                                                    "You have a new notification."
                                                                }
                                                            </p>

                                                            <small>
                                                                {formatNotificationTime(notification.created_at)}
                                                            </small>

                                                        </div>

                                                    </button>

                                                    <div className="portal-notification-item-action">

                                                        {!notification.is_read ? (
                                                            <button
                                                                type="button"
                                                                className="portal-notification-read-btn"
                                                                title="Mark as read"
                                                                aria-label="Mark notification as read"
                                                                onClick={(event) =>
                                                                    handleMarkNotificationRead(
                                                                        event,
                                                                        notification
                                                                    )
                                                                }
                                                            >
                                                                <CheckCircle2 size={14} />
                                                                <span>Read</span>
                                                            </button>
                                                        ) : (
                                                            <span className="portal-notification-read-label">
                                                                Read
                                                            </span>
                                                        )}

                                                    </div>

                                                </div>
                                            )
                                        )
                                    )}

                                </div>

                                {serviceAccess && (
                                    <div className="portal-notification-footer">
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setNotificationsOpen(false);
                                                setActiveTab("requests");
                                                loadPortalData(false);
                                            }}
                                        >
                                            View Service Requests
                                        </button>
                                    </div>
                                )}

                            </div>
                        )}

                        </div>
                    )}

                    <div className="customer-profile-avatar" aria-hidden="true">
                        <UserRound size={16} />
                    </div>

                    <span className="customer-welcome">
                        {user?.full_name ||
                            customer?.customer_name ||
                            "Customer"}
                    </span>

                    <button
                        type="button"
                        className="portal-secondary-btn"
                        onClick={() =>
                            loadPortalData(false)
                        }
                        disabled={refreshing}
                    >
                        <RefreshCw
                            size={15}
                            className={
                                refreshing
                                    ? "spin"
                                    : ""
                            }
                        />

                        Refresh
                    </button>

                    <button
                        type="button"
                        className="portal-secondary-btn"
                        onClick={logout}
                    >
                        <LogOut size={15} />
                        Logout
                    </button>

                </div>

            </header>


            <main className="customer-portal-main">

            {/* =================================================
                ERROR BANNER
            ================================================= */}

            {error && (
                <div className="portal-alert portal-alert-error">

                    <AlertCircle size={17} />

                    <span>
                        {error}
                    </span>

                    <button
                        type="button"
                        onClick={() =>
                            loadPortalData(false)
                        }
                    >
                        Try Again
                    </button>

                </div>
            )}


            {/* =================================================
                CUSTOMER SUMMARY
            ================================================= */}

            {serviceAccess && (
            <section className="portal-summary-grid">

                <div className="portal-summary-card">

                    <div className="portal-summary-icon">
                        <MonitorCog size={18} />
                    </div>

                    <div>

                        <span>
                            My Machines
                        </span>

                        <strong>
                            {pageLoading
                                ? "—"
                                : machines.length}
                        </strong>

                    </div>

                </div>


                <div className="portal-summary-card">

                    <div className="portal-summary-icon">
                        <Ticket size={18} />
                    </div>

                    <div>

                        <span>
                            Service Requests
                        </span>

                        <strong>
                            {pageLoading
                                ? "—"
                                : serviceRequests.length}
                        </strong>

                    </div>

                </div>


                <div className="portal-summary-card">

                    <div className="portal-summary-icon">
                        <Wrench size={18} />
                    </div>

                    <div>

                        <span>
                            Active Machines
                        </span>

                        <strong>
                            {pageLoading
                                ? "—"
                                : activeMachineCount}
                        </strong>

                    </div>

                </div>


                <div className="portal-summary-card">

                    <div className="portal-summary-icon portal-summary-icon-completed">
                        <CheckCircle2 size={18} />
                    </div>

                    <div>

                        <span>
                            Completed Requests
                        </span>

                        <strong>
                            {pageLoading
                                ? "—"
                                : completedRequestCount}
                        </strong>

                    </div>

                </div>

            </section>
            )}



            {/* =================================================
                TABS
            ================================================= */}

            <div className="portal-tab-bar">

                {serviceAccess && (
                    <>
                        <button
                            type="button"
                            className={activeTab === "machines" ? "portal-tab active" : "portal-tab"}
                            onClick={() => setActiveTab("machines")}
                        >
                            <Settings2 size={14} />
                            My Machines
                        </button>

                        <button
                            type="button"
                            className={activeTab === "requests" ? "portal-tab active" : "portal-tab"}
                            onClick={() => setActiveTab("requests")}
                        >
                            <FileText size={14} />
                            My Service Requests
                        </button>
                    </>
                )}

                {rentalAccess && (
                    <button
                        type="button"
                        className={activeTab === "rental" ? "portal-tab active" : "portal-tab"}
                        onClick={() => setActiveTab("rental")}
                    >
                        <Gauge size={14} />
                        Rental
                    </button>
                )}

            </div>


            {/* =================================================
                CONTENT
            ================================================= */}

            <section className="portal-content-card">

                {activeTab === "machines" && serviceAccess ? (

                    <>
                        <div className="portal-content-header">

                            <div>

                                <h2>
                                    My Machines
                                </h2>

                                <p>
                                    Machines registered under your customer account
                                </p>

                            </div>


                            <button
                                type="button"
                                className="portal-primary-btn"
                                onClick={() =>
                                    openRequestModal()
                                }
                                disabled={
                                    pageLoading ||
                                    machines.length === 0
                                }
                            >
                                <Plus size={16} />
                                Raise Service Request
                            </button>

                        </div>


                        {pageLoading ? (

                            <div className="portal-empty-state">

                                <Loader2
                                    size={30}
                                    className="customer-portal-spinner"
                                />

                                <p>
                                    Loading your machines...
                                </p>

                            </div>

                        ) : machines.length === 0 ? (

                            <div className="portal-empty-state">

                                <MonitorCog
                                    size={36}
                                />

                                <h3>
                                    No Machines Found
                                </h3>

                                <p>
                                    No machines are currently registered under your account.
                                </p>

                            </div>

                        ) : (

                            <div className="machine-grid">

                                {machines.map(
                                    (machine) => (

                                        <article
                                            key={
                                                machine.id
                                            }
                                            className="machine-card"
                                        >

                                            <div className="machine-card-top">

                                                <div className="machine-icon">
                                                    <MonitorCog
                                                        size={20}
                                                    />
                                                </div>

                                                <span
                                                    className={`portal-status-badge ${
                                                        statusClass(
                                                            machine.status
                                                        )
                                                    }`}
                                                >
                                                    {statusLabel(
                                                        machine.status ||
                                                        "ACTIVE"
                                                    )}
                                                </span>

                                            </div>


                                            <h3>
                                                {
                                                    machine.machine_name ||
                                                    machine.machineName ||
                                                    machine.name ||
                                                    "Unnamed Machine"
                                                }
                                            </h3>


                                            <div className="machine-meta">

                                                <div>
                                                    <span>
                                                        Serial Number
                                                    </span>

                                                    <strong>
                                                        {
                                                            machine.serial_number ||
                                                            machine.serialNumber ||
                                                            "—"
                                                        }
                                                    </strong>
                                                </div>

                                                <div>
                                                    <span>
                                                        Installation
                                                    </span>

                                                    <strong>
                                                        {formatDate(
                                                            machine.installation_date ||
                                                            machine.installationDate
                                                        )}
                                                    </strong>
                                                </div>

                                                <div>
                                                    <span>
                                                        Warranty Ends
                                                    </span>

                                                    <strong>
                                                        {formatDate(
                                                            machine.warranty_end ||
                                                            machine.warrantyEnd
                                                        )}
                                                    </strong>
                                                </div>

                                            </div>


                                            <button
                                                type="button"
                                                className="machine-request-btn"
                                                onClick={() =>
                                                    openRequestModal(
                                                        machine.id
                                                    )
                                                }
                                            >
                                                <Wrench size={15} />
                                                Request Service
                                                <ChevronRight
                                                    size={15}
                                                />
                                            </button>

                                        </article>

                                    )
                                )}

                            </div>

                        )}

                    </>

                ) : activeTab === "requests" && serviceAccess ? (

                    <>
                        <div className="portal-content-header">

                            <div>

                                <h2>
                                    My Service Requests
                                </h2>

                                <p>
                                    Track service requests raised for your machines
                                </p>

                            </div>


                            <button
                                type="button"
                                className="portal-primary-btn"
                                onClick={() =>
                                    openRequestModal()
                                }
                                disabled={
                                    machines.length === 0
                                }
                            >
                                <Plus size={16} />
                                New Request
                            </button>

                        </div>


                        {pageLoading ? (

                            <div className="portal-empty-state">

                                <Loader2
                                    size={30}
                                    className="customer-portal-spinner"
                                />

                                <p>
                                    Loading service requests...
                                </p>

                            </div>

                        ) : serviceRequests.length === 0 ? (

                            <div className="portal-empty-state">

                                <Ticket
                                    size={36}
                                />

                                <h3>
                                    No Service Requests
                                </h3>

                                <p>
                                    You have not raised any service requests yet.
                                </p>

                                {machines.length > 0 && (
                                    <button
                                        type="button"
                                        className="portal-primary-btn"
                                        onClick={() =>
                                            openRequestModal()
                                        }
                                    >
                                        <Plus size={16} />
                                        Raise Your First Request
                                    </button>
                                )}

                            </div>

                        ) : (

                            <div className="request-table-wrap">

                                <table className="request-table">

                                    <thead>

                                        <tr>
                                            <th>
                                                Ticket
                                            </th>

                                            <th>
                                                Machine
                                            </th>

                                            <th>
                                                Material Used
                                            </th>

                                            <th>
                                                Service Cost
                                            </th>

                                            <th>
                                                Service Engineer
                                            </th>

                                            <th>
                                                Complaint
                                            </th>

                                            <th>
                                                Priority
                                            </th>

                                            <th>
                                                Status
                                            </th>

                                            <th>
                                                Action
                                            </th>
                                        </tr>

                                    </thead>


                                    <tbody>

                                        {serviceRequests.map(
                                            (request) => {

                                                const machine =
                                                    machines.find(
                                                        (item) =>
                                                            Number(
                                                                item.id
                                                            ) ===
                                                            Number(
                                                                request.machine_id
                                                            )
                                                    );


                                                return (
                                                    <tr
                                                        key={
                                                            request.id
                                                        }
                                                    >

                                                        <td>
                                                            <strong>
                                                                {
                                                                    request.ticket_number ||
                                                                    `#${request.id}`
                                                                }
                                                            </strong>
                                                        </td>


                                                        <td>
                                                            <div className="request-machine-cell">

                                                                <strong>
                                                                    {
                                                                        machine?.machine_name ||
                                                                        machine?.machineName ||
                                                                        machine?.machine_number ||
                                                                        `Machine #${request.machine_id}`
                                                                    }
                                                                </strong>

                                                                <span>
                                                                    {
                                                                        request.serial_number ||
                                                                        machine?.serial_number ||
                                                                        "—"
                                                                    }
                                                                </span>

                                                            </div>
                                                        </td>


                                                        <td>
                                                            <div className="request-material-cell">
                                                                {
                                                                    request.material_used ||
                                                                    request.materialUsed ||
                                                                    "—"
                                                                }
                                                            </div>
                                                        </td>


                                                        <td>
                                                            <strong className="request-cost-cell">
                                                                {formatCurrency(
                                                                    request.service_cost ??
                                                                    request.serviceCost
                                                                )}
                                                            </strong>
                                                        </td>


                                                        <td>
                                                            <div className="request-engineer-cell">
                                                                {getEngineerName(request)}
                                                            </div>
                                                        </td>


                                                        <td>
                                                            <div className="request-complaint-cell">
                                                                {
                                                                    request.complaint
                                                                }
                                                            </div>
                                                        </td>


                                                        <td>
                                                            <span
                                                                className={`priority-badge priority-${(
                                                                    request.priority ||
                                                                    "MEDIUM"
                                                                )
                                                                    .toString()
                                                                    .toLowerCase()}`}
                                                            >
                                                                {
                                                                    request.priority ||
                                                                    "MEDIUM"
                                                                }
                                                            </span>
                                                        </td>


                                                        <td>
                                                            <span
                                                                className={`portal-status-badge ${
                                                                    statusClass(
                                                                        request.status
                                                                    )
                                                                }`}
                                                            >
                                                                {statusLabel(
                                                                    request.status
                                                                )}
                                                            </span>
                                                        </td>


                                                        <td>
                                                            <button
                                                                type="button"
                                                                className="view-request-btn"
                                                                onClick={() =>
                                                                    openRequestDetails(
                                                                        request
                                                                    )
                                                                }
                                                            >
                                                                View
                                                            </button>
                                                        </td>

                                                    </tr>
                                                );
                                            }
                                        )}

                                    </tbody>

                                </table>

                            </div>

                        )}

                    </>


                ) : activeTab === "rental" && rentalAccess ? (

                    <>
                        <div className="portal-content-header rental-content-header">
                            <div>
                                <h2>Rental</h2>
                                <p>
                                    Enter your monthly meter reading and view the calculated rental cost.
                                </p>
                            </div>

                            <div className="rental-header-count">
                                <span>Rental Machines</span>
                                <strong>{pageLoading ? "—" : rentalMachines.length}</strong>
                            </div>
                        </div>

                        <div className="rental-summary-grid">
                            <div className="rental-summary-card">
                                <div className="rental-summary-icon"><MonitorCog size={18} /></div>
                                <div><span>Rental Machines</span><strong>{pageLoading ? "—" : rentalMachines.length}</strong></div>
                            </div>
                            <div className="rental-summary-card">
                                <div className="rental-summary-icon"><Gauge size={18} /></div>
                                <div><span>Active Rentals</span><strong>{pageLoading ? "—" : activeRentalCount}</strong></div>
                            </div>
                            <div className="rental-summary-card">
                                <div className="rental-summary-icon warning"><History size={18} /></div>
                                <div><span>Pending Readings</span><strong>{pageLoading ? "—" : pendingRentalReadingCount}</strong></div>
                            </div>
                            <div className="rental-summary-card">
                                <div className="rental-summary-icon success"><IndianRupee size={18} /></div>
                                <div><span>Outstanding</span><strong>{pageLoading ? "—" : formatCurrency(rentalOutstandingAmount)}</strong></div>
                            </div>
                        </div>

                        {rentalMachines.length > 0 && (
                            <div className="rental-machine-selector-wrap">
                                <div className="rental-machine-selector-content">
                                    <label htmlFor="customer-rental-machine-select">
                                        Select Machine
                                    </label>
                                    <select
                                        id="customer-rental-machine-select"
                                        className="rental-machine-selector"
                                        value={selectedRentalMachineId}
                                        onChange={(event) =>
                                            setSelectedRentalMachineId(event.target.value)
                                        }
                                    >
                                        {rentalMachines.map((machine) => {
                                            const machineId = getRentalMachineId(machine);

                                            return (
                                                <option
                                                    key={machineId}
                                                    value={String(machineId)}
                                                >
                                                    {getRentalMachineName(machine)}
                                                    {getRentalSerialNumber(machine) !== "—"
                                                        ? ` • ${getRentalSerialNumber(machine)}`
                                                        : ""}
                                                </option>
                                            );
                                        })}
                                    </select>
                                    <span>
                                        Select a machine to view and update its complete monthly rental data.
                                    </span>
                                </div>
                            </div>
                        )}

                        <div className="rental-table-wrap">
                            {rentalMachines.length === 0 ? (
                                <div className="portal-empty-state rental-empty-state">
                                    <Gauge size={42} />
                                    <h3>No Rental Machines Found</h3>
                                    <p>No rental machines are currently registered under your account.</p>
                                </div>
                            ) : (
                                <div className="rental-table-scroll">
                                    <table className="rental-table rental-entry-table">
                                        <thead>
                                            <tr>
                                                <th>Machine</th>
                                                <th>Serial Number</th>
                                                <th>Last Month Reading</th>
                                                <th>New Reading</th>
                                                <th>Billing Month</th>
                                                <th>Price / Page</th>
                                                <th>Copies</th>
                                                <th>Cost</th>
                                                <th>Action</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {selectedRentalMachine ? (() => {
                                                const machine = selectedRentalMachine;
                                                const machineId = getRentalMachineId(machine);
                                                const machineReading = getRentalCurrentReading(machine);
                                                const machineRate = getRentalRate(machine);
                                                const currentMonthBill = getCurrentMonthRentalBill(machineId);
                                                const enteredReading = getRentalEnteredReading(machineId);
                                                const copiesUsed = getRentalCopiesUsed(machine);
                                                const estimatedAmount = getRentalEstimatedAmount(machine);
                                                const readingError = rentalReadingErrors[String(machineId)] || "";
                                                const submitting = Number(rentalSubmittingMachineId) === Number(machineId);

                                                // ---------------------------------------------------------
                                                // IMPORTANT:
                                                // Once a monthly bill exists, the BILL is the source of
                                                // truth for the customer's rental table.
                                                //
                                                // Do not use machine.current_meter for the previous reading
                                                // because the machine meter may already have been updated by
                                                // the backend/admin. This is why values could appear wrong
                                                // in the customer portal.
                                                // ---------------------------------------------------------
                                                const billPreviousReading = currentMonthBill
                                                    ? Number(
                                                        currentMonthBill.previous_meter ??
                                                        currentMonthBill.previousMeter ??
                                                        0
                                                    )
                                                    : Number(machineReading ?? 0);

                                                const billCurrentReading = currentMonthBill
                                                    ? Number(
                                                        currentMonthBill.current_meter ??
                                                        currentMonthBill.currentMeter ??
                                                        0
                                                    )
                                                    : null;

                                                // IMPORTANT:
                                                // The admin-managed machine price is the CURRENT
                                                // customer-specific price. Always display this price
                                                // in the customer portal, even when a monthly bill
                                                // already exists.
                                                //
                                                // Historical bill amounts remain stored in the bill.
                                                // The visible current Price / Page must come from the
                                                // rental machine so an admin price change is reflected
                                                // immediately after refresh.
                                                const billRate = Number(machineRate ?? 0);

                                                const billCopies = currentMonthBill
                                                    ? Number(
                                                        currentMonthBill.copies_used ??
                                                        currentMonthBill.copiesUsed ??
                                                        0
                                                    )
                                                    : copiesUsed;

                                                const storedBillAmount = currentMonthBill
                                                    ? Number(
                                                        currentMonthBill.total_amount ??
                                                        currentMonthBill.totalAmount ??
                                                        0
                                                    )
                                                    : null;

                                                const billAmount = currentMonthBill
                                                    ? (
                                                        Number.isFinite(storedBillAmount)
                                                            ? storedBillAmount
                                                            : 0
                                                    )
                                                    : estimatedAmount;

                                                return (
                                                    <tr key={machineId}>
                                                        <td>
                                                            <div className="rental-machine-cell">
                                                                <div className="rental-machine-icon"><MonitorCog size={18} /></div>
                                                                <div>
                                                                    <strong>{getRentalMachineName(machine)}</strong>
                                                                    <span>{machine.machine_number || machine.machineNumber || "Rental Machine"}</span>
                                                                </div>
                                                            </div>
                                                        </td>
                                                        <td><span className="rental-serial-text">{getRentalSerialNumber(machine)}</span></td>
                                                        <td>
                                                            <strong className="rental-reading-value">
                                                                {billPreviousReading.toLocaleString("en-IN")}
                                                            </strong>
                                                            <small className="rental-data-source">
                                                                {currentMonthBill
                                                                    ? "Previous reading"
                                                                    : "Last confirmed reading"}
                                                            </small>
                                                        </td>
                                                        <td>
                                                            {currentMonthBill ? (
                                                                <div className="rental-submitted-reading">
                                                                    <strong className="rental-reading-value">
                                                                        {billCurrentReading.toLocaleString("en-IN")}
                                                                    </strong>
                                                                    <small>Submitted</small>
                                                                </div>
                                                            ) : (
                                                                <div className="rental-inline-reading">
                                                                    <input
                                                                        type="number"
                                                                        min={machineReading ?? 0}
                                                                        step="1"
                                                                        inputMode="numeric"
                                                                        value={enteredReading}
                                                                        onChange={(event) => handleRentalMeterChange(machine, event)}
                                                                        placeholder="Enter reading"
                                                                        disabled={submitting}
                                                                        aria-label={`New reading for ${getRentalMachineName(machine)}`}
                                                                    />
                                                                    {readingError && <small className="rental-inline-error">{readingError}</small>}
                                                                </div>
                                                            )}
                                                        </td>
                                                        <td>
                                                            <strong className="rental-month-value">
                                                                {getRentalBillingMonthLabel(
                                                                    currentMonthBill?.billing_month ||
                                                                    currentMonthBill?.billingMonth ||
                                                                    getCurrentBillingMonth()
                                                                )}
                                                            </strong>
                                                            <small className="rental-data-source">
                                                                Current billing cycle
                                                            </small>
                                                        </td>
                                                        <td>
                                                            <strong className="rental-rate-value">
                                                                {formatCurrency(billRate)}
                                                            </strong>
                                                        </td>
                                                        <td>
                                                            <strong className="rental-reading-value">
                                                                {billCopies === null || !Number.isFinite(billCopies)
                                                                    ? "—"
                                                                    : billCopies.toLocaleString("en-IN")}
                                                            </strong>
                                                        </td>
                                                        <td>
                                                            <strong className="rental-rate-value">
                                                                {billAmount === null || !Number.isFinite(billAmount)
                                                                    ? "—"
                                                                    : formatCurrency(billAmount)}
                                                            </strong>
                                                        </td>
                                                        <td>
                                                            <button
                                                                type="button"
                                                                className="rental-update-btn"
                                                                onClick={() => handleSubmitRentalReading(machine)}
                                                                disabled={submitting || Boolean(currentMonthBill) || enteredReading === "" || Boolean(readingError)}
                                                            >
                                                                {submitting ? (
                                                                    <><Loader2 size={15} className="spin" /> Submitting...</>
                                                                ) : (
                                                                    <><Gauge size={15} /> {currentMonthBill ? "Submitted" : "Submit"}</>
                                                                )}
                                                            </button>
                                                        </td>
                                                    </tr>
                                                );
                                            })() : null}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>

                        {selectedRentalMachine && (
                            <div className="rental-history-section">
                                <div className="rental-history-header">
                                    <div>
                                        <h3>Monthly Rental History</h3>
                                        <p>
                                            Complete monthly reading and billing history for this machine.
                                        </p>
                                    </div>
                                    <div className="rental-history-month-badge">
                                        Current Month: {getRentalBillingMonthLabel(getCurrentBillingMonth())}
                                    </div>
                                </div>

                                {getRentalMachineHistory(getRentalMachineId(selectedRentalMachine)).length === 0 ? (
                                    <div className="rental-history-empty">
                                        <History size={22} />
                                        <span>No monthly rental history is available for this machine yet.</span>
                                    </div>
                                ) : (
                                    <div className="rental-history-table-wrap">
                                        <table className="rental-table rental-history-table">
                                            <thead>
                                                <tr>
                                                    <th>Billing Month</th>
                                                    <th>Previous Reading</th>
                                                    <th>New Reading</th>
                                                    <th>Price / Page</th>
                                                    <th>Copies</th>
                                                    <th>Cost</th>
                                                    <th>Payment Status</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {getRentalMachineHistory(
                                                    getRentalMachineId(selectedRentalMachine)
                                                ).map((bill) => {
                                                    const billMonth =
                                                        bill?.billing_month ||
                                                        bill?.billingMonth;

                                                    const paymentStatus =
                                                        String(
                                                            bill?.payment_status ||
                                                            bill?.paymentStatus ||
                                                            "PENDING"
                                                        )
                                                            .replaceAll("_", " ")
                                                            .toLowerCase()
                                                            .replace(/\b\w/g, (letter) => letter.toUpperCase());

                                                    return (
                                                        <tr key={bill.id}>
                                                            <td>
                                                                <strong>
                                                                    {getRentalBillingMonthLabel(billMonth)}
                                                                </strong>
                                                            </td>
                                                            <td>
                                                                {getRentalBillPreviousReading(bill).toLocaleString("en-IN")}
                                                            </td>
                                                            <td>
                                                                <strong>
                                                                    {getRentalBillCurrentReading(bill).toLocaleString("en-IN")}
                                                                </strong>
                                                            </td>
                                                            <td>
                                                                {formatCurrency(getRentalBillRate(bill))}
                                                            </td>
                                                            <td>
                                                                {getRentalBillCopies(bill).toLocaleString("en-IN")}
                                                            </td>
                                                            <td>
                                                                <strong>
                                                                    {formatCurrency(getRentalBillAmount(bill))}
                                                                </strong>
                                                            </td>
                                                            <td>
                                                                <span className={`rental-history-status ${String(bill?.payment_status || bill?.paymentStatus || "PENDING").toLowerCase()}`}>
                                                                    {paymentStatus}
                                                                </span>
                                                            </td>
                                                        </tr>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        )}

                        <div className="rental-monthly-note">
                            <Gauge size={16} />
                            <div>
                                <strong>Monthly meter reading</strong>
                                <span>
                                    Enter only the new meter reading. The previous reading is controlled by the rental billing system, and the current price per page is controlled by the administrator. The current price is shown from the rental machine assigned to your account.
                                </span>
                            </div>
                        </div>
                    </>
                ) : (

                    <div className="portal-empty-state">
                        <AlertCircle size={42} />
                        <h3>No Portal Access</h3>
                        <p>
                            Your customer portal does not currently have Service or Rental access enabled.
                            Please contact your administrator.
                        </p>
                    </div>

                )}

            </section>


            </main>


            {/* =================================================
                RAISE SERVICE REQUEST MODAL
            ================================================= */}

            {requestModalOpen && (
                <div
                    className="portal-modal-overlay"
                    onMouseDown={closeRequestModal}
                >

                    <div
                        className="portal-modal"
                        onMouseDown={(event) =>
                            event.stopPropagation()
                        }
                    >

                        <div className="portal-modal-header">

                            <div>

                                <h2>
                                    Raise Service Request
                                </h2>

                                <p>
                                    Submit a service complaint for one of your machines.
                                </p>

                            </div>


                            <button
                                type="button"
                                className="portal-modal-close"
                                onClick={
                                    closeRequestModal
                                }
                                disabled={
                                    submittingRequest
                                }
                            >
                                <X size={19} />
                            </button>

                        </div>


                        <form
                            onSubmit={
                                handleSubmitRequest
                            }
                        >

                            <div className="portal-modal-body">

                                {requestError && (
                                    <div className="portal-alert portal-alert-error">

                                        <AlertCircle
                                            size={16}
                                        />

                                        <span>
                                            {
                                                requestError
                                            }
                                        </span>

                                    </div>
                                )}


                                {requestSuccess && (
                                    <div className="portal-alert portal-alert-success">

                                        <CheckCircle2
                                            size={16}
                                        />

                                        <span>
                                            {
                                                requestSuccess
                                            }
                                        </span>

                                    </div>
                                )}


                                <div className="portal-form-group">

                                    <label>
                                        Machine
                                    </label>

                                    <select
                                        value={
                                            requestMachineId
                                        }
                                        onChange={(
                                            event
                                        ) =>
                                            setRequestMachineId(
                                                event.target.value
                                            )
                                        }
                                        disabled={
                                            submittingRequest
                                        }
                                    >

                                        <option value="">
                                            Select your machine
                                        </option>

                                        {machines.map(
                                            (machine) => (

                                                <option
                                                    key={
                                                        machine.id
                                                    }
                                                    value={
                                                        machine.id
                                                    }
                                                >
                                                    {getMachineLabel(
                                                        machine
                                                    )}
                                                </option>

                                            )
                                        )}

                                    </select>

                                </div>


                                <div className="portal-form-group">
                                    <label htmlFor="request-current-meter-reading">
                                        Current Machine Reading
                                    </label>
                                    <input
                                        id="request-current-meter-reading"
                                        type="number"
                                        min="0"
                                        step="1"
                                        inputMode="numeric"
                                        value={requestCurrentReading}
                                        onChange={(event) => {
                                            const value = event.target.value;
                                            if (value === "" || /^\d+$/.test(value)) {
                                                setRequestCurrentReading(value);
                                            }
                                        }}
                                        placeholder="Enter current meter reading"
                                        required
                                        disabled={submittingRequest}
                                    />
                                    <small className="portal-form-hint">
                                        Enter the number currently displayed on the machine meter.
                                    </small>
                                </div>


                                <div className="portal-form-group">

                                    <label>
                                        Priority
                                    </label>

                                    <select
                                        value={
                                            requestPriority
                                        }
                                        onChange={(
                                            event
                                        ) =>
                                            setRequestPriority(
                                                event.target.value
                                            )
                                        }
                                        disabled={
                                            submittingRequest
                                        }
                                    >

                                        <option value="LOW">
                                            Low
                                        </option>

                                        <option value="MEDIUM">
                                            Medium
                                        </option>

                                        <option value="HIGH">
                                            High
                                        </option>

                                        <option value="URGENT">
                                            Urgent
                                        </option>

                                    </select>

                                </div>


                                <div className="portal-form-group">

                                    <label>
                                        Complaint / Service Required
                                    </label>

                                    <textarea
                                        value={
                                            requestComplaint
                                        }
                                        onChange={(
                                            event
                                        ) =>
                                            setRequestComplaint(
                                                event.target.value
                                            )
                                        }
                                        minLength={5}
                                        maxLength={1000}
                                        rows={6}
                                        placeholder="Describe the problem or service required..."
                                        disabled={
                                            submittingRequest
                                        }
                                    />

                                    <div className="portal-character-count">
                                        {
                                            requestComplaint.length
                                        }
                                        /1000
                                    </div>

                                </div>

                            </div>


                            <div className="portal-modal-footer">

                                <button
                                    type="button"
                                    className="portal-secondary-btn"
                                    onClick={
                                        closeRequestModal
                                    }
                                    disabled={
                                        submittingRequest
                                    }
                                >
                                    Cancel
                                </button>


                                <button
                                    type="submit"
                                    className="portal-primary-btn"
                                    disabled={
                                        submittingRequest ||
                                        !requestMachineId ||
                                        requestCurrentReading === "" ||
                                        !Number.isInteger(Number(requestCurrentReading)) ||
                                        Number(requestCurrentReading) < 0 ||
                                        requestComplaint.trim()
                                            .length < 5
                                    }
                                >

                                    {submittingRequest ? (
                                        <>
                                            <Loader2
                                                size={16}
                                                className="spin"
                                            />
                                            Submitting...
                                        </>
                                    ) : (
                                        <>
                                            <Send
                                                size={16}
                                            />
                                            Raise Request
                                        </>
                                    )}

                                </button>

                            </div>

                        </form>

                    </div>

                </div>
            )}


            {/* =================================================
                REQUEST DETAILS MODAL
            ================================================= */}

            {requestDetailsOpen &&
                selectedRequest && (

                    <div
                        className="portal-modal-overlay"
                        onMouseDown={
                            closeRequestDetails
                        }
                    >

                        <div
                            className="portal-modal request-details-modal"
                            onMouseDown={(
                                event
                            ) =>
                                event.stopPropagation()
                            }
                        >

                            <div className="portal-modal-header">

                                <div>

                                    <h2>
                                        Service Request Details
                                    </h2>

                                    <p>
                                        {
                                            selectedRequest.ticket_number ||
                                            `Request #${selectedRequest.id}`
                                        }
                                    </p>

                                </div>


                                <button
                                    type="button"
                                    className="portal-modal-close"
                                    onClick={
                                        closeRequestDetails
                                    }
                                >
                                    <X size={19} />
                                </button>

                            </div>


                            <div className="portal-details-body">

                                <div className="request-detail-top">

                                    <div>
                                        <span>
                                            Ticket
                                        </span>

                                        <strong>
                                            {
                                                selectedRequest.ticket_number ||
                                                `#${selectedRequest.id}`
                                            }
                                        </strong>
                                    </div>


                                    <span
                                        className={`portal-status-badge ${
                                            statusClass(
                                                selectedRequest.status
                                            )
                                        }`}
                                    >
                                        {statusLabel(
                                            selectedRequest.status
                                        )}
                                    </span>

                                </div>


                                <div className="request-detail-grid">

                                    <div>
                                        <span>
                                            Machine
                                        </span>

                                        <strong>
                                            {
                                                machines.find(
                                                    (machine) =>
                                                        Number(
                                                            machine.id
                                                        ) ===
                                                        Number(
                                                            selectedRequest.machine_id
                                                        )
                                                )
                                                    ?.machine_name ||
                                                machines.find(
                                                    (machine) =>
                                                        Number(
                                                            machine.id
                                                        ) ===
                                                        Number(
                                                            selectedRequest.machine_id
                                                        )
                                                )
                                                    ?.machineName ||
                                                machines.find(
                                                    (machine) =>
                                                        Number(
                                                            machine.id
                                                        ) ===
                                                        Number(
                                                            selectedRequest.machine_id
                                                        )
                                                )
                                                    ?.machine_number ||
                                                `Machine #${selectedRequest.machine_id}`
                                            }
                                        </strong>
                                    </div>


                                    <div>
                                        <span>
                                            Serial Number
                                        </span>

                                        <strong>
                                            {
                                                selectedRequest.serial_number ||
                                                selectedRequest.serialNumber ||
                                                "—"
                                            }
                                        </strong>
                                    </div>


                                    <div>
                                        <span>
                                            Meter Reading Submitted
                                        </span>

                                        <strong>
                                            {
                                                selectedRequest.meter_reading ??
                                                selectedRequest.current_meter_reading ??
                                                selectedRequest.currentMeterReading ??
                                                selectedRequest.current_meter ??
                                                selectedRequest.currentMeter ??
                                                "Not provided"
                                            }
                                        </strong>
                                    </div>


                                    <div>
                                        <span>
                                            Priority
                                        </span>

                                        <strong>
                                            {
                                                selectedRequest.priority ||
                                                "MEDIUM"
                                            }
                                        </strong>
                                    </div>


                                    <div>
                                        <span>
                                            Service Engineer
                                        </span>

                                        <strong>
                                            {getEngineerName(selectedRequest)}
                                        </strong>
                                    </div>


                                    <div>
                                        <span>
                                            Material Used
                                        </span>

                                        <strong>
                                            {
                                                selectedRequest.material_used ||
                                                selectedRequest.materialUsed ||
                                                "—"
                                            }
                                        </strong>
                                    </div>


                                    <div>
                                        <span>
                                            Service Cost
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                selectedRequest.service_cost ??
                                                selectedRequest.serviceCost
                                            )}
                                        </strong>
                                    </div>


                                    <div>
                                        <span>
                                            Reported
                                        </span>

                                        <strong>
                                            {
                                                formatDate(
                                                    getRequestDate(selectedRequest)
                                                )
                                            }
                                        </strong>
                                    </div>


                                    <div>
                                        <span>
                                            Expected Visit
                                        </span>

                                        <strong>
                                            {
                                                formatDate(
                                                    selectedRequest.expected_visit_date ||
                                                    selectedRequest.scheduled_date ||
                                                    selectedRequest.expectedVisitDate
                                                )
                                            }
                                        </strong>
                                    </div>


                                    <div>
                                        <span>
                                            Completed
                                        </span>

                                        <strong>
                                            {
                                                formatDate(
                                                    selectedRequest.completed_date ||
                                                    selectedRequest.completion_date ||
                                                    selectedRequest.completed_at
                                                )
                                            }
                                        </strong>
                                    </div>

                                </div>


                                <div className="request-detail-section">

                                    <span>
                                        Complaint
                                    </span>

                                    <p>
                                        {
                                            selectedRequest.complaint ||
                                            "—"
                                        }
                                    </p>

                                </div>


                                <div className="request-detail-section">

                                    <span>
                                        Resolution
                                    </span>

                                    <p>
                                        {
                                            selectedRequest.resolution ||
                                            "No resolution has been added yet."
                                        }
                                    </p>

                                </div>

                            </div>


                            <div className="portal-modal-footer">

                                <button
                                    type="button"
                                    className="portal-secondary-btn"
                                    onClick={
                                        closeRequestDetails
                                    }
                                >
                                    Close
                                </button>

                            </div>

                        </div>

                    </div>

                )}

        </div>
    );
};


export default CustomerPortal;