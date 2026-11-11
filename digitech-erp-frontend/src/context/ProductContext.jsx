import {
    createContext,
    useContext,
    useEffect,
    useState,
    useCallback,
} from "react";

import {
    getProducts,
    createProduct,
    updateProduct,
    deleteProduct,
    exportProducts,
} from "../services/productService";

import { toast } from "react-toastify";

const ProductContext = createContext();

export const ProductProvider = ({ children }) => {

    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [search, setSearch] = useState("");
    const [category, setCategory] = useState("");
    const [brand, setBrand] = useState("");
    const [warehouse, setWarehouse] = useState("");
    const [status, setStatus] = useState("");

    const [page, setPage] = useState(1);
    const [size, setSize] = useState(10);

    const [totalPages, setTotalPages] = useState(1);
    const [totalRecords, setTotalRecords] = useState(0);

    const [selectedProduct, setSelectedProduct] = useState(null);

    const [drawerOpen, setDrawerOpen] = useState(false);
    const [drawerMode, setDrawerMode] = useState("add");

    const [inventoryDrawerOpen, setInventoryDrawerOpen] = useState(false);
    const [inventoryProduct, setInventoryProduct] = useState(null);

    // ==========================================
    // Load Products
    // ==========================================

    const loadProducts = useCallback(async () => {

        try {

            setLoading(true);
            setError("");

            const response = await getProducts({
                page,
                size,
                search: search || undefined,
                category_id: category || undefined,
                brand_id: brand || undefined,
                warehouse_id: warehouse || undefined,
                status: status || undefined,
            });

            const data = response.data;

            setProducts(data.items || []);
            setTotalPages(data.pages || 1);
            setTotalRecords(data.total || 0);

        }
        catch (err) {

            console.error("Load Products Error:", err);
            setError("Unable to load products.");

        }
        finally {

            setLoading(false);

        }

    }, [
        page,
        size,
        search,
        category,
        brand,
        warehouse,
        status,
    ]);

    // ==========================================
    // Initial Load
    // ==========================================

    useEffect(() => {

        let mounted = true;

        const initialize = async () => {

            if (!mounted) return;

            await loadProducts();

        };

        initialize();

        return () => {

            mounted = false;

        };

    }, [loadProducts]);

    // ==========================================
    // Add Product
    // ==========================================

    const addProduct = async (data) => {

        try {

            setLoading(true);

            await createProduct(data);

            // Reload latest products
            await loadProducts();

            toast.success("✅ Product added successfully.");

            closeDrawer();

        }
        catch (err) {

            console.error("Add Product Error:", err);
            toast.error("❌ Failed to add product.");
            throw err;

        }
        finally {

            setLoading(false);

        }

    };

    // ==========================================
    // Edit Product
    // ==========================================

    const editProduct = async (id, data) => {

        try {

            setLoading(true);

            await updateProduct(id, data);

            await loadProducts();

            toast.success("✅ Product updated successfully.");

            closeDrawer();

        }
        catch (err) {

            console.error("Update Product Error:", err);
            toast.error("❌ Failed to update product.");
            throw err;

        }
        finally {

            setLoading(false);

        }

    };

    // ==========================================
    // Delete Product
    // ==========================================

    const removeProduct = async (id) => {

        if (!window.confirm("Delete this product?")) return;

        try {

            setLoading(true);

            await deleteProduct(id);

            await loadProducts();

            toast.success("✅ Product deleted successfully.");

        }
        catch (err) {

            console.error("Delete Product Error:", err);
            toast.error("❌ Failed to delete product.");

        }
        finally {

            setLoading(false);

        }

    };

    // ==========================================
    // Export Products
    // ==========================================

    const downloadProducts = async () => {

        try {

            const blob = await exportProducts();

            const url = window.URL.createObjectURL(blob);

            const link = document.createElement("a");

            link.href = url;

            link.download = `Products_${new Date().toISOString().split("T")[0]}.xlsx`;

            document.body.appendChild(link);

            link.click();

            document.body.removeChild(link);

            window.URL.revokeObjectURL(url);

        }
        catch (err) {

            console.error("Export Products Error:", err);
            alert("Failed to export products.");

        }

    };

    // ==========================================
    // Refresh
    // ==========================================

    const refreshProducts = async () => {

        await loadProducts();

    };

    // ==========================================
    // Drawer Controls
    // ==========================================

    const openAddDrawer = () => {

        setDrawerMode("add");
        setSelectedProduct(null);
        setDrawerOpen(true);

    };

    const openEditDrawer = (product) => {

        setDrawerMode("edit");
        setSelectedProduct(product);
        setDrawerOpen(true);

    };

    const openViewDrawer = (product) => {

        setDrawerMode("view");
        setSelectedProduct(product);
        setDrawerOpen(true);

    };

    const closeDrawer = () => {

        setDrawerOpen(false);
        setSelectedProduct(null);

    };

    const openInventoryDrawer = (product) => {
        setInventoryProduct(product);
        setInventoryDrawerOpen(true);
    };

    const closeInventoryDrawer = () => {
        setInventoryDrawerOpen(false);
        setInventoryProduct(null);
    };

    return (

        <ProductContext.Provider

            value={{

                products,

                loading,

                error,

                page,

                size,

                totalPages,

                totalRecords,

                search,

                category,

                brand,

                warehouse,

                status,

                drawerOpen,

                drawerMode,

                selectedProduct,

                inventoryDrawerOpen,

                inventoryProduct,

                setSearch,

                setCategory,

                setBrand,

                setWarehouse,

                setStatus,

                setPage,

                setSize,

                loadProducts,

                refreshProducts,

                addProduct,

                editProduct,

                removeProduct,

                downloadProducts,

                openAddDrawer,

                openEditDrawer,

                openViewDrawer,

                closeDrawer,

                openInventoryDrawer,

                closeInventoryDrawer,

            }}

        >

            {children}

        </ProductContext.Provider>

    );

};

export const useProducts = () => useContext(ProductContext);