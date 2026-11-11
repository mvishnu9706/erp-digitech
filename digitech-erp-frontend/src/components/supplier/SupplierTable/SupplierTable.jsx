import "./SupplierTable.css";

import {
    Pencil,
    Trash2,
    Eye,
} from "lucide-react";

import { useSupplier } from "../../../context/SupplierContext";

const SupplierTable = () => {

    const {
        suppliers,
        loading,
        setDrawerOpen,
        setDrawerMode,
        setSelectedSupplier,
        setSupplierForm,
        setDeleteModalOpen,
    } = useSupplier();


    // ==========================================
    // Prepare Supplier Form
    // ==========================================

    const prepareSupplierForm = (supplier) => {

        return {
            company_name:
                supplier?.company_name ?? "",

            contact_person:
                supplier?.contact_person ?? "",

            phone:
                supplier?.phone ?? "",

            email:
                supplier?.email ?? "",

            gstin:
                supplier?.gstin ?? "",

            pan:
                supplier?.pan ?? "",

            city:
                supplier?.city ?? "",

            state:
                supplier?.state ?? "",

            address:
                supplier?.address ?? "",

            credit_limit:
                supplier?.credit_limit ?? 0,
        };
    };


    // ==========================================
    // View
    // ==========================================

    const handleView = (supplier) => {

        console.log(
            "VIEW SUPPLIER:",
            supplier
        );

        // Keep selected supplier
        setSelectedSupplier(supplier);

        // Load supplier data into form
        setSupplierForm(
            prepareSupplierForm(supplier)
        );

        // Open in view mode
        setDrawerMode("view");

        setDrawerOpen(true);
    };


    // ==========================================
    // Edit
    // ==========================================

    const handleEdit = (supplier) => {

        console.log(
            "EDIT SUPPLIER:",
            supplier
        );

        // Keep selected supplier
        setSelectedSupplier(supplier);

        // Load supplier data into form
        setSupplierForm(
            prepareSupplierForm(supplier)
        );

        // Open in edit mode
        setDrawerMode("edit");

        setDrawerOpen(true);
    };


    // ==========================================
    // Delete
    // ==========================================

    const handleDelete = (supplier) => {

        console.log(
            "Selected:",
            supplier
        );

        setSelectedSupplier(supplier);

        setDeleteModalOpen(true);
    };


    // ==========================================
    // Loading
    // ==========================================

    if (loading) {

        return (
            <div className="supplier-loading">
                Loading Suppliers...
            </div>
        );

    }


    // ==========================================
    // Render
    // ==========================================

    return (

        <div className="supplier-table-container">

            <table className="supplier-table">

                {/* ==========================================
                    Header
                ========================================== */}

                <thead>

                    <tr>

                        <th>
                            Supplier Code
                        </th>

                        <th>
                            Company
                        </th>

                        <th>
                            Contact Person
                        </th>

                        <th>
                            Phone
                        </th>

                        <th>
                            Email
                        </th>

                        <th>
                            City
                        </th>

                        <th>
                            Status
                        </th>

                        <th>
                            Balance
                        </th>

                        <th>
                            Actions
                        </th>

                    </tr>

                </thead>


                {/* ==========================================
                    Body
                ========================================== */}

                <tbody>

                    {

                        suppliers.length === 0 ? (

                            <tr>

                                <td
                                    colSpan="9"
                                    className="supplier-empty"
                                >
                                    No Suppliers Found
                                </td>

                            </tr>

                        ) : (

                            suppliers.map(
                                (supplier) => (

                                    <tr
                                        key={
                                            supplier.id
                                        }
                                    >

                                        {/* Supplier Code */}

                                        <td>

                                            {
                                                supplier.supplier_code
                                            }

                                        </td>


                                        {/* Company */}

                                        <td>

                                            {
                                                supplier.company_name
                                            }

                                        </td>


                                        {/* Contact Person */}

                                        <td>

                                            {
                                                supplier.contact_person
                                            }

                                        </td>


                                        {/* Phone */}

                                        <td>

                                            {
                                                supplier.phone
                                            }

                                        </td>


                                        {/* Email */}

                                        <td>

                                            {
                                                supplier.email
                                            }

                                        </td>


                                        {/* City */}

                                        <td>

                                            {
                                                supplier.city
                                            }

                                        </td>


                                        {/* Status */}

                                        <td>

                                            {

                                                supplier.is_active ?

                                                    (
                                                        <span
                                                            className="status active"
                                                        >
                                                            Active
                                                        </span>
                                                    )

                                                    :

                                                    (
                                                        <span
                                                            className="status inactive"
                                                        >
                                                            Inactive
                                                        </span>
                                                    )

                                            }

                                        </td>


                                        {/* Balance */}

                                        <td>

                                            ₹{" "}

                                            {
                                                Number(
                                                    supplier.current_balance ?? 0
                                                ).toLocaleString(
                                                    "en-IN"
                                                )
                                            }

                                        </td>


                                        {/* Actions */}

                                        <td>

                                            <div
                                                className="supplier-actions"
                                            >

                                                {/* =================================
                                                    View
                                                ================================= */}

                                                <button
                                                    type="button"
                                                    className="view-btn"
                                                    onClick={() =>
                                                        handleView(
                                                            supplier
                                                        )
                                                    }
                                                >

                                                    <Eye
                                                        size={18}
                                                    />

                                                </button>


                                                {/* =================================
                                                    Edit
                                                ================================= */}

                                                <button
                                                    type="button"
                                                    className="edit-btn"
                                                    onClick={() =>
                                                        handleEdit(
                                                            supplier
                                                        )
                                                    }
                                                >

                                                    <Pencil
                                                        size={18}
                                                    />

                                                </button>


                                                {/* =================================
                                                    Delete
                                                ================================= */}

                                                <button
                                                    type="button"
                                                    className="delete-btn"
                                                    onClick={() =>
                                                        handleDelete(
                                                            supplier
                                                        )
                                                    }
                                                >

                                                    <Trash2
                                                        size={18}
                                                    />

                                                </button>

                                            </div>

                                        </td>

                                    </tr>

                                )
                            )

                        )

                    }

                </tbody>

            </table>

        </div>

    );

};


export default SupplierTable;