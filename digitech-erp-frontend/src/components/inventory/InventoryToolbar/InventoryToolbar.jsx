import "./InventoryToolbar.css";

import {
    Search,
    History,
} from "lucide-react";

import { useInventory } from "../../../context/InventoryContext";
import { useWarehouses } from "../../../context/WarehouseContext";


const InventoryToolbar = () => {

    const {
        search,
        setSearch,

        warehouse,
        setWarehouse,

        status,
        setStatus,

        setPage,
    } = useInventory();


    const {
        warehouses = [],
    } = useWarehouses();


    // =====================================================
    // Search
    // =====================================================

    const handleSearch = (e) => {

        setSearch(
            e.target.value
        );

        // Always return to first page
        // when the search changes.

        setPage(1);

    };


    // =====================================================
    // Warehouse
    // =====================================================

    const handleWarehouse = (e) => {

        setWarehouse(
            e.target.value
        );

        // Reset pagination.

        setPage(1);

    };


    // =====================================================
    // Status
    // =====================================================

    const handleStatus = (e) => {

        setStatus(
            e.target.value
        );

        // Reset pagination.

        setPage(1);

    };


    // =====================================================
    // Stock Transfer History
    // =====================================================

    const handleTransferHistory = () => {

        window.dispatchEvent(
            new CustomEvent(
                "openTransferHistory"
            )
        );

    };


    return (

        <div className="inventory-toolbar">


            {/* =================================================
                Search
            ================================================= */}

            <div className="toolbar-search">

                <Search size={18} />

                <input
                    type="text"
                    placeholder="Search Product, SKU, Barcode, Brand, Category, Warehouse..."
                    value={search || ""}
                    onChange={handleSearch}
                />

            </div>


            {/* =================================================
                Warehouse
            ================================================= */}

            <select
                value={warehouse || ""}
                onChange={handleWarehouse}
            >

                <option value="">
                    All Warehouses
                </option>


                {warehouses.map((item) => (

                    <option
                        key={item.id}
                        value={item.id}
                    >

                        {item.warehouse_name}

                    </option>

                ))}

            </select>


            {/* =================================================
                Status
            ================================================= */}

            <select
                value={status || ""}
                onChange={handleStatus}
            >

                <option value="">
                    All Status
                </option>


                <option value="IN_STOCK">
                    In Stock
                </option>


                <option value="LOW_STOCK">
                    Low Stock
                </option>


                <option value="OUT_OF_STOCK">
                    Out Of Stock
                </option>

            </select>


            {/* =================================================
                Stock Transfer History
            ================================================= */}

            <button
                type="button"
                className="transfer-history-btn"
                onClick={handleTransferHistory}
            >

                <History size={18} />

                <span>
                    Stock Transfer History
                </span>

            </button>


        </div>

    );

};


export default InventoryToolbar;