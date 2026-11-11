import "./PurchaseToolbar.css";
import { useState, useEffect } from "react";
import {
    Search,
    RotateCcw,
    Download,
    BarChart3,
    Plus,
} from "lucide-react";
import { usePurchase } from "../../../context/PurchaseContext";

const PurchaseToolbar = () => {

    const {
        filters,
        suppliers,
        warehouses,
        updateFilter,
        loadPurchaseOrders,
        openCreateDrawer,
        exportPurchases,
    } = usePurchase();

    const [search, setSearch] = useState(filters.search || "");

    useEffect(() => {

        const timer = setTimeout(() => {

            updateFilter("search", search);

            loadPurchaseOrders({
                ...filters,
                search,
            });

        }, 500);

        return () => clearTimeout(timer);

    }, [search]);

    return (

        <div className="purchase-toolbar">

            <div className="toolbar-left">

                <div className="search-box">

                    <Search size={18} />

                    <input
                        type="text"
                        placeholder="Search PO, Supplier, Warehouse"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />

                </div>

                {/* Supplier */}

                <select
                    value={filters.supplier_id || ""}
                    onChange={(e) =>
                        updateFilter(
                            "supplier_id",
                            e.target.value || ""
                        )
                    }
                >

                    <option value="">
                        All Suppliers
                    </option>

                    {suppliers.map((supplier) => (

                        <option
                            key={supplier.id}
                            value={supplier.id}
                        >
                            {supplier.company_name}
                        </option>

                    ))}

                </select>

                {/* Warehouse */}

                <select
                    value={filters.warehouse_id || ""}
                    onChange={(e) =>
                        updateFilter(
                            "warehouse_id",
                            e.target.value || ""
                        )
                    }
                >

                    <option value="">
                        All Warehouses
                    </option>

                    {warehouses?.map((warehouse) => (

                        <option
                            key={warehouse.id}
                            value={warehouse.id}
                        >
                            {warehouse.warehouse_name}
                        </option>

                    ))}

                </select>

                {/* Date From */}

                <input
                    type="date"
                    value={filters.date_from || ""}
                    onChange={(e) =>
                        updateFilter(
                            "date_from",
                            e.target.value
                        )
                    }
                />

                {/* Date To */}

                <input
                    type="date"
                    value={filters.date_to || ""}
                    onChange={(e) =>
                        updateFilter(
                            "date_to",
                            e.target.value
                        )
                    }
                />

            </div>

            <div className="toolbar-right">

                <button
                    className="toolbar-btn"
                    onClick={() => loadPurchaseOrders(filters)}
                >
                    <RotateCcw size={18} />
                    Refresh
                </button>

                <button 
                    className="toolbar-btn"
                    onClick={exportPurchases}
                >
                    <Download size={18} />
                    Export
                </button>

                <button className="toolbar-btn">
                    <BarChart3 size={18} />
                    Reports
                </button>

                <button
                    className="add-btn"
                    onClick={openCreateDrawer}
                >
                    <Plus size={18} />
                    New Purchase
                </button>

            </div>

        </div>

    );

};

export default PurchaseToolbar;