import "./CustomerPage.css";

import DashboardLayout from "../../layouts/DashboardLayout";

import CustomerCards from "../../components/customer/CustomerCards/CustomerCards";
import CustomerToolbar from "../../components/customer/CustomerToolbar/CustomerToolbar";
import CustomerTable from "../../components/customer/CustomerTable/CustomerTable";
import CustomerForm from "../../components/customer/CustomerForm/CustomerForm";

import { Download } from "lucide-react";

import { useCustomers } from "../../context/CustomerContext";

import customerService from "../../services/customerService";


const CustomerPage = () => {

    const {
        selectedCustomer,
        filters,
    } = useCustomers();


    // =====================================================
    // EXPORT CUSTOMERS
    // =====================================================

    const handleExport = async () => {

        try {

            // ---------------------------------------------
            // Send only the actual filters.
            //
            // page and page_size are NOT sent because
            // export should download ALL matching records.
            // ---------------------------------------------

            const exportParams = {};

            if (
                filters?.search &&
                filters.search.trim() !== ""
            ) {

                exportParams.search =
                    filters.search.trim();

            }


            if (
                filters?.city &&
                filters.city.trim() !== ""
            ) {

                exportParams.city =
                    filters.city.trim();

            }


            if (
                filters?.state &&
                filters.state.trim() !== ""
            ) {

                exportParams.state =
                    filters.state.trim();

            }


            // ---------------------------------------------
            // Status
            //
            // ""     = all customers
            // true   = active
            // false  = inactive
            // ---------------------------------------------

            if (
                filters?.is_active !== "" &&
                filters?.is_active !== undefined &&
                filters?.is_active !== null
            ) {

                exportParams.is_active =
                    filters.is_active;

            }


            console.log(
                "Export filters:",
                exportParams
            );


            // ---------------------------------------------
            // Request Excel file
            // ---------------------------------------------

            const blob =
                await customerService.exportCustomers(
                    exportParams
                );


            // ---------------------------------------------
            // Create download URL
            // ---------------------------------------------

            const url =
                window.URL.createObjectURL(
                    blob
                );


            // ---------------------------------------------
            // Create temporary download link
            // ---------------------------------------------

            const link =
                document.createElement("a");

            link.href = url;

            link.download =
                `Customers_${new Date()
                    .toISOString()
                    .split("T")[0]
                }.xlsx`;


            document.body.appendChild(
                link
            );


            link.click();


            document.body.removeChild(
                link
            );


            // ---------------------------------------------
            // Clean URL
            // ---------------------------------------------

            window.URL.revokeObjectURL(
                url
            );


        }
        catch (error) {

            console.error(
                "Customer Export Error:",
                error
            );

            alert(
                "Failed to export customers."
            );

        }

    };


    return (

        <DashboardLayout>

            <div className="customer-page">


                {/* =====================================
                    HEADER
                ===================================== */}

                <div className="customer-page-header">

                    <div>

                        <h1>
                            Customers
                        </h1>

                        <p>
                            Manage your customers and their account information.
                        </p>

                    </div>


                    {/* =================================
                        EXPORT BUTTON
                    ================================= */}

                    <button
                        type="button"
                        className="customer-export-btn"
                        onClick={handleExport}
                    >

                        <Download
                            size={18}
                        />

                        Export

                    </button>

                </div>


                {/* =====================================
                    CARDS
                ===================================== */}

                <CustomerCards />


                {/* =====================================
                    TOOLBAR
                ===================================== */}

                <CustomerToolbar />


                {/* =====================================
                    TABLE
                ===================================== */}

                <CustomerTable />


                {/* =====================================
                    ADD / EDIT CUSTOMER DRAWER
                ===================================== */}

                {selectedCustomer && (

                    <CustomerForm />

                )}

            </div>

        </DashboardLayout>

    );

};


export default CustomerPage;