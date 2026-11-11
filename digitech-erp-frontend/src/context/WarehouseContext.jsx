import {
    createContext,
    useContext,
    useEffect,
    useState,
    useCallback,
} from "react";

import {
    getWarehouses,
    createWarehouse,
    updateWarehouse,
    deleteWarehouse,
} from "../services/warehouseService";

const WarehouseContext = createContext();

export const WarehouseProvider = ({ children }) => {

    const [warehouses, setWarehouses] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // ==========================================
    // Load Warehouses
    // ==========================================

    const loadWarehouses = useCallback(async () => {

        try {

            setLoading(true);
            setError("");

            const data = await getWarehouses();

            setWarehouses(data || []);

        }

        catch (err) {

            console.error("Load Warehouses Error:", err);

            setError("Unable to load warehouses.");

        }

        finally {

            setLoading(false);

        }

    }, []);

    // ==========================================
    // Initial Load
    // ==========================================

    useEffect(() => {

        let mounted = true;

        const initialize = async () => {

            if (!mounted) return;

            await loadWarehouses();

        };

        initialize();

        return () => {

            mounted = false;

        };

    }, [loadWarehouses]);

    // ==========================================
    // Refresh Warehouses
    // ==========================================

    const refreshWarehouses = async () => {

        await loadWarehouses();

    };

    // ==========================================
    // Add Warehouse
    // ==========================================

    const addWarehouse = async (data) => {

        const warehouse = await createWarehouse(data);

        await loadWarehouses();

        return warehouse;

    };

    // ==========================================
    // Edit Warehouse
    // ==========================================

    const editWarehouse = async (id, data) => {

        const warehouse = await updateWarehouse(id, data);

        await loadWarehouses();

        return warehouse;

    };

    // ==========================================
    // Delete Warehouse
    // ==========================================

    const removeWarehouse = async (id) => {

        await deleteWarehouse(id);

        await loadWarehouses();

    };

    return (

        <WarehouseContext.Provider

            value={{

                warehouses,

                loading,

                error,

                loadWarehouses,

                refreshWarehouses,

                addWarehouse,

                editWarehouse,

                removeWarehouse,

            }}

        >

            {children}

        </WarehouseContext.Provider>

    );

};

export const useWarehouses = () => useContext(WarehouseContext);