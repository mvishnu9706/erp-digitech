import DashboardLayout from "../../layouts/DashboardLayout";
import "./InventoryPage.css";

import {
    Plus,
    RefreshCcw,
    Download,
    BarChart3,
    ArrowRightLeft,
} from "lucide-react";

import InventoryCards from "../../components/inventory/InventoryCards/InventoryCards";
import InventoryToolbar from "../../components/inventory/InventoryToolbar/InventoryToolbar";
import InventoryTable from "../../components/inventory/InventoryTable/InventoryTable";
import InventoryDrawer from "../../components/inventory/InventoryDrawer/InventoryDrawer";
import TransferDrawer from "../../components/inventory/TransferDrawer/TransferDrawer";

// =====================================================
// NEW
// Stock Transfer History
// =====================================================

import StockTransferHistory from "../../components/inventory/StockTransferHistory/StockTransferHistory";

import { useInventory } from "../../context/InventoryContext";


const InventoryPage = () => {

    const {
        refreshInventory,
        downloadInventory,
        openAddDrawer,
        openTransferDrawer,
    } = useInventory();


    return (
        <DashboardLayout>

            <div className="inventory-page">

                {/* =================================================
                    Header
                ================================================= */}

                <div className="inventory-header">

                    <div className="inventory-header-left">

                        <h1>
                            Inventory Management
                        </h1>

                        <p>
                            Manage inventory across warehouses, track stock,
                            monitor movements and maintain accurate inventory.
                        </p>

                    </div>


                    <div className="inventory-header-right">

                        {/* Refresh */}

                        <button
                            className="btn-light"
                            onClick={refreshInventory}
                        >

                            <RefreshCcw size={18} />

                            Refresh

                        </button>


                        {/* Export */}

                        <button
                            className="btn-light"
                            onClick={downloadInventory}
                        >

                            <Download size={18} />

                            Export

                        </button>


                        {/* Reports */}

                        <button className="btn-light">

                            <BarChart3 size={18} />

                            Reports

                        </button>


                        {/* Stock Transfer */}

                        <button
                            className="btn-light"
                            onClick={() =>
                                openTransferDrawer(null)
                            }
                        >

                            <ArrowRightLeft size={18} />

                            Stock Transfer

                        </button>


                        {/* Add Inventory */}

                        <button
                            className="btn-primary"
                            onClick={openAddDrawer}
                        >

                            <Plus size={18} />

                            Add Inventory

                        </button>

                    </div>

                </div>


                {/* =================================================
                    Dashboard Cards
                ================================================= */}

                <InventoryCards />


                {/* =================================================
                    Toolbar
                ================================================= */}

                <InventoryToolbar />


                {/* =================================================
                    Inventory Table
                ================================================= */}

                <InventoryTable />


                {/* =================================================
                    Inventory Drawers
                ================================================= */}

                <TransferDrawer />

                <InventoryDrawer />


                {/* =================================================
                    Stock Transfer History
                ================================================= */}

                <StockTransferHistory />

            </div>

        </DashboardLayout>
    );
};


export default InventoryPage;