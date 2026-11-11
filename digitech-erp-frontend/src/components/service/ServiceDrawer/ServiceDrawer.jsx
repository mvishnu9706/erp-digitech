import "./ServiceDrawer.css";
import {
    X,
    Save,
    Wrench,
    Search,
    ChevronDown,
} from "lucide-react";

import {
    useEffect,
    useMemo,
    useState,
} from "react";

import api from "../../../api/axios";


// =====================================================
// EMPTY FORM
// =====================================================

const emptyForm = {
    ticket_number: "",

    customer_id: "",
    customer: "",

    machine_id: "",
    product: "",

    issue: "",
    description: "",

    engineer_id: "",
    technician: "",

    ticket_type: "BREAKDOWN",

    priority: "MEDIUM",

    // IMPORTANT:
    // Frontend displays this as "Open"
    // Backend value remains "REQUESTED"
    status: "REQUESTED",

    service_date: "",
    expected_visit_date: "",
    visit_date: "",
    completion_date: "",

    total_amount: "",

    material_used: "",

    payment_status: "PENDING",

    meter_reading: "0",

    remarks: "",

    phone: "",
    email: "",
    address: "",
};


// =====================================================
// STATUS OPTIONS
// =====================================================
//
// IMPORTANT:
//
// value = backend/database value
// label = frontend display value
//
// REQUESTED -> Open
//
// DO NOT change REQUESTED to OPEN here.
// =====================================================

const STATUS_OPTIONS = [
    {
        value: "REQUESTED",
        label: "Open",
    },
    {
        value: "ASSIGNED",
        label: "Assigned",
    },
    {
        value: "CONFIRMED",
        label: "Confirmed",
    },
    {
        value: "IN_PROGRESS",
        label: "In Progress",
    },
    {
        value: "ON_HOLD",
        label: "On Hold",
    },
    {
        value: "PARTS_PENDING",
        label: "Parts Pending",
    },
    {
        value: "COMPLETED",
        label: "Completed",
    },
    {
        value: "CLOSED",
        label: "Closed",
    },
    {
        value: "CANCELLED",
        label: "Cancelled",
    },
];


// =====================================================
// PRIORITY OPTIONS
// =====================================================

const PRIORITY_OPTIONS = [
    {
        value: "LOW",
        label: "Low",
    },
    {
        value: "MEDIUM",
        label: "Medium",
    },
    {
        value: "HIGH",
        label: "High",
    },
    {
        value: "URGENT",
        label: "Urgent",
    },
];


// =====================================================
// TICKET TYPE OPTIONS
// =====================================================

const TICKET_TYPE_OPTIONS = [
    {
        value: "BREAKDOWN",
        label: "Breakdown",
    },
    {
        value: "INSTALLATION",
        label: "Installation",
    },
    {
        value: "AMC",
        label: "AMC",
    },
    {
        value: "PREVENTIVE_MAINTENANCE",
        label: "Preventive Maintenance",
    },
    {
        value: "RENTAL",
        label: "Rental",
    },
    {
        value: "DEMO",
        label: "Demo",
    },
    {
        value: "SHIFTING",
        label: "Shifting",
    },
    {
        value: "REINSTALLATION",
        label: "Reinstallation",
    },
];


// =====================================================
// PAYMENT OPTIONS
// =====================================================

const PAYMENT_OPTIONS = [
    {
        value: "PENDING",
        label: "Pending",
    },
    {
        value: "RECEIVED",
        label: "Received",
    },
];


// =====================================================
// EXTRACT API LIST
// =====================================================

const extractList = (response) => {
    const data = response?.data ?? response;

    if (Array.isArray(data)) {
        return data;
    }

    if (Array.isArray(data?.items)) {
        return data.items;
    }

    if (Array.isArray(data?.customers)) {
        return data.customers;
    }

    if (Array.isArray(data?.machines)) {
        return data.machines;
    }

    if (Array.isArray(data?.users)) {
        return data.users;
    }

    if (Array.isArray(data?.engineers)) {
        return data.engineers;
    }

    return [];
};


// =====================================================
// FIRST NON-EMPTY VALUE
// =====================================================

const firstValue = (...values) => {
    return values.find(
        (value) =>
            value !== null &&
            value !== undefined &&
            String(value).trim() !== ""
    );
};


// =====================================================
// CUSTOMER NAME
// =====================================================

const getCustomerName = (customer) => {
    return String(
        firstValue(
            customer?.customer_name,
            customer?.name,
            customer?.company_name,
            customer?.customerName,
            customer?.username,
            ""
        )
    );
};


// =====================================================
// MACHINE NAME
// =====================================================

const getMachineName = (machine) => {
    return String(
        firstValue(
            machine?.machine_number,
            machine?.machine_name,
            machine?.asset_tag,
            machine?.serial_number,
            machine?.name,
            ""
        )
    );
};


// =====================================================
// PRODUCT NAME
// =====================================================

const getProductName = (machine) => {
    return String(
        firstValue(
            machine?.product_name,
            machine?.product?.product_name,
            machine?.product?.name,
            machine?.model_name,
            machine?.model_no,
            machine?.machine_name,
            machine?.machine_number,
            ""
        )
    );
};


// =====================================================
// ENGINEER NAME
// =====================================================

const getEngineerName = (engineer) => {
    return String(
        firstValue(
            engineer?.full_name,
            engineer?.name,
            engineer?.username,
            engineer?.email,
            ""
        )
    );
};


// =====================================================
// DATE FORMATTER
// =====================================================

const toDateInput = (value) => {
    if (!value) {
        return "";
    }

    const text = String(value);

    if (
        /^\d{4}-\d{2}-\d{2}$/.test(text)
    ) {
        return text;
    }

    const match = text.match(
        /^(\d{4}-\d{2}-\d{2})/
    );

    if (match) {
        return match[1];
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "";
    }

    return date
        .toISOString()
        .slice(0, 10);
};


// =====================================================
// SEARCHABLE SELECT
// =====================================================

const SearchableSelect = ({
    value,
    options = [],
    onChange,
    getLabel,
    getSearchText,
    placeholder = "Select...",
    searchPlaceholder = "Search...",
    loading = false,
    disabled = false,
    className = "",
}) => {
    const [open, setOpen] =
        useState(false);

    const [search, setSearch] =
        useState("");


    // -------------------------------------------------
    // SELECTED OPTION
    // -------------------------------------------------

    const selectedOption =
        useMemo(
            () =>
                options.find(
                    (option) =>
                        String(option?.id) ===
                        String(value)
                ),
            [
                options,
                value,
            ]
        );


    // -------------------------------------------------
    // FILTER OPTIONS
    // -------------------------------------------------

    const filteredOptions =
        useMemo(() => {
            const query =
                String(search || "")
                    .trim()
                    .toLowerCase();

            if (!query) {
                return options;
            }

            return options.filter(
                (option) => {
                    const text =
                        getSearchText
                            ? getSearchText(
                                option
                            )
                            : getLabel(
                                option
                            );

                    return String(
                        text || ""
                    )
                        .toLowerCase()
                        .includes(query);
                }
            );
        }, [
            options,
            search,
            getLabel,
            getSearchText,
        ]);


    // -------------------------------------------------
    // CLOSE WHEN CLICKING OUTSIDE
    // -------------------------------------------------

    useEffect(() => {
        if (!open) {
            return undefined;
        }

        const handleOutsideClick =
            (event) => {
                if (
                    !event.target.closest(
                        ".service-searchable-select"
                    )
                ) {
                    setOpen(false);
                    setSearch("");
                }
            };

        document.addEventListener(
            "mousedown",
            handleOutsideClick
        );

        return () => {
            document.removeEventListener(
                "mousedown",
                handleOutsideClick
            );
        };
    }, [open]);


    // -------------------------------------------------
    // SELECT OPTION
    // -------------------------------------------------

    const selectOption = (
        option
    ) => {
        onChange?.(option);

        setOpen(false);
        setSearch("");
    };


    const displayValue =
        selectedOption
            ? getLabel(
                selectedOption
            )
            : "";


    return (
        <div
            className={`service-searchable-select ${className}`}
            onMouseDown={(event) =>
                event.stopPropagation()
            }
        >
            <button
                type="button"
                className={`service-searchable-trigger ${
                    open
                        ? "is-open"
                        : ""
                }`}
                onClick={() => {
                    if (!disabled) {
                        setOpen(
                            (current) =>
                                !current
                        );
                    }
                }}
                disabled={disabled}
                aria-haspopup="listbox"
                aria-expanded={open}
            >
                <span
                    className={
                        displayValue
                            ? "service-searchable-value"
                            : "service-searchable-placeholder"
                    }
                >
                    {loading
                        ? "Loading..."
                        : displayValue ||
                          placeholder}
                </span>

                <ChevronDown
                    size={18}
                    className={`service-searchable-chevron ${
                        open
                            ? "rotated"
                            : ""
                    }`}
                />
            </button>


            {open &&
                !disabled && (
                    <div className="service-searchable-menu">

                        <div className="service-searchable-search-wrap">
                            <Search size={17} />

                            <input
                                type="text"
                                autoFocus
                                value={search}
                                onChange={(event) =>
                                    setSearch(
                                        event.target.value
                                    )
                                }
                                placeholder={
                                    searchPlaceholder
                                }
                                className="service-searchable-search"
                                onKeyDown={(
                                    event
                                ) => {
                                    if (
                                        event.key ===
                                        "Escape"
                                    ) {
                                        setOpen(
                                            false
                                        );

                                        setSearch(
                                            ""
                                        );
                                    }
                                }}
                            />
                        </div>


                        <div
                            className="service-searchable-options"
                            role="listbox"
                        >

                            {/* CLEAR OPTION */}

                            <button
                                type="button"
                                className={`service-searchable-option service-searchable-empty-option ${
                                    !value
                                        ? "selected"
                                        : ""
                                }`}
                                onClick={() =>
                                    selectOption(
                                        null
                                    )
                                }
                            >
                                {
                                    placeholder
                                }
                            </button>


                            {/* OPTIONS */}

                            {filteredOptions.length >
                            0 ? (
                                filteredOptions.map(
                                    (
                                        option
                                    ) => {
                                        const optionId =
                                            String(
                                                option?.id
                                            );

                                        const isSelected =
                                            String(
                                                value
                                            ) ===
                                            optionId;

                                        return (
                                            <button
                                                type="button"
                                                role="option"
                                                aria-selected={
                                                    isSelected
                                                }
                                                className={`service-searchable-option ${
                                                    isSelected
                                                        ? "selected"
                                                        : ""
                                                }`}
                                                key={
                                                    option?.id
                                                }
                                                onClick={() =>
                                                    selectOption(
                                                        option
                                                    )
                                                }
                                            >
                                                {
                                                    getLabel(
                                                        option
                                                    )
                                                }
                                            </button>
                                        );
                                    }
                                )
                            ) : (
                                <div className="service-searchable-no-results">
                                    No results found
                                </div>
                            )}

                        </div>
                    </div>
                )}
        </div>
    );
};


// =====================================================
// SERVICE DRAWER
// =====================================================

const ServiceDrawer = ({
    open = false,
    mode = "add",
    service = null,
    onClose,
    onSave,
}) => {

    const [form, setForm] =
        useState(emptyForm);

    const [errors, setErrors] =
        useState({});


    const [customers, setCustomers] =
        useState([]);

    const [machines, setMachines] =
        useState([]);

    const [engineers, setEngineers] =
        useState([]);


    const [
        loadingCustomers,
        setLoadingCustomers,
    ] = useState(false);

    const [
        loadingMachines,
        setLoadingMachines,
    ] = useState(false);

    const [
        loadingEngineers,
        setLoadingEngineers,
    ] = useState(false);


    // =================================================
    // SELECTED CUSTOMER
    // =================================================

    const selectedCustomer =
        useMemo(() => {
            return customers.find(
                (item) =>
                    Number(item?.id) ===
                    Number(
                        form.customer_id
                    )
            );
        }, [
            customers,
            form.customer_id,
        ]);


    // =================================================
    // SELECTED MACHINE
    // =================================================

    const selectedMachine =
        useMemo(() => {
            return machines.find(
                (item) =>
                    Number(item?.id) ===
                    Number(
                        form.machine_id
                    )
            );
        }, [
            machines,
            form.machine_id,
        ]);


    // =================================================
    // SELECTED ENGINEER
    // =================================================

    const selectedEngineer =
        useMemo(() => {
            return engineers.find(
                (item) =>
                    Number(item?.id) ===
                    Number(
                        form.engineer_id
                    )
            );
        }, [
            engineers,
            form.engineer_id,
        ]);


    // =================================================
    // LOAD CUSTOMERS
    // =================================================

    useEffect(() => {
        if (!open) {
            return;
        }

        let cancelled = false;

        const loadCustomers =
            async () => {
                try {
                    setLoadingCustomers(
                        true
                    );

                    const response =
                        await api.get(
                            "/customers/",
                            {
                                params: {
                                    page: 1,
                                    page_size: 100,
                                },
                            }
                        );

                    if (!cancelled) {
                        setCustomers(
                            extractList(
                                response
                            )
                        );
                    }
                } catch (error) {
                    console.error(
                        "Failed to load customers:",
                        error
                    );

                    if (!cancelled) {
                        setCustomers([]);
                    }
                } finally {
                    if (!cancelled) {
                        setLoadingCustomers(
                            false
                        );
                    }
                }
            };

        loadCustomers();

        return () => {
            cancelled = true;
        };
    }, [open]);


    // =================================================
    // LOAD ENGINEERS
    // =================================================

    useEffect(() => {
        if (!open) {
            return;
        }

        let cancelled = false;

        const loadEngineers =
            async () => {
                try {
                    setLoadingEngineers(
                        true
                    );

                    const response =
                        await api.get(
                            "/users/",
                            {
                                params: {
                                    page: 1,
                                    page_size: 100,
                                },
                            }
                        );

                    const list =
                        extractList(
                            response
                        );

                    const engineerList =
                        list.filter(
                            (item) => {
                                const role =
                                    String(
                                        item?.role ||
                                        item?.user_role ||
                                        ""
                                    )
                                        .trim()
                                        .toUpperCase()
                                        .replace(
                                            /[\s-]+/g,
                                            "_"
                                        );

                                return (
                                    role ===
                                    "ENGINEER"
                                );
                            }
                        );

                    if (!cancelled) {
                        setEngineers(
                            engineerList
                        );
                    }
                } catch (error) {
                    console.error(
                        "Failed to load engineers:",
                        error
                    );

                    if (!cancelled) {
                        setEngineers([]);
                    }
                } finally {
                    if (!cancelled) {
                        setLoadingEngineers(
                            false
                        );
                    }
                }
            };

        loadEngineers();

        return () => {
            cancelled = true;
        };
    }, [open]);


    // =================================================
    // LOAD MACHINES FOR CUSTOMER
    // =================================================

    const loadMachines =
        async (customerId) => {

            if (!customerId) {
                setMachines([]);
                return;
            }

            try {
                setLoadingMachines(
                    true
                );

                const response =
                    await api.get(
                        "/machines/",
                        {
                            params: {
                                customer_id:
                                    Number(
                                        customerId
                                    ),
                                page: 1,
                                page_size: 100,
                            },
                        }
                    );

                setMachines(
                    extractList(
                        response
                    )
                );

            } catch (error) {

                console.error(
                    "Failed to load machines:",
                    error
                );

                setMachines([]);

            } finally {

                setLoadingMachines(
                    false
                );
            }
        };


    // =================================================
    // INITIALIZE FORM
    // =================================================

    useEffect(() => {

        if (!open) {
            return;
        }


        const serviceCustomerId =
            service?.customer_id ||
            service?.customer?.id ||
            service?.customer_details?.id ||
            "";


        const serviceMachineId =
            service?.machine_id ||
            service?.machine?.id ||
            service?.machine_details?.id ||
            "";


        const serviceEngineerId =
            service?.assigned_engineer_id ||
            service?.engineer_id ||
            service?.engineer?.id ||
            service?.assigned_engineer?.id ||
            "";


        // -------------------------------------------------
        // EDIT
        // -------------------------------------------------

        if (
            mode === "edit" &&
            service
        ) {

            const rawStatus =
                String(
                    service?.status ||
                    "REQUESTED"
                )
                    .trim()
                    .toUpperCase();


            const priority =
                String(
                    service?.priority ||
                    "MEDIUM"
                )
                    .trim()
                    .toUpperCase();


            // IMPORTANT:
            //
            // If backend returns REQUESTED,
            // form keeps REQUESTED.
            //
            // The dropdown displays "Open"
            // because STATUS_OPTIONS maps
            // REQUESTED -> Open.

            const status =
                STATUS_OPTIONS.some(
                    (item) =>
                        item.value ===
                        rawStatus
                )
                    ? rawStatus
                    : "REQUESTED";


            setForm({
                ...emptyForm,

                ticket_number:
                    service?.ticket_number ||
                    "",

                customer_id:
                    serviceCustomerId,

                customer:
                    getCustomerName(
                        service?.customer
                    ) ||
                    service?.customer_name ||
                    service?.customer ||
                    "",

                machine_id:
                    serviceMachineId,

                product:
                    service?.product_name ||
                    getProductName(
                        service?.machine
                    ) ||
                    service?.product ||
                    "",

                issue:
                    service?.issue ||
                    service?.complaint ||
                    service?.subject ||
                    "",

                description:
                    service?.description ||
                    service?.problem_description ||
                    "",

                engineer_id:
                    serviceEngineerId,

                technician:
                    service?.technician ||
                    service?.engineer_name ||
                    getEngineerName(
                        service?.engineer
                    ) ||
                    "",

                ticket_type:
                    service?.ticket_type ||
                    "BREAKDOWN",

                priority:
                    PRIORITY_OPTIONS.some(
                        (item) =>
                            item.value ===
                            priority
                    )
                        ? priority
                        : "MEDIUM",

                status,

                service_date:
                    toDateInput(
                        service?.service_date ||
                        service?.reported_date ||
                        service?.created_at
                    ),

                expected_visit_date:
                    toDateInput(
                        service?.expected_visit_date
                    ),

                visit_date:
                    toDateInput(
                        service?.visit_date
                    ),

                completion_date:
                    toDateInput(
                        service?.completion_date ||
                        service?.completed_date ||
                        service?.completed_at
                    ),

                total_amount:
                    service?.service_cost ??
                    service?.total_amount ??
                    "",

                material_used:
                    service?.material_used ||
                    "",

                payment_status:
                    String(
                        service?.payment_status ||
                        "PENDING"
                    )
                        .trim()
                        .toUpperCase() ===
                    "RECEIVED"
                        ? "RECEIVED"
                        : "PENDING",

                meter_reading:
                    service?.meter_reading ??
                    "0",

                remarks:
                    service?.remarks ||
                    "",

                phone:
                    service?.phone ||
                    service?.customer?.phone ||
                    "",

                email:
                    service?.email ||
                    service?.customer?.email ||
                    "",

                address:
                    service?.address ||
                    service?.customer?.address ||
                    "",
            });


            if (
                serviceCustomerId
            ) {
                loadMachines(
                    serviceCustomerId
                );
            } else {
                setMachines([]);
            }

        }

        // -------------------------------------------------
        // ADD
        // -------------------------------------------------

        else {

            setForm({
                ...emptyForm,

                service_date:
                    new Date()
                        .toISOString()
                        .slice(0, 10),
            });

            setMachines([]);
        }


        setErrors({});

    }, [
        open,
        mode,
        service,
    ]);


    // =================================================
    // GENERIC CHANGE
    // =================================================

    const handleChange =
        (event) => {

            const {
                name,
                value,
            } = event.target;


            setForm(
                (previous) => ({
                    ...previous,
                    [name]: value,
                })
            );


            setErrors(
                (previous) => ({
                    ...previous,
                    [name]: "",
                })
            );
        };


    // =================================================
    // CUSTOMER CHANGE
    // =================================================

    const handleCustomerChange =
        async (event) => {

            const customerId =
                event.target.value;


            const customer =
                customers.find(
                    (item) =>
                        String(
                            item?.id
                        ) ===
                        String(
                            customerId
                        )
                );


            setForm(
                (previous) => ({
                    ...previous,

                    customer_id:
                        customerId,

                    customer:
                        getCustomerName(
                            customer
                        ),

                    machine_id: "",

                    product: "",

                    phone:
                        customer?.phone ||
                        customer?.mobile ||
                        "",

                    email:
                        customer?.email ||
                        "",

                    address:
                        customer?.shipping_address ||
                        customer?.billing_address ||
                        customer?.address ||
                        "",
                })
            );


            setErrors(
                (previous) => ({
                    ...previous,
                    customer_id: "",
                    machine_id: "",
                })
            );


            await loadMachines(
                customerId
            );
        };


    // =================================================
    // MACHINE CHANGE
    // =================================================

    const handleMachineChange =
        (event) => {

            const machineId =
                event.target.value;


            const machine =
                machines.find(
                    (item) =>
                        String(
                            item?.id
                        ) ===
                        String(
                            machineId
                        )
                );


            setForm(
                (previous) => ({
                    ...previous,

                    machine_id:
                        machineId,

                    product:
                        getProductName(
                            machine
                        ),
                })
            );


            setErrors(
                (previous) => ({
                    ...previous,
                    machine_id: "",
                })
            );
        };


    // =================================================
    // ENGINEER CHANGE
    // =================================================

    const handleEngineerChange =
        (event) => {

            const engineerId =
                event.target.value;


            const engineer =
                engineers.find(
                    (item) =>
                        String(
                            item?.id
                        ) ===
                        String(
                            engineerId
                        )
                );


            setForm(
                (previous) => ({
                    ...previous,

                    engineer_id:
                        engineerId,

                    technician:
                        getEngineerName(
                            engineer
                        ),
                })
            );


            setErrors(
                (previous) => ({
                    ...previous,
                    engineer_id: "",
                })
            );
        };


    // =================================================
    // VALIDATION
    // =================================================

    const validate = () => {

        const nextErrors = {};


        if (!form.customer_id) {
            nextErrors.customer_id =
                "Customer is required.";
        }


        if (!form.machine_id) {
            nextErrors.machine_id =
                "Machine is required.";
        }


        if (
            !String(
                form.issue || ""
            ).trim()
        ) {

            nextErrors.issue =
                "Service issue is required.";

        } else if (
            String(
                form.issue
            )
                .trim()
                .length < 5
        ) {

            nextErrors.issue =
                "Service issue must contain at least 5 characters.";
        }


        if (!form.service_date) {
            nextErrors.service_date =
                "Service date is required.";
        }


        if (
            form.total_amount !== "" &&
            (
                Number.isNaN(
                    Number(
                        form.total_amount
                    )
                ) ||
                Number(
                    form.total_amount
                ) < 0
            )
        ) {

            nextErrors.total_amount =
                "Service amount must be 0 or greater.";
        }


        if (
            form.meter_reading !== "" &&
            (
                Number.isNaN(
                    Number(
                        form.meter_reading
                    )
                ) ||
                Number(
                    form.meter_reading
                ) < 0
            )
        ) {

            nextErrors.meter_reading =
                "Meter reading must be 0 or greater.";
        }


        if (
            form.expected_visit_date &&
            form.service_date &&
            form.expected_visit_date <
                form.service_date
        ) {

            nextErrors.expected_visit_date =
                "Expected visit date cannot be before service date.";
        }


        if (
            form.visit_date &&
            form.service_date &&
            form.visit_date <
                form.service_date
        ) {

            nextErrors.visit_date =
                "Visit date cannot be before service date.";
        }


        if (
            form.completion_date &&
            form.service_date &&
            form.completion_date <
                form.service_date
        ) {

            nextErrors.completion_date =
                "Completion date cannot be before service date.";
        }


        setErrors(
            nextErrors
        );


        return (
            Object.keys(
                nextErrors
            ).length === 0
        );
    };


    // =================================================
    // SUBMIT
    // =================================================

    const handleSubmit =
        (event) => {

            event.preventDefault();


            if (!validate()) {
                return;
            }


            // =============================================
            // IMPORTANT
            //
            // This stays REQUESTED.
            //
            // Frontend label is "Open".
            //
            // Backend receives REQUESTED.
            // =============================================

            const status =
                String(
                    form.status ||
                    "REQUESTED"
                )
                    .trim()
                    .toUpperCase();


            const priority =
                String(
                    form.priority ||
                    "MEDIUM"
                )
                    .trim()
                    .toUpperCase();


            const serviceCost =
                form.total_amount === ""
                    ? null
                    : Number(
                        form.total_amount
                    );


            const meterReading =
                form.meter_reading === ""
                    ? 0
                    : Number(
                        form.meter_reading
                    );


            // =============================================
            // BACKEND PAYLOAD
            // =============================================

            const payload = {

                customer_id:
                    Number(
                        form.customer_id
                    ),

                machine_id:
                    Number(
                        form.machine_id
                    ),

                engineer_id:
                    form.engineer_id
                        ? Number(
                            form.engineer_id
                        )
                        : null,

                ticket_type:
                    form.ticket_type ||
                    "BREAKDOWN",

                priority,

                subject:
                    String(
                        form.issue || ""
                    )
                        .trim(),

                complaint:
                    String(
                        form.issue || ""
                    )
                        .trim(),

                problem_description:
                    String(
                        form.description ||
                        ""
                    )
                        .trim() ||
                    null,

                reported_date:
                    form.service_date,

                expected_visit_date:
                    form.expected_visit_date ||
                    null,

                visit_date:
                    form.visit_date ||
                    null,

                completion_date:
                    form.completion_date ||
                    null,

                // =========================================
                // DO NOT CHANGE THIS TO "OPEN"
                // =========================================

                status,

                meter_reading:
                    meterReading,

                remarks:
                    String(
                        form.remarks || ""
                    )
                        .trim() ||
                    null,

                material_used:
                    String(
                        form.material_used ||
                        ""
                    )
                        .trim() ||
                    null,

                service_cost:
                    serviceCost,

                payment_status:
                    form.payment_status ===
                    "RECEIVED"
                        ? "RECEIVED"
                        : "PENDING",
            };


            // =============================================
            // EDIT ID
            // =============================================

            if (
                mode === "edit"
            ) {

                payload.id =
                    service?.id;
            }


            console.log(
                "SERVICE SAVE PAYLOAD:",
                payload
            );


            onSave?.(
                payload
            );
        };


    // =================================================
    // CLOSE
    // =================================================

    if (!open) {
        return null;
    }


    // =================================================
    // RENDER
    // =================================================

    return (
        <div
            className="service-drawer-overlay"
            onMouseDown={(event) => {

                if (
                    event.target ===
                    event.currentTarget
                ) {
                    onClose?.();
                }
            }}
        >

            <div className="service-drawer">


                {/* =========================================
                    HEADER
                ========================================= */}

                <div className="service-drawer-header">

                    <div className="service-drawer-title">

                        <div className="service-drawer-title-icon">
                            <Wrench
                                size={20}
                            />
                        </div>

                        <div>

                            <h2>
                                {
                                    mode ===
                                    "edit"
                                        ? "Edit Service"
                                        : "New Service"
                                }
                            </h2>

                            <p>
                                {
                                    mode ===
                                    "edit"
                                        ? "Update service ticket details."
                                        : "Create a new service ticket."
                                }
                            </p>

                        </div>

                    </div>


                    <button
                        type="button"
                        className="service-drawer-close"
                        onClick={
                            onClose
                        }
                        aria-label="Close"
                    >
                        <X
                            size={20}
                        />
                    </button>

                </div>


                {/* =========================================
                    FORM
                ========================================= */}

                <form
                    className="service-drawer-form"
                    onSubmit={
                        handleSubmit
                    }
                >


                    {/* =========================================
                        SERVICE INFORMATION
                    ========================================= */}

                    <div className="service-form-section">

                        <h3>
                            Service Information
                        </h3>


                        <div className="service-form-grid">


                            {/* TICKET NUMBER */}

                            <div className="service-form-group">

                                <label>
                                    Ticket Number
                                </label>

                                <input
                                    type="text"
                                    value={
                                        form.ticket_number
                                    }
                                    placeholder="Auto generated"
                                    disabled
                                />

                            </div>


                            {/* SERVICE DATE */}

                            <div className="service-form-group">

                                <label>
                                    Service Date
                                    <span>*</span>
                                </label>

                                <input
                                    type="date"
                                    name="service_date"
                                    value={
                                        form.service_date
                                    }
                                    onChange={
                                        handleChange
                                    }
                                />

                                {errors.service_date && (
                                    <small className="service-form-error">
                                        {
                                            errors.service_date
                                        }
                                    </small>
                                )}

                            </div>


                            {/* CUSTOMER */}

                            <div className="service-form-group full">

                                <label>
                                    Customer
                                    <span>*</span>
                                </label>


                                <SearchableSelect
                                    value={
                                        form.customer_id
                                    }
                                    options={
                                        customers
                                    }
                                    loading={
                                        loadingCustomers
                                    }
                                    disabled={
                                        loadingCustomers
                                    }
                                    placeholder="Select Customer"
                                    searchPlaceholder="Search customer by name, phone or email..."
                                    getLabel={
                                        getCustomerName
                                    }
                                    getSearchText={(
                                        customer
                                    ) =>
                                        [
                                            getCustomerName(
                                                customer
                                            ),
                                            customer?.phone,
                                            customer?.mobile,
                                            customer?.email,
                                            customer?.customer_code,
                                            customer?.code,
                                        ]
                                            .filter(
                                                Boolean
                                            )
                                            .join(
                                                " "
                                            )
                                    }
                                    onChange={(
                                        customer
                                    ) => {

                                        handleCustomerChange(
                                            {
                                                target: {
                                                    value:
                                                        customer?.id ||
                                                        "",
                                                },
                                            }
                                        );
                                    }}
                                />


                                {errors.customer_id && (
                                    <small className="service-form-error">
                                        {
                                            errors.customer_id
                                        }
                                    </small>
                                )}

                            </div>


                            {/* PHONE */}

                            <div className="service-form-group">

                                <label>
                                    Phone
                                </label>

                                <input
                                    type="text"
                                    value={
                                        form.phone
                                    }
                                    readOnly
                                    placeholder="Customer phone"
                                />

                            </div>


                            {/* EMAIL */}

                            <div className="service-form-group">

                                <label>
                                    Email
                                </label>

                                <input
                                    type="email"
                                    value={
                                        form.email
                                    }
                                    readOnly
                                    placeholder="Customer email"
                                />

                            </div>


                            {/* ADDRESS */}

                            <div className="service-form-group full">

                                <label>
                                    Address
                                </label>

                                <textarea
                                    value={
                                        form.address
                                    }
                                    readOnly
                                    rows="2"
                                    placeholder="Customer address"
                                />

                            </div>

                        </div>

                    </div>


                    {/* =========================================
                        MACHINE & ISSUE
                    ========================================= */}

                    <div className="service-form-section">

                        <h3>
                            Machine & Issue
                        </h3>


                        <div className="service-form-grid">


                            {/* MACHINE */}

                            <div className="service-form-group full">

                                <label>
                                    Machine
                                    <span>*</span>
                                </label>


                                <select
                                    name="machine_id"
                                    value={
                                        form.machine_id
                                    }
                                    onChange={
                                        handleMachineChange
                                    }
                                    disabled={
                                        !form.customer_id ||
                                        loadingMachines
                                    }
                                >

                                    <option value="">
                                        {
                                            !form.customer_id
                                                ? "Select customer first"
                                                : loadingMachines
                                                    ? "Loading machines..."
                                                    : "Select Machine"
                                        }
                                    </option>


                                    {machines.map(
                                        (
                                            machine
                                        ) => (
                                            <option
                                                key={
                                                    machine.id
                                                }
                                                value={
                                                    machine.id
                                                }
                                            >

                                                {
                                                    getMachineName(
                                                        machine
                                                    )
                                                }

                                                {
                                                    machine?.serial_number
                                                        ? ` — Serial: ${machine.serial_number}`
                                                        : ""
                                                }

                                            </option>
                                        )
                                    )}

                                </select>


                                {errors.machine_id && (
                                    <small className="service-form-error">
                                        {
                                            errors.machine_id
                                        }
                                    </small>
                                )}


                                {selectedMachine && (
                                    <div className="service-drawer-machine-info">

                                        <strong>
                                            {
                                                getMachineName(
                                                    selectedMachine
                                                )
                                            }
                                        </strong>

                                        {selectedMachine?.serial_number && (
                                            <span>
                                                Serial:{" "}
                                                {
                                                    selectedMachine.serial_number
                                                }
                                            </span>
                                        )}

                                    </div>
                                )}

                            </div>


                            {/* PRODUCT */}

                            <div className="service-form-group full">

                                <label>
                                    Product
                                </label>

                                <input
                                    type="text"
                                    value={
                                        form.product
                                    }
                                    readOnly
                                    placeholder="Product from selected machine"
                                />

                            </div>


                            {/* SERVICE ISSUE */}

                            <div className="service-form-group full">

                                <label>
                                    Service Issue
                                    <span>*</span>
                                </label>

                                <input
                                    type="text"
                                    name="issue"
                                    value={
                                        form.issue
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Enter service issue"
                                />

                                {errors.issue && (
                                    <small className="service-form-error">
                                        {
                                            errors.issue
                                        }
                                    </small>
                                )}

                            </div>


                            {/* DESCRIPTION */}

                            <div className="service-form-group full">

                                <label>
                                    Problem Description
                                </label>

                                <textarea
                                    name="description"
                                    value={
                                        form.description
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Describe the issue or required service..."
                                    rows="4"
                                />

                            </div>

                        </div>

                    </div>


                    {/* =========================================
                        ASSIGNMENT & STATUS
                    ========================================= */}

                    <div className="service-form-section">

                        <h3>
                            Assignment & Status
                        </h3>


                        <div className="service-form-grid">


                            {/* TECHNICIAN */}

                            <div className="service-form-group">

                                <label>
                                    Technician
                                </label>


                                <SearchableSelect
                                    value={
                                        form.engineer_id
                                    }
                                    options={
                                        engineers
                                    }
                                    loading={
                                        loadingEngineers
                                    }
                                    disabled={
                                        loadingEngineers
                                    }
                                    placeholder="Unassigned"
                                    searchPlaceholder="Search technician by name or email..."
                                    getLabel={
                                        getEngineerName
                                    }
                                    getSearchText={(
                                        engineer
                                    ) =>
                                        [
                                            getEngineerName(
                                                engineer
                                            ),
                                            engineer?.email,
                                            engineer?.username,
                                            engineer?.employee_code,
                                            engineer?.phone,
                                        ]
                                            .filter(
                                                Boolean
                                            )
                                            .join(
                                                " "
                                            )
                                    }
                                    onChange={(
                                        engineer
                                    ) => {

                                        handleEngineerChange(
                                            {
                                                target: {
                                                    value:
                                                        engineer?.id ||
                                                        "",
                                                },
                                            }
                                        );
                                    }}
                                />


                                {selectedEngineer && (
                                    <small className="service-form-help">
                                        {
                                            getEngineerName(
                                                selectedEngineer
                                            )
                                        }
                                    </small>
                                )}

                            </div>


                            {/* SERVICE TYPE */}

                            <div className="service-form-group">

                                <label>
                                    Service Type
                                </label>

                                <select
                                    name="ticket_type"
                                    value={
                                        form.ticket_type
                                    }
                                    onChange={
                                        handleChange
                                    }
                                >

                                    {TICKET_TYPE_OPTIONS.map(
                                        (
                                            item
                                        ) => (
                                            <option
                                                key={
                                                    item.value
                                                }
                                                value={
                                                    item.value
                                                }
                                            >
                                                {
                                                    item.label
                                                }
                                            </option>
                                        )
                                    )}

                                </select>

                            </div>


                            {/* PRIORITY */}

                            <div className="service-form-group">

                                <label>
                                    Priority
                                </label>

                                <select
                                    name="priority"
                                    value={
                                        form.priority
                                    }
                                    onChange={
                                        handleChange
                                    }
                                >

                                    {PRIORITY_OPTIONS.map(
                                        (
                                            item
                                        ) => (
                                            <option
                                                key={
                                                    item.value
                                                }
                                                value={
                                                    item.value
                                                }
                                            >
                                                {
                                                    item.label
                                                }
                                            </option>
                                        )
                                    )}

                                </select>

                            </div>


                            {/* STATUS */}

                            <div className="service-form-group">

                                <label>
                                    Status
                                </label>

                                <select
                                    name="status"
                                    value={
                                        form.status
                                    }
                                    onChange={
                                        handleChange
                                    }
                                >

                                    {STATUS_OPTIONS.map(
                                        (
                                            item
                                        ) => (
                                            <option
                                                key={
                                                    item.value
                                                }
                                                value={
                                                    item.value
                                                }
                                            >
                                                {
                                                    item.label
                                                }
                                            </option>
                                        )
                                    )}

                                </select>


                                <small className="service-form-help">
                                    Open is stored in the backend as REQUESTED.
                                </small>

                            </div>


                            {/* SERVICE AMOUNT */}

                            <div className="service-form-group">

                                <label>
                                    Service Amount
                                </label>

                                <input
                                    type="number"
                                    name="total_amount"
                                    value={
                                        form.total_amount
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    min="0"
                                    step="0.01"
                                    placeholder="0.00"
                                />

                                {errors.total_amount && (
                                    <small className="service-form-error">
                                        {
                                            errors.total_amount
                                        }
                                    </small>
                                )}

                            </div>


                            {/* PAYMENT STATUS */}

                            <div className="service-form-group">

                                <label>
                                    Payment Status
                                </label>

                                <select
                                    name="payment_status"
                                    value={
                                        form.payment_status
                                    }
                                    onChange={
                                        handleChange
                                    }
                                >

                                    {PAYMENT_OPTIONS.map(
                                        (
                                            item
                                        ) => (
                                            <option
                                                key={
                                                    item.value
                                                }
                                                value={
                                                    item.value
                                                }
                                            >
                                                {
                                                    item.label
                                                }
                                            </option>
                                        )
                                    )}

                                </select>

                            </div>

                        </div>

                    </div>


                    {/* =========================================
                        SERVICE DETAILS
                    ========================================= */}

                    <div className="service-form-section">

                        <h3>
                            Service Details
                        </h3>


                        <div className="service-form-grid">


                            {/* EXPECTED VISIT DATE */}

                            <div className="service-form-group">

                                <label>
                                    Expected Visit Date
                                </label>

                                <input
                                    type="date"
                                    name="expected_visit_date"
                                    value={
                                        form.expected_visit_date
                                    }
                                    min={
                                        form.service_date ||
                                        undefined
                                    }
                                    onChange={
                                        handleChange
                                    }
                                />

                                {errors.expected_visit_date && (
                                    <small className="service-form-error">
                                        {
                                            errors.expected_visit_date
                                        }
                                    </small>
                                )}

                            </div>


                            {/* VISIT DATE */}

                            <div className="service-form-group">

                                <label>
                                    Visit Date
                                </label>

                                <input
                                    type="date"
                                    name="visit_date"
                                    value={
                                        form.visit_date
                                    }
                                    min={
                                        form.service_date ||
                                        undefined
                                    }
                                    onChange={
                                        handleChange
                                    }
                                />

                                {errors.visit_date && (
                                    <small className="service-form-error">
                                        {
                                            errors.visit_date
                                        }
                                    </small>
                                )}

                            </div>


                            {/* COMPLETION DATE */}

                            <div className="service-form-group">

                                <label>
                                    Completion Date
                                </label>

                                <input
                                    type="date"
                                    name="completion_date"
                                    value={
                                        form.completion_date
                                    }
                                    min={
                                        form.service_date ||
                                        undefined
                                    }
                                    onChange={
                                        handleChange
                                    }
                                />

                                {errors.completion_date && (
                                    <small className="service-form-error">
                                        {
                                            errors.completion_date
                                        }
                                    </small>
                                )}

                            </div>


                            {/* METER READING */}

                            <div className="service-form-group">

                                <label>
                                    Meter Reading
                                </label>

                                <input
                                    type="number"
                                    name="meter_reading"
                                    value={
                                        form.meter_reading
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    min="0"
                                    step="1"
                                    placeholder="0"
                                />

                                {errors.meter_reading && (
                                    <small className="service-form-error">
                                        {
                                            errors.meter_reading
                                        }
                                    </small>
                                )}

                            </div>


                            {/* MATERIAL USED */}

                            <div className="service-form-group full">

                                <label>
                                    Material Used
                                </label>

                                <textarea
                                    name="material_used"
                                    value={
                                        form.material_used
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Enter material used. Enter No if no material was used."
                                    rows="3"
                                    maxLength="5000"
                                />

                            </div>


                            {/* REMARKS */}

                            <div className="service-form-group full">

                                <label>
                                    Remarks
                                </label>

                                <textarea
                                    name="remarks"
                                    value={
                                        form.remarks
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Additional remarks..."
                                    rows="3"
                                    maxLength="2000"
                                />

                            </div>

                        </div>

                    </div>


                    {/* =========================================
                        FOOTER
                    ========================================= */}

                    <div className="service-drawer-footer">

                        <button
                            type="button"
                            className="service-drawer-cancel"
                            onClick={
                                onClose
                            }
                        >
                            Cancel
                        </button>


                        <button
                            type="submit"
                            className="service-drawer-save"
                        >

                            <Save
                                size={17}
                            />

                            {
                                mode ===
                                "edit"
                                    ? "Update Service"
                                    : "Create Service"
                            }

                        </button>

                    </div>

                </form>

            </div>

        </div>
    );
};


export default ServiceDrawer;