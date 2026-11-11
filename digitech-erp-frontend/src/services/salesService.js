import api from "../api/axios";


class SalesService {

    // =====================================================
    // Customers
    // =====================================================

    async getCustomers() {
        const response =
            await api.get(
                "/customers/"
            );

        return response.data;
    }


    // =====================================================
    // Products
    // =====================================================

    async getProducts() {
        const response =
            await api.get(
                "/products/"
            );

        return response.data;
    }


    // =====================================================
    // Warehouses
    // =====================================================

    async getWarehouses() {
        const response =
            await api.get(
                "/warehouses/"
            );

        return response.data;
    }


    // =====================================================
    // Get Current Stock
    // =====================================================

    async getCurrentStock(
        productId,
        warehouseId
    ) {

        if (
            productId === undefined ||
            productId === null ||
            productId === ""
        ) {

            console.warn(
                "getCurrentStock: Product ID is missing."
            );

            return 0;
        }


        if (
            warehouseId === undefined ||
            warehouseId === null ||
            warehouseId === ""
        ) {

            console.warn(
                "getCurrentStock: Warehouse ID is missing."
            );

            return 0;
        }


        const numericProductId =
            Number(productId);

        const numericWarehouseId =
            Number(warehouseId);


        if (
            !Number.isFinite(
                numericProductId
            ) ||
            !Number.isFinite(
                numericWarehouseId
            )
        ) {

            console.warn(
                "getCurrentStock: Invalid product or warehouse ID.",
                {
                    productId,
                    warehouseId,
                }
            );

            return 0;
        }


        try {

            const response =
                await api.get(
                    "/inventory/stock",
                    {
                        params: {

                            product_id:
                                numericProductId,

                            warehouse_id:
                                numericWarehouseId,

                        },
                    }
                );


            console.log(
                "CURRENT STOCK RESPONSE:",
                response.data
            );


            const stock =
                Number(
                    response.data?.stock ?? 0
                );


            console.log(
                "CURRENT STOCK:",
                {
                    productId:
                        numericProductId,

                    warehouseId:
                        numericWarehouseId,

                    stock,
                }
            );


            if (
                !Number.isFinite(
                    stock
                )
            ) {

                console.warn(
                    "Invalid stock value returned by backend:",
                    response.data
                );

                return 0;
            }


            return stock;

        } catch (error) {

            console.error(
                "GET CURRENT STOCK ERROR:",
                error
            );

            console.error(
                "STATUS:",
                error.response?.status
            );

            console.error(
                "RESPONSE:",
                error.response?.data
            );

            return 0;
        }
    }


    // =====================================================
    // Get Sales Orders
    // =====================================================

    async getSalesOrders(
        params = {}
    ) {

        const response =
            await api.get(
                "/sales-orders/",
                {
                    params: {

                        // ---------------------------------
                        // Search
                        // ---------------------------------

                        search:
                            params.search ||
                            undefined,


                        // ---------------------------------
                        // Customer Filter
                        // ---------------------------------

                        customer_id:
                            params.customer_id ||
                            undefined,


                        // ---------------------------------
                        // PRODUCT / ITEM FILTER
                        // ---------------------------------

                        product_id:
                            params.product_id ||
                            undefined,


                        // ---------------------------------
                        // Warehouse Filter
                        // ---------------------------------

                        warehouse_id:
                            params.warehouse_id ||
                            undefined,


                        // ---------------------------------
                        // Status
                        // ---------------------------------

                        status:
                            params.status ||
                            undefined,


                        // ---------------------------------
                        // Payment Status
                        // ---------------------------------

                        payment_status:
                            params.payment_status ||
                            undefined,


                        // ---------------------------------
                        // Date From
                        // ---------------------------------

                        date_from:
                            params.date_from ||
                            undefined,


                        // ---------------------------------
                        // Date To
                        // ---------------------------------

                        date_to:
                            params.date_to ||
                            undefined,


                        // ---------------------------------
                        // Pagination
                        // ---------------------------------

                        page:
                            params.page ||
                            1,

                        page_size:
                            params.page_size ||
                            10,

                    },
                }
            );


        return response.data;
    }


    // =====================================================
    // Get Single Sales Order
    // =====================================================

    async getSaleById(
        salesOrderId
    ) {

        if (
            salesOrderId === undefined ||
            salesOrderId === null ||
            salesOrderId === ""
        ) {

            throw new Error(
                "Sales Order ID is required."
            );
        }


        const response =
            await api.get(
                `/sales-orders/${salesOrderId}`
            );


        return response.data;
    }


    // =====================================================
    // Create Sales Order
    // =====================================================

    async createSale(
        payload
    ) {

        const response =
            await api.post(
                "/sales-orders/",
                payload
            );


        return response.data;
    }


    // =====================================================
    // Update Sales Order
    // =====================================================

    async updateSale(
        salesOrderId,
        payload
    ) {

        if (
            salesOrderId === undefined ||
            salesOrderId === null ||
            salesOrderId === ""
        ) {

            throw new Error(
                "Sales Order ID is required."
            );
        }


        console.log(
            "UPDATING SALES ORDER:",
            {
                salesOrderId,
                payload,
            }
        );


        const response =
            await api.put(
                `/sales-orders/${salesOrderId}`,
                payload
            );


        console.log(
            "UPDATE SALES ORDER RESPONSE:",
            response.data
        );


        return response.data;
    }


    // =====================================================
    // Complete Sales Order
    // =====================================================
    // Deducts Inventory Stock
    // =====================================================

    async completeSale(
        salesOrderId
    ) {

        if (
            salesOrderId === undefined ||
            salesOrderId === null ||
            salesOrderId === ""
        ) {

            throw new Error(
                "Sales Order ID is required."
            );
        }


        const response =
            await api.post(
                `/sales-orders/${salesOrderId}/complete`
            );


        return response.data;
    }


    // =====================================================
    // Delete / Cancel Sales Order
    // =====================================================

    async deleteSale(
        salesOrderId
    ) {

        if (
            salesOrderId === undefined ||
            salesOrderId === null ||
            salesOrderId === ""
        ) {

            throw new Error(
                "Sales Order ID is required."
            );
        }


        const response =
            await api.delete(
                `/sales-orders/${salesOrderId}`
            );


        return response.data;
    }


    // =====================================================
    // Sales Dashboard
    // =====================================================

    async getDashboard() {

        const response =
            await api.get(
                "/sales-orders/dashboard/summary"
            );


        return response.data;
    }


    // =====================================================
    // Export Sales Orders
    // =====================================================

    async exportSalesOrders(
        params = {}
    ) {

        const response =
            await api.get(
                "/sales-orders/export",
                {
                    params: {

                        // ---------------------------------
                        // Search
                        // ---------------------------------

                        search:
                            params.search ||
                            undefined,


                        // ---------------------------------
                        // Customer Filter
                        // ---------------------------------

                        customer_id:
                            params.customer_id ||
                            undefined,


                        // ---------------------------------
                        // PRODUCT / ITEM FILTER
                        // ---------------------------------

                        product_id:
                            params.product_id ||
                            undefined,


                        // ---------------------------------
                        // Warehouse Filter
                        // ---------------------------------

                        warehouse_id:
                            params.warehouse_id ||
                            undefined,


                        // ---------------------------------
                        // Status
                        // ---------------------------------

                        status:
                            params.status ||
                            undefined,


                        // ---------------------------------
                        // Payment Status
                        // ---------------------------------

                        payment_status:
                            params.payment_status ||
                            undefined,


                        // ---------------------------------
                        // Date From
                        // ---------------------------------

                        date_from:
                            params.date_from ||
                            undefined,


                        // ---------------------------------
                        // Date To
                        // ---------------------------------

                        date_to:
                            params.date_to ||
                            undefined,

                    },

                    responseType:
                        "blob",
                }
            );


        return response.data;
    }


    // =====================================================
    // Generate / Store Sales Order PDF
    // =====================================================

    async generateSalesOrderPdf(
        salesOrderId
    ) {

        if (
            salesOrderId === undefined ||
            salesOrderId === null ||
            salesOrderId === ""
        ) {

            throw new Error(
                "Sales Order ID is required."
            );
        }


        const response =
            await api.get(
                `/sales-orders/${salesOrderId}/pdf`,
                {
                    responseType:
                        "blob",
                }
            );


        return new Blob(
            [
                response.data
            ],
            {
                type:
                    "application/pdf",
            }
        );
    }


    // =====================================================
    // Download Sales Order PDF
    // =====================================================

    async downloadSalesOrderPdf(
        salesOrderId,
        soNumber = null
    ) {

        if (
            salesOrderId === undefined ||
            salesOrderId === null ||
            salesOrderId === ""
        ) {

            throw new Error(
                "Sales Order ID is required."
            );
        }


        const blob =
            await this.generateSalesOrderPdf(
                salesOrderId
            );


        const url =
            window.URL.createObjectURL(
                blob
            );


        try {

            const link =
                document.createElement(
                    "a"
                );


            link.href =
                url;


            link.download =
                soNumber
                    ? `${soNumber}.pdf`
                    : `Sales-Invoice-${salesOrderId}.pdf`;


            document.body.appendChild(
                link
            );


            link.click();


            link.remove();

        } finally {

            window.URL.revokeObjectURL(
                url
            );
        }


        return true;
    }


    // =====================================================
    // Get Sales Order PDF
    // =====================================================

    async getSalesOrderPdf(
        salesOrderId
    ) {

        return this.generateSalesOrderPdf(
            salesOrderId
        );
    }

}


// =========================================================
// Export Singleton
// =========================================================

export default new SalesService();