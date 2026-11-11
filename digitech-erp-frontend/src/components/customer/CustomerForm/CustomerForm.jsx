import "./CustomerForm.css";

import {
    X,
    Save,
    User,
    Building2,
    MapPin,
    CreditCard,
    Cpu,
    Plus,
    Trash2,
    FileText,
    Upload,
    Eye,
    Download,
} from "lucide-react";

import { useEffect, useState } from "react";
import { toast } from "react-toastify";

import { useCustomers } from "../../../context/CustomerContext";
import api from "../../../api/axios";

import rentalDocumentService from "../../../services/rentalDocumentService";


const MAX_PDF_SIZE = 10 * 1024 * 1024;


// =====================================================
// EMPTY MACHINE
// =====================================================

const createEmptyMachine = () => ({
    machine_id: null,

    machine_name: "",

    machine_serial_number: "",


    // Rental / Billing

    rental_rate: "",

    rental_advance: "",

    // Free-copy allowances per month, separated by print type
    a4_bw_free_copies: "",
    a4_color_free_copies: "",
    a3_bw_free_copies: "",
    a3_color_free_copies: "",


    // Per-copy billing rates

    a4_bw_rate: "",

    a4_color_rate: "",

    a3_bw_rate: "",

    a3_color_rate: "",


    // Documents

    rental_agreement_file: null,

    rental_agreement_url: "",

    rental_agreement_name: "",

    installation_report_file: null,

    installation_report_url: "",

    installation_report_name: "",
});


// =====================================================
// NORMALIZE CUSTOMER MACHINES
// =====================================================

const normalizeCustomerMachines = (customer) => {

    if (
        Array.isArray(customer?.machines) &&
        customer.machines.length > 0
    ) {

        return customer.machines.map((machine) => ({

            machine_id:
                machine.machine_id ??
                machine.id ??
                null,


            machine_name:
                machine.machine_name ??
                machine.name ??
                "",


            machine_serial_number:
                machine.machine_serial_number ??
                machine.serial_number ??
                "",


            rental_rate:
                machine.rental_rate ??
                machine.fixed_rental_amount ??
                machine.rental_amount ??
                "",


            rental_advance:
                machine.rental_advance ??
                machine.rental_advance_taken ??
                "",


            a4_bw_free_copies:
                machine.a4_bw_free_copies ??
                machine.a4_bw_free_prints ??
                "",

            a4_color_free_copies:
                machine.a4_color_free_copies ??
                machine.a4_color_free_prints ??
                "",

            a3_bw_free_copies:
                machine.a3_bw_free_copies ??
                machine.a3_bw_free_prints ??
                "",

            a3_color_free_copies:
                machine.a3_color_free_copies ??
                machine.a3_color_free_prints ??
                "",


            a4_bw_rate:
                machine.a4_bw_rate ??
                machine.a4_black_white_rate ??
                machine.a4_bw ??
                "",


            a4_color_rate:
                machine.a4_color_rate ??
                machine.a4_colour_rate ??
                machine.a4_color ??
                "",


            a3_bw_rate:
                machine.a3_bw_rate ??
                machine.a3_black_white_rate ??
                machine.a3_bw ??
                "",


            a3_color_rate:
                machine.a3_color_rate ??
                machine.a3_colour_rate ??
                machine.a3_color ??
                "",


            rental_agreement_file: null,

            rental_agreement_url:
                machine.rental_agreement_url ??
                machine.rental_agreement ??
                "",


            rental_agreement_name:
                machine.rental_agreement_name ??
                "",


            installation_report_file: null,

            installation_report_url:
                machine.installation_report_url ??
                machine.installation_report ??
                "",


            installation_report_name:
                machine.installation_report_name ??
                "",


            rental_agreement_exists:
                Boolean(
                    machine.rental_agreement_exists
                ),


            installation_report_exists:
                Boolean(
                    machine.installation_report_exists
                ),
        }));

    }


    // =================================================
    // BACKWARD COMPATIBILITY
    // =================================================

    if (
        customer?.machine_id ||
        customer?.machine_name ||
        customer?.machine_serial_number
    ) {

        return [
            {

                machine_id:
                    customer.machine_id ??
                    null,


                machine_name:
                    customer.machine_name ??
                    "",


                machine_serial_number:
                    customer.machine_serial_number ??
                    "",


                rental_rate:
                    customer.rental_rate ??
                    customer.fixed_rental_amount ??
                    customer.rental_amount ??
                    "",


                rental_advance:
                    customer.rental_advance ??
                    customer.rental_advance_taken ??
                    "",


                a4_bw_free_copies:
                    customer.a4_bw_free_copies ??
                    customer.a4_bw_free_prints ??
                    "",

                a4_color_free_copies:
                    customer.a4_color_free_copies ??
                    customer.a4_color_free_prints ??
                    "",

                a3_bw_free_copies:
                    customer.a3_bw_free_copies ??
                    customer.a3_bw_free_prints ??
                    "",

                a3_color_free_copies:
                    customer.a3_color_free_copies ??
                    customer.a3_color_free_prints ??
                    "",


                a4_bw_rate:
                    customer.a4_bw_rate ??
                    customer.a4_black_white_rate ??
                    customer.a4_bw ??
                    "",


                a4_color_rate:
                    customer.a4_color_rate ??
                    customer.a4_colour_rate ??
                    customer.a4_color ??
                    "",


                a3_bw_rate:
                    customer.a3_bw_rate ??
                    customer.a3_black_white_rate ??
                    customer.a3_bw ??
                    "",


                a3_color_rate:
                    customer.a3_color_rate ??
                    customer.a3_colour_rate ??
                    customer.a3_color ??
                    "",


                rental_agreement_file: null,

                rental_agreement_url:
                    customer.rental_agreement_url ??
                    customer.rental_agreement ??
                    "",


                rental_agreement_name:
                    customer.rental_agreement_name ??
                    "",


                installation_report_file: null,

                installation_report_url:
                    customer.installation_report_url ??
                    customer.installation_report ??
                    "",


                installation_report_name:
                    customer.installation_report_name ??
                    "",
            },
        ];

    }


    return [
        createEmptyMachine()
    ];
};


// =====================================================
// COMPONENT
// =====================================================

const CustomerForm = () => {

    const {
        selectedCustomer,
        setSelectedCustomer,
        createCustomer,
        updateCustomer,
    } = useCustomers();


    const isEdit =
        selectedCustomer &&
        selectedCustomer.__edit === true;


    const isCreate =
        selectedCustomer &&
        selectedCustomer.__create === true;


    // =================================================
    // FORM
    // =================================================

    const [form, setForm] = useState({

        customer_name: "",

        contact_person: "",

        phone: "",

        email: "",

        website: "",


        machines: [
            createEmptyMachine()
        ],

        removed_machine_ids: [],


        gstin: "",

        pan: "",


        billing_address: "",

        shipping_address: "",

        city: "",

        state: "",

        country: "India",

        pincode: "",


        credit_limit: "0",

        credit_days: "0",

        opening_balance: "0",


        remarks: "",

        is_active: true,
    });


    const [saving, setSaving] =
        useState(false);


    // =================================================
    // LOAD CUSTOMER INTO FORM
    // =================================================

    useEffect(() => {

        if (!selectedCustomer) {
            return;
        }


        // CREATE

        if (selectedCustomer.__create) {

            setForm({

                customer_name:
                    selectedCustomer.prefill_customer_name ||
                    "",

                contact_person: "",

                phone: "",

                email: "",

                website: "",


                machines: [
                    createEmptyMachine()
                ],

                removed_machine_ids: [],


                gstin: "",

                pan: "",


                billing_address: "",

                shipping_address: "",

                city: "",

                state: "",

                country: "India",

                pincode: "",


                credit_limit: "0",

                credit_days: "0",

                opening_balance: "0",


                remarks: "",

                is_active: true,
            });

            return;
        }


        // EDIT

        setForm({

            customer_name:
                selectedCustomer.customer_name ||
                "",


            contact_person:
                selectedCustomer.contact_person ||
                "",


            phone:
                selectedCustomer.phone ||
                "",


            email:
                selectedCustomer.email ||
                "",


            website:
                selectedCustomer.website ||
                "",


            machines:
                normalizeCustomerMachines(
                    selectedCustomer
                ),


            removed_machine_ids: [],


            gstin:
                selectedCustomer.gstin ||
                "",


            pan:
                selectedCustomer.pan ||
                "",


            billing_address:
                selectedCustomer.billing_address ||
                "",


            shipping_address:
                selectedCustomer.shipping_address ||
                "",


            city:
                selectedCustomer.city ||
                "",


            state:
                selectedCustomer.state ||
                "",


            country:
                selectedCustomer.country ||
                "India",


            pincode:
                selectedCustomer.pincode ||
                "",


            credit_limit:
                selectedCustomer.credit_limit ??
                "0",


            credit_days:
                selectedCustomer.credit_days ??
                "0",


            opening_balance:
                selectedCustomer.opening_balance ??
                "0",


            remarks:
                selectedCustomer.remarks ||
                "",


            is_active:
                selectedCustomer.is_active ??
                true,
        });


        // Load document status from PostgreSQL for each saved machine.
        // This allows the form to show View/Download even though the
        // PDF bytes themselves are not included in the customer JSON.
        const loadDocumentStatuses = async () => {

            const machines =
                normalizeCustomerMachines(
                    selectedCustomer
                );

            if (!machines.length) {
                return;
            }

            try {

                const statusResults =
                    await Promise.all(
                        machines.map(async (machine) => {

                            if (!machine.machine_id) {
                                return {
                                    machine_id: null,
                                    rental_agreement_exists: false,
                                    installation_report_exists: false,
                                };
                            }

                            try {

                                const status =
                                    await rentalDocumentService
                                        .getMachineDocumentStatus(
                                            machine.machine_id
                                        );

                                return status;

                            } catch (statusError) {

                                console.warn(
                                    `Could not load document status for machine ${machine.machine_id}:`,
                                    statusError
                                );

                                return {
                                    machine_id:
                                        machine.machine_id,
                                    rental_agreement_exists: false,
                                    installation_report_exists: false,
                                };
                            }
                        })
                    );


                setForm((prev) => ({

                    ...prev,

                    machines: prev.machines.map(
                        (machine) => {

                            const status =
                                statusResults.find(
                                    (item) =>
                                        Number(
                                            item?.machine_id
                                        ) ===
                                        Number(
                                            machine.machine_id
                                        )
                                );

                            if (!status) {
                                return machine;
                            }

                            return {
                                ...machine,
                                rental_agreement_exists:
                                    Boolean(
                                        status.rental_agreement_exists
                                    ),
                                installation_report_exists:
                                    Boolean(
                                        status.installation_report_exists
                                    ),
                                rental_agreement_name:
                                    status.rental_agreement_name ||
                                    machine.rental_agreement_name ||
                                    "",
                                installation_report_name:
                                    status.installation_report_name ||
                                    machine.installation_report_name ||
                                    "",
                            };
                        }
                    ),
                }));

            } catch (statusError) {

                console.error(
                    "Failed to load machine document statuses:",
                    statusError
                );
            }
        };


        loadDocumentStatuses();

    }, [selectedCustomer]);


    // =================================================
    // CLOSE
    // =================================================

    const handleClose = () => {

        if (saving) {
            return;
        }

        setSelectedCustomer(null);
    };


    // =================================================
    // CUSTOMER CHANGE
    // =================================================

    const handleChange = (e) => {

        const {
            name,
            value,
            type,
            checked,
        } = e.target;


        setForm((prev) => ({

            ...prev,

            [name]:
                type === "checkbox"
                    ? checked
                    : value,
        }));
    };


    // =================================================
    // MACHINE CHANGE
    // =================================================

    const handleMachineChange = (
        index,
        field,
        value
    ) => {

        setForm((prev) => ({

            ...prev,

            machines:
                prev.machines.map(
                    (
                        machine,
                        machineIndex
                    ) =>
                        machineIndex === index
                            ? {
                                ...machine,
                                [field]: value,
                            }
                            : machine
                ),
        }));
    };


    // =================================================
    // ADD MACHINE
    // =================================================

    const handleAddMachine = () => {

        setForm((prev) => ({

            ...prev,

            machines: [
                ...prev.machines,
                createEmptyMachine(),
            ],
        }));
    };


    // =================================================
    // REMOVE MACHINE
    // =================================================

    const handleRemoveMachine = (
        index
    ) => {

        setForm((prev) => {

            if (
                prev.machines.length === 1
            ) {
                return prev;
            }


            const machineToRemove =
                prev.machines[index];


            return {

                ...prev,

                machines:
                    prev.machines.filter(
                        (
                            _,
                            machineIndex
                        ) =>
                            machineIndex !== index
                    ),


                removed_machine_ids:
                    machineToRemove?.machine_id
                        ? [
                            ...(prev.removed_machine_ids ||
                                []),

                            machineToRemove.machine_id,
                        ]
                        : prev.removed_machine_ids ||
                          [],
            };

        });
    };


    // =================================================
    // PDF UPLOAD / SELECT
    // =================================================

    const handlePdfUpload = (
        index,
        field,
        event
    ) => {

        const file =
            event.target.files?.[0];


        if (!file) {
            return;
        }


        // Validate PDF

        if (
            file.type !==
                "application/pdf" &&
            !file.name
                .toLowerCase()
                .endsWith(".pdf")
        ) {

            toast.error(
                "Only PDF files are allowed."
            );

            event.target.value = "";

            return;
        }


        // Validate size

        if (
            file.size >
            MAX_PDF_SIZE
        ) {

            toast.error(
                "PDF file size must be 10 MB or less."
            );

            event.target.value = "";

            return;
        }


        const isRentalAgreement =
            field ===
            "rental_agreement";


        setForm((prev) => ({

            ...prev,

            machines:
                prev.machines.map(
                    (
                        machine,
                        machineIndex
                    ) => {

                        if (
                            machineIndex !==
                            index
                        ) {

                            return machine;
                        }


                        if (
                            isRentalAgreement
                        ) {

                            return {

                                ...machine,

                                rental_agreement_file:
                                    file,

                                rental_agreement_name:
                                    file.name,
                            };

                        }


                        return {

                            ...machine,

                            installation_report_file:
                                file,

                            installation_report_name:
                                file.name,
                        };

                    }
                ),
        }));


        event.target.value = "";
    };


    // =================================================
    // OPEN DOCUMENT
    // =================================================

    const openDocument = async (
        machineId,
        documentType,
        file,
        url
    ) => {
        try {
            // Newly selected file: open directly from browser memory.
            if (file) {
                const objectUrl =
                    window.URL.createObjectURL(file);

                window.open(
                    objectUrl,
                    "_blank",
                    "noopener,noreferrer"
                );

                setTimeout(() => {
                    window.URL.revokeObjectURL(objectUrl);
                }, 60000);

                return;
            }

            // Saved document: get it from FastAPI using the
            // authenticated Axios instance.
            if (machineId) {
                const response = await api.get(
                    `/rental-bills/machines/${machineId}/documents/${documentType}`,
                    {
                        responseType: "blob",
                    }
                );

                const blob = new Blob(
                    [response.data],
                    {
                        type:
                            response.headers?.["content-type"] ||
                            "application/pdf",
                    }
                );

                const objectUrl =
                    window.URL.createObjectURL(blob);

                window.open(
                    objectUrl,
                    "_blank",
                    "noopener,noreferrer"
                );

                setTimeout(() => {
                    window.URL.revokeObjectURL(objectUrl);
                }, 60000);

                return;
            }

            // Backward compatibility if an old URL is available.
            if (url) {
                window.open(
                    url,
                    "_blank",
                    "noopener,noreferrer"
                );
            }
        } catch (error) {
            console.error("Failed to open document:", error);

            const message =
                error?.response?.data?.detail ||
                "Failed to open document.";

            toast.error(
                typeof message === "string"
                    ? message
                    : "Failed to open document."
            );
        }
    };


    const downloadDocument = async (
        machineId,
        documentType,
        file,
        url,
        fileName
    ) => {
        try {
            // Newly selected file: download directly from browser memory.
            if (file) {
                const objectUrl =
                    window.URL.createObjectURL(file);

                const link =
                    document.createElement("a");

                link.href = objectUrl;
                link.download =
                    file.name ||
                    fileName ||
                    "document.pdf";

                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                setTimeout(() => {
                    window.URL.revokeObjectURL(objectUrl);
                }, 1000);

                return;
            }

            // Saved document: download through the authenticated API.
            if (machineId) {
                const response = await api.get(
                    `/rental-bills/machines/${machineId}/documents/${documentType}`,
                    {
                        responseType: "blob",
                    }
                );

                const blob = new Blob(
                    [response.data],
                    {
                        type:
                            response.headers?.["content-type"] ||
                            "application/pdf",
                    }
                );

                const objectUrl =
                    window.URL.createObjectURL(blob);

                const link =
                    document.createElement("a");

                link.href = objectUrl;
                link.download =
                    fileName ||
                    "document.pdf";

                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                setTimeout(() => {
                    window.URL.revokeObjectURL(objectUrl);
                }, 1000);

                return;
            }

            // Backward compatibility if an old URL is available.
            if (url) {
                const link =
                    document.createElement("a");

                link.href = url;
                link.target = "_blank";
                link.rel = "noopener noreferrer";
                link.download =
                    fileName ||
                    "document.pdf";

                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        } catch (error) {
            console.error("Failed to download document:", error);

            const message =
                error?.response?.data?.detail ||
                "Failed to download document.";

            toast.error(
                typeof message === "string"
                    ? message
                    : "Failed to download document."
            );
        }
    };


    // =================================================
    // HAS DOCUMENT
    // =================================================

    const hasDocument = (
        file,
        url,
        exists
    ) => Boolean(
        file ||
        url ||
        exists
    );


    // =====================================================
    // UPLOAD MACHINE DOCUMENTS
    // =====================================================

    const uploadMachineDocuments = async (
        savedCustomer,
        machineRows
    ) => {

        if (
            !savedCustomer?.machines ||
            !Array.isArray(
                savedCustomer.machines
            )
        ) {

            return;
        }


        for (
            const machineRow
            of machineRows
        ) {

            const rentalAgreement =
                machineRow.rental_agreement_file;


            const installationReport =
                machineRow.installation_report_file;


            // Nothing selected

            if (
                !rentalAgreement &&
                !installationReport
            ) {

                continue;
            }


            // -------------------------------------------------
            // Find saved machine
            // -------------------------------------------------

            const rowMachineId =
                machineRow.machine_id;


            let savedMachine = null;


            // First try machine ID

            if (rowMachineId) {

                savedMachine =
                    savedCustomer.machines.find(
                        (machine) =>
                            Number(
                                machine.id ??
                                machine.machine_id
                            ) ===
                            Number(
                                rowMachineId
                            )
                    );
            }


            // -------------------------------------------------
            // If new machine, find by serial number
            // -------------------------------------------------

            if (!savedMachine) {

                const rowSerial =
                    String(
                        machineRow
                            .machine_serial_number ||
                        ""
                    )
                        .trim()
                        .toLowerCase();


                savedMachine =
                    savedCustomer.machines.find(
                        (machine) => {

                            const savedSerial =
                                String(
                                    machine.machine_serial_number ??
                                    machine.serial_number ??
                                    ""
                                )
                                    .trim()
                                    .toLowerCase();


                            return (
                                savedSerial &&
                                savedSerial ===
                                    rowSerial
                            );
                        }
                    );
            }


            if (!savedMachine) {

                throw new Error(
                    `Machine with serial number "${machineRow.machine_serial_number}" was not found after saving.`
                );
            }


            const machineId =
                savedMachine.id ??
                savedMachine.machine_id;


            if (!machineId) {

                throw new Error(
                    `Machine ID missing for machine "${machineRow.machine_serial_number}".`
                );
            }


            // -------------------------------------------------
            // Upload
            // -------------------------------------------------

            try {

                await rentalDocumentService
                    .uploadMachineDocuments(
                        machineId,
                        rentalAgreement,
                        installationReport
                    );

            } catch (uploadError) {

                console.error(
                    "Machine document upload failed:",
                    uploadError
                );

                const detail =
                    uploadError?.response?.data?.detail ||
                    uploadError?.message ||
                    "Document upload failed.";

                throw new Error(
                    `Machine ${machineId}: ${
                        typeof detail === "string"
                            ? detail
                            : "Document upload failed."
                    }`
                );
            }
        }
    };


    // =================================================
    // SUBMIT
    // =================================================

    const handleSubmit = async (
        e
    ) => {

        e.preventDefault();


        // -------------------------------------------------
        // Customer validation
        // -------------------------------------------------

        if (
            !form.customer_name.trim()
        ) {

            toast.error(
                "Customer name is required."
            );

            return;
        }


        // -------------------------------------------------
        // Get meaningful machine rows
        // -------------------------------------------------

        const machineRows =
            form.machines.filter(
                (machine) =>

                    machine.machine_name.trim() ||

                    machine.machine_serial_number.trim() ||

                    machine.rental_rate !== "" ||

                    machine.rental_advance !== "" ||

                    machine.a4_bw_free_copies !== "" ||
                    machine.a4_color_free_copies !== "" ||
                    machine.a3_bw_free_copies !== "" ||
                    machine.a3_color_free_copies !== "" ||

                    machine.a4_bw_rate !== "" ||

                    machine.a4_color_rate !== "" ||

                    machine.a3_bw_rate !== "" ||

                    machine.a3_color_rate !== "" ||

                    machine.rental_agreement_file ||

                    machine.rental_agreement_url ||

                    machine.installation_report_file ||

                    machine.installation_report_url
            );


        // -------------------------------------------------
        // Validate machines
        // -------------------------------------------------

        for (
            let index = 0;
            index < machineRows.length;
            index += 1
        ) {

            const machine =
                machineRows[index];


            if (
                !machine.machine_name.trim() ||
                !machine.machine_serial_number.trim()
            ) {

                toast.error(
                    `Machine ${index + 1}: enter both machine name/model and serial number.`
                );

                return;
            }
        }


        // -------------------------------------------------
        // Duplicate serial validation
        // -------------------------------------------------

        const serialNumbers =
            machineRows.map(
                (machine) =>
                    machine.machine_serial_number
                        .trim()
                        .toLowerCase()
            );


        const duplicateSerial =
            serialNumbers.find(
                (
                    serial,
                    index
                ) =>
                    serialNumbers.indexOf(
                        serial
                    ) !== index
            );


        if (duplicateSerial) {

            toast.error(
                `Duplicate machine serial number: ${duplicateSerial}`
            );

            return;
        }


        try {

            setSaving(true);


            // -------------------------------------------------
            // Machine JSON payload
            // -------------------------------------------------

            const machinePayload =
                machineRows.map(
                    (machine) => ({

                        id:
                            machine.machine_id ??
                            null,


                        machine_id:
                            machine.machine_id ??
                            null,


                        machine_name:
                            machine.machine_name
                                .trim(),


                        machine_serial_number:
                            machine.machine_serial_number
                                .trim(),


                        rental_rate:
                            machine.rental_rate ||
                            "0",


                        rental_advance:
                            machine.rental_advance ||
                            "0",


                        a4_bw_free_copies:
                            machine.a4_bw_free_copies ||
                            "0",

                        a4_color_free_copies:
                            machine.a4_color_free_copies ||
                            "0",

                        a3_bw_free_copies:
                            machine.a3_bw_free_copies ||
                            "0",

                        a3_color_free_copies:
                            machine.a3_color_free_copies ||
                            "0",


                        a4_bw_rate:
                            machine.a4_bw_rate ||
                            "0",


                        a4_color_rate:
                            machine.a4_color_rate ||
                            "0",


                        a3_bw_rate:
                            machine.a3_bw_rate ||
                            "0",


                        a3_color_rate:
                            machine.a3_color_rate ||
                            "0",
                    })
                );


            // =================================================
            // CREATE
            // =================================================

            if (isCreate) {

                const payload = {

                    customer_name:
                        form.customer_name
                            .trim(),


                    contact_person:
                        form.contact_person
                            .trim() ||
                        null,


                    phone:
                        form.phone
                            .trim() ||
                        null,


                    email:
                        form.email
                            .trim() ||
                        null,


                    website:
                        form.website
                            .trim() ||
                        null,


                    machines:
                        machinePayload,


                    machine_name:
                        machineRows[0]
                            ?.machine_name
                            .trim() ||
                        null,


                    machine_serial_number:
                        machineRows[0]
                            ?.machine_serial_number
                            .trim() ||
                        null,


                    gstin:
                        form.gstin
                            .trim() ||
                        null,


                    pan:
                        form.pan
                            .trim() ||
                        null,


                    billing_address:
                        form.billing_address
                            .trim() ||
                        null,


                    shipping_address:
                        form.shipping_address
                            .trim() ||
                        null,


                    city:
                        form.city
                            .trim() ||
                        null,


                    state:
                        form.state
                            .trim() ||
                        null,


                    country:
                        form.country
                            .trim() ||
                        null,


                    pincode:
                        form.pincode
                            .trim() ||
                        null,


                    credit_limit:
                        form.credit_limit ||
                        "0",


                    credit_days:
                        Number(
                            form.credit_days ||
                            0
                        ),


                    opening_balance:
                        form.opening_balance ||
                        "0",


                    remarks:
                        form.remarks
                            .trim() ||
                        null,


                    is_active:
                        form.is_active,
                };


                // ---------------------------------------------
                // Save customer + machines
                // ---------------------------------------------

                const createdCustomer =
                    await createCustomer(
                        payload
                    );


                // ---------------------------------------------
                // Upload PDFs
                // ---------------------------------------------

                await uploadMachineDocuments(
                    createdCustomer,
                    machineRows
                );


                toast.success(
                    machineRows.length > 0
                        ? "Customer, machines and documents saved successfully."
                        : "Customer created successfully."
                );
            }


            // =================================================
            // EDIT
            // =================================================

            if (isEdit) {

                const payload = {

                    customer_name:
                        form.customer_name
                            .trim(),


                    contact_person:
                        form.contact_person
                            .trim() ||
                        null,


                    phone:
                        form.phone
                            .trim() ||
                        null,


                    email:
                        form.email
                            .trim() ||
                        null,


                    website:
                        form.website
                            .trim() ||
                        null,


                    machines:
                        machinePayload,


                    removed_machine_ids:
                        form.removed_machine_ids ||
                        [],


                    machine_id:
                        machineRows[0]
                            ?.machine_id ??
                        selectedCustomer.machine_id ??
                        null,


                    machine_name:
                        machineRows[0]
                            ?.machine_name
                            .trim() ||
                        null,


                    machine_serial_number:
                        machineRows[0]
                            ?.machine_serial_number
                            .trim() ||
                        null,


                    gstin:
                        form.gstin
                            .trim() ||
                        null,


                    pan:
                        form.pan
                            .trim() ||
                        null,


                    billing_address:
                        form.billing_address
                            .trim() ||
                        null,


                    shipping_address:
                        form.shipping_address
                            .trim() ||
                        null,


                    city:
                        form.city
                            .trim() ||
                        null,


                    state:
                        form.state
                            .trim() ||
                        null,


                    country:
                        form.country
                            .trim() ||
                        null,


                    pincode:
                        form.pincode
                            .trim() ||
                        null,


                    credit_limit:
                        form.credit_limit ||
                        "0",


                    credit_days:
                        Number(
                            form.credit_days ||
                            0
                        ),


                    remarks:
                        form.remarks
                            .trim() ||
                        null,


                    is_active:
                        form.is_active,
                };


                // ---------------------------------------------
                // Update customer + machines
                // ---------------------------------------------

                const updatedCustomer =
                    await updateCustomer(
                        selectedCustomer.id,
                        payload
                    );


                // ---------------------------------------------
                // Upload new/replaced PDFs
                // ---------------------------------------------

                await uploadMachineDocuments(
                    updatedCustomer,
                    machineRows
                );


                toast.success(
                    "Customer, machines and documents updated successfully."
                );
            }


            setSelectedCustomer(null);

        }

        catch (error) {

            console.error(
                "Customer save failed:",
                error
            );


            const message =
                error?.response?.data?.detail ||
                error?.message ||
                "Failed to save customer.";


            toast.error(
                Array.isArray(message)
                    ? message
                        .map(
                            (item) =>
                                item.msg
                        )
                        .join(", ")
                    : message
            );

        }

        finally {

            setSaving(false);

        }
    };


    // =================================================
    // NO CUSTOMER SELECTED
    // =================================================

    if (!selectedCustomer) {
        return null;
    }


    // =================================================
    // UI
    // =================================================

    return (

        <div className="customer-drawer-overlay">

            <div className="customer-drawer">


                {/* =================================================
                    HEADER
                ================================================= */}

                <div className="customer-drawer-header">

                    <div>

                        <h2>
                            {isEdit
                                ? "Edit Customer"
                                : "Add Customer"}
                        </h2>


                        <p>
                            {isEdit
                                ? "Update customer information and assigned machines"
                                : "Create a new customer account and assign leased equipment"}
                        </p>

                    </div>


                    <button
                        type="button"
                        className="customer-drawer-close"
                        onClick={handleClose}
                        disabled={saving}
                    >

                        <X size={20} />

                    </button>

                </div>


                <form
                    className="customer-form"
                    onSubmit={handleSubmit}
                >


                    {/* =================================================
                        CUSTOMER INFORMATION
                    ================================================= */}

                    <div className="customer-form-section customer-information-section">

                        <div className="customer-form-section-title">

                            <User size={17} />

                            <span>
                                Customer Information
                            </span>

                        </div>


                        <div className="customer-form-grid">


                            <div className="customer-form-group full">

                                <label>

                                    Customer / Company Name

                                    <span>*</span>

                                </label>


                                <input
                                    type="text"
                                    name="customer_name"
                                    value={
                                        form.customer_name
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="e.g. Apex Copiers Pvt. Ltd."
                                    required
                                    disabled={saving}
                                />

                            </div>


                            <div className="customer-form-group">

                                <label>
                                    Contact Person
                                </label>


                                <input
                                    type="text"
                                    name="contact_person"
                                    value={
                                        form.contact_person
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="e.g. John Doe"
                                    disabled={saving}
                                />

                            </div>


                            <div className="customer-form-group">

                                <label>
                                    Phone Number
                                </label>


                                <input
                                    type="tel"
                                    name="phone"
                                    value={
                                        form.phone
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="+91 98765 43210"
                                    disabled={saving}
                                />

                            </div>


                            <div className="customer-form-group">

                                <label>
                                    Email Address
                                </label>


                                <input
                                    type="email"
                                    name="email"
                                    value={
                                        form.email
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="name@company.com"
                                    disabled={saving}
                                />

                            </div>


                            <div className="customer-form-group">

                                <label>
                                    Website
                                </label>


                                <input
                                    type="text"
                                    name="website"
                                    value={
                                        form.website
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="https://company.com"
                                    disabled={saving}
                                />

                            </div>

                        </div>

                    </div>


                    {/* =================================================
                        MACHINE INFORMATION
                    ================================================= */}

                    <div className="customer-form-section customer-machines-section">


                        <div className="customer-machine-section-header">


                            <div className="customer-form-section-title customer-machine-section-title">

                                <Cpu size={17} />

                                <span>

                                    Assigned Machines (
                                    {form.machines.length}
                                    )

                                </span>

                            </div>


                            {(isCreate ||
                                isEdit) && (

                                <button
                                    type="button"
                                    className="customer-add-machine-btn"
                                    onClick={
                                        handleAddMachine
                                    }
                                    disabled={saving}
                                >

                                    <Plus size={15} />

                                    Add Machine

                                </button>

                            )}

                        </div>


                        <div className="customer-machines-list">


                            {form.machines.map(
                                (
                                    machine,
                                    index
                                ) => {

                                    const agreementExists =
                                        hasDocument(
                                            machine.rental_agreement_file,
                                            machine.rental_agreement_url
                                        );


                                    const installationExists =
                                        hasDocument(
                                            machine.installation_report_file,
                                            machine.installation_report_url,
                                            machine.installation_report_exists
                                        );


                                    return (

                                        <div
                                            className="customer-machine-card"
                                            key={
                                                machine.machine_id ??
                                                `machine-${index}`
                                            }
                                        >


                                            <div className="customer-machine-card-header">


                                                <div className="customer-machine-number">

                                                    <span>
                                                        #
                                                        {index + 1}
                                                    </span>


                                                    <strong>
                                                        Machine{" "}
                                                        {index + 1}
                                                    </strong>

                                                </div>


                                                {(isCreate ||
                                                    isEdit) && (

                                                    <button
                                                        type="button"
                                                        className="customer-machine-card-remove"
                                                        onClick={() =>
                                                            handleRemoveMachine(
                                                                index
                                                            )
                                                        }
                                                        disabled={
                                                            saving ||
                                                            form.machines.length === 1
                                                        }
                                                        title={
                                                            form.machines.length === 1
                                                                ? "At least one machine is required"
                                                                : "Remove machine"
                                                        }
                                                    >

                                                        <Trash2
                                                            size={16}
                                                        />

                                                    </button>

                                                )}

                                            </div>


                                            {/* MACHINE BASIC DETAILS */}

                                            <div className="customer-form-grid">


                                                <div className="customer-form-group">

                                                    <label>

                                                        Machine Name / Model

                                                        <span>*</span>

                                                    </label>


                                                    <input
                                                        type="text"
                                                        value={
                                                            machine.machine_name
                                                        }
                                                        onChange={(e) =>
                                                            handleMachineChange(
                                                                index,
                                                                "machine_name",
                                                                e.target.value
                                                            )
                                                        }
                                                        placeholder="e.g. Canon imageRUNNER 2625"
                                                        disabled={
                                                            saving
                                                        }
                                                    />

                                                </div>


                                                <div className="customer-form-group">

                                                    <label>

                                                        Serial Number

                                                        <span>*</span>

                                                    </label>


                                                    <input
                                                        type="text"
                                                        value={
                                                            machine.machine_serial_number
                                                        }
                                                        onChange={(e) =>
                                                            handleMachineChange(
                                                                index,
                                                                "machine_serial_number",
                                                                e.target.value
                                                            )
                                                        }
                                                        placeholder="e.g. CN-IR2625-9941"
                                                        disabled={
                                                            saving
                                                        }
                                                    />

                                                </div>

                                            </div>


                                            {/* RENTAL INFORMATION */}

                                            <div className="customer-rental-information">


                                                <div className="customer-rental-title">

                                                    <CreditCard
                                                        size={15}
                                                    />

                                                    <span>
                                                        Rental & Billing Terms
                                                    </span>

                                                </div>


                                                <div className="customer-rental-grid">


                                                    <div className="customer-rental-group">

                                                        <label>
                                                            Fixed Rent (₹)
                                                        </label>


                                                        <input
                                                            type="number"
                                                            min="0"
                                                            step="0.01"
                                                            value={
                                                                machine.rental_rate
                                                            }
                                                            onChange={(e) =>
                                                                handleMachineChange(
                                                                    index,
                                                                    "rental_rate",
                                                                    e.target.value
                                                                )
                                                            }
                                                            placeholder="e.g. 4500"
                                                            disabled={
                                                                saving
                                                            }
                                                        />

                                                    </div>


                                                    <div className="customer-rental-group">

                                                        <label>
                                                            Rental Advance (₹)
                                                        </label>


                                                        <input
                                                            type="number"
                                                            min="0"
                                                            step="0.01"
                                                            value={
                                                                machine.rental_advance
                                                            }
                                                            onChange={(e) =>
                                                                handleMachineChange(
                                                                    index,
                                                                    "rental_advance",
                                                                    e.target.value
                                                                )
                                                            }
                                                            placeholder="e.g. 10000"
                                                            disabled={
                                                                saving
                                                            }
                                                        />

                                                    </div>


                                                    {/* FREE-COPY ALLOWANCES: separate allowance for each print type */}
                                                    <div className="customer-rental-group">
                                                        <label>A4 B/W Free Copies / Mo</label>
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            step="1"
                                                            value={machine.a4_bw_free_copies ?? ""}
                                                            onChange={(e) =>
                                                                handleMachineChange(index, "a4_bw_free_copies", e.target.value)
                                                            }
                                                            placeholder="e.g. 500"
                                                            disabled={saving}
                                                        />
                                                    </div>

                                                    <div className="customer-rental-group">
                                                        <label>A4 Color Free Copies / Mo</label>
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            step="1"
                                                            value={machine.a4_color_free_copies ?? ""}
                                                            onChange={(e) =>
                                                                handleMachineChange(index, "a4_color_free_copies", e.target.value)
                                                            }
                                                            placeholder="e.g. 100"
                                                            disabled={saving}
                                                        />
                                                    </div>

                                                    <div className="customer-rental-group">
                                                        <label>A3 B/W Free Copies / Mo</label>
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            step="1"
                                                            value={machine.a3_bw_free_copies ?? ""}
                                                            onChange={(e) =>
                                                                handleMachineChange(index, "a3_bw_free_copies", e.target.value)
                                                            }
                                                            placeholder="e.g. 50"
                                                            disabled={saving}
                                                        />
                                                    </div>

                                                    <div className="customer-rental-group">
                                                        <label>A3 Color Free Copies / Mo</label>
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            step="1"
                                                            value={machine.a3_color_free_copies ?? ""}
                                                            onChange={(e) =>
                                                                handleMachineChange(index, "a3_color_free_copies", e.target.value)
                                                            }
                                                            placeholder="e.g. 25"
                                                            disabled={saving}
                                                        />
                                                    </div>

                                                </div>


                                                {/* PER-COPY BILLING RATES */}

                                                <div className="customer-rental-rate-section">


                                                    <div className="customer-rental-rate-title">

                                                        <span>
                                                            Per-Copy Billing Rates
                                                        </span>

                                                        <small>
                                                            Enter the rate for each paper size and print type.
                                                        </small>

                                                    </div>


                                                    <div className="customer-rental-grid customer-rental-rate-grid">


                                                        <div className="customer-rental-group">

                                                            <label>
                                                                A4 B/W (₹/copy)
                                                            </label>


                                                            <input
                                                                type="number"
                                                                min="0"
                                                                step="0.01"
                                                                value={
                                                                    machine.a4_bw_rate
                                                                }
                                                                onChange={(e) =>
                                                                    handleMachineChange(
                                                                        index,
                                                                        "a4_bw_rate",
                                                                        e.target.value
                                                                    )
                                                                }
                                                                placeholder="e.g. 0.40"
                                                                disabled={
                                                                    saving
                                                                }
                                                            />

                                                        </div>


                                                        <div className="customer-rental-group">

                                                            <label>
                                                                A4 Color (₹/copy)
                                                            </label>


                                                            <input
                                                                type="number"
                                                                min="0"
                                                                step="0.01"
                                                                value={
                                                                    machine.a4_color_rate
                                                                }
                                                                onChange={(e) =>
                                                                    handleMachineChange(
                                                                        index,
                                                                        "a4_color_rate",
                                                                        e.target.value
                                                                    )
                                                                }
                                                                placeholder="e.g. 2.00"
                                                                disabled={
                                                                    saving
                                                                }
                                                            />

                                                        </div>


                                                        <div className="customer-rental-group">

                                                            <label>
                                                                A3 B/W (₹/copy)
                                                            </label>


                                                            <input
                                                                type="number"
                                                                min="0"
                                                                step="0.01"
                                                                value={
                                                                    machine.a3_bw_rate
                                                                }
                                                                onChange={(e) =>
                                                                    handleMachineChange(
                                                                        index,
                                                                        "a3_bw_rate",
                                                                        e.target.value
                                                                    )
                                                                }
                                                                placeholder="e.g. 0.80"
                                                                disabled={
                                                                    saving
                                                                }
                                                            />

                                                        </div>


                                                        <div className="customer-rental-group">

                                                            <label>
                                                                A3 Color (₹/copy)
                                                            </label>


                                                            <input
                                                                type="number"
                                                                min="0"
                                                                step="0.01"
                                                                value={
                                                                    machine.a3_color_rate
                                                                }
                                                                onChange={(e) =>
                                                                    handleMachineChange(
                                                                        index,
                                                                        "a3_color_rate",
                                                                        e.target.value
                                                                    )
                                                                }
                                                                placeholder="e.g. 4.00"
                                                                disabled={
                                                                    saving
                                                                }
                                                            />

                                                        </div>

                                                    </div>

                                                </div>

                                            </div>


                                            {/* =================================================
                                                DOCUMENTS
                                            ================================================= */}

                                            <div className="customer-machine-documents">


                                                <div className="customer-documents-title">

                                                    <FileText
                                                        size={15}
                                                    />

                                                    <span>
                                                        Machine Documents
                                                    </span>

                                                </div>


                                                <div className="customer-document-grid">


                                                    {/* =================================================
                                                        RENTAL AGREEMENT
                                                    ================================================= */}

                                                    <div className="customer-document-box">


                                                        <div className="customer-document-box-header">

                                                            <div>

                                                                <strong>
                                                                    Rental Agreement
                                                                </strong>

                                                                <span>
                                                                    PDF only · Max 10 MB
                                                                </span>

                                                            </div>

                                                        </div>


                                                        {agreementExists ? (

                                                            <div className="customer-document-existing">


                                                                <div className="customer-document-existing-info">

                                                                    <FileText
                                                                        size={17}
                                                                    />


                                                                    <div>

                                                                        <strong>

                                                                            {machine.rental_agreement_name ||
                                                                                machine.rental_agreement_file?.name ||
                                                                                "Rental Agreement.pdf"}

                                                                        </strong>


                                                                        <span>
                                                                            PDF uploaded
                                                                        </span>

                                                                    </div>

                                                                </div>


                                                                <div className="customer-document-actions">


                                                                    <button
                                                                        type="button"
                                                                        className="customer-document-btn"
                                                                        onClick={() =>
                                                                            openDocument(
                                                                                machine.machine_id,
                                                                                "rental_agreement",
                                                                                machine.rental_agreement_file,
                                                                                machine.rental_agreement_url
                                                                            )
                                                                        }
                                                                    >

                                                                        <Eye
                                                                            size={14}
                                                                        />

                                                                        View

                                                                    </button>


                                                                    <button
                                                                        type="button"
                                                                        className="customer-document-btn"
                                                                        onClick={() =>
                                                                            downloadDocument(
                                                                                machine.rental_agreement_file,
                                                                                machine.rental_agreement_url,
                                                                                machine.rental_agreement_name ||
                                                                                "rental-agreement.pdf"
                                                                            )
                                                                        }
                                                                    >

                                                                        <Download
                                                                            size={14}
                                                                        />

                                                                        Download

                                                                    </button>

                                                                </div>

                                                            </div>

                                                        ) : (

                                                            <label className="customer-document-upload">


                                                                <div className="customer-document-upload-icon">

                                                                    <Upload
                                                                        size={17}
                                                                    />

                                                                </div>


                                                                <strong>
                                                                    Upload Rental Agreement
                                                                </strong>


                                                                <span>
                                                                    Click to select PDF
                                                                </span>


                                                                <input
                                                                    type="file"
                                                                    accept="application/pdf,.pdf"
                                                                    onChange={(e) =>
                                                                        handlePdfUpload(
                                                                            index,
                                                                            "rental_agreement",
                                                                            e
                                                                        )
                                                                    }
                                                                    disabled={
                                                                        saving
                                                                    }
                                                                />

                                                            </label>

                                                        )}


                                                        {agreementExists && (

                                                            <label className="customer-document-replace">

                                                                <Upload
                                                                    size={13}
                                                                />

                                                                Replace PDF


                                                                <input
                                                                    type="file"
                                                                    accept="application/pdf,.pdf"
                                                                    onChange={(e) =>
                                                                        handlePdfUpload(
                                                                            index,
                                                                            "rental_agreement",
                                                                            e
                                                                        )
                                                                    }
                                                                    disabled={
                                                                        saving
                                                                    }
                                                                />

                                                            </label>

                                                        )}

                                                    </div>


                                                    {/* =================================================
                                                        INSTALLATION REPORT
                                                    ================================================= */}

                                                    <div className="customer-document-box">


                                                        <div className="customer-document-box-header">

                                                            <div>

                                                                <strong>
                                                                    Installation Report
                                                                </strong>

                                                                <span>
                                                                    PDF only · Max 10 MB
                                                                </span>

                                                            </div>

                                                        </div>


                                                        {installationExists ? (

                                                            <div className="customer-document-existing">


                                                                <div className="customer-document-existing-info">

                                                                    <FileText
                                                                        size={17}
                                                                    />


                                                                    <div>

                                                                        <strong>

                                                                            {machine.installation_report_name ||
                                                                                machine.installation_report_file?.name ||
                                                                                "Installation Report.pdf"}

                                                                        </strong>


                                                                        <span>
                                                                            PDF uploaded
                                                                        </span>

                                                                    </div>

                                                                </div>


                                                                <div className="customer-document-actions">


                                                                    <button
                                                                        type="button"
                                                                        className="customer-document-btn"
                                                                        onClick={() =>
                                                                            openDocument(
                                                                                machine.machine_id,
                                                                                "installation_report",
                                                                                machine.installation_report_file,
                                                                                machine.installation_report_url
                                                                            )
                                                                        }
                                                                    >

                                                                        <Eye
                                                                            size={14}
                                                                        />

                                                                        View

                                                                    </button>


                                                                    <button
                                                                        type="button"
                                                                        className="customer-document-btn"
                                                                        onClick={() =>
                                                                            downloadDocument(
                                                                                machine.installation_report_file,
                                                                                machine.installation_report_url,
                                                                                machine.installation_report_name ||
                                                                                "installation-report.pdf"
                                                                            )
                                                                        }
                                                                    >

                                                                        <Download
                                                                            size={14}
                                                                        />

                                                                        Download

                                                                    </button>

                                                                </div>

                                                            </div>

                                                        ) : (

                                                            <label className="customer-document-upload">


                                                                <div className="customer-document-upload-icon">

                                                                    <Upload
                                                                        size={17}
                                                                    />

                                                                </div>


                                                                <strong>
                                                                    Upload Installation Report
                                                                </strong>


                                                                <span>
                                                                    Click to select PDF
                                                                </span>


                                                                <input
                                                                    type="file"
                                                                    accept="application/pdf,.pdf"
                                                                    onChange={(e) =>
                                                                        handlePdfUpload(
                                                                            index,
                                                                            "installation_report",
                                                                            e
                                                                        )
                                                                    }
                                                                    disabled={
                                                                        saving
                                                                    }
                                                                />

                                                            </label>

                                                        )}


                                                        {installationExists && (

                                                            <label className="customer-document-replace">

                                                                <Upload
                                                                    size={13}
                                                                />

                                                                Replace PDF


                                                                <input
                                                                    type="file"
                                                                    accept="application/pdf,.pdf"
                                                                    onChange={(e) =>
                                                                        handlePdfUpload(
                                                                            index,
                                                                            "installation_report",
                                                                            e
                                                                        )
                                                                    }
                                                                    disabled={
                                                                        saving
                                                                    }
                                                                />

                                                            </label>

                                                        )}

                                                    </div>

                                                </div>

                                            </div>

                                        </div>

                                    );

                                }
                            )}

                        </div>

                    </div>


                    {/* =================================================
                        TAX DETAILS
                    ================================================= */}

                    <div className="customer-form-section customer-tax-section">

                        <div className="customer-form-section-title">

                            <Building2 size={17} />

                            <span>
                                Tax Details
                            </span>

                        </div>


                        <div className="customer-form-grid">


                            <div className="customer-form-group">

                                <label>
                                    GSTIN
                                </label>


                                <input
                                    type="text"
                                    name="gstin"
                                    value={
                                        form.gstin
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Enter GSTIN"
                                    disabled={
                                        saving
                                    }
                                />

                            </div>


                            <div className="customer-form-group">

                                <label>
                                    PAN
                                </label>


                                <input
                                    type="text"
                                    name="pan"
                                    value={
                                        form.pan
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Enter PAN"
                                    disabled={
                                        saving
                                    }
                                />

                            </div>

                        </div>

                    </div>


                    {/* =================================================
                        ADDRESS
                    ================================================= */}

                    <div className="customer-form-section customer-address-section">

                        <div className="customer-form-section-title">

                            <MapPin size={17} />

                            <span>
                                Address
                            </span>

                        </div>


                        <div className="customer-form-grid">


                            <div className="customer-form-group full">

                                <label>
                                    Billing Address
                                </label>


                                <textarea
                                    name="billing_address"
                                    value={
                                        form.billing_address
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Enter billing address"
                                    rows="3"
                                    disabled={
                                        saving
                                    }
                                />

                            </div>


                            <div className="customer-form-group full">

                                <label>
                                    Shipping Address
                                </label>


                                <textarea
                                    name="shipping_address"
                                    value={
                                        form.shipping_address
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Enter shipping address"
                                    rows="3"
                                    disabled={
                                        saving
                                    }
                                />

                            </div>


                            <div className="customer-form-group">

                                <label>
                                    City
                                </label>


                                <input
                                    type="text"
                                    name="city"
                                    value={
                                        form.city
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Bengaluru"
                                    disabled={
                                        saving
                                    }
                                />

                            </div>


                            <div className="customer-form-group">

                                <label>
                                    State
                                </label>


                                <input
                                    type="text"
                                    name="state"
                                    value={
                                        form.state
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Karnataka"
                                    disabled={
                                        saving
                                    }
                                />

                            </div>


                            <div className="customer-form-group">

                                <label>
                                    Country
                                </label>


                                <input
                                    type="text"
                                    name="country"
                                    value={
                                        form.country
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="India"
                                    disabled={
                                        saving
                                    }
                                />

                            </div>


                            <div className="customer-form-group">

                                <label>
                                    Pincode
                                </label>


                                <input
                                    type="text"
                                    name="pincode"
                                    value={
                                        form.pincode
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="560001"
                                    disabled={
                                        saving
                                    }
                                />

                            </div>

                        </div>

                    </div>


                    {/* =================================================
                        FINANCIAL
                    ================================================= */}

                    <div className="customer-form-section customer-financial-section">

                        <div className="customer-form-section-title">

                            <CreditCard size={17} />

                            <span>
                                Financial Information
                            </span>

                        </div>


                        <div className="customer-form-grid">


                            <div className="customer-form-group">

                                <label>
                                    Credit Limit
                                </label>


                                <input
                                    type="number"
                                    name="credit_limit"
                                    value={
                                        form.credit_limit
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    min="0"
                                    step="0.01"
                                    placeholder="0.00"
                                    disabled={
                                        saving
                                    }
                                />

                            </div>


                            <div className="customer-form-group">

                                <label>
                                    Credit Days
                                </label>


                                <input
                                    type="number"
                                    name="credit_days"
                                    value={
                                        form.credit_days
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    min="0"
                                    placeholder="0"
                                    disabled={
                                        saving
                                    }
                                />

                            </div>


                            {!isEdit && (

                                <div className="customer-form-group">

                                    <label>
                                        Opening Balance
                                    </label>


                                    <input
                                        type="number"
                                        name="opening_balance"
                                        value={
                                            form.opening_balance
                                        }
                                        onChange={
                                            handleChange
                                        }
                                        min="0"
                                        step="0.01"
                                        placeholder="0.00"
                                        disabled={
                                            saving
                                        }
                                    />

                                </div>

                            )}

                        </div>

                    </div>


                    {/* =================================================
                        REMARKS
                    ================================================= */}

                    <div className="customer-form-section customer-remarks-section">

                        <div className="customer-form-group full">

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
                                placeholder="Enter any additional remarks..."
                                rows="4"
                                disabled={
                                    saving
                                }
                            />

                        </div>

                    </div>


                    {/* =================================================
                        STATUS
                    ================================================= */}

                    <div className="customer-active-row customer-status-section">

                        <label>

                            <input
                                type="checkbox"
                                name="is_active"
                                checked={
                                    form.is_active
                                }
                                onChange={
                                    handleChange
                                }
                                disabled={
                                    saving
                                }
                            />


                            <span>
                                Active Customer
                            </span>

                        </label>

                    </div>


                    {/* =================================================
                        FOOTER
                    ================================================= */}

                    <div className="customer-drawer-footer">


                        <button
                            type="button"
                            className="customer-cancel-btn"
                            onClick={
                                handleClose
                            }
                            disabled={
                                saving
                            }
                        >

                            Cancel

                        </button>


                        <button
                            type="submit"
                            className="customer-save-btn"
                            disabled={
                                saving
                            }
                        >

                            <Save size={17} />


                            {saving
                                ? "Saving..."
                                : isEdit
                                    ? "Update Customer"
                                    : "Save Customer"}

                        </button>

                    </div>


                </form>

            </div>

        </div>

    );
};


export default CustomerForm;