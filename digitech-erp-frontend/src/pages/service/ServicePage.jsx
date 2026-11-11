import "./ServicePage.css";

import {
    Plus,
    RefreshCcw,
    Download,
    BarChart3,
    Users,
    Wrench,
    Search,
    CalendarDays,
    Filter,
    RotateCcw,
} from "lucide-react";

import { useMemo, useState } from "react";
import * as XLSX from "xlsx";

import DashboardLayout from "../../layouts/DashboardLayout";

import ServiceCards from "../../components/service/ServiceCards/ServiceCards";
import ServiceToolbar from "../../components/service/ServiceToolbar/ServiceToolbar";
import ServiceEngineerToolbar from "../../components/service/ServiceEngineerToolbar/ServiceEngineerToolbar";
import ServiceEngineerDetails from "../../components/service/ServiceEngineerDetails/ServiceEngineerDetails";
import ServiceTable from "../../components/service/ServiceTable/ServiceTable";
import ServiceDrawer from "../../components/service/ServiceDrawer/ServiceDrawer";
import ServiceDetails from "../../components/service/ServiceDetails/ServiceDetails";
import DeleteServiceModal from "../../components/service/DeleteServiceModal/DeleteServiceModal";
import AssignEngineerModal from "../../components/service/AssignEngineerModal/AssignEngineerModal";

import { useService } from "../../context/ServiceContext";


/* =====================================================
   ENGINEER EXCEL EXPORT HELPERS
   Export uses the active Engineer Management filters.
   If no engineer filters are selected, all services are exported.
   The generated .xls file opens directly in Microsoft Excel.
===================================================== */

const exportValue = (value) => {
    if (value === null || value === undefined || value === "") {
        return "";
    }

    if (typeof value === "object") {
        return (
            value?.full_name ||
            value?.name ||
            value?.company_name ||
            value?.model_name ||
            value?.serial_number ||
            ""
        ).toString();
    }

    return String(value);
};

const exportEngineerName = (service) =>
    exportValue(
        service?.engineer_name ||
        service?.technician ||
        service?.engineer?.full_name ||
        service?.engineer?.name ||
        service?.assigned_engineer?.full_name ||
        service?.assigned_engineer?.name ||
        service?.engineer_details?.full_name ||
        service?.engineer_details?.name ||
        ""
    ).trim();

const exportCustomerName = (service) =>
    exportValue(
        service?.customer_name ||
        service?.customer?.name ||
        service?.customer?.full_name ||
        service?.customerName ||
        ""
    ).trim();

const exportProductName = (service) =>
    exportValue(
        service?.product_name ||
        service?.product?.name ||
        service?.machine_name ||
        service?.machine?.name ||
        service?.productName ||
        ""
    ).trim();

const exportTicketNumber = (service) =>
    exportValue(
        service?.ticket_number ||
        service?.ticket_no ||
        service?.ticket ||
        service?.service_ticket_number ||
        service?.ticketNumber ||
        service?.id ||
        ""
    ).trim();

const exportServiceDate = (service) =>
    service?.completed_date ||
    service?.completed_at ||
    service?.completion_date ||
    service?.service_date ||
    service?.serviceDate ||
    service?.date ||
    service?.created_at ||
    service?.createdAt ||
    "";

const exportDateOnly = (value) => {
    if (!value) return "";

    const text = String(value);
    const isoMatch = text.match(/^(\d{4}-\d{2}-\d{2})/);

    if (isoMatch) {
        return isoMatch[1];
    }

    const parsed = new Date(value);

    if (Number.isNaN(parsed.getTime())) {
        return "";
    }

    return `${parsed.getFullYear()}-${String(
        parsed.getMonth() + 1
    ).padStart(2, "0")}-${String(parsed.getDate()).padStart(2, "0")}`;
};

const exportFormattedDate = (value) => {
    const date = exportDateOnly(value);

    if (!date) return "";

    const [year, month, day] = date.split("-");
    return `${day}-${month}-${year}`;
};

const exportIssue = (service) =>
    exportValue(
        service?.issue ||
        service?.problem_description ||
        service?.complaint ||
        service?.description ||
        ""
    );

const exportMaterial = (service) =>
    exportValue(
        service?.material_used ??
        service?.materials_used ??
        service?.materialUsed ??
        service?.materialsUsed ??
        ""
    );

const exportCost = (service) => {
    const value =
        service?.service_cost ??
        service?.serviceCost ??
        service?.cost ??
        0;

    const numeric = Number(value);

    return Number.isFinite(numeric) ? numeric : 0;
};

const exportPaymentStatus = (service) =>
    exportValue(
        service?.payment_status ||
        service?.payment?.status ||
        service?.payment?.payment_status ||
        "PENDING"
    )
        .trim()
        .replace(/_/g, " ");

const exportPhone = (service) =>
    exportValue(
        service?.customer_phone ||
        service?.phone ||
        service?.customer?.phone ||
        service?.customer?.mobile ||
        service?.mobile ||
        ""
    );

const exportSerialNumber = (service) =>
    exportValue(
        service?.serial_number ||
        service?.serialNo ||
        service?.machine?.serial_number ||
        service?.product?.serial_number ||
        ""
    );

const downloadEngineerExcel = (rows, filters) => {
    const headers = [
        "S.No",
        "Ticket Number",
        "Engineer",
        "Customer",
        "Phone",
        "Product / Machine",
        "Serial Number",
        "Issue",
        "Status",
        "Completed / Service Date",
        "Material Used",
        "Service Cost",
        "Payment Status",
    ];

    const dataRows = rows.map((service, index) => ({
        "S.No": index + 1,
        "Ticket Number": exportTicketNumber(service),
        "Engineer": exportEngineerName(service) || "-",
        "Customer": exportCustomerName(service) || "-",
        "Phone": exportPhone(service) || "-",
        "Product / Machine": exportProductName(service) || "-",
        "Serial Number": exportSerialNumber(service) || "-",
        "Issue": exportIssue(service) || "-",
        "Status": exportValue(service?.status || "-").replace(/_/g, " "),
        "Completed / Service Date": exportFormattedDate(exportServiceDate(service)) || "-",
        "Material Used": exportMaterial(service) || "-",
        "Service Cost": exportCost(service),
        "Payment Status": exportPaymentStatus(service),
    }));

    const totalCost = rows.reduce(
        (total, service) => total + exportCost(service),
        0
    );

    const filterText = [
        filters?.engineer
            ? `Engineer: ${filters.engineer}`
            : "All Engineers",
        filters?.dateFrom
            ? `From: ${filters.dateFrom}`
            : "From: All",
        filters?.dateTo
            ? `To: ${filters.dateTo}`
            : "To: All",
        filters?.search
            ? `Search: ${filters.search}`
            : "Search: All",
    ].join(" | ");

    const title = filters?.engineer
        ? `${filters.engineer} - Service Report`
        : "Service Report";

    /*
       Create a real XLSX workbook.
       This is different from the old HTML-in-.xls approach and
       will open in Excel without the "file format and extension
       don't match" warning.
    */
    const worksheetData = [
        [title],
        [filterText],
        [],
        headers,
        ...dataRows.map((row) =>
            headers.map((header) => row[header])
        ),
        [],
        [
            "Total Service Cost",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            totalCost,
            `${rows.length} Services`,
        ],
    ];

    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);

    /* Column widths */
    worksheet["!cols"] = [
        { wch: 7 },
        { wch: 22 },
        { wch: 20 },
        { wch: 24 },
        { wch: 15 },
        { wch: 28 },
        { wch: 22 },
        { wch: 30 },
        { wch: 16 },
        { wch: 24 },
        { wch: 20 },
        { wch: 16 },
        { wch: 24 },
    ];

    /* Merge title and filter rows across all columns */
    worksheet["!merges"] = [
        {
            s: { r: 0, c: 0 },
            e: { r: 0, c: headers.length - 1 },
        },
        {
            s: { r: 1, c: 0 },
            e: { r: 1, c: headers.length - 1 },
        },
    ];

    /* Format the service-cost column as INR */
    const serviceCostColumn = 11;
    const firstDataRow = 4;
    const lastDataRow = firstDataRow + dataRows.length - 1;

    for (let rowIndex = firstDataRow; rowIndex <= lastDataRow; rowIndex += 1) {
        const cellAddress = XLSX.utils.encode_cell({
            r: rowIndex,
            c: serviceCostColumn,
        });

        if (worksheet[cellAddress]) {
            worksheet[cellAddress].t = "n";
            worksheet[cellAddress].z = '₹#,##0.00';
        }
    }

    /* Format total cost */
    const totalRowIndex = 5 + dataRows.length;
    const totalCostCell = XLSX.utils.encode_cell({
        r: totalRowIndex,
        c: serviceCostColumn,
    });

    if (worksheet[totalCostCell]) {
        worksheet[totalCostCell].t = "n";
        worksheet[totalCostCell].z = '₹#,##0.00';
    }

    /* Basic Excel cell styling where supported */
    const titleCell = worksheet["A1"];
    const filterCell = worksheet["A2"];

    if (titleCell) {
        titleCell.s = {
            font: {
                bold: true,
                sz: 16,
                color: { rgb: "102B4C" },
            },
            alignment: {
                vertical: "center",
            },
        };
    }

    if (filterCell) {
        filterCell.s = {
            font: {
                sz: 10,
                color: { rgb: "52667E" },
            },
        };
    }

    /* Freeze the header row */
    worksheet["!freeze"] = {
        xSplit: 0,
        ySplit: 4,
    };

    /* Auto-filter the actual data header */
    worksheet["!autofilter"] = {
        ref: `A4:M${4 + dataRows.length}`,
    };

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(
        workbook,
        worksheet,
        "Service Report"
    );

    const dateStamp = new Date()
        .toISOString()
        .slice(0, 10);

    const engineerPart = filters?.engineer
        ? `_${filters.engineer
              .replace(/[^a-z0-9]+/gi, "_")
              .replace(/^_|_$/g, "")}`
        : "_All_Engineers";

    XLSX.writeFile(
        workbook,
        `Service_Report${engineerPart}_${dateStamp}.xlsx`
    );
};


const ServicePage = () => {

    // =====================================================
    // ACTIVE TAB
    // =====================================================

    const [
        activeTab,
        setActiveTab,
    ] = useState("service");


    // =====================================================
    // SERVICE CONTEXT
    // =====================================================

    const {

        // =================================================
        // Data
        // =================================================

        services,

        filteredServices,

        dashboard,

        loading,

        error,


        // =================================================
        // Drawer
        // =================================================

        drawerOpen,

        drawerMode,

        selectedService,

        openAddDrawer,

        openEditDrawer,

        closeDrawer,

        saveService,


        // =================================================
        // Cancel
        // =================================================
        cancelService,


        // =================================================
        // Details
        // =================================================

        detailsOpen,

        openDetails,

        closeDetails,


        // =================================================
        // Other
        // =================================================

        refreshServices,

        exportServices,

    } = useService();


    // =====================================================
    // CANCEL CONFIRMATION STATE
    // =====================================================

    const [
        cancelConfirmOpen,
        setCancelConfirmOpen,
    ] = useState(false);

    const [
        serviceToCancel,
        setServiceToCancel,
    ] = useState(null);


    // =====================================================
    // ENGINEER MANAGEMENT FILTERS
    // =====================================================

    const [
        selectedEngineer,
        setSelectedEngineer,
    ] = useState("");

    const [
        engineerDateFrom,
        setEngineerDateFrom,
    ] = useState("");

    const [
        engineerDateTo,
        setEngineerDateTo,
    ] = useState("");

    

    const [
        engineerSearch,
        setEngineerSearch,
    ] = useState("");
const engineerOptions = useMemo(() => {
        const names = (services || [])
            .map((service) =>
                (
                    service?.engineer_name ||
                    service?.technician ||
                    service?.engineer?.full_name ||
                    service?.engineer?.name ||
                    service?.assigned_engineer?.full_name ||
                    service?.assigned_engineer?.name ||
                    service?.engineer_details?.full_name ||
                    service?.engineer_details?.name ||
                    ""
                )
                    .toString()
                    .trim()
            )
            .filter(
                (name) =>
                    name &&
                    name !== "-" &&
                    name.toLowerCase() !== "unassigned"
            );

        return [...new Set(names)].sort((a, b) =>
            a.localeCompare(b)
        );
    }, [services]);

    const applyEngineerFilters = () => {
        // The controls are kept local to the Engineer tab.
        // This prevents changing the normal Service Management filters.
        setEngineerFilterApplied({
            engineer: selectedEngineer,
            dateFrom: engineerDateFrom,
            dateTo: engineerDateTo,
            search: engineerSearch,
        });
    };

    const [
        engineerFilterApplied,
        setEngineerFilterApplied,
    ] = useState({
        engineer: "",
        dateFrom: "",
        dateTo: "",
        search: "",
    });

    const resetEngineerFilters = () => {
        setSelectedEngineer("");
        setEngineerDateFrom("");
        setEngineerDateTo("");
        setEngineerFilterApplied({
            engineer: "",
            dateFrom: "",
            dateTo: "",
            search: "",
        });
    };


    // =====================================================
    // ENGINEER MANAGEMENT EXPORT
    // =====================================================

    const handleEngineerExport = () => {
        const filters = engineerFilterApplied || {
            engineer: "",
            dateFrom: "",
            dateTo: "",
            search: "",
        };

        const searchValue = String(
            filters.search || ""
        )
            .trim()
            .toLowerCase();

        const exportRows = (services || []).filter(
            (service) => {
                const engineerName = exportEngineerName(
                    service
                );

                if (
                    filters.engineer &&
                    engineerName.toLowerCase() !==
                        String(filters.engineer)
                            .trim()
                            .toLowerCase()
                ) {
                    return false;
                }

                const serviceDate = exportDateOnly(
                    exportServiceDate(service)
                );

                if (
                    filters.dateFrom &&
                    serviceDate &&
                    serviceDate < filters.dateFrom
                ) {
                    return false;
                }

                if (
                    filters.dateTo &&
                    serviceDate &&
                    serviceDate > filters.dateTo
                ) {
                    return false;
                }

                if (
                    (filters.dateFrom || filters.dateTo) &&
                    !serviceDate
                ) {
                    return false;
                }

                if (searchValue) {
                    const haystack = [
                        exportTicketNumber(service),
                        exportCustomerName(service),
                        exportProductName(service),
                        exportIssue(service),
                        engineerName,
                        exportMaterial(service),
                        exportPhone(service),
                        exportSerialNumber(service),
                        service?.status,
                        exportPaymentStatus(service),
                    ]
                        .join(" ")
                        .toLowerCase();

                    if (!haystack.includes(searchValue)) {
                        return false;
                    }
                }

                return true;
            }
        );

        if (!exportRows.length) {
            window.alert(
                "No service records match the selected filters."
            );
            return;
        }

        downloadEngineerExcel(
            exportRows,
            filters
        );
    };


    // =====================================================
    // OPEN CANCEL CONFIRMATION
    // =====================================================

    const openCancelConfirm = (service) => {
        if (!service?.id) {
            return;
        }

        if (
            String(service.status || "")
                .trim()
                .toUpperCase() === "CANCELLED"
        ) {
            return;
        }

        setServiceToCancel(service);
        setCancelConfirmOpen(true);
    };


    // =====================================================
    // CLOSE CANCEL CONFIRMATION
    // =====================================================

    const closeCancelConfirm = () => {
        setCancelConfirmOpen(false);
        setServiceToCancel(null);
    };


    // =====================================================
    // CONFIRM CANCEL
    // =====================================================

    const handleConfirmCancel = async () => {
        if (!serviceToCancel?.id) {
            return;
        }

        await cancelService(serviceToCancel);
        closeCancelConfirm();
    };


    // =====================================================
    // ASSIGN ENGINEER STATE
    // =====================================================

    const [
        assignEngineerOpen,
        setAssignEngineerOpen,
    ] = useState(false);


    const [
        serviceToAssign,
        setServiceToAssign,
    ] = useState(null);


    // =====================================================
    // OPEN ASSIGN ENGINEER MODAL
    // =====================================================

    const openAssignEngineer = (
        service
    ) => {

        console.log(
            "Opening Assign Engineer:",
            service
        );

        setServiceToAssign(
            service
        );

        setAssignEngineerOpen(
            true
        );
    };


    // =====================================================
    // CLOSE ASSIGN ENGINEER MODAL
    // =====================================================

    const closeAssignEngineer = () => {

        setAssignEngineerOpen(
            false
        );

        setServiceToAssign(
            null
        );
    };


    // =====================================================
    // ENGINEER ASSIGNMENT SUCCESS
    // =====================================================

    const handleEngineerAssigned = async (
        updatedTicket
    ) => {

        console.log(
            "Engineer assigned successfully:",
            updatedTicket
        );

        closeAssignEngineer();

        // Refresh service table from backend
        await refreshServices();
    };


    // =====================================================
    // ENGINEER SERVICES
    // =====================================================
    //
    // Only tickets that have an engineer assigned.
    //
    // =====================================================

    const engineerServices = useMemo(
        () => {

            return (
                services || []
            ).filter(
                (service) => {

                    return (

                        service.engineer_id ||

                        (
                            service.technician &&
                            service.technician !== "-" &&
                            service.technician !== "Unassigned"
                        )

                    );

                }
            );

        },
        [
            services,
        ]
    );


    // =====================================================
    // ASSIGNED TICKET COUNT
    // =====================================================
    //
    // Count all tickets that currently have an engineer
    // assigned. This uses the service records returned by
    // the backend/database; no dummy data is used.
    //
    // engineer_id is preferred. technician is kept as a
    // fallback because the table can receive the engineer
    // name from the backend as well.
    // =====================================================

    const assignedTickets = useMemo(
        () => {

            return (
                services || []
            ).filter(
                (service) => {

                    const hasEngineerId =
                        service?.engineer_id !== null &&
                        service?.engineer_id !== undefined &&
                        String(
                            service?.engineer_id
                        ).trim() !== "";

                    const technician =
                        String(
                            service?.technician ?? ""
                        ).trim();

                    const hasTechnician =
                        technician !== "" &&
                        technician !== "-" &&
                        technician.toLowerCase() !== "unassigned";

                    return (
                        hasEngineerId ||
                        hasTechnician
                    );

                }
            ).length;

        },
        [
            services,
        ]
    );



    // =====================================================
    // TAB CHANGE
    // =====================================================

    const handleTabChange = (
        tab
    ) => {

        setActiveTab(
            tab
        );

    };


    // =====================================================
    // RENDER
    // =====================================================

    return (

        <DashboardLayout>

            <div className="service-page">


                {/* =================================================
                    HEADER
                ================================================= */}

                <div className="service-page-header">


                    {/* =================================================
                        LEFT
                    ================================================= */}

                    <div className="service-page-header-left">

                        <h1>
                            Service Management
                        </h1>

                        <p>
                            Manage service requests, repairs,
                            technicians and customer service records.
                        </p>

                    </div>


                    {/* =================================================
                        RIGHT
                    ================================================= */}

                    <div className="service-page-header-right">


                        {/* =================================================
                            REFRESH
                        ================================================= */}

                        <button
                            type="button"
                            className="btn-light"
                            onClick={
                                refreshServices
                            }
                            disabled={
                                loading
                            }
                        >

                            <RefreshCcw
                                size={18}
                                className={
                                    loading
                                        ? "service-refresh-spinning"
                                        : ""
                                }
                            />

                            {loading
                                ? "Refreshing..."
                                : "Refresh"
                            }

                        </button>


                        {/* =================================================
                            EXPORT
                        ================================================= */}

                        <button
                            type="button"
                            className="btn-light"
                            onClick={
                                activeTab === "engineer"
                                    ? handleEngineerExport
                                    : exportServices
                            }
                            disabled={
                                activeTab === "engineer"
                                    ? !(services || []).length
                                    : !filteredServices?.length
                            }
                        >

                            <Download
                                size={18}
                            />

                            Export

                        </button>


                        {/* =================================================
                            REPORTS
                        ================================================= */}

                        <button
                            type="button"
                            className="btn-light"
                        >

                            <BarChart3
                                size={18}
                            />

                            Reports

                        </button>


                        {/* =================================================
                            ADD SERVICE
                        ================================================= */}

                        {activeTab === "service" && (

                            <button
                                type="button"
                                className="btn-primary"
                                onClick={
                                    openAddDrawer
                                }
                            >

                                <Plus
                                    size={18}
                                />

                                Add Service

                            </button>

                        )}

                    </div>

                </div>


                {/* =================================================
                    ERROR MESSAGE
                ================================================= */}

                {error && (

                    <div
                        className="service-page-error"
                        role="alert"
                    >

                        {error}

                    </div>

                )}


                {/* =================================================
                    SERVICE TABS
                ================================================= */}

                <div className="service-management-tabs">


                    {/* =================================================
                        SERVICE MANAGEMENT TAB
                    ================================================= */}

                    <button
                        type="button"
                        className={
                            `service-management-tab ${
                                activeTab === "service"
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            handleTabChange(
                                "service"
                            )
                        }
                    >

                        <Wrench
                            size={18}
                        />

                        <span>
                            Service Management
                        </span>

                    </button>


                    {/* =================================================
                        ENGINEER SERVICE MANAGEMENT TAB
                    ================================================= */}

                    <button
                        type="button"
                        className={
                            `service-management-tab ${
                                activeTab === "engineer"
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            handleTabChange(
                                "engineer"
                            )
                        }
                    >

                        <Users
                            size={18}
                        />

                        <span>
                            Engineer Service Management
                        </span>

                    </button>

                </div>


                {/* =================================================
                    SERVICE MANAGEMENT TAB
                ================================================= */}

                {activeTab === "service" && (

                    <>

                        {/* =============================================
                            DASHBOARD CARDS
                        ============================================= */}

                        <ServiceCards

                            totalTickets={
                                dashboard?.totalTickets ?? 0
                            }

                            openTickets={
                                dashboard?.openTickets ?? 0
                            }

                            assignedTickets={
                                assignedTickets
                            }

                            inProgressTickets={
                                dashboard?.inProgressTickets ?? 0
                            }

                            completedTickets={
                                dashboard?.completedTickets ?? 0
                            }

                            monthlyCompletedTickets={
                                dashboard?.monthlyCompletedTickets ?? 0
                            }

                            pendingTickets={
                                dashboard?.pendingTickets ?? 0
                            }

                            totalServiceValue={
                                dashboard?.totalServiceValue ?? 0
                            }

                        />


                        {/* =============================================
                            TOOLBAR
                        ============================================= */}

                        <ServiceToolbar />


                        {/* =============================================
                            TABLE
                        ============================================= */}

                        <ServiceTable

                            services={
                                filteredServices
                            }

                            onView={
                                openDetails
                            }

                            onEdit={
                                openEditDrawer
                            }

                            onDelete={
                                openCancelConfirm
                            }

                            onAssignEngineer={
                                openAssignEngineer
                            }

                        />

                    </>

                )}


                {/* =================================================
                    ENGINEER SERVICE MANAGEMENT TAB
                ================================================= */}

                {activeTab === "engineer" && (

                    <>

                        {/* =============================================
                            ENGINEER HEADER
                        ============================================= */}

                        <div className="engineer-service-header">
                            <div>
                                <h2>
                                    Engineer Service Management
                                </h2>

                                <p>
                                    View and filter service records
                                    assigned to engineers.
                                </p>
                            </div>
                        </div>



                        {/* =============================================
                            ENGINEER-SPECIFIC TOOLBAR
                        ============================================= */}

                        <ServiceEngineerToolbar
                            engineers={engineerOptions}
                            selectedEngineer={selectedEngineer}
                            setSelectedEngineer={
                                setSelectedEngineer
                            }
                            dateFrom={engineerDateFrom}
                            setDateFrom={
                                setEngineerDateFrom
                            }
                            dateTo={engineerDateTo}
                            setDateTo={
                                setEngineerDateTo
                            }
                            search={engineerSearch}
                            setSearch={setEngineerSearch}
                            onFilter={applyEngineerFilters}
                            onReset={resetEngineerFilters}
                        />

                        {/* =============================================
                            ENGINEER SERVICE DETAILS
                        ============================================= */}

                        <ServiceEngineerDetails
                            services={services}
                            selectedEngineer={
                                engineerFilterApplied.engineer
                            }
                            dateFrom={
                                engineerFilterApplied.dateFrom
                            }
                            dateTo={
                                engineerFilterApplied.dateTo
                            }
                            search={
                                engineerFilterApplied.search
                            }
                        />
                    </>

                )}

                {/* =================================================
                    ADD / EDIT DRAWER
                ================================================= */}

                <ServiceDrawer

                    open={
                        drawerOpen
                    }

                    mode={
                        drawerMode
                    }

                    service={
                        selectedService
                    }

                    onClose={
                        closeDrawer
                    }

                    onSave={
                        saveService
                    }

                />


                {/* =================================================
                    VIEW DETAILS
                ================================================= */}

                <ServiceDetails

                    open={
                        detailsOpen
                    }

                    service={
                        selectedService
                    }

                    onClose={
                        closeDetails
                    }

                />


                {/* =================================================
                    CANCEL SERVICE CONFIRMATION MODAL

                    IMPORTANT:
                    We reuse the existing DeleteServiceModal component.
                    No CancelServiceModal folder is required.
                ================================================= */}

                <DeleteServiceModal
                    open={cancelConfirmOpen}
                    service={serviceToCancel}
                    onClose={closeCancelConfirm}
                    onConfirm={handleConfirmCancel}
                    loading={loading}
                />


                <AssignEngineerModal

                    open={
                        assignEngineerOpen
                    }

                    service={
                        serviceToAssign
                    }

                    onClose={
                        closeAssignEngineer
                    }

                    onAssigned={
                        handleEngineerAssigned
                    }

                />


            </div>

        </DashboardLayout>

    );

};


export default ServicePage;