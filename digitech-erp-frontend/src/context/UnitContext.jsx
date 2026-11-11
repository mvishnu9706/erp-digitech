import {
    createContext,
    useContext,
    useEffect,
    useState,
    useCallback,
} from "react";

import {
    getUnits,
    createUnit,
    updateUnit,
    deleteUnit,
} from "../services/unitService";

const UnitContext = createContext();

export const UnitProvider = ({ children }) => {

    const [units, setUnits] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // ==========================================
    // Load Units
    // ==========================================

    const loadUnits = useCallback(async () => {

        try {

            setLoading(true);
            setError("");

            const data = await getUnits();

            setUnits(data || []);

        }

        catch (err) {

            console.error("Load Units Error:", err);

            setError("Unable to load units.");

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

            await loadUnits();

        };

        initialize();

        return () => {

            mounted = false;

        };

    }, [loadUnits]);

    // ==========================================
    // Refresh Units
    // ==========================================

    const refreshUnits = async () => {

        await loadUnits();

    };

    // ==========================================
    // Add Unit
    // ==========================================

    const addUnit = async (data) => {

        const unit = await createUnit(data);

        await loadUnits();

        return unit;

    };

    // ==========================================
    // Edit Unit
    // ==========================================

    const editUnit = async (id, data) => {

        const unit = await updateUnit(id, data);

        await loadUnits();

        return unit;

    };

    // ==========================================
    // Delete Unit
    // ==========================================

    const removeUnit = async (id) => {

        await deleteUnit(id);

        await loadUnits();

    };

    return (

        <UnitContext.Provider

            value={{

                units,

                loading,

                error,

                loadUnits,

                refreshUnits,

                addUnit,

                editUnit,

                removeUnit,

            }}

        >

            {children}

        </UnitContext.Provider>

    );

};

export const useUnits = () => useContext(UnitContext);