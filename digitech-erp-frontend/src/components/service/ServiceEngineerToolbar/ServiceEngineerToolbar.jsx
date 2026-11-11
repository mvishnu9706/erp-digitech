import React, { useMemo } from "react";

import {
    Search,
    Users,
    CalendarDays,
    Filter,
    RotateCcw,
} from "lucide-react";

import "./ServiceEngineerToolbar.css";

/**
 * =========================================================
 * SERVICE ENGINEER TOOLBAR
 * =========================================================
 *
 * Used only by Engineer Service Management.
 *
 * Features:
 * - Search service records
 * - Select engineer
 * - Select From date
 * - Select To date
 * - Apply filters
 * - Reset filters
 *
 * Engineer values are intentionally stored as ENGINEER NAME
 * because ServiceEngineerDetails filters the service records
 * using the engineer name.
 */

const ServiceEngineerToolbar = ({
    engineers = [],

    selectedEngineer = "",
    setSelectedEngineer,

    dateFrom = "",
    setDateFrom,

    dateTo = "",
    setDateTo,

    onFilter,
    onReset,

    search = "",
    setSearch,
}) => {
    /* =====================================================
       NORMALIZE ENGINEER LIST
    ===================================================== */

    const normalizedEngineers = useMemo(() => {
        if (!Array.isArray(engineers)) {
            return [];
        }

        const names = engineers
            .map((engineer) => {
                /*
                 * Support both:
                 *
                 * "Arjun Kumar"
                 *
                 * {
                 *   id: 1,
                 *   name: "Arjun Kumar"
                 * }
                 */

                if (
                    typeof engineer ===
                    "string"
                ) {
                    return engineer
                        .trim();
                }

                if (
                    engineer &&
                    typeof engineer ===
                        "object"
                ) {
                    return String(
                        engineer.full_name ||
                        engineer.name ||
                        engineer.username ||
                        engineer.engineer_name ||
                        engineer.technician ||
                        ""
                    ).trim();
                }

                return "";
            })
            .filter((name) => {
                const value =
                    String(name)
                        .trim()
                        .toLowerCase();

                return (
                    value !== "" &&
                    value !== "-" &&
                    value !== "unassigned"
                );
            });

        /*
         * Remove duplicate engineer names.
         */
        return [
            ...new Set(names),
        ].sort((a, b) =>
            a.localeCompare(b)
        );
    }, [engineers]);

    /* =====================================================
       SEARCH
    ===================================================== */

    const handleSearchChange = (
        event
    ) => {
        const value =
            event.target.value;

        if (
            typeof setSearch ===
            "function"
        ) {
            setSearch(value);
        }
    };

    /* =====================================================
       ENGINEER
    ===================================================== */

    const handleEngineerChange = (
        event
    ) => {
        const value =
            event.target.value;

        if (
            typeof setSelectedEngineer ===
            "function"
        ) {
            setSelectedEngineer(value);
        }
    };

    /* =====================================================
       FROM DATE
    ===================================================== */

    const handleDateFromChange = (
        event
    ) => {
        const value =
            event.target.value;

        if (
            typeof setDateFrom ===
            "function"
        ) {
            setDateFrom(value);
        }

        /*
         * If From becomes later than To,
         * automatically move To to the same
         * date.
         */
        if (
            value &&
            dateTo &&
            value > dateTo
        ) {
            if (
                typeof setDateTo ===
                "function"
            ) {
                setDateTo(value);
            }
        }
    };

    /* =====================================================
       TO DATE
    ===================================================== */

    const handleDateToChange = (
        event
    ) => {
        const value =
            event.target.value;

        /*
         * Do not allow To date before From date.
         */
        if (
            value &&
            dateFrom &&
            value < dateFrom
        ) {
            if (
                typeof setDateTo ===
                "function"
            ) {
                setDateTo(dateFrom);
            }

            return;
        }

        if (
            typeof setDateTo ===
            "function"
        ) {
            setDateTo(value);
        }
    };

    /* =====================================================
       APPLY FILTER
    ===================================================== */

    const handleFilter = () => {
        if (
            typeof onFilter ===
            "function"
        ) {
            onFilter();
        }
    };

    /* =====================================================
       RESET
    ===================================================== */

    const handleReset = () => {
        if (
            typeof onReset ===
            "function"
        ) {
            onReset();
        }
    };

    /* =====================================================
       CLEAR SEARCH
       Used when reset is clicked if the parent does not
       clear it immediately.
    ===================================================== */

    const hasFilters =
        Boolean(
            selectedEngineer ||
            dateFrom ||
            dateTo ||
            search
        );

    /* =====================================================
       RENDER
    ===================================================== */

    return (
        <div className="service-engineer-toolbar">

            {/* =================================================
               SEARCH
            ================================================= */}

            <div className="service-engineer-toolbar-search">

                <Search
                    size={17}
                    aria-hidden="true"
                />

                <input
                    type="text"
                    value={
                        search || ""
                    }
                    onChange={
                        handleSearchChange
                    }
                    placeholder="Search ticket, customer, product, phone..."
                    aria-label="Search engineer services"
                />

            </div>

            {/* =================================================
               ENGINEER
            ================================================= */}

            <div className="service-engineer-toolbar-field engineer-select-field">

                <label
                    htmlFor="service-engineer-filter"
                >
                    <Users
                        size={15}
                        aria-hidden="true"
                    />

                    <span>
                        Engineer
                    </span>
                </label>

                <select
                    id="service-engineer-filter"
                    value={
                        selectedEngineer ||
                        ""
                    }
                    onChange={
                        handleEngineerChange
                    }
                    aria-label="Filter by engineer"
                >

                    {/* ALL ENGINEERS */}

                    <option value="">
                        All Engineers
                    </option>

                    {/* ENGINEERS */}

                    {normalizedEngineers.map(
                        (
                            engineerName
                        ) => (
                            <option
                                key={
                                    engineerName
                                }
                                value={
                                    engineerName
                                }
                            >
                                {
                                    engineerName
                                }
                            </option>
                        )
                    )}

                </select>

            </div>

            {/* =================================================
               FROM DATE
            ================================================= */}

            <div className="service-engineer-toolbar-field">

                <label
                    htmlFor="service-engineer-date-from"
                >
                    <CalendarDays
                        size={15}
                        aria-hidden="true"
                    />

                    <span>
                        From
                    </span>
                </label>

                <input
                    id="service-engineer-date-from"
                    type="date"
                    value={
                        dateFrom || ""
                    }
                    onChange={
                        handleDateFromChange
                    }
                    max={
                        dateTo ||
                        undefined
                    }
                    aria-label="Engineer service from date"
                />

            </div>

            {/* =================================================
               TO DATE
            ================================================= */}

            <div className="service-engineer-toolbar-field">

                <label
                    htmlFor="service-engineer-date-to"
                >
                    <CalendarDays
                        size={15}
                        aria-hidden="true"
                    />

                    <span>
                        To
                    </span>
                </label>

                <input
                    id="service-engineer-date-to"
                    type="date"
                    value={
                        dateTo || ""
                    }
                    min={
                        dateFrom ||
                        undefined
                    }
                    onChange={
                        handleDateToChange
                    }
                    aria-label="Engineer service to date"
                />

            </div>

            {/* =================================================
               FILTER BUTTON
            ================================================= */}

            <button
                type="button"
                className="service-engineer-toolbar-filter"
                onClick={
                    handleFilter
                }
                aria-label="Apply engineer service filters"
            >

                <Filter
                    size={16}
                    aria-hidden="true"
                />

                <span>
                    Filter
                </span>

            </button>

            {/* =================================================
               RESET BUTTON
            ================================================= */}

            <button
                type="button"
                className="service-engineer-toolbar-reset"
                onClick={
                    handleReset
                }
                disabled={
                    !hasFilters
                }
                aria-label="Reset engineer service filters"
            >

                <RotateCcw
                    size={16}
                    aria-hidden="true"
                />

                <span>
                    Reset
                </span>

            </button>

        </div>
    );
};

export default ServiceEngineerToolbar;