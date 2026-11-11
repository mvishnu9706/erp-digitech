import {
    createContext,
    useContext,
    useEffect,
    useState,
    useCallback,
} from "react";

import {
    getInventory,
    addInventory as createInventory,
    editInventory as updateInventory,
    deleteInventory,
    getInventoryDashboard,
    transferInventory,
    adjustInventory,
    exportInventory,
    getInventoryDetails,
    getStockMovements,
    checkInventoryExists,
    getInventoryStock,
    getStockTransferHistory,
} from "../services/inventoryService";

import { toast } from "react-toastify";


const InventoryContext = createContext();


export const InventoryProvider = ({ children }) => {

    // =====================================================
    // Inventory
    // =====================================================

    const [inventory, setInventory] = useState([]);

    const [loading, setLoading] = useState(false);

    const [actionLoading, setActionLoading] = useState(false);

    const [error, setError] = useState("");


    // =====================================================
    // Pagination
    // =====================================================

    const [page, setPage] = useState(1);

    const [size, setSize] = useState(10);

    const [totalPages, setTotalPages] = useState(1);

    const [totalRecords, setTotalRecords] = useState(0);


    // =====================================================
    // Filters
    // =====================================================

    const [search, setSearch] = useState("");

    const [warehouse, setWarehouse] = useState("");

    const [product, setProduct] = useState("");

    const [status, setStatus] = useState("");

    const [category, setCategory] = useState("");

    const [brand, setBrand] = useState("");

    const [supplier, setSupplier] = useState("");

    const [barcode, setBarcode] = useState("");


    // =====================================================
    // Dashboard
    // =====================================================

    const [dashboard, setDashboard] = useState(null);


    // =====================================================
    // Selected Inventory
    // =====================================================

    const [
        selectedInventory,
        setSelectedInventory,
    ] = useState(null);


    // =====================================================
    // Drawer
    // =====================================================

    const [
        drawerOpen,
        setDrawerOpen,
    ] = useState(false);

    const [
        drawerMode,
        setDrawerMode,
    ] = useState("add");


    // =====================================================
    // Transfer Drawer
    // =====================================================

    const [
        transferDrawerOpen,
        setTransferDrawerOpen,
    ] = useState(false);

    const [
        transferInventoryItem,
        setTransferInventoryItem,
    ] = useState(null);


    // =====================================================
    // Stock Adjustment
    // =====================================================

    const [
        adjustmentDrawerOpen,
        setAdjustmentDrawerOpen,
    ] = useState(false);

    const [
        adjustmentInventory,
        setAdjustmentInventory,
    ] = useState(null);


    // =====================================================
    // Transfer History
    // =====================================================

    const [
        transferHistory,
        setTransferHistory,
    ] = useState([]);

    const [
        transferHistoryLoading,
        setTransferHistoryLoading,
    ] = useState(false);


    // =====================================================
    // Load Inventory
    // =====================================================

    const loadInventory = useCallback(async () => {

        try {

            setLoading(true);

            setError("");

            const response = await getInventory({

                page,

                size,

                search:
                    search?.trim() || undefined,

                warehouse_id:
                    warehouse
                        ? Number(warehouse)
                        : undefined,

                product_id:
                    product
                        ? Number(product)
                        : undefined,

                stock_status:
                    status || undefined,

            });


            const data =
                response?.data || {};


            setInventory(
                data.items ||
                data.results ||
                data.data ||
                []
            );


            setTotalPages(
                data.pages ||
                data.total_pages ||
                1
            );


            setTotalRecords(
                data.total ||
                data.total_records ||
                0
            );


        } catch (err) {

            console.error(
                "Load Inventory Error:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Unable to load inventory."
            );

        } finally {

            setLoading(false);

        }

    }, [

        page,

        size,

        search,

        warehouse,

        product,

        status,

    ]);


    // =====================================================
    // Load Dashboard
    // =====================================================

    const loadDashboard = useCallback(async () => {

        try {

            const response =
                await getInventoryDashboard({

                    search:
                        search?.trim() || undefined,

                    warehouse_id:
                        warehouse
                            ? Number(warehouse)
                            : undefined,

                    product_id:
                        product
                            ? Number(product)
                            : undefined,

                    stock_status:
                        status || undefined,

                });


            setDashboard(
                response?.data || {}
            );


        } catch (err) {

            console.error(
                "Inventory Dashboard Error:",
                err
            );

        }

    }, [

        search,

        warehouse,

        product,

        status,

    ]);


    // =====================================================
    // Initial / Filter Load
    // =====================================================

    useEffect(() => {

        loadInventory();

    }, [
        loadInventory
    ]);


    useEffect(() => {

        loadDashboard();

    }, [
        loadDashboard
    ]);


    // =====================================================
    // Refresh Inventory
    // =====================================================

    const refreshInventory = useCallback(async () => {

        await Promise.all([
            loadInventory(),
            loadDashboard(),
        ]);

    }, [
        loadInventory,
        loadDashboard,
    ]);

    // Refresh automatically when a successful sale changes stock.
    useEffect(() => {
        const handleInventoryRefresh = () => {
            refreshInventory();
        };

        window.addEventListener(
            "erp:inventory-refresh",
            handleInventoryRefresh
        );

        return () => {
            window.removeEventListener(
                "erp:inventory-refresh",
                handleInventoryRefresh
            );
        };
    }, [refreshInventory]);


    // =====================================================
    // Create Inventory
    // =====================================================

    const addInventory = async (data) => {

        try {

            setActionLoading(true);

            await createInventory(data);

            await refreshInventory();

            toast.success(
                "Inventory added successfully."
            );

            closeDrawer();

        } catch (err) {

            console.error(
                "Add Inventory Error:",
                err
            );

            toast.error(
                err?.response?.data?.detail ||
                "Failed to add inventory."
            );

            throw err;

        } finally {

            setActionLoading(false);

        }

    };


    // =====================================================
    // Update Inventory
    // =====================================================

    const editInventory = async (
        id,
        data
    ) => {

        try {

            setActionLoading(true);

            await updateInventory(
                id,
                data
            );

            await refreshInventory();

            toast.success(
                "Inventory updated successfully."
            );

            closeDrawer();

        } catch (err) {

            console.error(
                "Update Inventory Error:",
                err
            );

            toast.error(
                err?.response?.data?.detail ||
                "Failed to update inventory."
            );

            throw err;

        } finally {

            setActionLoading(false);

        }

    };


    // =====================================================
    // Delete Inventory
    // =====================================================

    const removeInventory = async (
        id
    ) => {

        if (
            !window.confirm(
                "Delete this inventory record?"
            )
        ) {

            return;

        }


        try {

            setActionLoading(true);

            await deleteInventory(id);

            await refreshInventory();

            toast.success(
                "Inventory deleted successfully."
            );

        } catch (err) {

            console.error(
                "Delete Inventory Error:",
                err
            );

            toast.error(
                err?.response?.data?.detail ||
                "Failed to delete inventory."
            );

        } finally {

            setActionLoading(false);

        }

    };


    // =====================================================
    // Get Inventory Details
    // =====================================================

    const getInventoryById = async (
        id
    ) => {

        try {

            const response =
                await getInventoryDetails(id);

            return response?.data;

        } catch (err) {

            console.error(
                "Get Inventory Details Error:",
                err
            );

            throw err;

        }

    };


    // =====================================================
    // Stock Transfer
    // =====================================================

    const transferStock = async (
        data
    ) => {

        try {

            setActionLoading(true);

            await transferInventory(data);

            await refreshInventory();

            toast.success(
                "Stock transferred successfully."
            );

            closeTransferDrawer();

        } catch (err) {

            console.error(
                "Transfer Stock Error:",
                err
            );

            toast.error(
                err?.response?.data?.detail ||
                "Failed to transfer stock."
            );

            throw err;

        } finally {

            setActionLoading(false);

        }

    };


    // =====================================================
    // Stock Adjustment
    // =====================================================

    const adjustStock = async (
        data
    ) => {

        try {

            setActionLoading(true);

            await adjustInventory(data);

            await refreshInventory();

            toast.success(
                "Stock adjusted successfully."
            );

            closeAdjustmentDrawer();

        } catch (err) {

            console.error(
                "Adjust Stock Error:",
                err
            );

            toast.error(
                err?.response?.data?.detail ||
                "Failed to adjust stock."
            );

            throw err;

        } finally {

            setActionLoading(false);

        }

    };


    // =====================================================
    // CHECK INVENTORY EXISTS
    // =====================================================

    const checkInventory = async (
        productId,
        warehouseId
    ) => {

        try {

            const response =
                await checkInventoryExists(
                    productId,
                    warehouseId
                );

            return response?.data;

        } catch (err) {

            console.error(
                "Check Inventory Error:",
                err
            );

            throw err;

        }

    };


    // =====================================================
    // GET CURRENT STOCK
    // =====================================================

    const getCurrentStock = async (
        productId,
        warehouseId
    ) => {

        try {

            const response =
                await getInventoryStock(
                    productId,
                    warehouseId
                );

            return response?.data;

        } catch (err) {

            console.error(
                "Get Current Stock Error:",
                err
            );

            throw err;

        }

    };


    // =====================================================
    // EXPORT INVENTORY
    // =====================================================
    //
    // IMPORTANT:
    //
    // InventoryPage.jsx already calls:
    //
    //     downloadInventory
    //
    // Therefore this function MUST be exposed as
    // downloadInventory below.
    //
    // =====================================================

    const exportInventoryData = async () => {

        try {

            setActionLoading(true);


            // =================================================
            // Current filters
            // =================================================
            //
            // We intentionally DO NOT send:
            //
            // page
            // size
            //
            // Therefore backend exports all matching records.
            //
            // =================================================

            const exportFilters = {

                search:
                    search?.trim() || undefined,

                warehouse_id:
                    warehouse
                        ? Number(warehouse)
                        : undefined,

                product_id:
                    product
                        ? Number(product)
                        : undefined,

                stock_status:
                    status || undefined,

            };


            console.log(
                "Inventory Export Filters:",
                exportFilters
            );


            // =================================================
            // Call Excel endpoint
            // =================================================

            const response =
                await exportInventory(
                    exportFilters
                );


            // =================================================
            // Axios response contains Blob in data
            // =================================================

            const blob =
                response?.data;


            if (
                !blob ||
                !(blob instanceof Blob)
            ) {

                console.error(
                    "Invalid export response:",
                    response
                );

                throw new Error(
                    "Invalid Excel file received from server."
                );

            }


            // =================================================
            // Create download URL
            // =================================================

            const url =
                window.URL.createObjectURL(
                    blob
                );


            // =================================================
            // Create download link
            // =================================================

            const link =
                document.createElement(
                    "a"
                );


            link.href =
                url;


            link.download =
                `Inventory_${new Date()
                    .toISOString()
                    .split("T")[0]
                }.xlsx`;


            document.body.appendChild(
                link
            );


            link.click();


            document.body.removeChild(
                link
            );


            // =================================================
            // Release URL
            // =================================================

            window.URL.revokeObjectURL(
                url
            );


            toast.success(
                "Inventory exported successfully."
            );


        } catch (err) {

            console.error(
                "Inventory Export Error:",
                err
            );


            toast.error(
                err?.response?.data?.detail ||
                "Failed to export inventory."
            );

        } finally {

            setActionLoading(false);

        }

    };


    // =====================================================
    // Transfer History
    // =====================================================

    const loadTransferHistory = async (
        params = {}
    ) => {

        try {

            setTransferHistoryLoading(
                true
            );


            const response =
                await getStockTransferHistory(
                    params
                );


            const data =
                response?.data || {};


            setTransferHistory(
                data.items ||
                data.results ||
                data.data ||
                []
            );


        } catch (err) {

            console.error(
                "Transfer History Error:",
                err
            );

            toast.error(
                "Failed to load transfer history."
            );

        } finally {

            setTransferHistoryLoading(
                false
            );

        }

    };


    // =====================================================
    // Drawer Controls
    // =====================================================

    const openAddDrawer = () => {

        setDrawerMode(
            "add"
        );

        setSelectedInventory(
            null
        );

        setDrawerOpen(
            true
        );

    };


    const openEditDrawer = (
        item
    ) => {

        setDrawerMode(
            "edit"
        );

        setSelectedInventory(
            item
        );

        setDrawerOpen(
            true
        );

    };


    const openViewDrawer = (
        item
    ) => {

        setDrawerMode(
            "view"
        );

        setSelectedInventory(
            item
        );

        setDrawerOpen(
            true
        );

    };


    const closeDrawer = () => {

        setDrawerOpen(
            false
        );

        setSelectedInventory(
            null
        );

    };


    // =====================================================
    // Transfer Drawer
    // =====================================================

    const openTransferDrawer = (
        item = null
    ) => {

        setTransferInventoryItem(
            item
        );

        setTransferDrawerOpen(
            true
        );

    };


    const closeTransferDrawer = () => {

        setTransferDrawerOpen(
            false
        );

        setTransferInventoryItem(
            null
        );

    };


    // =====================================================
    // Adjustment Drawer
    // =====================================================

    const openAdjustmentDrawer = (
        item
    ) => {

        setAdjustmentInventory(
            item
        );

        setAdjustmentDrawerOpen(
            true
        );

    };


    const closeAdjustmentDrawer = () => {

        setAdjustmentDrawerOpen(
            false
        );

        setAdjustmentInventory(
            null
        );

    };


    // =====================================================
    // Reset Filters
    // =====================================================

    const resetFilters = () => {

        setSearch("");

        setWarehouse("");

        setProduct("");

        setStatus("");

        setCategory("");

        setBrand("");

        setSupplier("");

        setBarcode("");

        setPage(1);

    };


    // =====================================================
    // Provider
    // =====================================================

    return (

        <InventoryContext.Provider
            value={{

                // -----------------------------------------
                // Inventory
                // -----------------------------------------

                inventory,

                loading,

                actionLoading,

                error,


                // -----------------------------------------
                // Pagination
                // -----------------------------------------

                page,

                size,

                totalPages,

                totalRecords,


                setPage,

                setSize,


                // -----------------------------------------
                // Filters
                // -----------------------------------------

                search,

                warehouse,

                product,

                status,

                category,

                brand,

                supplier,

                barcode,


                setSearch,

                setWarehouse,

                setProduct,

                setStatus,

                setCategory,

                setBrand,

                setSupplier,

                setBarcode,


                // -----------------------------------------
                // Dashboard
                // -----------------------------------------

                dashboard,


                // -----------------------------------------
                // Selected Inventory
                // -----------------------------------------

                selectedInventory,

                setSelectedInventory,


                // -----------------------------------------
                // Drawer
                // -----------------------------------------

                drawerOpen,

                drawerMode,


                openAddDrawer,

                openEditDrawer,

                openViewDrawer,

                closeDrawer,


                // -----------------------------------------
                // Transfer Drawer
                // -----------------------------------------

                transferDrawerOpen,

                transferInventoryItem,

                openTransferDrawer,

                closeTransferDrawer,


                // -----------------------------------------
                // Adjustment Drawer
                // -----------------------------------------

                adjustmentDrawerOpen,

                adjustmentInventory,

                openAdjustmentDrawer,

                closeAdjustmentDrawer,


                // -----------------------------------------
                // Actions
                // -----------------------------------------

                loadInventory,

                refreshInventory,

                addInventory,

                editInventory,

                removeInventory,

                transferStock,

                adjustStock,

                getInventoryById,

                checkInventory,

                getCurrentStock,


                // -----------------------------------------
                // EXPORT
                //
                // IMPORTANT:
                // InventoryPage uses downloadInventory.
                // -----------------------------------------

                downloadInventory:
                    exportInventoryData,


                // -----------------------------------------
                // Transfer History
                // -----------------------------------------

                transferHistory,

                transferHistoryLoading,

                loadTransferHistory,


                // -----------------------------------------
                // Reset
                // -----------------------------------------

                resetFilters,

            }}
        >

            {children}

        </InventoryContext.Provider>

    );

};


// =====================================================
// Hook
// =====================================================

export const useInventory = () =>
    useContext(
        InventoryContext
    );