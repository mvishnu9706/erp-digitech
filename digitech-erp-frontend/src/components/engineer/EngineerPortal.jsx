import React, {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    RefreshCw,
    AlertCircle,
    X,
    CheckCircle2,
} from "lucide-react";

import api from "../../api/axios";

import { useAuth } from "../../context/AuthContext";

import EngineerCards from "./cards/EngineerCards";
import EngineerTable from "./table/EngineerTable";
import EngineerHeader from "./EngineerHeader";

import "./EngineerPortal.css";


/* =====================================================
   ENGINEER PORTAL
===================================================== */

const EngineerPortal = () => {

    const { user, logout } = useAuth();


    /* =================================================
       STATE
    ================================================= */

    const [services, setServices] = useState([]);

    const [loading, setLoading] = useState(true);

    const [refreshing, setRefreshing] = useState(false);

    const [error, setError] = useState("");

    const [successMessage, setSuccessMessage] = useState("");


    /* =================================================
       GET ENGINEER SERVICES
    ================================================= */

    const loadServices = useCallback(
        async (showLoader = true) => {

            try {

                if (showLoader) {
                    setLoading(true);
                } else {
                    setRefreshing(true);
                }

                setError("");


                const response = await api.get(
                    "/service-tickets/engineer/my-services",
                    {
                        params: {
                            page: 1,
                            page_size: 100,
                        },
                    }
                );


                const data = response?.data;


                /*
                 * Backend returns:
                 *
                 * {
                 *   total,
                 *   page,
                 *   page_size,
                 *   items: []
                 * }
                 */

                const items =
                    Array.isArray(data?.items)
                        ? data.items
                        : [];


                setServices(items);

            } catch (err) {

                console.error(
                    "Engineer services error:",
                    err
                );


                const message =
                    err?.response?.data?.detail ||
                    err?.response?.data?.message ||
                    "Unable to load service requests.";


                setError(message);

            } finally {

                setLoading(false);

                setRefreshing(false);

            }

        },
        []
    );


    /* =================================================
       INITIAL LOAD
    ================================================= */

    useEffect(() => {

        loadServices(true);

    }, [loadServices]);


    /* =================================================
       AUTO REFRESH
    ================================================= */

    useEffect(() => {

        const interval = setInterval(() => {

            loadServices(false);

        }, 15000);


        return () => {

            clearInterval(interval);

        };

    }, [loadServices]);


    /* =================================================
       SUCCESS MESSAGE AUTO HIDE
    ================================================= */

    useEffect(() => {

        if (!successMessage) {
            return;
        }


        const timer = setTimeout(() => {

            setSuccessMessage("");

        }, 4000);


        return () => {

            clearTimeout(timer);

        };

    }, [successMessage]);


    /* =================================================
       NORMALIZE STATUS
    ================================================= */

    const getStatus = useCallback(
        (service) => {

            return String(
                service?.status || ""
            ).toUpperCase();

        },
        []
    );


    /* =================================================
       COUNTS
    ================================================= */

    const counts = useMemo(() => {

        let assigned = 0;

        let accepted = 0;

        let inProgress = 0;

        let completed = 0;


        services.forEach((service) => {

            const status =
                getStatus(service);


            if (status === "ASSIGNED") {

                assigned++;

            }


            else if (
                status === "CONFIRMED" ||
                status === "ACCEPTED"
            ) {

                accepted++;

            }


            else if (
                status === "IN_PROGRESS"
            ) {

                inProgress++;

            }


            else if (
                status === "COMPLETED" ||
                status === "CLOSED"
            ) {

                completed++;

            }

        });


        return {
            assigned,
            accepted,
            inProgress,
            completed,
        };

    }, [services, getStatus]);


    /* =================================================
       ACCEPT SERVICE
    ================================================= */

    const handleAccept = async (
        service
    ) => {

        if (!service?.id) {
            return;
        }


        try {

            setError("");


            await api.put(
                `/service-tickets/${service.id}/accept`
            );


            /*
             * Backend workflow:
             *
             * ASSIGNED
             *      ↓
             * IN_PROGRESS
             *
             * The backend moves the service directly
             * to IN_PROGRESS when the engineer accepts.
             */


            setSuccessMessage(
                "Service accepted successfully."
            );


            await loadServices(false);

        } catch (err) {

            console.error(
                "Accept service error:",
                err
            );


            setError(
                err?.response?.data?.detail ||
                err?.response?.data?.message ||
                "Unable to accept this service."
            );

        }

    };


    /* =================================================
       REJECT SERVICE
    ================================================= */

    const handleReject = async (
        service
    ) => {

        if (!service?.id) {
            return;
        }


        const confirmed =
            window.confirm(
                `Reject service ${service.ticket_number || service.id}?`
            );


        if (!confirmed) {
            return;
        }


        try {

            setError("");


            /*
             * Existing backend has a general status
             * endpoint for admin.
             *
             * Do NOT use this endpoint for engineers
             * unless your backend has been changed to
             * allow engineer rejection.
             *
             * The request below expects the engineer
             * reject endpoint to exist.
             */

            await api.put(
                `/service-tickets/${service.id}/reject`
            );


            setSuccessMessage(
                "Service rejected successfully."
            );


            await loadServices(false);

        } catch (err) {

            console.error(
                "Reject service error:",
                err
            );


            setError(
                err?.response?.data?.detail ||
                err?.response?.data?.message ||
                "Unable to reject this service."
            );

        }

    };


    /* =================================================
       COMPLETE SERVICE
       Called by EngineerTable after the user submits
       the single Complete Service popup.
    ================================================= */

    const handleCompleteService = async (service, data = {}) => {

        if (!service?.id) {
            throw new Error("Service ID is missing.");
        }

        const finalMaterial =
            String(data?.material_used ?? "").trim() || "No";

        let finalCost = null;

        if (
            data?.service_cost !== "" &&
            data?.service_cost !== null &&
            data?.service_cost !== undefined
        ) {
            finalCost = Number(data.service_cost);

            if (Number.isNaN(finalCost) || finalCost < 0) {
                throw new Error("Service cost must be a valid amount.");
            }
        }

        const normalizedPaymentStatus = String(
            data?.payment_status || "PENDING"
        )
            .trim()
            .toUpperCase();

        const paymentStatus =
            normalizedPaymentStatus === "RECEIVED"
                ? "RECEIVED"
                : "PENDING";

        try {
            setError("");

            const response = await api.put(
                `/service-tickets/${service.id}/complete`,
                {
                    material_used: finalMaterial,
                    service_cost: finalCost,
                    resolution: data?.resolution?.trim() || null,
                    completion_date: data?.completion_date || null,
                    payment_status: paymentStatus,
                }
            );

            setSuccessMessage("Service completed successfully.");

            await loadServices(false);

            return response?.data || true;
        } catch (err) {
            console.error("Complete service error:", err);

            const message =
                err?.response?.data?.detail ||
                err?.response?.data?.message ||
                err?.message ||
                "Unable to complete this service.";

            setError(message);
            throw err;
        }
    };


    /* =================================================
       UPDATE SERVICE
       Called by EngineerTable -> Save Update
    ================================================= */

    const handleUpdateService = async (service, data) => {

        if (!service?.id) {
            throw new Error("Service ID is missing.");
        }

        const serviceCost =
            data?.service_cost === "" ||
            data?.service_cost === null ||
            data?.service_cost === undefined
                ? null
                : Number(data.service_cost);

        if (
            serviceCost !== null &&
            (Number.isNaN(serviceCost) || serviceCost < 0)
        ) {
            throw new Error("Service cost must be a valid amount.");
        }

        const normalizedPaymentStatus = String(
            data?.payment_status || "PENDING"
        )
            .trim()
            .toUpperCase();

        const safePaymentStatus =
            normalizedPaymentStatus === "RECEIVED"
                ? "RECEIVED"
                : "PENDING";

        const payload = {
            completion_date:
                data?.completion_date || null,

            material_used:
                data?.material_used?.trim() || null,

            service_cost:
                serviceCost,

            payment_status:
                safePaymentStatus,
        };

        try {

            setError("");

            const response = await api.put(
                `/service-tickets/${service.id}`,
                payload
            );

            setSuccessMessage(
                "Service updated successfully."
            );

            // Reload the table so the values displayed
            // come directly from PostgreSQL/backend.
            await loadServices(false);

            return response?.data || true;

        } catch (err) {

            console.error(
                "Update service error:",
                err
            );

            const message =
                err?.response?.data?.detail ||
                err?.response?.data?.message ||
                "Unable to update this service.";

            setError(message);

            throw err;
        }
    };


    /* =================================================
       MANUAL REFRESH
    ================================================= */

    const handleRefresh = () => {

        loadServices(false);

    };


    /* =================================================
       USER NAME
    ================================================= */

    const engineerName =
        user?.full_name ||
        user?.name ||
        user?.username ||
        "Engineer";


    /* =================================================
       RENDER
    ================================================= */

    return (

        <div className="engineer-portal">


            {/* =================================================
               HEADER
            ================================================= */}

            <EngineerHeader
                engineerName={engineerName}
                logout={logout}
            />


            {/* =================================================
               MAIN
            ================================================= */}

            <main className="engineer-portal-main">


                {/* =================================================
                   PAGE HEADER
                ================================================= */}

                <section className="engineer-page-header">

                    <div>

                        <span className="engineer-page-label">
                            SERVICE MANAGEMENT
                        </span>


                        <h1>
                            Engineer Service Portal
                        </h1>


                        <p>
                            Welcome, {engineerName}. Manage your
                            assigned service requests from one place.
                        </p>

                    </div>


                    <button
                        type="button"
                        className="engineer-refresh-button"
                        onClick={handleRefresh}
                        disabled={refreshing}
                    >

                        <RefreshCw
                            size={15}
                            className={
                                refreshing
                                    ? "engineer-spin"
                                    : ""
                            }
                        />

                        {refreshing
                            ? "Refreshing..."
                            : "Refresh"}

                    </button>

                </section>


                {/* =================================================
                   ERROR
                ================================================= */}

                {error && (

                    <div className="engineer-alert engineer-alert-error">

                        <AlertCircle size={17} />

                        <div>

                            <strong>
                                Something went wrong
                            </strong>

                            <span>
                                {error}
                            </span>

                        </div>


                        <button
                            type="button"
                            onClick={() =>
                                setError("")
                            }
                            aria-label="Close error"
                        >

                            <X size={17} />

                        </button>

                    </div>

                )}


                {/* =================================================
                   SUCCESS
                ================================================= */}

                {successMessage && (

                    <div className="engineer-alert engineer-alert-success">

                        <CheckCircle2 size={17} />

                        <span>
                            {successMessage}
                        </span>


                        <button
                            type="button"
                            onClick={() =>
                                setSuccessMessage("")
                            }
                            aria-label="Close success"
                        >

                            <X size={17} />

                        </button>

                    </div>

                )}


                {/* =================================================
                   CARDS
                ================================================= */}

                <EngineerCards
                    assignedCount={
                        counts.assigned
                    }

                    acceptedCount={
                        counts.accepted
                    }

                    inProgressCount={
                        counts.inProgress
                    }

                    completedCount={
                        counts.completed
                    }
                />


                {/* =================================================
                   SERVICE TABLE
                ================================================= */}

                <EngineerTable

                    services={
                        services
                    }

                    loading={
                        loading
                    }

                    onAccept={
                        handleAccept
                    }

                    onReject={
                        handleReject
                    }

                    onComplete={
                        handleCompleteService
                    }

                    onUpdate={
                        handleUpdateService
                    }

                    onRefresh={
                        handleRefresh
                    }

                />

            </main>


            {/* Complete Service popup is rendered only by EngineerTable. */}

        </div>

    );

};


export default EngineerPortal;