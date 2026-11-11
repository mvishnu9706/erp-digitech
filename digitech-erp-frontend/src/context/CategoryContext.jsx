import {
    createContext,
    useContext,
    useEffect,
    useState,
    useCallback,
} from "react";

import {
    getCategories,
    createCategory,
    updateCategory,
    deleteCategory,
} from "../services/categoryService";

const CategoryContext = createContext();

export const CategoryProvider = ({ children }) => {

    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // ==========================================
    // Load Categories
    // ==========================================

    const loadCategories = useCallback(async () => {

        try {

            setLoading(true);
            setError("");

            const data = await getCategories();

            setCategories(data || []);

        }

        catch (err) {

            console.error("Load Categories Error:", err);

            setError("Unable to load categories.");

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

            await loadCategories();

        };

        initialize();

        return () => {

            mounted = false;

        };

    }, [loadCategories]);

    // ==========================================
    // Refresh Categories
    // ==========================================

    const refreshCategories = async () => {

        await loadCategories();

    };

    // ==========================================
    // Add Category
    // ==========================================

    const addCategory = async (data) => {

        const category = await createCategory(data);

        await loadCategories();

        return category;

    };

    // ==========================================
    // Edit Category
    // ==========================================

    const editCategory = async (id, data) => {

        const category = await updateCategory(id, data);

        await loadCategories();

        return category;

    };

    // ==========================================
    // Delete Category
    // ==========================================

    const removeCategory = async (id) => {

        await deleteCategory(id);

        await loadCategories();

    };

    return (

        <CategoryContext.Provider

            value={{

                categories,

                loading,

                error,

                loadCategories,
                refreshCategories,

                addCategory,

                editCategory,

                removeCategory,

            }}

        >

            {children}

        </CategoryContext.Provider>

    );

};

export const useCategories = () => useContext(CategoryContext);