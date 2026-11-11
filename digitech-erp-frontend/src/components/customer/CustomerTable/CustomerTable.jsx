import React from "react";
import "./CustomerTable.css";

import {
    Eye,
    Pencil,
    Trash2,
} from "lucide-react";

import { useCustomers } from "../../../context/CustomerContext";
import { toast } from "react-toastify";


const CustomerTable = () => {

    const {
        customers,
        loading,
        error,
        setSelectedCustomer,
        loadCustomer,
        deleteCustomer,
    } = useCustomers();


    // =====================================================
    // Format Money
    // =====================================================

    const formatMoney = (value) => {

        return `₹${Number(
            value || 0
        ).toLocaleString("en-IN", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        })}`;

    };


    // =====================================================
    // Get Customer Machines
    // =====================================================

    const getCustomerMachines = (customer) => {
        /*
         * Preferred API format:
         *
         * customer.machines = [
         *   {
         *     id,
         *     machine_number,
         *     machine_name,
         *     serial_number
         *   }
         * ]
         *
         * A customer can have multiple machines.
         *
         * The fallback fields are kept for older API responses.
         */

        if (
            Array.isArray(customer?.machines) &&
            customer.machines.length > 0
        ) {
            return customer.machines;
        }

        if (
            customer?.machine &&
            typeof customer.machine === "object"
        ) {
            return [customer.machine];
        }

        if (
            customer?.machine_name ||
            customer?.machine_serial_number ||
            customer?.serial_number ||
            customer?.machine_number
        ) {
            return [
                {
                    id: customer.machine_id || null,
                    machine_number:
                        customer.machine_number || null,
                    machine_name:
                        customer.machine_name || null,
                    serial_number:
                        customer.machine_serial_number ||
                        customer.serial_number ||
                        null,
                },
            ];
        }

        return [];
    };


    // =====================================================
    // Machine Cell
    // =====================================================

    const renderMachine = (customer) => {
        const machines = getCustomerMachines(customer);

        if (machines.length === 0) {
            return (
                <span className="customer-machine-empty">
                    —
                </span>
            );
        }

        return (
            <div
                className="customer-machine-list"
                style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    justifyContent: "center",
                    gap: "8px",
                    width: "100%",
                    minWidth: "180px",
                    maxWidth: "260px",
                }}
            >
                {machines.map((machine, index) => {
                    const machineName =
                        machine?.machine_name ||
                        machine?.name ||
                        null;

                    const serialNumber =
                        machine?.serial_number ||
                        machine?.machine_serial_number ||
                        machine?.serialNo ||
                        null;

                    const machineNumber =
                        machine?.machine_number ||
                        null;

                    if (
                        !machineName &&
                        !serialNumber &&
                        !machineNumber
                    ) {
                        return null;
                    }

                    return (
                        <div
                            key={
                                machine?.id ||
                                machine?.machine_id ||
                                `${customer.id}-machine-${index}`
                            }
                            className="customer-machine-item"
                            style={{
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "flex-start",
                                gap: "2px",
                                width: "100%",
                                lineHeight: "1.3",
                            }}
                        >
                            {machineName && (
                                <span
                                    className="customer-machine-name"
                                    style={{
                                        fontSize: "13px",
                                        fontWeight: 700,
                                        color: "#14213d",
                                        whiteSpace: "nowrap",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                        maxWidth: "250px",
                                    }}
                                    title={machineName}
                                >
                                    {machineName}
                                </span>
                            )}

                            {serialNumber && (
                                <span
                                    className="customer-machine-serial"
                                    style={{
                                        fontSize: "11px",
                                        fontWeight: 500,
                                        color: "#64748b",
                                        whiteSpace: "nowrap",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                        maxWidth: "250px",
                                    }}
                                    title={serialNumber}
                                >
                                    <span
                                        style={{
                                            fontWeight: 600,
                                            color: "#475569",
                                        }}
                                    >
                                        Serial No:
                                    </span>{" "}
                                    {serialNumber}
                                </span>
                            )}

                            {false && machineNumber && (
                                <span
                                    className="customer-machine-number"
                                    style={{
                                        fontSize: "10px",
                                        fontWeight: 500,
                                        color: "#94a3b8",
                                        whiteSpace: "nowrap",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                        maxWidth: "250px",
                                    }}
                                    title={machineNumber}
                                >
                                    <span
                                        style={{
                                            fontWeight: 600,
                                            color: "#64748b",
                                        }}
                                    >
                                        Machine No:
                                    </span>{" "}
                                    {machineNumber}
                                </span>
                            )}
                        </div>
                    );
                })}
            </div>
        );
    };


    // =====================================================
    // View
    // =====================================================

    const handleView = async (customer) => {

        try {

            const fullCustomer =
                await loadCustomer(customer.id);

            setSelectedCustomer({
                ...fullCustomer,
                __view: true,
            });

        } catch (error) {

            console.error(
                "Failed to load customer details:",
                error
            );

            toast.error(
                error?.response?.data?.detail ||
                "Failed to load customer details."
            );

        }

    };


    // =====================================================
    // Edit
    // =====================================================

    const handleEdit = async (customer) => {

        try {

            const fullCustomer =
                await loadCustomer(customer.id);

            setSelectedCustomer({
                ...fullCustomer,
                __edit: true,
            });

        } catch (error) {

            console.error(
                "Failed to load customer for editing:",
                error
            );

            toast.error(
                error?.response?.data?.detail ||
                "Failed to load customer details."
            );

        }

    };


    // =====================================================
    // Delete
    // =====================================================

    const handleDelete = async (customer) => {

        const confirmed = window.confirm(
            `Are you sure you want to delete "${customer.customer_name}"?`
        );


        if (!confirmed) {

            return;

        }


        try {

            await deleteCustomer(
                customer.id
            );


            toast.success(
                "Customer deleted successfully."
            );

        } catch (error) {

            console.error(
                "Customer delete failed:",
                error
            );


            toast.error(
                error?.response?.data?.detail ||
                "Failed to delete customer."
            );

        }

    };


    // =====================================================
    // Loading
    // =====================================================

    if (
        loading &&
        customers.length === 0
    ) {

        return (

            <div className="customer-table-container">

                <div className="customer-table-message">

                    Loading customers...

                </div>

            </div>

        );

    }


    // =====================================================
    // Error
    // =====================================================

    if (
        error &&
        customers.length === 0
    ) {

        return (

            <div className="customer-table-container">

                <div className="customer-table-error">

                    {error}

                </div>

            </div>

        );

    }


    // =====================================================
    // Table
    // =====================================================

    return (

        <div className="customer-table-container">

            <div className="customer-table-scroll">

                <table className="customer-table">

                    <thead>

                        <tr>

                            {/* Customer Code */}

                            <th>
                                Customer Code
                            </th>


                            {/* Customer Name */}

                            <th>
                                Customer Name
                            </th>


                            {/* Machine */}

                            <th>
                                Machine
                            </th>


                            {/* Contact Person */}

                            <th>
                                Contact Person
                            </th>


                            {/* Phone */}

                            <th>
                                Phone
                            </th>


                            {/* Email */}

                            <th>
                                Email
                            </th>


                            {/* City */}

                            <th>
                                City
                            </th>


                            {/* Balance */}

                            <th>
                                Balance
                            </th>


                            {/* Status */}

                            <th>
                                Status
                            </th>


                            {/* Actions */}

                            <th>
                                Actions
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        {customers.map(
                            (customer) => (

                                <tr
                                    key={customer.id}
                                >

                                    {/* =================================
                                        Customer Code
                                    ================================= */}

                                    <td>

                                        <span className="customer-code">

                                            {customer.customer_code}

                                        </span>

                                    </td>


                                    {/* =================================
                                        Customer Name
                                    ================================= */}

                                    <td>

                                        <div className="customer-name-cell">

                                            <strong>

                                                {customer.customer_name}

                                            </strong>

                                        </div>

                                    </td>


                                    {/* =================================
                                        Machine
                                    ================================= */}

                                    <td>

                                        {renderMachine(
                                            customer
                                        )}

                                    </td>


                                    {/* =================================
                                        Contact Person
                                    ================================= */}

                                    <td>

                                        {customer.contact_person || "—"}

                                    </td>


                                    {/* =================================
                                        Phone
                                    ================================= */}

                                    <td>

                                        {customer.phone || "—"}

                                    </td>


                                    {/* =================================
                                        Email
                                    ================================= */}

                                    <td>

                                        <span className="customer-email">

                                            {customer.email || "—"}

                                        </span>

                                    </td>


                                    {/* =================================
                                        City
                                    ================================= */}

                                    <td>

                                        {customer.city || "—"}

                                    </td>


                                    {/* =================================
                                        Balance
                                    ================================= */}

                                    <td>

                                        <span
                                            className={
                                                Number(
                                                    customer.current_balance || 0
                                                ) > 0
                                                    ? "customer-balance pending"
                                                    : "customer-balance"
                                            }
                                        >

                                            {formatMoney(
                                                customer.current_balance
                                            )}

                                        </span>

                                    </td>


                                    {/* =================================
                                        Status
                                    ================================= */}

                                    <td>

                                        <span
                                            className={
                                                customer.is_active
                                                    ? "customer-status active"
                                                    : "customer-status inactive"
                                            }
                                        >

                                            {customer.is_active
                                                ? "Active"
                                                : "Inactive"
                                            }

                                        </span>

                                    </td>


                                    {/* =================================
                                        Actions
                                    ================================= */}

                                    <td>

                                        <div className="customer-actions">

                                            {/* View */}

                                            <button
                                                type="button"
                                                title="View"
                                                onClick={() =>
                                                    handleView(
                                                        customer
                                                    )
                                                }
                                            >

                                                <Eye size={16} />

                                            </button>


                                            {/* Edit */}

                                            <button
                                                type="button"
                                                title="Edit"
                                                onClick={() =>
                                                    handleEdit(
                                                        customer
                                                    )
                                                }
                                            >

                                                <Pencil size={16} />

                                            </button>


                                            {/* Delete */}

                                            <button
                                                type="button"
                                                title="Delete"
                                                className="customer-delete-btn"
                                                onClick={() =>
                                                    handleDelete(
                                                        customer
                                                    )
                                                }
                                            >

                                                <Trash2 size={17} />

                                            </button>

                                        </div>

                                    </td>

                                </tr>

                            )
                        )}


                        {/* =================================
                            Empty
                        ================================= */}

                        {customers.length === 0 && (

                            <tr>

                                <td
                                    colSpan="10"
                                    className="customer-empty"
                                >

                                    No customers found.

                                </td>

                            </tr>

                        )}

                    </tbody>

                </table>

            </div>

        </div>

    );

};


export default CustomerTable;