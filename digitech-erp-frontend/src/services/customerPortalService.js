const API_BASE_URL =
    import.meta.env.VITE_API_URL ||
    "http://127.0.0.1:8000";


/* =====================================================
   GET AUTH TOKEN
===================================================== */

const getToken = () => {

    return (
        localStorage.getItem("access_token") ||
        localStorage.getItem("token")
    );

};


/* =====================================================
   COMMON HEADERS
===================================================== */

const getHeaders = () => {

    const token = getToken();

    return {

        "Content-Type": "application/json",

        ...(token
            ? {
                Authorization: `Bearer ${token}`
            }
            : {})

    };

};


/* =====================================================
   GET CUSTOMER MACHINES
===================================================== */

export const getCustomerMachines = async () => {

    const response = await fetch(
        `${API_BASE_URL}/customer/machines`,
        {
            method: "GET",
            headers: getHeaders()
        }
    );

    if (!response.ok) {

        let message = "Failed to load machines";

        try {

            const data = await response.json();

            message =
                data?.detail ||
                data?.message ||
                message;

        } catch {
            // ignore
        }

        throw new Error(message);

    }

    return response.json();

};


/* =====================================================
   GET CUSTOMER SERVICE REQUESTS
===================================================== */

export const getCustomerServiceRequests = async () => {

    const response = await fetch(
        `${API_BASE_URL}/customer/service-requests`,
        {
            method: "GET",
            headers: getHeaders()
        }
    );

    if (!response.ok) {

        let message =
            "Failed to load service requests";

        try {

            const data = await response.json();

            message =
                data?.detail ||
                data?.message ||
                message;

        } catch {
            // ignore
        }

        throw new Error(message);

    }

    return response.json();

};


/* =====================================================
   CREATE SERVICE REQUEST
===================================================== */

export const createCustomerServiceRequest = async (
    requestData
) => {

    const response = await fetch(
        `${API_BASE_URL}/customer/service-requests`,
        {
            method: "POST",

            headers: getHeaders(),

            body: JSON.stringify(
                requestData
            )
        }
    );

    if (!response.ok) {

        let message =
            "Failed to create service request";

        try {

            const data = await response.json();

            message =
                data?.detail ||
                data?.message ||
                message;

        } catch {
            // ignore
        }

        throw new Error(message);

    }

    return response.json();

};