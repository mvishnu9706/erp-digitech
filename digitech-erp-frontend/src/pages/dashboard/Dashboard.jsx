import React, {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    Activity,
    AlertTriangle,
    ArrowDownRight,
    ArrowUpRight,
    Boxes,
    CalendarDays,
    CheckCircle2,
    ChevronRight,
    CircleDollarSign,
    ClipboardList,
    Clock3,
    FileText,
    Package,
    Plus,
    RefreshCw,
    ShoppingCart,
    Truck,
    Users,
    WalletCards,
    Wrench,
} from "lucide-react";

import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import api from "../../api/axios";

import Sidebar from "../../components/layout/Sidebar/Sidebar";
import Navbar from "../../components/layout/Navbar/Navbar";

import "./Dashboard.css";


/* ============================================================
   HELPERS
   ============================================================ */

const unwrap = (response) => {
    return response?.data?.data ?? response?.data ?? response ?? {};
};


const toNumber = (value) => {
    const number = Number(value);

    return Number.isFinite(number) ? number : 0;
};


const formatCurrency = (value) => {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2,
    }).format(toNumber(value));
};


const formatNumber = (value) => {
    return new Intl.NumberFormat("en-IN").format(
        toNumber(value)
    );
};


const getValue = (
    object,
    keys,
    fallback = 0
) => {
    if (!object || typeof object !== "object") {
        return fallback;
    }

    for (const key of keys) {
        if (
            object[key] !== undefined &&
            object[key] !== null
        ) {
            return object[key];
        }
    }

    return fallback;
};


const getText = (
    object,
    keys,
    fallback = ""
) => {
    if (!object || typeof object !== "object") {
        return fallback;
    }

    for (const key of keys) {
        if (
            object[key] !== undefined &&
            object[key] !== null &&
            String(object[key]).trim() !== ""
        ) {
            return String(object[key]);
        }
    }

    return fallback;
};


const normalizeStatus = (value) => {
    return String(value || "")
        .trim()
        .toUpperCase()
        .replace(/[\s-]+/g, "_");
};


/* ============================================================
   DASHBOARD
   ============================================================ */

const Dashboard = () => {
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const [sales, setSales] = useState({});
    const [service, setService] = useState({});
    const [inventory, setInventory] = useState({});
    const [purchase, setPurchase] = useState({});
    const [machines, setMachines] = useState({});
    const [rentalBills, setRentalBills] = useState([]);

    const [lastUpdated, setLastUpdated] = useState(null);


    /* ========================================================
       LOAD DASHBOARD
       ======================================================== */

    const loadDashboard = useCallback(
        async (showLoader = true) => {
            try {
                if (showLoader) {
                    setLoading(true);
                } else {
                    setRefreshing(true);
                }

                const results = await Promise.allSettled([
                    api.get(
                        "/sales-orders/dashboard/summary"
                    ),

                    api.get(
                        "/service-tickets/dashboard/summary"
                    ),

                    api.get(
                        "/inventory-transactions/dashboard/summary"
                    ),

                    api.get(
                        "/rental-bills/"
                    ),

                    api.get(
                        "/purchase-orders/dashboard/summary"
                    ),

                    api.get(
                        "/machines/"
                    ),
                ]);


                if (
                    results[0].status === "fulfilled"
                ) {
                    setSales(
                        unwrap(results[0].value)
                    );
                }


                if (
                    results[1].status === "fulfilled"
                ) {
                    setService(
                        unwrap(results[1].value)
                    );
                }


                if (
                    results[2].status === "fulfilled"
                ) {
                    setInventory(
                        unwrap(results[2].value)
                    );
                }


                if (
                    results[3].status === "fulfilled"
                ) {
                    const data =
                        unwrap(results[3].value);

                    if (Array.isArray(data)) {
                        setRentalBills(data);
                    } else if (
                        Array.isArray(data?.items)
                    ) {
                        setRentalBills(data.items);
                    } else if (
                        Array.isArray(data?.results)
                    ) {
                        setRentalBills(data.results);
                    } else {
                        setRentalBills([]);
                    }
                }


                if (
                    results[4].status === "fulfilled"
                ) {
                    setPurchase(
                        unwrap(results[4].value)
                    );
                }


                if (
                    results[5].status === "fulfilled"
                ) {
                    const data =
                        unwrap(results[5].value);

                    if (Array.isArray(data)) {
                        setMachines({
                            total: data.length,
                            items: data,
                        });
                    } else {
                        setMachines(data);
                    }
                }


                setLastUpdated(new Date());


                const failed =
                    results.filter(
                        (result) =>
                            result.status === "rejected"
                    );


                if (
                    failed.length === results.length
                ) {
                    toast.error(
                        "Unable to load dashboard data."
                    );
                }
            } catch (error) {
                console.error(
                    "Dashboard error:",
                    error
                );

                toast.error(
                    "Failed to load dashboard."
                );
            } finally {
                setLoading(false);
                setRefreshing(false);
            }
        },
        []
    );


    /* ========================================================
       INITIAL LOAD + AUTO REFRESH
       ======================================================== */

    useEffect(() => {
        loadDashboard(true);

        const interval = setInterval(() => {
            loadDashboard(false);
        }, 60000);

        return () => {
            clearInterval(interval);
        };
    }, [loadDashboard]);


    /* ========================================================
       SALES
       ======================================================== */

    const salesToday = useMemo(() => {
        return getValue(
            sales,
            [
                "today_sales",
                "today_total",
                "sales_today",
                "today_revenue",
                "daily_sales",
            ]
        );
    }, [sales]);


    const monthlySales = useMemo(() => {
        return getValue(
            sales,
            [
                "monthly_sales",
                "month_sales",
                "monthly_revenue",
                "month_revenue",
                "total_month_sales",
            ]
        );
    }, [sales]);


    const pendingReceivables = useMemo(() => {
        return getValue(
            sales,
            [
                "pending_receivables",
                "pending_amount",
                "receivable_amount",
                "outstanding_amount",
                "total_receivable",
            ]
        );
    }, [sales]);


    /* ========================================================
       SERVICE
       ======================================================== */

    const totalServiceTickets = useMemo(() => {
        return getValue(
            service,
            [
                "total_tickets",
                "total",
                "ticket_count",
                "total_services",
            ]
        );
    }, [service]);


    const openServiceTickets = useMemo(() => {
        return getValue(
            service,
            [
                "open_tickets",
                "open",
                "open_count",
            ]
        );
    }, [service]);


    const assignedServiceTickets = useMemo(() => {
        return getValue(
            service,
            [
                "assigned_tickets",
                "assigned",
                "assigned_count",
            ]
        );
    }, [service]);


    const inProgressServiceTickets =
        useMemo(() => {
            return getValue(
                service,
                [
                    "in_progress",
                    "in_progress_tickets",
                    "in_progress_count",
                ]
            );
        }, [service]);


    const completedServiceTickets =
        useMemo(() => {
            return getValue(
                service,
                [
                    "completed_tickets",
                    "completed",
                    "completed_count",
                ]
            );
        }, [service]);


    const monthlyCompletedServices =
        useMemo(() => {
            return getValue(
                service,
                [
                    "monthly_completed",
                    "completed_this_month",
                    "monthly_completed_tickets",
                ]
            );
        }, [service]);


    /* ========================================================
       INVENTORY
       ======================================================== */

    const totalInventoryItems = useMemo(() => {
        return getValue(
            inventory,
            [
                "total_items",
                "total_products",
                "product_count",
                "total",
            ]
        );
    }, [inventory]);


    const lowStockItems = useMemo(() => {
        return getValue(
            inventory,
            [
                "low_stock_items",
                "low_stock",
                "low_stock_count",
                "low_stock_products",
            ]
        );
    }, [inventory]);


    const inventoryValue = useMemo(() => {
        return getValue(
            inventory,
            [
                "inventory_value",
                "stock_value",
                "total_stock_value",
            ]
        );
    }, [inventory]);


    /* ========================================================
       PURCHASE
       ======================================================== */

    const purchaseMonth = useMemo(() => {
        return getValue(
            purchase,
            [
                "monthly_purchase",
                "month_purchase",
                "monthly_total",
                "purchase_this_month",
                "total_month_purchase",
            ]
        );
    }, [purchase]);


    const pendingPurchase = useMemo(() => {
        return getValue(
            purchase,
            [
                "pending_purchase",
                "pending_amount",
                "pending",
                "outstanding_amount",
            ]
        );
    }, [purchase]);


    /* ========================================================
       RENTAL
       ======================================================== */

    const rentalTotal = rentalBills.length;


    const rentalPaid = rentalBills.filter(
        (bill) => {
            const status =
                normalizeStatus(
                    getText(
                        bill,
                        [
                            "payment_status",
                            "status",
                        ]
                    )
                );

            return (
                status === "PAID" ||
                status === "COMPLETED"
            );
        }
    ).length;


    const rentalPending =
        rentalBills.filter(
            (bill) => {
                const status =
                    normalizeStatus(
                        getText(
                            bill,
                            [
                                "payment_status",
                                "status",
                            ]
                        )
                    );

                return (
                    status === "PENDING" ||
                    status === "UNPAID" ||
                    status === "PARTIALLY_PAID"
                );
            }
        ).length;


    const rentalAmount =
        rentalBills.reduce(
            (total, bill) => {
                return (
                    total +
                    toNumber(
                        getValue(
                            bill,
                            [
                                "total_amount",
                                "amount",
                                "grand_total",
                                "bill_amount",
                                "payable_amount",
                            ]
                        )
                    )
                );
            },
            0
        );


    const pendingRentalAmount =
        rentalBills
            .filter((bill) => {
                const status =
                    normalizeStatus(
                        getText(
                            bill,
                            [
                                "payment_status",
                                "status",
                            ]
                        )
                    );

                return (
                    status === "PENDING" ||
                    status === "UNPAID" ||
                    status === "PARTIALLY_PAID"
                );
            })
            .reduce(
                (total, bill) => {
                    return (
                        total +
                        toNumber(
                            getValue(
                                bill,
                                [
                                    "total_amount",
                                    "amount",
                                    "grand_total",
                                    "bill_amount",
                                    "payable_amount",
                                ]
                            )
                        )
                    );
                },
                0
            );


    /* ========================================================
       MACHINES
       ======================================================== */

    const totalMachines = useMemo(() => {
        return getValue(
            machines,
            [
                "total",
                "total_machines",
                "machine_count",
            ]
        );
    }, [machines]);


    /* ========================================================
       NAVIGATION
       ======================================================== */

    const goTo = (path) => {
        navigate(path);
    };


    /* ========================================================
       LOADING
       ======================================================== */

    if (loading) {
        return (
            <div className="dashboard-layout">
                <Sidebar />

                <main className="dashboard-main">
                    <Navbar />

                    <div className="dashboard-loading">
                        <div className="dashboard-spinner">
                            <RefreshCw
                                size={30}
                                className="spin"
                            />
                        </div>

                        <h3>
                            Loading Dashboard
                        </h3>

                        <p>
                            Please wait while your
                            ERP data is loading.
                        </p>
                    </div>
                </main>
            </div>
        );
    }


    /* ========================================================
       RENDER
       ======================================================== */

    return (
        <div className="dashboard-layout">

            <Sidebar />


            <main className="dashboard-main">

                <Navbar />


                <div className="dashboard-content">

                    {/* ==================================================
                        HEADER
                    ================================================== */}

                    <div className="dashboard-header">

                        <div className="dashboard-title-row">

                            <div className="dashboard-title-icon">
                                <Activity size={22} />
                            </div>

                            <div>
                                <h1>
                                    Dashboard
                                </h1>

                                <p>
                                    Business overview
                                    and daily activity
                                </p>
                            </div>

                        </div>


                        <div className="dashboard-header-actions">

                            {lastUpdated && (
                                <div className="last-updated">
                                    <Clock3 size={14} />

                                    <span>
                                        Updated{" "}
                                        {lastUpdated.toLocaleTimeString(
                                            "en-IN",
                                            {
                                                hour: "2-digit",
                                                minute: "2-digit",
                                            }
                                        )}
                                    </span>
                                </div>
                            )}


                            <button
                                type="button"
                                className="refresh-button"
                                onClick={() =>
                                    loadDashboard(false)
                                }
                                disabled={refreshing}
                            >
                                <RefreshCw
                                    size={16}
                                    className={
                                        refreshing
                                            ? "spin"
                                            : ""
                                    }
                                />

                                Refresh
                            </button>

                        </div>

                    </div>


                    {/* ==================================================
                        KPI CARDS
                    ================================================== */}

                    <section className="dashboard-kpi-grid">

                        <div
                            className="dashboard-kpi-card sales-card"
                            onClick={() =>
                                goTo("/sales")
                            }
                        >
                            <div className="kpi-card-top">
                                <div className="kpi-icon">
                                    <CircleDollarSign
                                        size={21}
                                    />
                                </div>

                                <span className="kpi-label">
                                    Today's Sales
                                </span>
                            </div>

                            <div className="kpi-value">
                                {formatCurrency(
                                    salesToday
                                )}
                            </div>

                            <div className="kpi-footer">
                                <ArrowUpRight size={15} />
                                Sales activity today
                            </div>
                        </div>


                        <div
                            className="dashboard-kpi-card revenue-card"
                            onClick={() =>
                                goTo("/sales")
                            }
                        >
                            <div className="kpi-card-top">
                                <div className="kpi-icon">
                                    <WalletCards
                                        size={21}
                                    />
                                </div>

                                <span className="kpi-label">
                                    Monthly Revenue
                                </span>
                            </div>

                            <div className="kpi-value">
                                {formatCurrency(
                                    monthlySales
                                )}
                            </div>

                            <div className="kpi-footer">
                                <CalendarDays size={15} />
                                Current month
                            </div>
                        </div>


                        <div
                            className="dashboard-kpi-card receivable-card"
                            onClick={() =>
                                goTo("/sales")
                            }
                        >
                            <div className="kpi-card-top">
                                <div className="kpi-icon">
                                    <WalletCards
                                        size={21}
                                    />
                                </div>

                                <span className="kpi-label">
                                    Receivables
                                </span>
                            </div>

                            <div className="kpi-value">
                                {formatCurrency(
                                    pendingReceivables
                                )}
                            </div>

                            <div className="kpi-footer">
                                <ArrowDownRight size={15} />
                                Pending collection
                            </div>
                        </div>


                        <div
                            className="dashboard-kpi-card service-card"
                            onClick={() =>
                                goTo("/service")
                            }
                        >
                            <div className="kpi-card-top">
                                <div className="kpi-icon">
                                    <Wrench size={21} />
                                </div>

                                <span className="kpi-label">
                                    Open Service
                                </span>
                            </div>

                            <div className="kpi-value">
                                {formatNumber(
                                    openServiceTickets
                                )}
                            </div>

                            <div className="kpi-footer">
                                <ClipboardList size={15} />
                                Service tickets
                            </div>
                        </div>


                        <div
                            className="dashboard-kpi-card stock-card"
                            onClick={() =>
                                goTo("/inventory")
                            }
                        >
                            <div className="kpi-card-top">
                                <div className="kpi-icon">
                                    <AlertTriangle
                                        size={21}
                                    />
                                </div>

                                <span className="kpi-label">
                                    Low Stock
                                </span>
                            </div>

                            <div className="kpi-value">
                                {formatNumber(
                                    lowStockItems
                                )}
                            </div>

                            <div className="kpi-footer">
                                <Boxes size={15} />
                                Items need attention
                            </div>
                        </div>


                        <div
                            className="dashboard-kpi-card rental-card"
                            onClick={() =>
                                goTo("/rental")
                            }
                        >
                            <div className="kpi-card-top">
                                <div className="kpi-icon">
                                    <Package size={21} />
                                </div>

                                <span className="kpi-label">
                                    Rental Bills
                                </span>
                            </div>

                            <div className="kpi-value">
                                {formatNumber(
                                    rentalTotal
                                )}
                            </div>

                            <div className="kpi-footer">
                                <FileText size={15} />
                                Rental / AMC
                            </div>
                        </div>

                    </section>


                    {/* ==================================================
                        MAIN PANELS
                    ================================================== */}

                    <section className="dashboard-main-grid">

                        {/* SALES / PURCHASE */}

                        <div className="dashboard-panel">

                            <div className="panel-header">

                                <div>
                                    <h2>
                                        Sales & Purchase
                                    </h2>

                                    <p>
                                        Current month
                                        financial overview
                                    </p>
                                </div>

                                <div className="panel-header-icon">
                                    <CircleDollarSign
                                        size={20}
                                    />
                                </div>

                            </div>


                            <div className="finance-overview">

                                <div className="finance-row">

                                    <div className="finance-row-left">

                                        <div className="finance-small-icon sales">
                                            <ArrowUpRight
                                                size={16}
                                            />
                                        </div>

                                        <div>
                                            <span>
                                                Sales
                                            </span>

                                            <strong>
                                                {formatCurrency(
                                                    monthlySales
                                                )}
                                            </strong>
                                        </div>

                                    </div>

                                    <span className="finance-row-right positive">
                                        Revenue
                                    </span>

                                </div>


                                <div className="finance-divider" />


                                <div className="finance-row">

                                    <div className="finance-row-left">

                                        <div className="finance-small-icon purchase">
                                            <ArrowDownRight
                                                size={16}
                                            />
                                        </div>

                                        <div>
                                            <span>
                                                Purchase
                                            </span>

                                            <strong>
                                                {formatCurrency(
                                                    purchaseMonth
                                                )}
                                            </strong>
                                        </div>

                                    </div>

                                    <span className="finance-row-right">
                                        Purchase
                                    </span>

                                </div>


                                <div className="finance-divider" />


                                <div className="finance-row">

                                    <div className="finance-row-left">

                                        <div className="finance-small-icon pending">
                                            <Clock3
                                                size={16}
                                            />
                                        </div>

                                        <div>
                                            <span>
                                                Pending Purchase
                                            </span>

                                            <strong>
                                                {formatCurrency(
                                                    pendingPurchase
                                                )}
                                            </strong>
                                        </div>

                                    </div>

                                    <span className="finance-row-right warning">
                                        Pending
                                    </span>

                                </div>

                            </div>


                            <button
                                type="button"
                                className="panel-link-button"
                                onClick={() =>
                                    goTo("/sales")
                                }
                            >
                                Open Sales
                                <ChevronRight size={16} />
                            </button>

                        </div>


                        {/* SERVICE */}

                        <div className="dashboard-panel">

                            <div className="panel-header">

                                <div>
                                    <h2>
                                        Service Overview
                                    </h2>

                                    <p>
                                        Current service
                                        ticket status
                                    </p>
                                </div>

                                <div className="panel-header-icon service">
                                    <Wrench size={20} />
                                </div>

                            </div>


                            <div className="service-status-grid">

                                <div className="service-status-box">
                                    <span>Total</span>
                                    <strong>
                                        {formatNumber(
                                            totalServiceTickets
                                        )}
                                    </strong>
                                </div>

                                <div className="service-status-box warning">
                                    <span>Open</span>
                                    <strong>
                                        {formatNumber(
                                            openServiceTickets
                                        )}
                                    </strong>
                                </div>

                                <div className="service-status-box assigned">
                                    <span>Assigned</span>
                                    <strong>
                                        {formatNumber(
                                            assignedServiceTickets
                                        )}
                                    </strong>
                                </div>

                                <div className="service-status-box progress">
                                    <span>In Progress</span>
                                    <strong>
                                        {formatNumber(
                                            inProgressServiceTickets
                                        )}
                                    </strong>
                                </div>

                                <div className="service-status-box completed">
                                    <span>Completed</span>
                                    <strong>
                                        {formatNumber(
                                            completedServiceTickets
                                        )}
                                    </strong>
                                </div>

                                <div className="service-status-box monthly">
                                    <span>This Month</span>
                                    <strong>
                                        {formatNumber(
                                            monthlyCompletedServices
                                        )}
                                    </strong>
                                </div>

                            </div>


                            <button
                                type="button"
                                className="panel-link-button"
                                onClick={() =>
                                    goTo("/service")
                                }
                            >
                                Open Service
                                <ChevronRight size={16} />
                            </button>

                        </div>


                        {/* RENTAL */}

                        <div className="dashboard-panel">

                            <div className="panel-header">

                                <div>
                                    <h2>
                                        Rental / AMC
                                    </h2>

                                    <p>
                                        Rental billing
                                        overview
                                    </p>
                                </div>

                                <div className="panel-header-icon rental">
                                    <Package size={20} />
                                </div>

                            </div>


                            <div className="rental-summary">

                                <div className="rental-main-amount">
                                    <span>
                                        Total Billing
                                    </span>

                                    <strong>
                                        {formatCurrency(
                                            rentalAmount
                                        )}
                                    </strong>
                                </div>


                                <div className="rental-stat-grid">

                                    <div className="rental-stat">
                                        <span>Bills</span>
                                        <strong>
                                            {formatNumber(
                                                rentalTotal
                                            )}
                                        </strong>
                                    </div>

                                    <div className="rental-stat">
                                        <span>Paid</span>
                                        <strong>
                                            {formatNumber(
                                                rentalPaid
                                            )}
                                        </strong>
                                    </div>

                                    <div className="rental-stat">
                                        <span>Pending</span>
                                        <strong>
                                            {formatNumber(
                                                rentalPending
                                            )}
                                        </strong>
                                    </div>

                                </div>


                                <div className="rental-pending">

                                    <Clock3 size={16} />

                                    <span>
                                        Pending amount
                                    </span>

                                    <strong>
                                        {formatCurrency(
                                            pendingRentalAmount
                                        )}
                                    </strong>

                                </div>

                            </div>


                            <button
                                type="button"
                                className="panel-link-button"
                                onClick={() =>
                                    goTo("/rental")
                                }
                            >
                                Open Rental
                                <ChevronRight size={16} />
                            </button>

                        </div>


                        {/* INVENTORY */}

                        <div className="dashboard-panel">

                            <div className="panel-header">

                                <div>
                                    <h2>
                                        Inventory
                                    </h2>

                                    <p>
                                        Current stock
                                        information
                                    </p>
                                </div>

                                <div className="panel-header-icon inventory">
                                    <Boxes size={20} />
                                </div>

                            </div>


                            <div className="inventory-summary">

                                <div className="inventory-highlight">

                                    <div>
                                        <span>
                                            Inventory Value
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                inventoryValue
                                            )}
                                        </strong>
                                    </div>

                                    <Package size={28} />

                                </div>


                                <div className="inventory-grid">

                                    <div className="inventory-box">
                                        <span>
                                            Products
                                        </span>

                                        <strong>
                                            {formatNumber(
                                                totalInventoryItems
                                            )}
                                        </strong>
                                    </div>

                                    <div className="inventory-box danger">
                                        <span>
                                            Low Stock
                                        </span>

                                        <strong>
                                            {formatNumber(
                                                lowStockItems
                                            )}
                                        </strong>
                                    </div>

                                </div>


                                {toNumber(
                                    lowStockItems
                                ) > 0 && (
                                    <div className="inventory-warning">
                                        <AlertTriangle
                                            size={17}
                                        />

                                        Some products are
                                        below the stock
                                        threshold.
                                    </div>
                                )}

                            </div>


                            <button
                                type="button"
                                className="panel-link-button"
                                onClick={() =>
                                    goTo("/inventory")
                                }
                            >
                                Open Inventory
                                <ChevronRight size={16} />
                            </button>

                        </div>

                    </section>


                    {/* ==================================================
                        BOTTOM SECTION
                    ================================================== */}

                    <section className="dashboard-bottom-grid">

                        {/* ATTENTION */}

                        <div className="dashboard-panel">

                            <div className="panel-header">

                                <div>
                                    <h2>
                                        Needs Your Attention
                                    </h2>

                                    <p>
                                        Items that may
                                        require action
                                    </p>
                                </div>

                                <div className="panel-header-icon warning">
                                    <AlertTriangle
                                        size={20}
                                    />
                                </div>

                            </div>


                            <div className="attention-list">

                                {toNumber(
                                    lowStockItems
                                ) > 0 && (
                                    <button
                                        type="button"
                                        className="attention-item"
                                        onClick={() =>
                                            goTo(
                                                "/inventory"
                                            )
                                        }
                                    >
                                        <div className="attention-icon danger">
                                            <AlertTriangle
                                                size={17}
                                            />
                                        </div>

                                        <div className="attention-content">
                                            <strong>
                                                Low stock
                                            </strong>

                                            <span>
                                                {
                                                    formatNumber(
                                                        lowStockItems
                                                    )
                                                }{" "}
                                                item(s)
                                                need attention
                                            </span>
                                        </div>

                                        <ChevronRight size={17} />
                                    </button>
                                )}


                                {toNumber(
                                    openServiceTickets
                                ) > 0 && (
                                    <button
                                        type="button"
                                        className="attention-item"
                                        onClick={() =>
                                            goTo("/service")
                                        }
                                    >
                                        <div className="attention-icon service">
                                            <Wrench size={17} />
                                        </div>

                                        <div className="attention-content">
                                            <strong>
                                                Open service
                                                tickets
                                            </strong>

                                            <span>
                                                {
                                                    formatNumber(
                                                        openServiceTickets
                                                    )
                                                }{" "}
                                                ticket(s)
                                                waiting
                                            </span>
                                        </div>

                                        <ChevronRight size={17} />
                                    </button>
                                )}


                                {toNumber(
                                    pendingReceivables
                                ) > 0 && (
                                    <button
                                        type="button"
                                        className="attention-item"
                                        onClick={() =>
                                            goTo("/sales")
                                        }
                                    >
                                        <div className="attention-icon money">
                                            <WalletCards
                                                size={17}
                                            />
                                        </div>

                                        <div className="attention-content">
                                            <strong>
                                                Pending
                                                receivables
                                            </strong>

                                            <span>
                                                {
                                                    formatCurrency(
                                                        pendingReceivables
                                                    )
                                                }{" "}
                                                to collect
                                            </span>
                                        </div>

                                        <ChevronRight size={17} />
                                    </button>
                                )}


                                {rentalPending > 0 && (
                                    <button
                                        type="button"
                                        className="attention-item"
                                        onClick={() =>
                                            goTo("/rental")
                                        }
                                    >
                                        <div className="attention-icon rental">
                                            <Package size={17} />
                                        </div>

                                        <div className="attention-content">
                                            <strong>
                                                Pending rental
                                                bills
                                            </strong>

                                            <span>
                                                {
                                                    formatNumber(
                                                        rentalPending
                                                    )
                                                }{" "}
                                                pending
                                                bill(s)
                                            </span>
                                        </div>

                                        <ChevronRight size={17} />
                                    </button>
                                )}


                                {toNumber(
                                    lowStockItems
                                ) === 0 &&
                                    toNumber(
                                        openServiceTickets
                                    ) === 0 &&
                                    toNumber(
                                        pendingReceivables
                                    ) === 0 &&
                                    rentalPending === 0 && (
                                        <div className="attention-empty">

                                            <CheckCircle2
                                                size={26}
                                            />

                                            <strong>
                                                No immediate
                                                attention items
                                            </strong>

                                            <span>
                                                Everything looks
                                                clear.
                                            </span>

                                        </div>
                                    )}

                            </div>

                        </div>


                        {/* QUICK ACTIONS */}

                        <div className="dashboard-panel">

                            <div className="panel-header">

                                <div>
                                    <h2>
                                        Quick Actions
                                    </h2>

                                    <p>
                                        Frequently used
                                        operations
                                    </p>
                                </div>

                                <div className="panel-header-icon">
                                    <Plus size={20} />
                                </div>

                            </div>


                            <div className="quick-actions">

                                <button
                                    type="button"
                                    className="quick-action"
                                    onClick={() =>
                                        goTo("/sales")
                                    }
                                >
                                    <div className="quick-action-icon sales">
                                        <ShoppingCart
                                            size={19}
                                        />
                                    </div>

                                    <div>
                                        <strong>
                                            Sales
                                        </strong>

                                        <span>
                                            Manage sales
                                        </span>
                                    </div>

                                    <ChevronRight size={17} />
                                </button>


                                <button
                                    type="button"
                                    className="quick-action"
                                    onClick={() =>
                                        goTo("/purchase")
                                    }
                                >
                                    <div className="quick-action-icon purchase">
                                        <Truck size={19} />
                                    </div>

                                    <div>
                                        <strong>
                                            Purchase
                                        </strong>

                                        <span>
                                            Manage purchases
                                        </span>
                                    </div>

                                    <ChevronRight size={17} />
                                </button>


                                <button
                                    type="button"
                                    className="quick-action"
                                    onClick={() =>
                                        goTo("/service")
                                    }
                                >
                                    <div className="quick-action-icon service">
                                        <Wrench size={19} />
                                    </div>

                                    <div>
                                        <strong>
                                            Service
                                        </strong>

                                        <span>
                                            Manage service
                                        </span>
                                    </div>

                                    <ChevronRight size={17} />
                                </button>


                                <button
                                    type="button"
                                    className="quick-action"
                                    onClick={() =>
                                        goTo("/customers")
                                    }
                                >
                                    <div className="quick-action-icon customer">
                                        <Users size={19} />
                                    </div>

                                    <div>
                                        <strong>
                                            Customers
                                        </strong>

                                        <span>
                                            Manage customers
                                        </span>
                                    </div>

                                    <ChevronRight size={17} />
                                </button>


                                <button
                                    type="button"
                                    className="quick-action"
                                    onClick={() =>
                                        goTo("/inventory")
                                    }
                                >
                                    <div className="quick-action-icon inventory">
                                        <Boxes size={19} />
                                    </div>

                                    <div>
                                        <strong>
                                            Inventory
                                        </strong>

                                        <span>
                                            Manage stock
                                        </span>
                                    </div>

                                    <ChevronRight size={17} />
                                </button>


                                <button
                                    type="button"
                                    className="quick-action"
                                    onClick={() =>
                                        goTo("/rental")
                                    }
                                >
                                    <div className="quick-action-icon rental">
                                        <Package size={19} />
                                    </div>

                                    <div>
                                        <strong>
                                            Rental / AMC
                                        </strong>

                                        <span>
                                            Manage rentals
                                        </span>
                                    </div>

                                    <ChevronRight size={17} />
                                </button>

                            </div>

                        </div>

                    </section>


                    {/* ==================================================
                        FOOTER
                    ================================================== */}

                    <div className="dashboard-footer">
                        <span>
                            Digitech ERP
                        </span>

                        <span>•</span>

                        <span>
                            Business Management
                        </span>

                        <span>•</span>

                        <span>
                            {totalMachines
                                ? `${formatNumber(
                                      totalMachines
                                  )} machines`
                                : "ERP Dashboard"}
                        </span>
                    </div>

                </div>

            </main>

        </div>
    );
};


export default Dashboard;
