import "./SalesPage.css";

import {
    SalesProvider,
    useSales,
} from "../../context/SalesContext";

import SalesCards from "../../components/sales/SalesCards/SalesCards";
import SalesToolbar from "../../components/sales/SalesToolbar/SalesToolbar";
import SalesTable from "../../components/sales/SalesTable/SalesTable";
import SalesDrawer from "../../components/sales/SalesDrawer/SalesDrawer";

import DashboardLayout from "../../layouts/DashboardLayout";


// =====================================================
// Sales Content
// =====================================================

const SalesContent = () => {

    const {
        drawerOpen,
    } = useSales();


    return (

        <div className="sales-page">

            {/* =========================================
                Page Header
            ========================================= */}

            <div className="sales-page-header">

                <div className="sales-page-title-row">

                    <h1>
                        Sales
                    </h1>

                    <span className="sales-page-subtitle">
                        (Manage sales orders, invoices, payments and deliveries)
                    </span>

                </div>


                <div className="sales-page-actions">
                </div>

            </div>


            {/* =========================================
                Sales KPI Cards
            ========================================= */}

            <SalesCards />


            {/* =========================================
                Sales Toolbar
            ========================================= */}

            <SalesToolbar />


            {/* =========================================
                Sales Table
            ========================================= */}

            <SalesTable />


            {/* =========================================
                Sales Drawer
            ========================================= */}

            {drawerOpen && (
                <SalesDrawer />
            )}

        </div>

    );

};


// =====================================================
// Sales Page
// =====================================================

const SalesPage = () => {

    return (

        <DashboardLayout>

            <SalesProvider>

                <SalesContent />

            </SalesProvider>

        </DashboardLayout>

    );

};


export default SalesPage;