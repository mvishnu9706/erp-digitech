import api from "../api/axios";

class PurchaseService {

    constructor() {
        console.log("PurchaseService Loaded");
    }

    // ===============================
    // Suppliers
    // ===============================

    async getSuppliers() {
        const response = await api.get("/suppliers");
        return response.data;
    }

    // ===============================
    // Warehouses
    // ===============================

    async getWarehouses() {
        const response = await api.get("/warehouses/", {
            params: {
                page: 1,
                page_size: 100,
            },
        });

        return response.data;
    }

    // ===============================
    // Products
    // ===============================

    async getProducts() {
        const response = await api.get("/products");
        return response.data;
    }

    // ===============================
    // Purchase Dashboard
    // ===============================

    async getDashboard() {
        const response = await api.get(
            "/purchase-orders/dashboard/summary"
        );

        return response.data;
    }

    // ===============================
    // Create Purchase Order
    // ===============================

    async createPurchase(data) {
        const response = await api.post(
            "/purchase-orders",
            data
        );

        return response.data;
    }

    // ===============================
    // Search Purchase Orders
    // ===============================

    async searchPurchaseOrders({
        search = "",
        supplier_id = "",
        warehouse_id = "",
        date_from = "",
        date_to = "",
        page = 1,
        page_size = 10,
    }) {

        const params = {
            page,
            page_size,
        };

        if (search) params.search = search;
        if (supplier_id) params.supplier_id = supplier_id;
        if (warehouse_id) params.warehouse_id = warehouse_id;
        if (date_from) params.date_from = date_from;
        if (date_to) params.date_to = date_to;

        const response = await api.get(
            "/purchase-orders",
            {
                params,
            }
        );

        return response.data;
    }

    // ===============================
    // Get Purchase Orders
    // ===============================

    async getPurchaseOrders(filters = {}) {
        return this.searchPurchaseOrders(filters);
    }

    // ===============================
    // Get Purchase By ID
    // ===============================

    async getPurchaseById(id) {
        const response = await api.get(
            `/purchase-orders/${id}`
        );

        return response.data;
    }

    // ===============================
    // Update Purchase
    // ===============================

    async updatePurchase(id, data) {
        const response = await api.put(
            `/purchase-orders/${id}`,
            data
        );

        return response.data;
    }

    // ===============================
    // Delete Purchase
    // ===============================

    async deletePurchase(id) {
        const response = await api.delete(
            `/purchase-orders/${id}`
        );

        return response.data;
    }

    // ===============================
    // Get Current Stock
    // ===============================

    async getCurrentStock(productId, warehouseId) {
        const response = await api.get(
            `/inventory/stock`,
            {
                params: {
                    product_id: productId,
                    warehouse_id: warehouseId,
                },
            }
        );

        return response.data.current_stock;
    }

    // ===============================
    // Export Purchase Orders
    // ===============================

    async exportPurchaseOrders({
        search = "",
        supplier_id = "",
        warehouse_id = "",
        date_from = "",
        date_to = "",
    } = {}) {
        console.log("EXPORT METHOD CALLED");

        const params = {};

        if (search) params.search = search;
        if (supplier_id) params.supplier_id = supplier_id;
        if (warehouse_id) params.warehouse_id = warehouse_id;
        if (date_from) params.date_from = date_from;
        if (date_to) params.date_to = date_to;

        const response = await api.get(
            "/purchase-orders/export",
            {
                params,
                responseType: "blob",
            }
        );

        return response.data;
    }
}

export default new PurchaseService();