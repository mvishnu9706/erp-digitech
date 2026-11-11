import "./SupplierPage.css";

import DashboardLayout from "../../layouts/DashboardLayout";

import DeleteSupplierModal from "../../components/supplier/DeleteSupplierModal/DeleteSupplierModal";

import {
    Plus,
    RefreshCcw,
    Download,
    BarChart3,
} from "lucide-react";

import SupplierCards from "../../components/supplier/SupplierCards/SupplierCards";
import SupplierToolbar from "../../components/supplier/SupplierToolbar/SupplierToolbar";
import SupplierTable from "../../components/supplier/SupplierTable/SupplierTable";
import SupplierDrawer from "../../components/supplier/SupplierDrawer/SupplierDrawer";

import { useSupplier } from "../../context/SupplierContext";

import { exportSuppliers } from "../../services/supplierService";


const SupplierPage = () => {

    const {
        reloadEverything,
        setDrawerOpen,
        setDrawerMode,
        setSelectedSupplier,
        filters,
    } = useSupplier();


    // ==========================================================
    // EXPORT SUPPLIERS
    // ==========================================================

    const handleExport = async () => {

        try {

            const exportParams = {

                search:
                    filters?.search?.trim()
                        ? filters.search.trim()
                        : undefined,

                city:
                    filters?.city?.trim()
                        ? filters.city.trim()
                        : undefined,

                state:
                    filters?.state?.trim()
                        ? filters.state.trim()
                        : undefined,

                is_active:
                    filters?.is_active !== ""
                        ? filters.is_active
                        : undefined,

            };


            const blob = await exportSuppliers(
                exportParams
            );


            // ==================================================
            // Create Download URL
            // ==================================================

            const url =
                window.URL.createObjectURL(blob);


            const link =
                document.createElement("a");


            link.href = url;


            link.download =
                `Suppliers_${new Date()
                    .toISOString()
                    .split("T")[0]}.xlsx`;


            document.body.appendChild(link);


            link.click();


            link.remove();


            window.URL.revokeObjectURL(url);

        }
        catch (error) {

            console.error(
                "Supplier Export Error:",
                error
            );


            alert(
                "Failed to export suppliers."
            );

        }

    };


    return (

        <DashboardLayout>

            <div className="supplier-page">


                {/* ==================================================
                   HEADER
                ================================================== */}

                <div className="supplier-header">


                    <div className="supplier-header-left">

                        <h1>
                            Supplier Management
                        </h1>


                        <p>
                            Manage suppliers, maintain company information,
                            contact details, payment terms and supplier records.
                        </p>

                    </div>


                    <div className="supplier-header-right">


                        {/* ==================================================
                           REFRESH
                        ================================================== */}

                        <button
                            type="button"
                            className="btn-light"
                            onClick={reloadEverything}
                        >

                            <RefreshCcw size={18} />

                            Refresh

                        </button>


                        {/* ==================================================
                           EXPORT
                        ================================================== */}

                        <button
                            type="button"
                            className="btn-light"
                            onClick={handleExport}
                        >

                            <Download size={18} />

                            Export

                        </button>


                        {/* ==================================================
                           REPORTS
                        ================================================== */}

                        <button
                            type="button"
                            className="btn-light"
                        >

                            <BarChart3 size={18} />

                            Reports

                        </button>


                        {/* ==================================================
                           ADD SUPPLIER
                        ================================================== */}

                        <button
                            type="button"
                            className="btn-primary"
                            onClick={() => {

                                setSelectedSupplier(null);

                                setDrawerMode("add");

                                setDrawerOpen(true);

                            }}
                        >

                            <Plus size={18} />

                            Add Supplier

                        </button>

                    </div>

                </div>


                {/* ==================================================
                   DASHBOARD CARDS
                ================================================== */}

                <SupplierCards />


                {/* ==================================================
                   TOOLBAR
                ================================================== */}

                <SupplierToolbar />


                {/* ==================================================
                   SUPPLIER TABLE
                ================================================== */}

                <SupplierTable />


                {/* ==================================================
                   SUPPLIER DRAWER
                ================================================== */}

                <SupplierDrawer />


                {/* ==================================================
                   DELETE MODAL
                ================================================== */}

                <DeleteSupplierModal />

            </div>

        </DashboardLayout>

    );

};


export default SupplierPage;