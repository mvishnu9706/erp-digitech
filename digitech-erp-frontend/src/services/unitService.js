import api from "../api/axios";

// ======================================
// Get All Units
// ======================================

export const getUnits = async () => {

    const response = await api.get("/units", {
        params: {
            page: 1,
            page_size: 100,
        },
    });

    return response.data;

};

// ======================================
// Get Unit By Id
// ======================================

export const getUnit = async (id) => {

    const response = await api.get(`/units/${id}`);

    return response.data;

};

// ======================================
// Create Unit
// ======================================

export const createUnit = async (data) => {

    const response = await api.post(
        "/units",
        data
    );

    return response.data;

};

// ======================================
// Update Unit
// ======================================

export const updateUnit = async (id, data) => {

    const response = await api.put(
        `/units/${id}`,
        data
    );

    return response.data;

};

// ======================================
// Delete Unit
// ======================================

export const deleteUnit = async (id) => {

    const response = await api.delete(
        `/units/${id}`
    );

    return response.data;

};