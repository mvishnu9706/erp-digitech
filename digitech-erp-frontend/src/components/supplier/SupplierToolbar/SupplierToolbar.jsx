import "./SupplierToolbar.css";
import { Search, RotateCcw } from "lucide-react";
import { useSupplier } from "../../../context/SupplierContext";

const SupplierToolbar = () => {
    const {
        filters,
        setFilters,
        reloadEverything,
    } = useSupplier();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFilters((prev) => ({
            ...prev,
            [name]: value,
            page: 1,
        }));
    };

    const handleReset = () => {
        setFilters({
            search: "",
            city: "",
            state: "",
            is_active: "",
            page: 1,
            page_size: 10,
        });
        reloadEverything();
    };

    return (
        <div className="supplier-toolbar">
            {/* Search */}
            <div className="toolbar-search">
                <Search size={18} />
                <input
                    type="text"
                    placeholder="Search Supplier..."
                    name="search"
                    value={filters.search}
                    onChange={handleChange}
                />
            </div>

            {/* City */}
            <input
                type="text"
                placeholder="City"
                name="city"
                value={filters.city}
                onChange={handleChange}
            />

            {/* State */}
            <input
                type="text"
                placeholder="State"
                name="state"
                value={filters.state}
                onChange={handleChange}
            />

            {/* Status */}
            <select
                name="is_active"
                value={filters.is_active}
                onChange={handleChange}
            >
                <option value="">All Status</option>
                <option value="true">Active</option>
                <option value="false">Inactive</option>
            </select>

            {/* Page Size */}
            <select
                name="page_size"
                value={filters.page_size}
                onChange={handleChange}
            >
                <option value="10">10</option>
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
            </select>

            {/* Reset */}
            <button
                className="btn-light"
                onClick={handleReset}
            >
                <RotateCcw size={18} />
                Reset
            </button>
        </div>
    );
};

export default SupplierToolbar;