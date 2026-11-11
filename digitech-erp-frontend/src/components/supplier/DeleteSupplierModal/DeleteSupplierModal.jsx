import "./DeleteSupplierModal.css";

import { Trash2, X } from "lucide-react";

import { useSupplier } from "../../../context/SupplierContext";

const DeleteSupplierModal = () => {
    const {
        deleteModalOpen,
        setDeleteModalOpen,
        selectedSupplier,
        deleteSupplier,
        loading,
    } = useSupplier();

    if (!deleteModalOpen) return null;

    return (
        <div className="delete-modal-overlay">
            <div className="delete-modal">
                <div className="delete-modal-header">
                    <div className="delete-icon">
                        <Trash2 size={24} />
                    </div>
                    <button
                        className="close-btn"
                        onClick={() => setDeleteModalOpen(false)}
                    >
                        <X size={20} />
                    </button>
                </div>

                <div className="delete-modal-body">
                    <h2>Delete Supplier</h2>
                    <p>
                        Are you sure you want to delete
                        <strong>
                            {" "}
                            {selectedSupplier?.company_name}
                            {" "}
                        </strong>
                        ?
                    </p>
                    <p className="warning">
                        This action cannot be undone.
                    </p>
                </div>

                <div className="delete-modal-footer">
                    <button
                        className="btn-light"
                        onClick={() => setDeleteModalOpen(false)}
                    >
                        Cancel
                    </button>
                    <button
                        className="btn-danger"
                        onClick={() => {
                            console.log("Delete button clicked");
                            deleteSupplier();
                        }}
                        disabled={loading}
                    >
                        {loading ? "Deleting..." : "Delete"}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DeleteSupplierModal;