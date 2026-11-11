import "./SearchableCustomer.css";

import {
    Search,
    User,
    ChevronDown,
    ChevronUp,
    Phone,
    Mail,
    Check,
} from "lucide-react";

import { useEffect, useRef, useState } from "react";

const SearchableCustomer = ({
    customers = [],
    value,
    onChange,
}) => {

    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState("");

    const containerRef = useRef(null);
    const searchInputRef = useRef(null);

    // =========================================
    // Selected Customer
    // =========================================

    const selectedCustomer = customers.find(
        (customer) =>
            String(customer.id) === String(value)
    );


    // =========================================
    // Filter Customers
    // =========================================

    const filteredCustomers = customers.filter(
        (customer) => {

            const searchText =
                search.trim().toLowerCase();

            if (!searchText) {
                return true;
            }

            return (
                customer.customer_name
                    ?.toLowerCase()
                    .includes(searchText) ||

                customer.customer_code
                    ?.toLowerCase()
                    .includes(searchText) ||

                customer.contact_person
                    ?.toLowerCase()
                    .includes(searchText) ||

                customer.phone
                    ?.toLowerCase()
                    .includes(searchText) ||

                customer.email
                    ?.toLowerCase()
                    .includes(searchText)
            );
        }
    );


    // =========================================
    // Close On Outside Click
    // =========================================

    useEffect(() => {

        const handleClickOutside = (event) => {

            if (
                containerRef.current &&
                !containerRef.current.contains(
                    event.target
                )
            ) {
                setOpen(false);
                setSearch("");
            }

        };

        document.addEventListener(
            "mousedown",
            handleClickOutside
        );

        return () => {

            document.removeEventListener(
                "mousedown",
                handleClickOutside
            );

        };

    }, []);


    // =========================================
    // Open Dropdown
    // =========================================

    const handleOpen = () => {

        setOpen((previous) => !previous);

        setTimeout(() => {

            searchInputRef.current?.focus();

        }, 50);

    };


    // =========================================
    // Select Customer
    // =========================================

    const handleSelect = (customer) => {

        onChange(customer.id);

        setOpen(false);

        setSearch("");

    };


    return (

        <div
            className="searchable-customer"
            ref={containerRef}
        >

            {/* =====================================
                Selected Customer Button
            ================================     */}

            <button
                type="button"
                className={`searchable-customer-control ${
                    open ? "open" : ""
                }`}
                onClick={handleOpen}
            >

                <div className="customer-control-left">

                    <User
                        size={17}
                        className="customer-control-icon"
                    />

                    <div className="customer-control-text">

                        {selectedCustomer ? (

                            <span className="customer-selected-name">
                                <strong>
                                    {selectedCustomer.customer_name}
                                </strong>
                            </span>

                        ) : (

                            <span className="customer-placeholder">

                                Select Customer

                            </span>

                        )}

                    </div>

                </div>


                <div className="customer-control-arrow">

                    {open ? (
                        <ChevronUp size={17} />
                    ) : (
                        <ChevronDown size={17} />
                    )}

                </div>

            </button>


            {/* =====================================
                Dropdown
            ===================================== */}

            {open && (

                <div className="searchable-customer-dropdown">

                    {/* Search */}

                    <div className="customer-search-box">

                        <Search
                            size={17}
                            className="customer-search-icon"
                        />

                        <input
                            ref={searchInputRef}
                            type="text"
                            value={search}
                            placeholder="Search customer by name, code, phone..."
                            onChange={(e) =>
                                setSearch(
                                    e.target.value
                                )
                            }
                        />

                        {search && (

                            <button
                                type="button"
                                className="customer-search-clear"
                                onClick={() =>
                                    setSearch("")
                                }
                            >
                                ×
                            </button>

                        )}

                    </div>


                    {/* Results Header */}

                    <div className="customer-results-header">

                        <span>
                            Customers
                        </span>

                        <span>
                            {filteredCustomers.length}
                        </span>

                    </div>


                    {/* Customer Results */}

                    <div className="customer-results">

                        {filteredCustomers.length > 0 ? (

                            filteredCustomers.map(
                                (customer) => {

                                    const isSelected =
                                        String(customer.id) ===
                                        String(value);

                                    return (

                                        <button
                                            key={customer.id}
                                            type="button"
                                            className={`customer-option ${
                                                isSelected
                                                    ? "selected"
                                                    : ""
                                            }`}
                                            onClick={() =>
                                                handleSelect(
                                                    customer
                                                )
                                            }
                                        >

                                            {/* Avatar */}

                                            <div className="customer-avatar">

                                                {customer.customer_name
                                                    ?.charAt(0)
                                                    ?.toUpperCase() || "C"}

                                            </div>


                                            {/* Main Content */}

                                            <div className="customer-option-content">

                                                <div className="customer-option-top">

                                                    <span className="customer-name">
                                                        <strong>
                                                            {
                                                                customer.customer_name
                                                            }
                                                        </strong>
                                                    </span>

                                                </div>


                                                <div className="customer-option-bottom">

                                                    {customer.contact_person && (

                                                        <span>

                                                            {
                                                                customer.contact_person
                                                            }

                                                        </span>

                                                    )}

                                                    {customer.phone && (

                                                        <span className="customer-detail">

                                                            <Phone
                                                                size={12}
                                                            />

                                                            {
                                                                customer.phone
                                                            }

                                                        </span>

                                                    )}

                                                    {customer.email && (

                                                        <span className="customer-detail email">

                                                            <Mail
                                                                size={12}
                                                            />

                                                            {
                                                                customer.email
                                                            }

                                                        </span>

                                                    )}

                                                </div>

                                            </div>


                                            {/* Selected */}

                                            {isSelected && (

                                                <div className="customer-selected-check">

                                                    <Check
                                                        size={17}
                                                    />

                                                </div>

                                            )}

                                        </button>

                                    );

                                }

                            )

                        ) : (

                            <div className="customer-empty">

                                <div className="customer-empty-icon">

                                    <Search
                                        size={22}
                                    />

                                </div>

                                <strong>
                                    No customers found
                                </strong>

                                <span>
                                    Try searching with another name,
                                    code or phone number.
                                </span>

                            </div>

                        )}

                    </div>

                </div>

            )}

        </div>

    );
};

export default SearchableCustomer;