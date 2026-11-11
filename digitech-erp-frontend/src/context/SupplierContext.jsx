import {
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

import { toast } from "react-toastify";

import { useAuth } from "./AuthContext";

import {
    getSuppliers,
    getSupplierDashboard,
    createSupplier as createSupplierApi,
    updateSupplier as updateSupplierApi,
    deleteSupplier as deleteSupplierApi,
} from "../services/supplierService";


const SupplierContext = createContext();


export const SupplierProvider = ({ children }) => {

    // =====================================================
    // Authentication
    // =====================================================

    const {
        loading: authLoading,
        isAuthenticated,
    } = useAuth();


    // =====================================================
    // Loading
    // =====================================================

    const [loading, setLoading] = useState(false);


    // =====================================================
    // Dashboard
    // =====================================================

    const [dashboard, setDashboard] = useState({});


    // =====================================================
    // Suppliers
    // =====================================================

    const [suppliers, setSuppliers] = useState([]);


    // =====================================================
    // Drawer
    // =====================================================

    const [drawerOpen, setDrawerOpen] = useState(false);

    const [drawerMode, setDrawerMode] = useState("add");


    // =====================================================
    // Delete Modal
    // =====================================================

    const [deleteModalOpen, setDeleteModalOpen] = useState(false);


    // =====================================================
    // Selected Supplier
    // =====================================================

    const [selectedSupplier, setSelectedSupplier] = useState(null);


    // =====================================================
    // Filters
    // =====================================================

    const [filters, setFilters] = useState({

        search: "",

        city: "",

        state: "",

        is_active: "",

        page: 1,

        page_size: 10,

    });


    // =====================================================
    // Supplier Form
    // =====================================================

    const [supplierForm, setSupplierForm] = useState({

        company_name: "",

        contact_person: "",

        phone: "",

        email: "",

        gstin: "",

        pan: "",

        city: "",

        state: "",

        address: "",

        credit_limit: 0,

    });


    // =====================================================
    // Prepare Supplier Payload
    // =====================================================

    const prepareSupplierPayload = (data) => {

        const payload = {
            // Required field
            company_name:
                data.company_name?.trim() || "",

            // Numeric field
            credit_limit:
                data.credit_limit === "" ||
                data.credit_limit === null ||
                data.credit_limit === undefined
                    ? 0
                    : Number(data.credit_limit),
        };

        // Send optional fields only when they contain a value.
        // This keeps empty form fields out of the request and lets
        // SupplierCreate apply its own defaults.
        const optionalFields = [
            "contact_person",
            "phone",
            "email",
            "gstin",
            "pan",
            "city",
            "state",
            "address",
        ];

        optionalFields.forEach((field) => {
            const value = data?.[field];

            if (
                typeof value === "string" &&
                value.trim() !== ""
            ) {
                payload[field] = value.trim();
            }
        });

        return payload;
    };


    // =====================================================
    // Fetch Dashboard
    // =====================================================

    const fetchDashboard = async () => {

        try {

            const data =
                await getSupplierDashboard();

            console.log(
                "SUPPLIER DASHBOARD:",
                data
            );

            setDashboard(data);

        } catch (error) {

            console.error(
                "SUPPLIER DASHBOARD ERROR:",
                error
            );

        }

    };


    // =====================================================
    // Fetch Suppliers
    // =====================================================

    const fetchSuppliers = async () => {

        try {

            setLoading(true);

            const data =
                await getSuppliers(filters);

            console.log(
                "SUPPLIER API RESPONSE:",
                data
            );


            // Backend list response
            setSuppliers(
                data?.suppliers || []
            );

        } catch (error) {

            console.error(
                "SUPPLIER FETCH ERROR:",
                error
            );

            toast.error(
                error?.response?.data?.detail ||
                "Failed to load suppliers."
            );

        } finally {

            setLoading(false);

        }

    };


    // =====================================================
    // Create Supplier
    // =====================================================

    const createSupplier = async (
        data = supplierForm
    ) => {

        try {

            setLoading(true);


            // ---------------------------------------------
            // Prepare payload
            // ---------------------------------------------

            const payload =
                prepareSupplierPayload(data);


            console.log(
                "================================"
            );

            console.log(
                "CREATE SUPPLIER"
            );

            console.log(
                "PAYLOAD SENT:",
                payload
            );

            console.log(
                "================================"
            );


            // ---------------------------------------------
            // API Request
            // ---------------------------------------------

            const response =
                await createSupplierApi(
                    payload
                );


            console.log(
                "SUPPLIER CREATE RESPONSE:",
                response
            );


            // ---------------------------------------------
            // Success
            // ---------------------------------------------

            toast.success(
                "Supplier created successfully!"
            );


            // ---------------------------------------------
            // Reset Form
            // ---------------------------------------------

            setSupplierForm({

                company_name: "",

                contact_person: "",

                phone: "",

                email: "",

                gstin: "",

                pan: "",

                city: "",

                state: "",

                address: "",

                credit_limit: 0,

            });


            // ---------------------------------------------
            // Close Drawer
            // ---------------------------------------------

            setDrawerOpen(false);


            // ---------------------------------------------
            // Clear Selected Supplier
            // ---------------------------------------------

            setSelectedSupplier(null);


            // ---------------------------------------------
            // Refresh Dashboard + Suppliers
            // ---------------------------------------------

            await reloadEverything();

        } catch (error) {

            console.error(
                "================================"
            );

            console.error(
                "CREATE SUPPLIER ERROR"
            );

            console.error(
                "STATUS:",
                error?.response?.status
            );

            console.error(
                "BACKEND RESPONSE:",
                error?.response?.data
            );

            console.error(
                "ERROR:",
                error
            );

            console.error(
                "================================"
            );


            const detail =
                error?.response?.data?.detail;


            // ---------------------------------------------
            // FastAPI Validation Error
            // ---------------------------------------------

            if (Array.isArray(detail)) {

                detail.forEach((item) => {

                    console.error(
                        "Validation Location:",
                        item?.loc
                    );

                    console.error(
                        "Validation Message:",
                        item?.msg
                    );

                });


                const messages =
                    detail
                        .map(
                            (item) =>
                                item?.msg
                        )
                        .filter(Boolean)
                        .join(", ");


                toast.error(
                    messages ||
                    "Please check the supplier details."
                );

            } else {

                toast.error(
                    detail ||
                    "Failed to create supplier."
                );

            }

        } finally {

            setLoading(false);

        }

    };


    // =====================================================
    // Update Supplier
    // =====================================================

    const updateSupplier = async (
        data = supplierForm
    ) => {

        // ---------------------------------------------
        // Check selected supplier
        // ---------------------------------------------

        if (!selectedSupplier) {

            toast.error(
                "No supplier selected."
            );

            return;

        }


        try {

            setLoading(true);


            // ---------------------------------------------
            // Prepare payload
            // ---------------------------------------------

            const payload =
                prepareSupplierPayload(data);


            console.log(
                "================================"
            );

            console.log(
                "UPDATE SUPPLIER"
            );

            console.log(
                "SUPPLIER ID:",
                selectedSupplier.id
            );

            console.log(
                "PAYLOAD SENT:",
                payload
            );

            console.log(
                "================================"
            );


            // ---------------------------------------------
            // API Request
            // ---------------------------------------------

            const response =
                await updateSupplierApi(

                    selectedSupplier.id,

                    payload

                );


            console.log(
                "SUPPLIER UPDATE RESPONSE:",
                response
            );


            // ---------------------------------------------
            // Success
            // ---------------------------------------------

            toast.success(
                "Supplier updated successfully!"
            );


            // ---------------------------------------------
            // Close Drawer
            // ---------------------------------------------

            setDrawerOpen(false);


            // ---------------------------------------------
            // Clear Selected Supplier
            // ---------------------------------------------

            setSelectedSupplier(null);


            // ---------------------------------------------
            // Refresh
            // ---------------------------------------------

            await reloadEverything();

        } catch (error) {

            console.error(
                "================================"
            );

            console.error(
                "UPDATE SUPPLIER ERROR"
            );

            console.error(
                "STATUS:",
                error?.response?.status
            );

            console.error(
                "BACKEND RESPONSE:",
                error?.response?.data
            );

            console.error(
                "ERROR:",
                error
            );

            console.error(
                "================================"
            );


            const detail =
                error?.response?.data?.detail;


            // ---------------------------------------------
            // FastAPI Validation Error
            // ---------------------------------------------

            if (Array.isArray(detail)) {

                detail.forEach((item) => {

                    console.error(
                        "Validation Location:",
                        item?.loc
                    );

                    console.error(
                        "Validation Message:",
                        item?.msg
                    );

                });


                const messages =
                    detail
                        .map(
                            (item) =>
                                item?.msg
                        )
                        .filter(Boolean)
                        .join(", ");


                toast.error(
                    messages ||
                    "Please check the supplier details."
                );

            } else {

                toast.error(
                    detail ||
                    "Failed to update supplier."
                );

            }

        } finally {

            setLoading(false);

        }

    };


    // =====================================================
    // Delete Supplier
    // =====================================================

    const deleteSupplier = async () => {

        console.log(
            "================================"
        );

        console.log(
            "DELETE SUPPLIER"
        );

        console.log(
            "SELECTED SUPPLIER:",
            selectedSupplier
        );

        console.log(
            "================================"
        );


        // ---------------------------------------------
        // Check selected supplier
        // ---------------------------------------------

        if (!selectedSupplier) {

            toast.error(
                "No supplier selected."
            );

            return;

        }


        try {

            setLoading(true);


            console.log(
                "DELETING SUPPLIER ID:",
                selectedSupplier.id
            );


            // ---------------------------------------------
            // API Request
            // ---------------------------------------------

            const response =
                await deleteSupplierApi(
                    selectedSupplier.id
                );


            console.log(
                "DELETE RESPONSE:",
                response
            );


            // ---------------------------------------------
            // Success
            // ---------------------------------------------

            toast.success(
                "Supplier deleted successfully!"
            );


            // ---------------------------------------------
            // Close Delete Modal
            // ---------------------------------------------

            setDeleteModalOpen(false);


            // ---------------------------------------------
            // Clear Selected Supplier
            // ---------------------------------------------

            setSelectedSupplier(null);


            // ---------------------------------------------
            // Refresh
            // ---------------------------------------------

            await reloadEverything();

        } catch (error) {

            console.error(
                "================================"
            );

            console.error(
                "DELETE SUPPLIER ERROR"
            );

            console.error(
                "STATUS:",
                error?.response?.status
            );

            console.error(
                "BACKEND RESPONSE:",
                error?.response?.data
            );

            console.error(
                "ERROR:",
                error
            );

            console.error(
                "================================"
            );


            toast.error(

                error?.response?.data?.detail ||

                "Failed to delete supplier."

            );

        } finally {

            setLoading(false);

        }

    };


    // =====================================================
    // Reload Everything
    // =====================================================

    const reloadEverything = async () => {

        await Promise.all([

            fetchDashboard(),

            fetchSuppliers(),

        ]);

    };


    // =====================================================
    // Initial Dashboard Load
    // =====================================================

    useEffect(() => {

        // Wait until authentication state is known.
        if (authLoading) {
            return;
        }

        // Do not call supplier APIs before login.
        if (!isAuthenticated) {
            return;
        }

        fetchDashboard();

    }, [
        authLoading,
        isAuthenticated,
    ]);


    // =====================================================
    // Suppliers Load / Filter Change
    // =====================================================

    useEffect(() => {

        // Wait until authentication state is known.
        if (authLoading) {
            return;
        }

        // Do not call supplier APIs before login.
        if (!isAuthenticated) {
            return;
        }

        fetchSuppliers();

    }, [
        authLoading,
        isAuthenticated,
        filters,
    ]);


    // =====================================================
    // Context
    // =====================================================

    return (

        <SupplierContext.Provider
            value={{

                // Loading
                loading,


                // Dashboard
                dashboard,


                // Suppliers
                suppliers,


                // Form
                supplierForm,
                setSupplierForm,


                // Drawer
                drawerOpen,
                setDrawerOpen,

                drawerMode,
                setDrawerMode,


                // Delete
                deleteModalOpen,
                setDeleteModalOpen,


                // Selected Supplier
                selectedSupplier,
                setSelectedSupplier,


                // Filters
                filters,
                setFilters,


                // Functions
                fetchSuppliers,

                reloadEverything,

                createSupplier,

                updateSupplier,

                deleteSupplier,

            }}
        >

            {children}

        </SupplierContext.Provider>

    );

};


// =====================================================
// Hook
// =====================================================

export const useSupplier = () => {

    return useContext(
        SupplierContext
    );

};