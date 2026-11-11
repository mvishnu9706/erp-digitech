import React, {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useRef,
    useState,
} from "react";


// =====================================================
// API
// =====================================================
//
// Use the same authenticated Axios instance used by the
// rest of the application. This is important because the
// previous fetch() implementation could miss the current
// login token and cause:
//
//     GET /service-tickets/ -> 401 Unauthorized
//
// =====================================================

import api from "../api/axios";


// =====================================================
// CONTEXT
// =====================================================

const ServiceContext = createContext(null);


// =====================================================
// MAP BACKEND TICKET
// =====================================================
//
// The backend ServiceTicket object may contain
// nested customer / machine / engineer objects,
// depending on your Pydantic response schema.
//
// This mapper keeps the ServiceTable compatible
// with the existing frontend fields:
//
// customer
// phone
// email
// address
// product
// issue
// technician
// priority
// status
// service_date
// total_amount
//
// =====================================================

const mapServiceTicket = (
    ticket
) => {

    if (!ticket) {
        return null;
    }


    const customer =
        ticket.customer ||
        ticket.customer_details ||
        {};


    const machine =
        ticket.machine ||
        ticket.machine_details ||
        {};


    const engineer =
        ticket.engineer ||
        ticket.assigned_engineer ||
        ticket.engineer_details ||
        {};


    const customerName =
        typeof customer === "string"
            ? customer
            : (
                customer.customer_name ||
                customer.name ||
                ticket.customer_name ||
                "-"
            );


    const phone =
        typeof customer === "string"
            ? (
                ticket.phone ||
                "-"
            )
            : (
                customer.phone ||
                customer.mobile ||
                customer.mobile_number ||
                ticket.phone ||
                "-"
            );


    const email =
        typeof customer === "string"
            ? (
                ticket.email ||
                "-"
            )
            : (
                customer.email ||
                ticket.email ||
                "-"
            );


    const address =
        typeof customer === "string"
            ? (
                ticket.address ||
                "-"
            )
            : (
                customer.shipping_address ||
                customer.billing_address ||
                customer.address ||
                ticket.address ||
                "-"
            );


    const product =
        typeof machine === "string"
            ? machine
            : (
                machine.product_name ||
                machine.machine_name ||
                machine.model_name ||
                machine.machine_number ||
                ticket.product_name ||
                ticket.machine_name ||
                ticket.product ||
                "-"
            );


    const technician =
        typeof engineer === "string"
            ? engineer
            : (
                engineer.full_name ||
                engineer.name ||
                engineer.username ||
                ticket.engineer_name ||
                ticket.technician ||
                "-"
            );


    const serviceDate =
        ticket.service_date ||
        ticket.reported_date ||
        ticket.created_at ||
        ticket.expected_visit_date ||
        "-";


    const formattedDate =
        serviceDate &&
        serviceDate !== "-"
            ? String(serviceDate).slice(0, 10)
            : "-";


    // -----------------------------------------------------
    // SERVICE AMOUNT
    // -----------------------------------------------------
    // Different service-ticket responses can expose the
    // service cost under different field names. The table
    // already displays the amount, so the dashboard must use
    // the same source instead of depending only on
    // ticket.total_amount.
    //
    // Priority:
    //   total_amount
    //   service_amount
    //   service_cost
    //   serviceCost
    //   amount
    //   payment amount fields
    // -----------------------------------------------------
    const amountCandidates = [
        ticket.total_amount,
        ticket.service_amount,
        ticket.service_cost,
        ticket.serviceCost,
        ticket.amount,
        ticket.payment?.total_amount,
        ticket.payment?.amount,
        ticket.payment_details?.total_amount,
        ticket.payment_details?.amount,
    ];

    const totalAmount =
        amountCandidates.reduce(
            (result, candidate) => {
                if (result !== null) {
                    return result;
                }

                if (
                    candidate !== null &&
                    candidate !== undefined &&
                    String(candidate).trim() !== ""
                ) {
                    const numericValue =
                        Number(
                            String(candidate)
                                .replace(/[₹,\s]/g, "")
                                .trim()
                        );

                    if (
                        Number.isFinite(numericValue) &&
                        numericValue > 0
                    ) {
                        return numericValue;
                    }
                }

                return null;
            },
            null
        ) ?? 0;


    return {

        ...ticket,

        // ---------------------------------------------
        // ID
        // ---------------------------------------------

        id:
            ticket.id ??
            ticket.ticket_id,


        // ---------------------------------------------
        // Ticket
        // ---------------------------------------------

        ticket_number:
            ticket.ticket_number ||
            "-",

        
        // ---------------------------------------------
        // Customer
        // ---------------------------------------------

        customer:
            customerName,

        phone,

        email,

        address,


        // ---------------------------------------------
        // Product
        // ---------------------------------------------

        product,


        // ---------------------------------------------
        // Issue
        // ---------------------------------------------

        issue:
            ticket.complaint ||
            ticket.subject ||
            ticket.problem_description ||
            "-",

        
        // ---------------------------------------------
        // Description
        // ---------------------------------------------

        description:
            ticket.problem_description ||
            ticket.complaint ||
            "-",

        
        // ---------------------------------------------
        // Technician
        // ---------------------------------------------

        technician,


        // ---------------------------------------------
        // Priority
        // ---------------------------------------------

        priority:
            String(
                ticket.priority ||
                "MEDIUM"
            )
                .trim()
                .toUpperCase()
                .replace(/[\s-]+/g, "_"),


        // ---------------------------------------------
        // Status
        // ---------------------------------------------

        status:
            String(
                ticket.status ||
                "REQUESTED"
            )
                .trim()
                .toUpperCase()
                .replace(/[\s-]+/g, "_"),


        // ---------------------------------------------
        // Date
        // ---------------------------------------------

        service_date:
            formattedDate,


        // ---------------------------------------------
        // Amount
        // ---------------------------------------------

        total_amount:
            Number(totalAmount || 0),

        // ---------------------------------------------
        // Payment
        // ---------------------------------------------
        // Preserve the backend payment fields instead of dropping them
        // while mapping the service ticket for the ServiceTable.
        payment_status:
            ticket.payment_status ??
            ticket.payment?.payment_status ??
            ticket.payment?.status ??
            ticket.payment_details?.payment_status ??
            ticket.payment_details?.status ??
            "PENDING",

        payment:
            ticket.payment ??
            ticket.payment_details ??
            null,

        payment_details:
            ticket.payment_details ??
            ticket.payment ??
            null,

        // Keep service-cost/material fields available to both the
        // admin ServiceTable and the edit/detail views.
        material_used:
            ticket.material_used ??
            ticket.materialUsed ??
            null,

        service_cost:
            ticket.service_cost ??
            ticket.serviceCost ??
            null,

        completion_date:
            ticket.completion_date ??
            ticket.completed_date ??
            ticket.completed_at ??
            null,

        completed_date:
            ticket.completed_date ??
            ticket.completion_date ??
            ticket.completed_at ??
            null,

    };
};


// =====================================================
// PROVIDER
// =====================================================

export const ServiceProvider = ({
    children,
}) => {


    // =================================================
    // SERVICES
    // =================================================

    const [
        services,
        setServices,
    ] = useState([]);


    // =================================================
    // LOADING
    // =================================================

    const [
        loading,
        setLoading,
    ] = useState(false);


    // =================================================
    // ERROR
    // =================================================

    const [
        error,
        setError,
    ] = useState("");


    // =================================================
    // SERVER TOTAL
    // =================================================

    const [
        total,
        setTotal,
    ] = useState(0);


    // =================================================
    // FILTERS
    // =================================================

    const [
        search,
        setSearch,
    ] = useState("");


    const [
        statusFilter,
        setStatusFilter,
    ] = useState("");


    const [
        priorityFilter,
        setPriorityFilter,
    ] = useState("");


    // Date filters
    const [
        dateFrom,
        setDateFrom,
    ] = useState("");


    const [
        dateTo,
        setDateTo,
    ] = useState("");


    // =================================================
    // DRAWER
    // =================================================

    const [
        drawerOpen,
        setDrawerOpen,
    ] = useState(false);


    const [
        drawerMode,
        setDrawerMode,
    ] = useState("add");


    // =================================================
    // SELECTED SERVICE
    // =================================================

    const [
        selectedService,
        setSelectedService,
    ] = useState(null);


    // =================================================
    // DETAILS
    // =================================================

    const [
        detailsOpen,
        setDetailsOpen,
    ] = useState(false);


    // =================================================
    // DELETE MODAL
    // =================================================

    const [
        deleteModalOpen,
        setDeleteModalOpen,
    ] = useState(false);


    const [
        serviceToDelete,
        setServiceToDelete,
    ] = useState(null);


    // =================================================
    // POLLING REF
    // =================================================

    const refreshInProgress =
        useRef(false);


    // =================================================
    // LOAD SERVICES
    // =================================================

    const loadServices = useCallback(
        async ({
            silent = false,
        } = {}) => {

            // -----------------------------------------
            // Prevent overlapping requests
            // -----------------------------------------

            if (
                refreshInProgress.current
            ) {
                return;
            }


            refreshInProgress.current =
                true;


            if (!silent) {
                setLoading(true);
            }


            setError("");


            try {

                // -------------------------------------
                // Load ALL tickets for the table
                // -------------------------------------
                //
                // page_size is 100 because your backend
                // allows a maximum of 100.
                //
                // This ensures the dashboard calculations
                // have all currently loaded tickets.
                // -------------------------------------

                const response =
                    await api.get(
                        "/service-tickets/",
                        {
                            params: {
                                page: 1,
                                page_size: 100,
                            },
                        }
                    );


                const data =
                    response?.data || {};


                const items =
                    Array.isArray(
                        data?.items
                    )
                        ? data.items
                        : [];


                const mapped =
                    items
                        .map(
                            mapServiceTicket
                        )
                        .filter(Boolean);


                setServices(
                    mapped
                );


                setTotal(
                    Number(
                        data?.total ??
                        mapped.length
                    )
                );


            } catch (err) {

                console.error(
                    "Failed to load service tickets:",
                    err
                );


                setError(
                    err?.message ||
                    "Failed to load service tickets."
                );


            } finally {

                refreshInProgress.current =
                    false;


                if (!silent) {
                    setLoading(false);
                }

            }

        },
        []
    );


    // =================================================
    // INITIAL LOAD
    // =================================================

    useEffect(() => {

        loadServices();

    }, [
        loadServices,
    ]);


    // =================================================
    // AUTOMATIC REFRESH
    // =================================================
    //
    // Customer creates ticket
    //      ↓
    // Database
    //      ↓
    // Admin ServiceContext
    //      ↓
    // Every 5 seconds
    //      ↓
    // New ticket appears
    //
    // =================================================

    useEffect(() => {

        const interval =
            setInterval(
                () => {

                    loadServices({
                        silent: true,
                    });

                },
                5000
            );


        return () => {

            clearInterval(
                interval
            );

        };

    }, [
        loadServices,
    ]);


    // =================================================
    // FILTER SERVICES
    // =================================================

    const filteredServices =
        useMemo(
            () => {

                const normalizeText = (value) =>
                    String(value ?? "")
                        .trim()
                        .toLowerCase();

                const normalizeStatus = (value) =>
                    String(value ?? "")
                        .trim()
                        .toUpperCase()
                        .replace(/[\s-]+/g, "_");

                const normalizePriority = (value) =>
                    String(value ?? "")
                        .trim()
                        .toUpperCase()
                        .replace(/[\s-]+/g, "_");

                const normalizeDate = (value) => {
                    if (!value) return "";

                    const text = String(value).trim();

                    const isoMatch = text.match(/^(\d{4}-\d{2}-\d{2})/);
                    if (isoMatch) return isoMatch[1];

                    const dmyMatch = text.match(
                        /^(\d{2})[-\/](\d{2})[-\/](\d{4})$/
                    );

                    if (dmyMatch) {
                        return `${dmyMatch[3]}-${dmyMatch[2]}-${dmyMatch[1]}`;
                    }

                    const parsed = new Date(value);

                    if (Number.isNaN(parsed.getTime())) return "";

                    const year = parsed.getFullYear();
                    const month = String(parsed.getMonth() + 1).padStart(2, "0");
                    const day = String(parsed.getDate()).padStart(2, "0");

                    return `${year}-${month}-${day}`;
                };

                const getServiceDate = (service) =>
                    normalizeDate(
                        service?.service_date ||
                        service?.completed_date ||
                        service?.completion_date ||
                        service?.reported_date ||
                        service?.created_at ||
                        service?.expected_visit_date ||
                        service?.date
                    );

                const normalizedStatusFilter =
                    normalizeStatus(statusFilter);

                const normalizedPriorityFilter =
                    normalizePriority(priorityFilter);

                const normalizedDateFrom =
                    normalizeDate(dateFrom);

                const normalizedDateTo =
                    normalizeDate(dateTo);

                const searchValue =
                    normalizeText(search);

                return (services || []).filter((service) => {

                    // ---------------------------------
                    // SEARCH
                    // ---------------------------------

                    const searchText = [
                        service?.ticket_number,
                        service?.ticket_no,
                        service?.service_ticket_number,
                        service?.customer,
                        service?.customer_name,
                        service?.phone,
                        service?.mobile,
                        service?.mobile_number,
                        service?.product,
                        service?.product_name,
                        service?.machine_name,
                        service?.machine_number,
                        service?.issue,
                        service?.complaint,
                        service?.subject,
                        service?.problem_description,
                        service?.technician,
                        service?.engineer_name,
                        service?.serial_number,
                        service?.email,
                    ]
                        .map(normalizeText)
                        .join(" ");

                    const matchesSearch =
                        !searchValue ||
                        searchText.includes(searchValue);

                    // ---------------------------------
                    // STATUS
                    // ---------------------------------

                    const serviceStatus =
                        normalizeStatus(service?.status);

                    let matchesStatus = true;

                    if (normalizedStatusFilter) {
                        if (normalizedStatusFilter === "OPEN") {
                            matchesStatus = [
                                "OPEN",
                                "REQUESTED",
                                "CONFIRMED",
                                "REACHED",
                            ].includes(serviceStatus);
                        } else if (normalizedStatusFilter === "PENDING") {
                            matchesStatus = [
                                "PENDING",
                                "WAITING_FOR_PARTS",
                                "PARTS_PENDING",
                                "ON_HOLD",
                            ].includes(serviceStatus);
                        } else if (normalizedStatusFilter === "COMPLETED") {
                            matchesStatus = [
                                "COMPLETED",
                                "CLOSED",
                            ].includes(serviceStatus);
                        } else {
                            matchesStatus =
                                serviceStatus === normalizedStatusFilter;
                        }
                    }

                    // ---------------------------------
                    // PRIORITY
                    // ---------------------------------

                    const servicePriority =
                        normalizePriority(service?.priority);

                    const matchesPriority =
                        !normalizedPriorityFilter ||
                        servicePriority === normalizedPriorityFilter;

                    // ---------------------------------
                    // DATE RANGE
                    // ---------------------------------

                    const serviceDate =
                        getServiceDate(service);

                    let matchesDate = true;

                    if (normalizedDateFrom || normalizedDateTo) {
                        if (!serviceDate) {
                            matchesDate = false;
                        } else {
                            if (
                                normalizedDateFrom &&
                                serviceDate < normalizedDateFrom
                            ) {
                                matchesDate = false;
                            }

                            if (
                                normalizedDateTo &&
                                serviceDate > normalizedDateTo
                            ) {
                                matchesDate = false;
                            }
                        }
                    }

                    return (
                        matchesSearch &&
                        matchesStatus &&
                        matchesPriority &&
                        matchesDate
                    );
                });
            },
            [
                services,
                search,
                statusFilter,
                priorityFilter,
                dateFrom,
                dateTo,
            ]
        );


    // =================================================
    // DASHBOARD
    // =================================================

    const dashboard =
        useMemo(
            () => {

                // -------------------------------------
                // TOTAL
                // -------------------------------------

                const totalTickets =
                    total ||
                    services.length;


                // -------------------------------------
                // OPEN
                // -------------------------------------
                //
                // Customer portal creates REQUESTED.
                // REQUESTED is treated as open.
                // -------------------------------------

                const openTickets =
                    services.filter(
                        (service) => {
                            const status =
                                String(
                                    service?.status ||
                                    ""
                                )
                                    .trim()
                                    .toUpperCase()
                                    .replace(
                                        /[\s-]+/g,
                                        "_"
                                    );

                            return [
                                "OPEN",
                                "REQUESTED",
                                "CONFIRMED",
                                "REACHED",
                            ].includes(status);
                        }
                    ).length;


                // -------------------------------------
                // IN PROGRESS
                // -------------------------------------

                const inProgressTickets =
                    services.filter(
                        (service) => {
                            const status =
                                String(
                                    service?.status ||
                                    ""
                                )
                                    .trim()
                                    .toUpperCase()
                                    .replace(
                                        /[\s-]+/g,
                                        "_"
                                    );

                            return (
                                status ===
                                "IN_PROGRESS"
                            );
                        }
                    ).length;


                // -------------------------------------
                // COMPLETED
                // -------------------------------------

                const completedServices =
                    services.filter(
                        (service) => {
                            const status =
                                String(
                                    service?.status ||
                                    ""
                                )
                                    .trim()
                                    .toUpperCase()
                                    .replace(
                                        /[\s-]+/g,
                                        "_"
                                    );

                            return (
                                status ===
                                    "COMPLETED" ||
                                status ===
                                    "CLOSED"
                            );
                        }
                    );

                const completedTickets =
                    completedServices.length;


                // -------------------------------------
                // COMPLETED THIS MONTH
                // -------------------------------------
                //
                // Use completion_date first because this
                // represents when the service was actually
                // completed.
                //
                // If the backend does not provide a
                // completion date, fall back to service_date,
                // reported_date, created_at, or expected date.
                // -------------------------------------

                const now =
                    new Date();

                const currentYear =
                    now.getFullYear();

                const currentMonth =
                    now.getMonth();

                const getDashboardServiceDate =
                    (service) => {

                        const value =
                            service?.completion_date ||
                            service?.completed_date ||
                            service?.completed_at ||
                            service?.service_date ||
                            service?.reported_date ||
                            service?.created_at ||
                            service?.expected_visit_date ||
                            service?.date ||
                            "";

                        if (!value) {
                            return null;
                        }

                        const text =
                            String(value)
                                .trim();

                        // YYYY-MM-DD / ISO
                        const isoMatch =
                            text.match(
                                /^(\d{4})-(\d{2})-(\d{2})/
                            );

                        if (isoMatch) {
                            const year =
                                Number(
                                    isoMatch[1]
                                );

                            const month =
                                Number(
                                    isoMatch[2]
                                ) - 1;

                            const day =
                                Number(
                                    isoMatch[3]
                                );

                            return new Date(
                                year,
                                month,
                                day
                            );
                        }

                        // DD-MM-YYYY or DD/MM/YYYY
                        const dmyMatch =
                            text.match(
                                /^(\d{2})[-\/](\d{2})[-\/](\d{4})/
                            );

                        if (dmyMatch) {
                            const day =
                                Number(
                                    dmyMatch[1]
                                );

                            const month =
                                Number(
                                    dmyMatch[2]
                                ) - 1;

                            const year =
                                Number(
                                    dmyMatch[3]
                                );

                            return new Date(
                                year,
                                month,
                                day
                            );
                        }

                        const parsed =
                            new Date(value);

                        if (
                            Number.isNaN(
                                parsed.getTime()
                            )
                        ) {
                            return null;
                        }

                        return parsed;
                    };

                const monthlyCompletedTickets =
                    completedServices.filter(
                        (service) => {

                            const date =
                                getDashboardServiceDate(
                                    service
                                );

                            if (!date) {
                                return false;
                            }

                            return (
                                date.getFullYear() ===
                                    currentYear &&
                                date.getMonth() ===
                                    currentMonth
                            );
                        }
                    ).length;


                // -------------------------------------
                // PENDING
                // -------------------------------------

                const pendingTickets =
                    services.filter(
                        (service) => {
                            const status =
                                String(
                                    service?.status ||
                                    ""
                                )
                                    .trim()
                                    .toUpperCase()
                                    .replace(
                                        /[\s-]+/g,
                                        "_"
                                    );

                            return [
                                "PENDING",
                                "WAITING_FOR_PARTS",
                                "PARTS_PENDING",
                                "ON_HOLD",
                            ].includes(status);
                        }
                    ).length;


                // -------------------------------------
                // TOTAL SERVICE VALUE
                // -------------------------------------
                //
                // IMPORTANT:
                // The ServiceTable can receive the amount
                // through service_cost/service_amount/etc.
                // The old dashboard only summed total_amount,
                // which caused the card to show ₹0.
                //
                // Use the same normalized amount source as
                // the mapped service record.
                // -------------------------------------

                const getServiceAmount =
                    (service) => {

                        const candidates = [
                            service?.total_amount,
                            service?.service_amount,
                            service?.service_cost,
                            service?.serviceCost,
                            service?.amount,
                            service?.payment?.total_amount,
                            service?.payment?.amount,
                            service?.payment_details?.total_amount,
                            service?.payment_details?.amount,
                        ];

                        for (
                            const candidate
                            of candidates
                        ) {
                            if (
                                candidate ===
                                    null ||
                                candidate ===
                                    undefined ||
                                String(
                                    candidate
                                ).trim() === ""
                            ) {
                                continue;
                            }

                            const numericValue =
                                Number(
                                    String(candidate)
                                        .replace(
                                            /[₹,\s]/g,
                                            ""
                                        )
                                        .trim()
                                );

                            if (
                                Number.isFinite(
                                    numericValue
                                ) &&
                                numericValue > 0
                            ) {
                                return numericValue;
                            }
                        }

                        return 0;
                    };

                const totalServiceValue =
                    services.reduce(
                        (
                            sum,
                            service
                        ) =>
                            sum +
                            getServiceAmount(
                                service
                            ),
                        0
                    );


                return {

                    totalTickets,

                    openTickets,

                    inProgressTickets,

                    completedTickets,

                    monthlyCompletedTickets,

                    pendingTickets,

                    totalServiceValue,

                };

            },
            [
                services,
                total,
            ]
        );


    // =================================================
    // RESET FILTERS
    // =================================================

    const resetFilters =
        useCallback(
            () => {

                setSearch("");

                setStatusFilter("");

                setPriorityFilter("");

                setDateFrom("");

                setDateTo("");

            },
            []
        );


    // =================================================
    // MANUAL REFRESH
    // =================================================

    const refreshServices =
        useCallback(
            async () => {

                resetFilters();

                await loadServices();

            },
            [
                resetFilters,
                loadServices,
            ]
        );


    // =================================================
    // OPEN ADD DRAWER
    // =================================================

    const openAddDrawer =
        useCallback(
            () => {

                setSelectedService(
                    null
                );

                setDrawerMode(
                    "add"
                );

                setDrawerOpen(
                    true
                );

            },
            []
        );


    // =================================================
    // OPEN EDIT DRAWER
    // =================================================

    const openEditDrawer =
        useCallback(
            (service) => {

                setSelectedService(
                    service
                );

                setDrawerMode(
                    "edit"
                );

                setDrawerOpen(
                    true
                );

            },
            []
        );


    // =================================================
    // CLOSE DRAWER
    // =================================================

    const closeDrawer =
        useCallback(
            () => {

                setDrawerOpen(
                    false
                );

                setSelectedService(
                    null
                );

            },
            []
        );


    // =================================================
    // SAVE SERVICE
    // =================================================
    //
    // ADD
    //   POST /service-tickets/
    //
    // EDIT
    //   PUT /service-tickets/{id}
    //
    // =====================================================

    const saveService =
        useCallback(
            async (data) => {

                try {

                    setLoading(true);

                    setError("");


                    // ---------------------------------
                    // EDIT
                    // ---------------------------------

                    if (
                        drawerMode ===
                            "edit" &&
                        data?.id
                    ) {

                        const response =
                            await api.put(
                                `/service-tickets/${data.id}`,
                                data
                            );


                        const updated =
                            response?.data;


                        const mapped =
                            mapServiceTicket(
                                updated
                            );


                        setServices(
                            previous =>
                                previous.map(
                                    service =>
                                        service.id ===
                                            data.id
                                            ? mapped
                                            : service
                                )
                        );

                    }


                    // ---------------------------------
                    // CREATE
                    // ---------------------------------

                    else {

                        const response =
                            await api.post(
                                "/service-tickets/",
                                data
                            );


                        const created =
                            response?.data;


                        const mapped =
                            mapServiceTicket(
                                created
                            );


                        setServices(
                            previous => [
                                mapped,
                                ...previous,
                            ]
                        );


                        setTotal(
                            previous =>
                                Number(
                                    previous || 0
                                ) + 1
                        );

                    }


                    closeDrawer();


                    // ---------------------------------
                    // Reload from backend
                    // ---------------------------------

                    await loadServices({
                        silent: true,
                    });


                } catch (err) {

                    console.error(
                        "Save service failed:",
                        err
                    );


                    setError(
                        err?.response?.data?.detail ||
                        err?.response?.data?.message ||
                        err?.message ||
                        "Failed to save service ticket."
                    );


                    throw err;

                } finally {

                    setLoading(false);

                }

            },
            [
                drawerMode,
                closeDrawer,
                loadServices,
            ]
        );


    // =================================================
    // OPEN DETAILS
    // =================================================

    const openDetails =
        useCallback(
            (service) => {

                setSelectedService(
                    service
                );

                setDetailsOpen(
                    true
                );

            },
            []
        );


    // =================================================
    // CLOSE DETAILS
    // =================================================

    const closeDetails =
        useCallback(
            () => {

                setDetailsOpen(
                    false
                );

                setSelectedService(
                    null
                );

            },
            []
        );


    // =================================================
    // CANCEL SERVICE - STATUS ONLY
    // =================================================
    //
    // IMPORTANT:
    // This action NEVER deletes the service ticket.
    //
    // It calls:
    // POST /service-tickets/{id}/cancel
    //
    // The backend keeps the ticket and changes only:
    //     status -> CANCELLED
    //
    // The row is then updated locally and reloaded from the
    // backend so the table always shows the saved status.
    //
    // =================================================

    const cancelService =
        useCallback(
            async (service) => {

                const ticketId =
                    service?.id ??
                    service?.ticket_id ??
                    null;

                if (
                    ticketId === null ||
                    ticketId === undefined ||
                    String(ticketId).trim() === ""
                ) {
                    const message =
                        "Unable to identify the service ticket.";

                    console.error(
                        "Cannot cancel service:",
                        service
                    );

                    setError(message);

                    throw new Error(message);
                }


                const currentStatus =
                    String(
                        service?.status ||
                        ""
                    )
                        .trim()
                        .toUpperCase();


                if (
                    currentStatus ===
                    "CANCELLED"
                ) {
                    return service;
                }


                try {

                    setLoading(true);

                    setError("");


                    console.log(
                        "Cancelling service ticket:",
                        service?.ticket_number ||
                        ticketId
                    );


                    // =================================================
                    // IMPORTANT:
                    // POST /cancel is a STATUS CHANGE.
                    // It is NOT DELETE.
                    // =================================================

                    const response =
                        await api.post(
                            `/service-tickets/${ticketId}/cancel`
                        );


                    const responseTicket =
                        response?.data?.ticket ||
                        response?.data?.data ||
                        (
                            response?.data &&
                            typeof response.data === "object"
                                ? response.data
                                : null
                        );


                    // =================================================
                    // UPDATE THE EXISTING ROW
                    // =================================================

                    setServices(
                        previous =>
                            previous.map(
                                item => {

                                    const itemId =
                                        item?.id ??
                                        item?.ticket_id ??
                                        null;

                                    if (
                                        String(itemId) !==
                                        String(ticketId)
                                    ) {
                                        return item;
                                    }

                                    return {
                                        ...item,
                                        ...(responseTicket || {}),
                                        id:
                                            item?.id ??
                                            responseTicket?.id ??
                                            ticketId,
                                        status:
                                            "CANCELLED",
                                        customer_status:
                                            "CANCELLED",
                                    };
                                }
                            )
                    );


                    // =================================================
                    // RELOAD FROM BACKEND
                    //
                    // This verifies that the database status is
                    // actually saved and prevents stale table data.
                    // =================================================

                    await loadServices({
                        silent: true,
                    });


                    console.log(
                        "Service ticket cancelled successfully:",
                        response?.data
                    );


                    return (
                        responseTicket ||
                        response?.data ||
                        {
                            ...service,
                            status: "CANCELLED",
                            customer_status: "CANCELLED",
                        }
                    );

                } catch (err) {

                    console.error(
                        "Cancel service failed:",
                        err
                    );


                    const message =
                        err?.response?.data?.detail ||
                        err?.response?.data?.message ||
                        err?.message ||
                        "Failed to cancel service ticket.";


                    setError(message);


                    // IMPORTANT:
                    // Re-throw so ServicePage does NOT close the
                    // confirmation modal when the API fails.
                    throw err;

                } finally {

                    setLoading(false);

                }

            },
            [
                loadServices,
            ]
        );


    // =================================================
    // OPEN DELETE MODAL
    // =================================================

    const openDeleteModal =
        useCallback(
            (service) => {

                setServiceToDelete(
                    service
                );

                setDeleteModalOpen(
                    true
                );

            },
            []
        );


    // =================================================
    // CLOSE DELETE MODAL
    // =================================================

    const closeDeleteModal =
        useCallback(
            () => {

                setDeleteModalOpen(
                    false
                );

                setServiceToDelete(
                    null
                );

            },
            []
        );


    // =================================================
    // CONFIRM CANCEL - STATUS ONLY
    // =================================================
    //
    // The backend CANCEL endpoint performs a SOFT CANCEL.
    // The service ticket is kept in the database and its status
    // becomes CANCELLED. Therefore the frontend must update the
    // existing row instead of removing it from the table.
    //
    // =================================================

    const confirmDelete =
        useCallback(
            async () => {

                if (!serviceToDelete?.id) {
                    return;
                }

                try {
                    // Use the single cancel implementation above.
                    // It updates the row and reloads from the backend.
                    const cancelledService =
                        await cancelService(serviceToDelete);

                    // IMPORTANT:
                    // Keep the existing service row. Never remove it from
                    // the services array. The cancellation is a status-only
                    // change: status -> CANCELLED.
                    if (cancelledService) {
                        setServices(
                            previous =>
                                previous.map(
                                    item =>
                                        String(
                                            item?.id ??
                                            item?.ticket_id ??
                                            ""
                                        ) ===
                                        String(
                                            serviceToDelete?.id ??
                                            serviceToDelete?.ticket_id ??
                                            ""
                                        )
                                            ? {
                                                ...item,
                                                ...cancelledService,
                                                status: "CANCELLED",
                                                customer_status:
                                                    "CANCELLED",
                                            }
                                            : item
                                )
                        );
                    }

                    closeDeleteModal();
                } catch (err) {
                    // cancelService already sets the error and rethrows,
                    // so the modal remains open when the request fails.
                    console.error(
                        "Confirm cancel failed:",
                        err
                    );
                }

            },
            [
                serviceToDelete,
                cancelService,
                closeDeleteModal,
            ]
        );


    // =================================================
    // EXPORT SERVICES
    // =================================================

    const exportServices =
        useCallback(
            () => {

                const rows =
                    filteredServices;


                if (!rows.length) {

                    alert(
                        "No service data available to export."
                    );

                    return;
                }


                const headers = [

                    "Ticket Number",

                    "Customer",

                    "Phone",

                    "Email",

                    "Address",

                    "Product",

                    "Issue",

                    "Description",

                    "Technician",

                    "Priority",

                    "Status",

                    "Service Date",

                    "Service Amount",

                    "Payment Status",

                ];


                const csvRows =
                    rows.map(
                        service => [

                            service.ticket_number,

                            service.customer,

                            service.phone,

                            service.email,

                            service.address,

                            service.product,

                            service.issue,

                            service.description,

                            service.technician,

                            service.priority,

                            service.status,

                            service.service_date,

                            service.total_amount,

                            service.payment_status || "PENDING",

                        ]
                    );


                const escapeCsv =
                    (value) => {

                        const text =
                            String(
                                value ?? ""
                            );


                        return `"${text.replace(
                            /"/g,
                            '""'
                        )}"`;

                    };


                const csv = [

                    headers
                        .map(
                            escapeCsv
                        )
                        .join(","),

                    ...csvRows.map(
                        row =>
                            row
                                .map(
                                    escapeCsv
                                )
                                .join(",")
                    ),

                ].join("\n");


                const blob =
                    new Blob(
                        [csv],
                        {
                            type:
                                "text/csv;charset=utf-8;",
                        }
                    );


                const url =
                    URL.createObjectURL(
                        blob
                    );


                const link =
                    document.createElement(
                        "a"
                    );


                link.href =
                    url;


                link.download =
                    `service_export_${new Date()
                        .toISOString()
                        .slice(0, 10)}.csv`;


                document.body.appendChild(
                    link
                );


                link.click();


                document.body.removeChild(
                    link
                );


                URL.revokeObjectURL(
                    url
                );

            },
            [
                filteredServices,
            ]
        );


    // =================================================
    // CONTEXT VALUE
    // =================================================

    const value = {

        // ---------------------------------------------
        // Data
        // ---------------------------------------------

        services,

        filteredServices,

        dashboard,

        loading,

        error,


        // ---------------------------------------------
        // Filters
        // ---------------------------------------------

        search,

        setSearch,

        statusFilter,

        setStatusFilter,

        priorityFilter,

        setPriorityFilter,

        dateFrom,

        setDateFrom,

        dateTo,

        setDateTo,

        resetFilters,


        // ---------------------------------------------
        // Refresh
        // ---------------------------------------------

        refreshServices,

        loadServices,


        // ---------------------------------------------
        // Drawer
        // ---------------------------------------------

        drawerOpen,

        drawerMode,

        selectedService,

        openAddDrawer,

        openEditDrawer,

        closeDrawer,

        saveService,


        // ---------------------------------------------
        // Details
        // ---------------------------------------------

        detailsOpen,

        openDetails,

        closeDetails,


        // ---------------------------------------------
        // Cancel
        // ---------------------------------------------
        cancelService,

        // ---------------------------------------------
        // Delete (legacy modal support)
        // ---------------------------------------------

        deleteModalOpen,

        serviceToDelete,

        openDeleteModal,

        closeDeleteModal,

        confirmDelete,


        // ---------------------------------------------
        // Export
        // ---------------------------------------------

        exportServices,

    };


    // =================================================
    // PROVIDER
    // =================================================

    return (

        <ServiceContext.Provider
            value={value}
        >

            {children}

        </ServiceContext.Provider>

    );

};


// =====================================================
// HOOK
// =====================================================

export const useService = () => {

    const context =
        useContext(
            ServiceContext
        );


    if (!context) {

        throw new Error(
            "useService must be used inside ServiceProvider"
        );

    }


    return context;

};


export default ServiceContext;