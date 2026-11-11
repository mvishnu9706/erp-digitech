import React from "react";

import {
    AlertTriangle,
    X,
    Ban,
} from "lucide-react";

import "./DeleteServiceModal.css";


const DeleteServiceModal = ({
    open,
    service,
    onClose,
    onConfirm,
    loading = false,
}) => {

    if (!open) {
        return null;
    }


    const ticketNumber =
        service?.ticket_number ||
        service?.ticket_id ||
        service?.id ||
        "-";


    return (
        <div
            className="delete-service-modal-overlay"
            onMouseDown={(event) => {
                if (
                    event.target === event.currentTarget &&
                    !loading
                ) {
                    onClose?.();
                }
            }}
        >

            <div
                className="delete-service-modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="cancel-service-title"
            >

                {/* =========================================
                    CLOSE
                ========================================= */}

                <button
                    type="button"
                    className="delete-service-modal-close"
                    onClick={onClose}
                    disabled={loading}
                    aria-label="Close"
                >
                    <X size={20} />
                </button>


                {/* =========================================
                    WARNING ICON
                ========================================= */}

                <div className="delete-service-modal-icon">
                    <AlertTriangle size={28} />
                </div>


                {/* =========================================
                    TITLE
                ========================================= */}

                <h2 id="cancel-service-title">
                    Cancel Service?
                </h2>


                {/* =========================================
                    MESSAGE
                ========================================= */}

                <p className="delete-service-modal-message">
                    Are you sure you want to cancel service
                    ticket{" "}
                    <strong>
                        {ticketNumber}
                    </strong>
                    ?
                </p>


                {/* =========================================
                    IMPORTANT NOTE
                ========================================= */}

                <p className="delete-service-modal-note">
                    The service ticket will remain in the
                    system. Only its status will change to{" "}
                    <strong>Cancelled</strong>.
                </p>


                {/* =========================================
                    ACTIONS
                ========================================= */}

                <div className="delete-service-modal-actions">

                    <button
                        type="button"
                        className="delete-service-modal-cancel"
                        onClick={onClose}
                        disabled={loading}
                    >
                        Cancel
                    </button>


                    <button
                        type="button"
                        className="delete-service-modal-confirm"
                        onClick={onConfirm}
                        disabled={loading}
                    >
                        <Ban size={17} />

                        {loading
                            ? "Cancelling..."
                            : "Confirm Cancel"}
                    </button>

                </div>

            </div>

        </div>
    );
};


export default DeleteServiceModal;
