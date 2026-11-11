import api from "./api";

/**
 * ==========================================
 * Get Inventory List
 * ==========================================
 */
export const getInventory = async (params = {}) => {
  const response = await api.get("/inventory", {
    params,
  });

  return response.data;
};

/**
 * ==========================================
 * Get Inventory By ID
 * ==========================================
 */
export const getInventoryById = async (id) => {
  const response = await api.get(`/inventory/${id}`);

  return response.data;
};

/**
 * ==========================================
 * Create Inventory
 * ==========================================
 */
export const addInventory = async (data) => {
  const response = await api.post("/inventory", data);

  return response.data;
};

/**
 * ==========================================
 * Update Inventory
 * ==========================================
 */
export const editInventory = async (id, data) => {
  const response = await api.put(`/inventory/${id}`, data);

  return response.data;
};

/**
 * ==========================================
 * Delete Inventory
 * ==========================================
 */
export const deleteInventory = async (id) => {
  const response = await api.delete(`/inventory/${id}`);

  return response.data;
};

/**
 * ==========================================
 * Inventory Dashboard
 * ==========================================
 */
export const getInventoryDashboard = async () => {
  const response = await api.get("/inventory/dashboard");

  return response.data;
};