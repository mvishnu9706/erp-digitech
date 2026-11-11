import api from "../api/axios";

// ======================================
// Get All Brands
// ======================================

export const getBrands = async () => {

    const response = await api.get("/brands", {
        params: {
            page: 1,
            page_size: 100,
        },
    });

    return response.data;

};

// ======================================
// Get Brand By Id
// ======================================

export const getBrand = async (id) => {

    const response = await api.get(`/brands/${id}`);

    return response.data;

};

// ======================================
// Create Brand
// ======================================

export const createBrand = async (data) => {

    const response = await api.post(
        "/brands",
        data
    );

    return response.data;

};

// ======================================
// Update Brand
// ======================================

export const updateBrand = async (id, data) => {

    const response = await api.put(
        `/brands/${id}`,
        data
    );

    return response.data;

};

// ======================================
// Delete Brand
// ======================================

export const deleteBrand = async (id) => {

    const response = await api.delete(
        `/brands/${id}`
    );

    return response.data;

};