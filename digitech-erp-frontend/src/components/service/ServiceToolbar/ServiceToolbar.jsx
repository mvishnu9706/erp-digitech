import React from "react";

import "./ServiceToolbar.css";

import {
    Search,
    RotateCcw,
    CalendarDays,
} from "lucide-react";

import { useService } from "../../../context/ServiceContext";


const ServiceToolbar = () => {

    // =====================================================
    // SERVICE CONTEXT
    // =====================================================

    const {
        search,
        setSearch,

        statusFilter,
        setStatusFilter,

        priorityFilter,
        setPriorityFilter,

        dateFrom,
        setDateFrom,

        dateTo,
        setDateTo,

        resetFilters,
    } = useService();


    // =====================================================
    // FROM DATE
    // =====================================================

    const handleFromDate = (event) => {

        const value =
            event.target.value;

        setDateFrom(value);

        /*
         * Keep the date range valid.
         *
         * If From becomes later than To,
         * move To to the same date.
         */

        if (
            value &&
            dateTo &&
            value > dateTo
        ) {
            setDateTo(value);
        }
    };


    // =====================================================
    // TO DATE
    // =====================================================

    const handleToDate = (event) => {

        const value =
            event.target.value;

        /*
         * Prevent selecting a To date
         * earlier than the From date.
         */

        if (
            value &&
            dateFrom &&
            value < dateFrom
        ) {
            setDateTo(dateFrom);
            return;
        }

        setDateTo(value);
    };


    // =====================================================
    // RESET
    // =====================================================

    const handleReset = () => {

        resetFilters();

    };


    // =====================================================
    // RENDER
    // =====================================================

    return (

        <div className="service-toolbar">


            {/* =================================================
                SEARCH
            ================================================= */}

            <div className="service-toolbar-search">

                <Search size={18} />

                <input
                    type="text"
                    value={search || ""}
                    onChange={(event) =>
                        setSearch(
                            event.target.value
                        )
                    }
                    placeholder="Search ticket, customer, product, phone..."
                    aria-label="Search services"
                />

            </div>


            {/* =================================================
                STATUS
            ================================================= */}

            <select
                className="service-toolbar-select"
                value={statusFilter || ""}
                onChange={(event) =>
                    setStatusFilter(
                        event.target.value
                    )
                }
                aria-label="Filter services by status"
            >

                <option value="">
                    All Status
                </option>

                <option value="OPEN">
                    Open
                </option>

                <option value="REQUESTED">
                    Requested
                </option>

                <option value="CONFIRMED">
                    Confirmed
                </option>

                <option value="REACHED">
                    Reached
                </option>

                <option value="IN_PROGRESS">
                    In Progress
                </option>

                <option value="PENDING">
                    Pending
                </option>

                <option value="WAITING_FOR_PARTS">
                    Waiting For Parts
                </option>

                <option value="PARTS_PENDING">
                    Parts Pending
                </option>

                <option value="ON_HOLD">
                    On Hold
                </option>

                <option value="COMPLETED">
                    Completed
                </option>

                <option value="CLOSED">
                    Closed
                </option>

                <option value="CANCELLED">
                    Cancelled
                </option>

            </select>


            {/* =================================================
                PRIORITY
            ================================================= */}

            <select
                className="service-toolbar-select"
                value={priorityFilter || ""}
                onChange={(event) =>
                    setPriorityFilter(
                        event.target.value
                    )
                }
                aria-label="Filter services by priority"
            >

                <option value="">
                    All Priority
                </option>

                <option value="LOW">
                    Low
                </option>

                <option value="MEDIUM">
                    Medium
                </option>

                <option value="HIGH">
                    High
                </option>

                <option value="URGENT">
                    Urgent
                </option>

            </select>


            {/* =================================================
                FROM DATE
            ================================================= */}

            <div className="service-toolbar-date">

                <span>
                    From
                </span>

                <div className="service-toolbar-date-input">

                    <CalendarDays size={15} />

                    <input
                        id="service-from-date"
                        type="date"
                        value={dateFrom || ""}
                        onChange={handleFromDate}
                        aria-label="Filter services from date"
                    />

                </div>

            </div>


            {/* =================================================
                TO DATE
            ================================================= */}

            <div className="service-toolbar-date">

                <span>
                    To
                </span>

                <div className="service-toolbar-date-input">

                    <CalendarDays size={15} />

                    <input
                        id="service-to-date"
                        type="date"
                        value={dateTo || ""}
                        min={
                            dateFrom || undefined
                        }
                        onChange={handleToDate}
                        aria-label="Filter services to date"
                    />

                </div>

            </div>


            {/* =================================================
                RESET
            ================================================= */}

            <button
                type="button"
                className="service-toolbar-reset"
                onClick={handleReset}
                aria-label="Reset service filters"
            >

                <RotateCcw size={17} />

                <span>
                    Reset
                </span>

            </button>

        </div>

    );

};


export default ServiceToolbar;