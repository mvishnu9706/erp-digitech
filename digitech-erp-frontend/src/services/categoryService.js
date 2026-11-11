import api from "../api/axios";

// ======================================
// Get All Categories
// ======================================

export const getCategories = async () => {

    const response = await api.get("/categories", {
        params: {
            page: 1,
            page_size: 100,
        },
    });

    return response.data;

};

// ======================================
// Get Category By Id
// ======================================

export const getCategory = async (id) => {

    const response = await api.get(`/categories/${id}`);

    return response.data;

};

// ======================================
// Create Category
// ======================================

export const createCategory = async (data) => {

    const response = await api.post(
        "/categories",
        data
    );

    return response.data;

};

// ======================================
// Update Category
// ======================================

export const updateCategory = async (id, data) => {

    const response = await api.put(
        `/categories/${id}`,
        data
    );

    return response.data;

};

// ======================================
// Delete Category
// ======================================

export const deleteCategory = async (id) => {

    const response = await api.delete(
        `/categories/${id}`
    );

    return response.data;

};