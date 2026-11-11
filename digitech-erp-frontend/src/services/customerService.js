import api from "../api/axios";

class CustomerService {

    // =====================================================
    // GET CUSTOMERS
    // =====================================================

    async getCustomers(params = {}) {

        const response = await api.get(
            "/customers/",
            {
                params
            }
        );

        return response.data;
    }


    // =====================================================
    // GET CUSTOMER BY ID
    // =====================================================

    async getCustomerById(customerId) {

        const response = await api.get(
            `/customers/${customerId}`
        );

        return response.data;
    }


    // =====================================================
    // GET DASHBOARD
    // =====================================================

    async getDashboard() {

        const response = await api.get(
            "/customers/dashboard/summary"
        );

        return response.data;
    }


    // =====================================================
    // CREATE CUSTOMER
    // =====================================================

    async createCustomer(customerData) {

        const response = await api.post(
            "/customers/",
            customerData
        );

        return response.data;
    }


    // =====================================================
    // UPDATE CUSTOMER
    // =====================================================

    async updateCustomer(
        customerId,
        customerData
    ) {

        const response = await api.put(
            `/customers/${customerId}`,
            customerData
        );

        return response.data;
    }


    // =====================================================
    // DELETE CUSTOMER
    // =====================================================

    async deleteCustomer(customerId) {

        const response = await api.delete(
            `/customers/${customerId}`
        );

        return response.data;
    }


    // =====================================================
    // EXPORT CUSTOMERS TO EXCEL
    // =====================================================

    async exportCustomers(params = {}) {

        const response = await api.get(
            "/customers/export",
            {
                params,
                responseType: "blob"
            }
        );

        return response.data;
    }

}


export default new CustomerService();