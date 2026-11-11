import {
    createContext,
    useContext,
    useEffect,
    useState,
    useCallback,
} from "react";

import {
    getBrands,
    createBrand,
    updateBrand,
    deleteBrand,
} from "../services/brandService";

const BrandContext = createContext();

export const BrandProvider = ({ children }) => {

    const [brands, setBrands] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // ==========================================
    // Load Brands
    // ==========================================

    const loadBrands = useCallback(async () => {

        try {

            setLoading(true);
            setError("");

            const data = await getBrands();

            setBrands(data || []);

        } catch (err) {

            console.error("Load Brands Error:", err);

            setError("Unable to load brands.");

        } finally {

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

            await loadBrands();

        };

        initialize();

        return () => {

            mounted = false;

        };

    }, [loadBrands]);

    // ==========================================
    // Refresh
    // ==========================================

    const refreshBrands = async () => {

        await loadBrands();

    };

    // ==========================================
    // Add
    // ==========================================

    const addBrand = async (data) => {

        const brand = await createBrand(data);

        await loadBrands();

        return brand;

    };

    // ==========================================
    // Update
    // ==========================================

    const editBrand = async (id, data) => {

        const brand = await updateBrand(id, data);

        await loadBrands();

        return brand;

    };

    // ==========================================
    // Delete
    // ==========================================

    const removeBrand = async (id) => {

        await deleteBrand(id);

        await loadBrands();

    };

    return (

        <BrandContext.Provider

            value={{

                brands,

                loading,

                error,

                loadBrands,
                refreshBrands,

                addBrand,

                editBrand,

                removeBrand,

            }}

        >

            {children}

        </BrandContext.Provider>

    );

};

export const useBrands = () => useContext(BrandContext);