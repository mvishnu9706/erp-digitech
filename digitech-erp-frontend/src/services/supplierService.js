import API from "../api/axios";


const authHeader = () => ({
    headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
});


// =======================================================
// Dashboard
// =======================================================

export const getSupplierDashboard = async () => {

    const response = await API.get(
        "/suppliers/dashboard",
        authHeader()
    );

    return response.data;

};


// =======================================================
// Get Suppliers
// =======================================================

export const getSuppliers = async (
    filters = {}
) => {

    const params = {};


    // ===================================================
    // Search
    // ===================================================

    if (
        filters.search &&
        filters.search.trim() !== ""
    ) {

        params.search =
            filters.search.trim();

    }


    // ===================================================
    // City
    // ===================================================

    if (
        filters.city &&
        filters.city.trim() !== ""
    ) {

        params.city =
            filters.city.trim();

    }


    // ===================================================
    // State
    // ===================================================

    if (
        filters.state &&
        filters.state.trim() !== ""
    ) {

        params.state =
            filters.state.trim();

    }


    // ===================================================
    // Status
    // ===================================================

    if (
        filters.is_active !== undefined &&
        filters.is_active !== null &&
        filters.is_active !== ""
    ) {

        params.is_active =
            filters.is_active;

    }


    // ===================================================
    // Pagination
    // ===================================================

    params.page =
        filters.page || 1;

    params.page_size =
        filters.page_size || 10;


    // ===================================================
    // Request
    // ===================================================

    const response = await API.get(
        "/suppliers",
        {
            ...authHeader(),
            params,
        }
    );


    return response.data;

};


// =======================================================
// EXPORT SUPPLIERS
//
// No filters:
//     Export ALL suppliers
//
// Filters:
//     Export only matching suppliers
//
// Supported filters:
//     search
//     city
//     state
//     is_active
// =======================================================

export const exportSuppliers = async (
    filters = {}
) => {

    const params = {};


    // ===================================================
    // Search
    // ===================================================

    if (
        filters.search &&
        filters.search.trim() !== ""
    ) {

        params.search =
            filters.search.trim();

    }


    // ===================================================
    // City
    // ===================================================

    if (
        filters.city &&
        filters.city.trim() !== ""
    ) {

        params.city =
            filters.city.trim();

    }


    // ===================================================
    // State
    // ===================================================

    if (
        filters.state &&
        filters.state.trim() !== ""
    ) {

        params.state =
            filters.state.trim();

    }


    // ===================================================
    // Status
    // ===================================================

    if (
        filters.is_active !== undefined &&
        filters.is_active !== null &&
        filters.is_active !== ""
    ) {

        params.is_active =
            filters.is_active;

    }


    // ===================================================
    // Export Request
    //
    // responseType = blob is required because the
    // backend returns an Excel file.
    // ===================================================

    const response = await API.get(

        "/suppliers/export",

        {
            ...authHeader(),

            params,

            responseType: "blob",
        }

    );


    return response.data;

};


// =======================================================
// Get Supplier By ID
// =======================================================

export const getSupplierById = async (
    id
) => {

    const response = await API.get(
        `/suppliers/${id}`,
        authHeader()
    );

    return response.data;

};


// =======================================================
// Create Supplier
// =======================================================

export const createSupplier = async (
    data
) => {

    const response = await API.post(
        "/suppliers",
        data,
        authHeader()
    );

    return response.data;

};


// =======================================================
// Update Supplier
// =======================================================

export const updateSupplier = async (
    id,
    data
) => {

    const response = await API.put(
        `/suppliers/${id}`,
        data,
        authHeader()
    );

    return response.data;

};


// =======================================================
// Delete Supplier
// =======================================================

export const deleteSupplier = async (
    id
) => {

    const response = await API.delete(
        `/suppliers/${id}`,
        authHeader()
    );

    return response.data;

};