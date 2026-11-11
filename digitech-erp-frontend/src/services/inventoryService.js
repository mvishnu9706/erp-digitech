import api from "../api/axios";


/* ==========================================================
   Inventory List
========================================================== */

export const getInventory = (params = {}) => {

    return api.get("/inventory", {
        params,
    });

};


/* ==========================================================
   Inventory Dashboard
========================================================== */

export const getInventoryDashboard = () => {

    return api.get("/inventory/dashboard");

};


/* ==========================================================
   Inventory Details
========================================================== */

export const getInventoryDetails = (id) => {

    return api.get(`/inventory/${id}`);

};


/* ==========================================================
   Create Inventory
========================================================== */

export const addInventory = (data) => {

    return api.post("/inventory", data);

};


/* ==========================================================
   Update Inventory
========================================================== */

export const editInventory = (id, data) => {

    return api.put(
        `/inventory/${id}`,
        data
    );

};


/* ==========================================================
   Delete Inventory
========================================================== */

export const deleteInventory = (id) => {

    return api.delete(
        `/inventory/${id}`
    );

};


/* ==========================================================
   Stock Transfer
========================================================== */

export const transferInventory = (data) => {

    return api.post(
        "/inventory/transfer",
        data
    );

};


/* ==========================================================
   Stock Transfer History
========================================================== */

export const getStockTransferHistory = (
    params = {}
) => {

    return api.get(
        "/inventory-transactions/transfers/history",
        {
            params,
        }
    );

};


/* ==========================================================
   Export Stock Transfer History
========================================================== */

export const exportStockTransferHistory = (
    params = {}
) => {

    return api.get(
        "/inventory-transactions/transfers/history/export",
        {
            params,
            responseType: "blob",
        }
    );

};


/* ==========================================================
   Stock Adjustment
========================================================== */

export const adjustInventory = (data) => {

    return api.post(
        "/inventory/adjust",
        data
    );

};


/* ==========================================================
   Stock Movement History
========================================================== */

export const getStockMovements = (
    params = {}
) => {

    return api.get(
        "/inventory/movements",
        {
            params,
        }
    );

};


/* ==========================================================
   EXPORT INVENTORY TO EXCEL
==========================================================

   Filters supported:

       search
       warehouse_id
       product_id
       category_id
       brand_id
       supplier_id
       barcode
       stock_status

   Pagination is intentionally NOT sent.

   Therefore:

       No filters
           ↓
       Export ALL inventory

       Filters selected
           ↓
       Export ONLY matching inventory

========================================================== */

export const exportInventory = (
    params = {}
) => {

    return api.get(
        "/inventory/export",
        {
            params,
            responseType: "blob",
        }
    );

};


/* ==========================================================
   Download Inventory Report
==========================================================

   Kept for compatibility with any existing component
   that may still use this function.

========================================================== */

export const downloadInventoryReport = (
    params = {}
) => {

    return api.get(
        "/inventory/report",
        {
            params,
            responseType: "blob",
        }
    );

};


/* ==========================================================
   Check Inventory Exists
========================================================== */

export const checkInventoryExists = (
    productId,
    warehouseId
) => {

    return api.get(
        "/inventory/check",
        {
            params: {
                product_id: Number(productId),
                warehouse_id: Number(warehouseId),
            },
        }
    );

};


/* ==========================================================
   Get Current Stock
========================================================== */

export const getInventoryStock = (
    productId,
    warehouseId
) => {

    return api.get(
        "/inventory/stock",
        {
            params: {
                product_id: Number(productId),
                warehouse_id: Number(warehouseId),
            },
        }
    );

};