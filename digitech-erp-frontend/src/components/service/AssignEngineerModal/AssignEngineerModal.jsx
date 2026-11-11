import React, {
    useEffect,
    useState,
} from "react";

import {
    X,
    UserRound,
    Phone,
    Wrench,
    Loader2,
    CheckCircle2,
} from "lucide-react";

import { toast } from "react-toastify";

import api from "../../../api/axios";

import "./AssignEngineerModal.css";


const AssignEngineerModal = ({
    open,
    service,
    onClose,
    onAssigned,
}) => {

    // =====================================================
    // ENGINEERS FROM DATABASE
    // =====================================================

    const [
        engineers,
        setEngineers,
    ] = useState([]);


    // =====================================================
    // LOADING ENGINEERS
    // =====================================================

    const [
        loadingEngineers,
        setLoadingEngineers,
    ] = useState(false);


    // =====================================================
    // ASSIGNING
    // =====================================================

    const [
        assigning,
        setAssigning,
    ] = useState(false);


    // =====================================================
    // SELECTED ENGINEER
    // =====================================================

    const [
        selectedEngineerId,
        setSelectedEngineerId,
    ] = useState("");


    // =====================================================
    // ERROR
    // =====================================================

    const [
        error,
        setError,
    ] = useState("");


    // =====================================================
    // LOAD ENGINEERS FROM DATABASE
    // =====================================================

    useEffect(() => {

        if (!open) {
            return;
        }


        const loadEngineers = async () => {

            try {

                setLoadingEngineers(true);

                setError("");

                setEngineers([]);

                setSelectedEngineerId("");


                // =================================================
                // IMPORTANT:
                //
                // This gets users directly from your backend.
                //
                // There are NO hardcoded engineers here.
                // =================================================

                const response =
                    await api.get(
                        "/users/"
                    );


                console.log(
                    "Users returned from database:",
                    response.data
                );


                // =================================================
                // NORMALIZE API RESPONSE
                // =================================================

                let users = [];


                if (
                    Array.isArray(
                        response?.data
                    )
                ) {

                    users =
                        response.data;

                } else if (
                    Array.isArray(
                        response?.data?.items
                    )
                ) {

                    users =
                        response.data.items;

                } else if (
                    Array.isArray(
                        response?.data?.data
                    )
                ) {

                    users =
                        response.data.data;

                }


                // =================================================
                // ONLY ENGINEERS
                //
                // Database role must be ENGINEER.
                // =================================================

                const databaseEngineers =
                    users.filter(
                        (user) => {

                            const role =
                                String(
                                    user?.role ?? ""
                                )
                                    .trim()
                                    .toUpperCase();


                            const active =
                                user?.is_active !== false;


                            return (
                                role === "ENGINEER" &&
                                active
                            );

                        }
                    );


                console.log(
                    "Engineers from database:",
                    databaseEngineers
                );


                setEngineers(
                    databaseEngineers
                );


            } catch (err) {

                console.error(
                    "Failed to load engineers:",
                    err
                );


                const message =
                    err?.response?.data?.detail ||
                    err?.response?.data?.message ||
                    "Unable to load engineers from database.";


                setError(
                    message
                );


                setEngineers([]);

            } finally {

                setLoadingEngineers(
                    false
                );

            }

        };


        loadEngineers();

    }, [open]);


    // =====================================================
    // CLOSE
    // =====================================================

    const handleClose = () => {

        if (assigning) {
            return;
        }


        setSelectedEngineerId("");

        setError("");

        onClose?.();

    };


    // =====================================================
    // ASSIGN ENGINEER
    // =====================================================

    const handleAssign = async (
        event
    ) => {

        event.preventDefault();


        // =================================================
        // CHECK SERVICE
        // =================================================

        if (!service?.id) {

            toast.error(
                "Service ticket ID is missing."
            );

            return;
        }


        // =================================================
        // CHECK ENGINEER
        // =================================================

        if (!selectedEngineerId) {

            toast.error(
                "Please select an engineer."
            );

            return;
        }


        try {

            setAssigning(true);

            setError("");


            console.log(
                "Assigning database engineer:",
                {
                    ticket_id:
                        service.id,

                    engineer_id:
                        selectedEngineerId,
                }
            );


            // =================================================
            // SAVE ASSIGNMENT IN DATABASE
            // =================================================

            const response =
                await api.put(
                    `/service-tickets/${service.id}/assign/${selectedEngineerId}`
                );


            console.log(
                "Assignment saved:",
                response.data
            );


            toast.success(
                "Engineer assigned successfully."
            );


            // =================================================
            // SEND RESULT TO SERVICE PAGE
            // =================================================

            if (onAssigned) {

                await onAssigned(
                    response.data
                );

            }


        } catch (err) {

            console.error(
                "Engineer assignment failed:",
                err
            );


            const message =
                err?.response?.data?.detail ||
                err?.response?.data?.message ||
                "Failed to assign engineer.";


            setError(
                message
            );


            toast.error(
                message
            );

        } finally {

            setAssigning(
                false
            );

        }

    };


    // =====================================================
    // CLOSED
    // =====================================================

    if (!open) {

        return null;

    }


    // =====================================================
    // SELECTED ENGINEER
    // =====================================================

    const selectedEngineer =
        engineers.find(
            (engineer) =>
                String(
                    engineer.id
                ) ===
                String(
                    selectedEngineerId
                )
        );


    // =====================================================
    // RENDER
    // =====================================================

    return (

        <div
            className="assign-engineer-overlay"

            onMouseDown={(
                event
            ) => {

                if (
                    event.target ===
                    event.currentTarget
                ) {

                    handleClose();

                }

            }}
        >

            <div
                className="assign-engineer-modal"

                role="dialog"

                aria-modal="true"
            >


                {/* =================================================
                    HEADER
                ================================================= */}

                <div className="assign-engineer-header">

                    <div className="assign-engineer-title-wrap">

                        <div className="assign-engineer-icon">

                            <Wrench
                                size={20}
                            />

                        </div>


                        <div>

                            <h2>
                                Assign Engineer
                            </h2>

                            <p>
                                Select an engineer
                                for this service ticket.
                            </p>

                        </div>

                    </div>


                    <button
                        type="button"

                        className="assign-engineer-close"

                        onClick={
                            handleClose
                        }

                        disabled={
                            assigning
                        }
                    >

                        <X
                            size={20}
                        />

                    </button>

                </div>


                {/* =================================================
                    TICKET DETAILS
                ================================================= */}

                <div className="assign-engineer-ticket">

                    <div>

                        <span className="assign-engineer-label">
                            Ticket
                        </span>

                        <strong>

                            {
                                service?.ticket_number ||
                                service?.ticket ||
                                "-"
                            }

                        </strong>

                    </div>


                    <div>

                        <span className="assign-engineer-label">
                            Customer
                        </span>

                        <strong>

                            {
                                service?.customer_name ||
                                service?.customer ||
                                "-"
                            }

                        </strong>

                    </div>

                </div>


                {/* =================================================
                    FORM
                ================================================= */}

                <form
                    onSubmit={
                        handleAssign
                    }
                >

                    <div className="assign-engineer-body">


                        <label className="assign-engineer-form-label">

                            Select Engineer

                        </label>


                        {/* =================================================
                            LOADING
                        ================================================= */}

                        {loadingEngineers && (

                            <div className="assign-engineer-loading">

                                <Loader2
                                    size={20}
                                    className="assign-engineer-spinner"
                                />

                                <span>
                                    Loading engineers from database...
                                </span>

                            </div>

                        )}


                        {/* =================================================
                            ERROR
                        ================================================= */}

                        {!loadingEngineers &&
                            error && (

                            <div
                                className="assign-engineer-error"
                                role="alert"
                            >

                                {error}

                            </div>

                        )}


                        {/* =================================================
                            NO ENGINEERS
                        ================================================= */}

                        {!loadingEngineers &&
                            !error &&
                            engineers.length === 0 && (

                            <div className="assign-engineer-empty">

                                <UserRound
                                    size={25}
                                />

                                <strong>
                                    No active engineers found
                                </strong>

                                <span>
                                    There are no active
                                    ENGINEER users in the
                                    database.
                                </span>

                            </div>

                        )}


                        {/* =================================================
                            DATABASE ENGINEERS
                        ================================================= */}

                        {!loadingEngineers &&
                            !error &&
                            engineers.length > 0 && (

                            <div className="assign-engineer-list">

                                {engineers.map(
                                    (engineer) => {

                                        const isSelected =
                                            String(
                                                selectedEngineerId
                                            ) ===
                                            String(
                                                engineer.id
                                            );


                                        return (

                                            <button
                                                key={
                                                    engineer.id
                                                }

                                                type="button"

                                                className={
                                                    `assign-engineer-option ${
                                                        isSelected
                                                            ? "selected"
                                                            : ""
                                                    }`
                                                }

                                                onClick={() =>
                                                    setSelectedEngineerId(
                                                        String(
                                                            engineer.id
                                                        )
                                                    )
                                                }
                                            >

                                                {/* =================================
                                                    AVATAR
                                                ================================= */}

                                                <div className="assign-engineer-avatar">

                                                    {(
                                                        engineer.full_name ||
                                                        "E"
                                                    )
                                                        .charAt(0)
                                                        .toUpperCase()}

                                                </div>


                                                {/* =================================
                                                    DATABASE USER DATA
                                                ================================= */}

                                                <div className="assign-engineer-info">

                                                    <strong>

                                                        {
                                                            engineer.full_name ||
                                                            "Unnamed Engineer"
                                                        }

                                                    </strong>


                                                    <span>

                                                        <Phone
                                                            size={13}
                                                        />

                                                        {
                                                            engineer.phone ||
                                                            "No phone number"
                                                        }

                                                    </span>

                                                </div>


                                                {/* =================================
                                                    SELECTED
                                                ================================= */}

                                                <div className="assign-engineer-radio">

                                                    {isSelected && (

                                                        <CheckCircle2
                                                            size={20}
                                                        />

                                                    )}

                                                </div>

                                            </button>

                                        );

                                    }
                                )}

                            </div>

                        )}


                        {/* =================================================
                            SELECTED ENGINEER
                        ================================================= */}

                        {selectedEngineer && (

                            <div className="assign-engineer-selected">

                                <CheckCircle2
                                    size={18}
                                />

                                <div>

                                    <span>
                                        Selected Engineer
                                    </span>

                                    <strong>
                                        {
                                            selectedEngineer.full_name
                                        }
                                    </strong>

                                </div>

                            </div>

                        )}

                    </div>


                    {/* =================================================
                        FOOTER
                    ================================================= */}

                    <div className="assign-engineer-footer">

                        <button
                            type="button"

                            className="assign-engineer-cancel"

                            onClick={
                                handleClose
                            }

                            disabled={
                                assigning
                            }
                        >

                            Cancel

                        </button>


                        <button
                            type="submit"

                            className="assign-engineer-submit"

                            disabled={
                                assigning ||
                                loadingEngineers ||
                                engineers.length === 0 ||
                                !selectedEngineerId
                            }
                        >

                            {assigning ? (

                                <>

                                    <Loader2
                                        size={17}
                                        className="assign-engineer-spinner"
                                    />

                                    Assigning...

                                </>

                            ) : (

                                <>

                                    <CheckCircle2
                                        size={17}
                                    />

                                    Assign Engineer

                                </>

                            )}

                        </button>

                    </div>

                </form>

            </div>

        </div>

    );

};


export default AssignEngineerModal;