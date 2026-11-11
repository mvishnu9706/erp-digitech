import "./CustomerToolbar.css";

import {
    Search,
    RotateCcw,
    Plus,
} from "lucide-react";

import { useEffect, useState } from "react";

import { useCustomers } from "../../../context/CustomerContext";


const CustomerToolbar = () => {

    const {
        filters,
        updateFilter,
        resetFilters,
        loadCustomers,
        setSelectedCustomer,
    } = useCustomers();


    const [localSearch, setLocalSearch] = useState(
        filters?.search || ""
    );


    // =====================================================
    // Keep Search Synchronized
    // =====================================================

    useEffect(() => {

        setLocalSearch(
            filters?.search || ""
        );

    }, [filters?.search]);


    // =====================================================
    // Search
    // =====================================================

    const handleSearch = (e) => {

        const value = e.target.value;

        setLocalSearch(value);

        updateFilter(
            "search",
            value
        );

    };


    // =====================================================
    // Status
    // =====================================================

    const handleStatusChange = (e) => {

        const value = e.target.value;

        if (value === "") {

            updateFilter(
                "is_active",
                ""
            );

        } else {

            updateFilter(
                "is_active",
                value === "true"
            );

        }

    };


    // =====================================================
    // Reset
    // =====================================================

    const handleReset = () => {

        setLocalSearch("");

        resetFilters();

    };


    // =====================================================
    // Apply Filters
    // =====================================================

    useEffect(() => {

        const timer = setTimeout(() => {

            loadCustomers(filters);

        }, 300);

        return () => clearTimeout(timer);

    }, [
        filters.search,
        filters.city,
        filters.state,
        filters.is_active,
        filters.page,
        filters.page_size,
    ]);


    return (

        <div className="customer-toolbar">

            {/* Search */}

            <div className="customer-search-box">

                <Search size={18} />

                <input
                    type="text"
                    placeholder="Search customer, code, phone..."
                    value={localSearch}
                    onChange={handleSearch}
                />

            </div>


            {/* Status */}

            <select
                value={
                    filters?.is_active === ""
                        ? ""
                        : String(filters?.is_active)
                }
                onChange={handleStatusChange}
            >

                <option value="">
                    All Status
                </option>

                <option value="true">
                    Active
                </option>

                <option value="false">
                    Inactive
                </option>

            </select>


            {/* Reset */}

            <button
                type="button"
                className="customer-reset-btn"
                onClick={handleReset}
            >

                <RotateCcw size={16} />

                Reset

            </button>


            {/* Add */}

            <button
                type="button"
                className="customer-add-btn"
                onClick={() =>
                    setSelectedCustomer({
                        __create: true
                    })
                }
            >

                <Plus size={18} />

                Add Customer

            </button>

        </div>

    );

};


export default CustomerToolbar;