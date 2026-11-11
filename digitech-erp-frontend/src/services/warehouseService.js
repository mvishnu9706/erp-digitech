import api from "../api/axios";

// ======================================
// Get All Warehouses
// ======================================

export const getWarehouses = async () => {

    const response = await api.get("/warehouses", {
        params: {
            page: 1,
            page_size: 100,
        },
    });

    return response.data;

};

// ======================================
// Get Warehouse By Id
// ======================================

export const getWarehouse = async (id) => {

    const response = await api.get(`/warehouses/${id}`);

    return response.data;

};

// ======================================
// Create Warehouse
// ======================================

export const createWarehouse = async (data) => {

    const response = await api.post(
        "/warehouses",
        data
    );

    return response.data;

};

// ======================================
// Update Warehouse
// ======================================

export const updateWarehouse = async (id, data) => {

    const response = await api.put(
        `/warehouses/${id}`,
        data
    );

    return response.data;

};

// ======================================
// Delete Warehouse
// ======================================

export const deleteWarehouse = async (id) => {

    const response = await api.delete(
        `/warehouses/${id}`
    );

    return response.data;

};