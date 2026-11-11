import api from "../api/axios";


// ==========================================================
// Products
// ==========================================================

export const getProducts = (params) =>
    api.get("/products", {
        params,
    });


export const getProduct = (id) =>
    api.get(`/products/${id}`);


export const createProduct = (data) =>
    api.post("/products", data);


export const updateProduct = (id, data) =>
    api.put(`/products/${id}`, data);


export const deleteProduct = (id) =>
    api.delete(`/products/${id}`);


// ==========================================================
// Import Products
// ==========================================================

export const importProducts = async (file) => {

    const formData = new FormData();

    formData.append(
        "file",
        file
    );


    const response = await api.post(
        "/products/import",
        formData,
        {
            headers: {
                "Content-Type":
                    "multipart/form-data",
            },
        }
    );


    return response.data;

};


// ==========================================================
// Export Products
//
// params can contain:
//
// search
// category_id
// brand_id
// warehouse_id
// status
//
// If params are empty, backend exports ALL products.
// ==========================================================

export const exportProducts = async (
    params = {}
) => {

    const response = await api.get(
        "/products/export",
        {
            params,
            responseType: "blob",
        }
    );


    return response.data;

};