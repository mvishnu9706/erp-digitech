import { useEffect, useState } from "react";

import { useAuth } from "../context/AuthContext";

import { useBrands } from "../context/BrandContext";
import { useCategories } from "../context/CategoryContext";
import { useUnits } from "../context/UnitContext";
import { useWarehouses } from "../context/WarehouseContext";

export default function AppInitializer({ children }) {

    const { loading: authLoading, isAuthenticated } = useAuth();

    const { loadBrands } = useBrands();
    const { loadCategories } = useCategories();
    const { loadUnits } = useUnits();
    const { loadWarehouses } = useWarehouses();

    const [ready, setReady] = useState(false);

    useEffect(() => {

        const initialize = async () => {

            if (authLoading) return;

            if (!isAuthenticated) {

                setReady(true);

                return;

            }

            try {

                await Promise.all([

                    loadBrands(),

                    loadCategories(),

                    loadUnits(),

                    loadWarehouses(),

                ]);

            }

            finally {

                setReady(true);

            }

        };

        initialize();

    }, [

        authLoading,

        isAuthenticated,

        loadBrands,

        loadCategories,

        loadUnits,

        loadWarehouses,

    ]);

    if (!ready) {

        return <div>Loading ERP...</div>;

    }

    return children;

}