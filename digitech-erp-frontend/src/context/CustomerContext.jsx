import {
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

import customerService from "../services/customerService";


// =====================================================
// Context
// =====================================================

const CustomerContext = createContext(null);


// =====================================================
// Provider
// =====================================================

export const CustomerProvider = ({ children }) => {

    // =================================================
    // Customers
    // =================================================

    const [customers, setCustomers] = useState([]);


    // =================================================
    // Dashboard
    // =================================================

    const [dashboard, setDashboard] = useState({
        total_customers: 0,
        active_customers: 0,
        inactive_customers: 0,
        total_outstanding: 0,
        total_credit_limit: 0,
    });


    // =================================================
    // Loading
    // =================================================

    const [loading, setLoading] = useState(false);


    // =================================================
    // Error
    // =================================================

    const [error, setError] = useState(null);


    // =================================================
    // Filters
    // =================================================

    const [filters, setFilters] = useState({

        search: "",

        city: "",

        state: "",

        is_active: "",

        page: 1,

        page_size: 10,

    });


    // =================================================
    // Selected Customer
    // =================================================

    const [selectedCustomer, setSelectedCustomer] =
        useState(null);


    // =================================================
    // Load Customers
    // =================================================

    const loadCustomers = async (
        customFilters = filters
    ) => {

        try {

            setLoading(true);

            setError(null);

            const params = {};

            // -----------------------------------------
            // Search
            // -----------------------------------------

            if (customFilters.search?.trim()) {

                params.search =
                    customFilters.search.trim();

            }

            // -----------------------------------------
            // City
            // -----------------------------------------

            if (customFilters.city) {

                params.city =
                    customFilters.city;

            }

            // -----------------------------------------
            // State
            // -----------------------------------------

            if (customFilters.state) {

                params.state =
                    customFilters.state;

            }

            // -----------------------------------------
            // Active Status
            // -----------------------------------------

            if (
                customFilters.is_active !== "" &&
                customFilters.is_active !== null &&
                customFilters.is_active !== undefined
            ) {

                params.is_active =
                    customFilters.is_active;

            }

            // -----------------------------------------
            // Pagination
            // -----------------------------------------

            params.page =
                customFilters.page || 1;

            params.page_size =
                customFilters.page_size || 10;


            const data =
                await customerService.getCustomers(
                    params
                );


            setCustomers(data || []);

        } catch (err) {

            console.error(
                "Failed to load customers:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to load customers."
            );

        } finally {

            setLoading(false);

        }

    };


    // =================================================
    // Load Dashboard
    // =================================================

    const loadDashboard = async () => {

        try {

            const data =
                await customerService.getDashboard();

            setDashboard(
                data || {
                    total_customers: 0,
                    active_customers: 0,
                    inactive_customers: 0,
                    total_outstanding: 0,
                    total_credit_limit: 0,
                }
            );

        } catch (err) {

            console.error(
                "Failed to load customer dashboard:",
                err
            );

        }

    };


    // =================================================
    // Load Customer By ID
    // =================================================

    const loadCustomer = async (
        customerId
    ) => {

        try {

            setLoading(true);

            setError(null);

            const data =
                await customerService.getCustomerById(
                    customerId
                );

            setSelectedCustomer(data);

            return data;

        } catch (err) {

            console.error(
                "Failed to load customer:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to load customer."
            );

            throw err;

        } finally {

            setLoading(false);

        }

    };


    // =================================================
    // Create Customer
    // =================================================

    const createCustomer = async (
        customerData
    ) => {

        try {

            setLoading(true);

            setError(null);

            const data =
                await customerService.createCustomer(
                    customerData
                );

            // Add new customer to current list

            setCustomers((prev) => [
                data,
                ...prev,
            ]);

            // Refresh dashboard

            await loadDashboard();

            return data;

        } catch (err) {

            console.error(
                "Failed to create customer:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to create customer."
            );

            throw err;

        } finally {

            setLoading(false);

        }

    };


    // =================================================
    // Update Customer
    // =================================================

    const updateCustomer = async (
        customerId,
        customerData
    ) => {

        try {

            setLoading(true);

            setError(null);

            const data =
                await customerService.updateCustomer(
                    customerId,
                    customerData
                );


            // Update list

            setCustomers((prev) =>
                prev.map((customer) =>
                    customer.id === customerId
                        ? data
                        : customer
                )
            );


            // Update selected customer

            setSelectedCustomer((prev) =>
                prev?.id === customerId
                    ? data
                    : prev
            );


            // Refresh dashboard

            await loadDashboard();

            return data;

        } catch (err) {

            console.error(
                "Failed to update customer:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to update customer."
            );

            throw err;

        } finally {

            setLoading(false);

        }

    };


    // =================================================
    // Delete / Deactivate Customer
    // =================================================

    const deleteCustomer = async (
        customerId
    ) => {

        try {

            setLoading(true);

            setError(null);

            const data =
                await customerService.deleteCustomer(
                    customerId
                );


            // Remove from current list

            setCustomers((prev) =>
                prev.filter(
                    (customer) =>
                        customer.id !== customerId
                )
            );


            // Clear selected customer

            setSelectedCustomer((prev) =>
                prev?.id === customerId
                    ? null
                    : prev
            );


            // Refresh dashboard

            await loadDashboard();


            return data;

        } catch (err) {

            console.error(
                "Failed to delete customer:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to delete customer."
            );

            throw err;

        } finally {

            setLoading(false);

        }

    };


    // =================================================
    // Update Filter
    // =================================================

    const updateFilter = (
        key,
        value
    ) => {

        setFilters((prev) => ({

            ...prev,

            [key]: value,

            // Reset page whenever
            // a filter changes

            ...(key !== "page"
                ? { page: 1 }
                : {}),

        }));

    };


    // =================================================
    // Reset Filters
    // =================================================

    const resetFilters = () => {

        setFilters({

            search: "",

            city: "",

            state: "",

            is_active: "",

            page: 1,

            page_size: 10,

        });

    };


    // =================================================
    // Initial Load
    // =================================================

    useEffect(() => {

        loadCustomers();

        loadDashboard();

    }, []);


    // =================================================
    // Context Value
    // =================================================

    const value = {

        // Data
        customers,
        dashboard,
        selectedCustomer,

        // State
        loading,
        error,
        filters,

        // Customer actions
        loadCustomers,
        loadCustomer,
        createCustomer,
        updateCustomer,
        deleteCustomer,

        // Filter actions
        updateFilter,
        setFilters,
        resetFilters,

        // Selected customer
        setSelectedCustomer,

    };


    return (

        <CustomerContext.Provider value={value}>

            {children}

        </CustomerContext.Provider>

    );

};


// =====================================================
// Hook
// =====================================================

export const useCustomers = () => {

    const context =
        useContext(CustomerContext);

    if (!context) {

        throw new Error(
            "useCustomers must be used inside CustomerProvider"
        );

    }

    return context;

};