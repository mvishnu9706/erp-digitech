import "./ProductToolbar.css";

import {
    Search,
    RefreshCcw,
    Plus,
    Upload,
    Download,
} from "lucide-react";

import {
    exportProducts,
    importProducts,
} from "../../../services/productService";

import { useRef } from "react";

import { useProducts } from "../../../context/ProductContext";
import { useCategories } from "../../../context/CategoryContext";
import { useBrands } from "../../../context/BrandContext";
import { useWarehouses } from "../../../context/WarehouseContext";


const ProductToolbar = () => {

    const {

        search,
        setSearch,

        category,
        setCategory,

        brand,
        setBrand,

        warehouse,
        setWarehouse,

        status,
        setStatus,

        setPage,

        refreshProducts,

        openAddDrawer,

    } = useProducts();


    const { categories = [] } = useCategories();

    const { brands = [] } = useBrands();

    const { warehouses = [] } = useWarehouses();


    const fileInputRef = useRef(null);


    // ==========================================================
    // Search
    // ==========================================================

    const handleSearch = (e) => {

        setSearch(e.target.value);

        setPage(1);

    };


    // ==========================================================
    // Category
    // ==========================================================

    const handleCategory = (e) => {

        setCategory(e.target.value);

        setPage(1);

    };


    // ==========================================================
    // Brand
    // ==========================================================

    const handleBrand = (e) => {

        setBrand(e.target.value);

        setPage(1);

    };


    // ==========================================================
    // Warehouse
    // ==========================================================

    const handleWarehouse = (e) => {

        setWarehouse(e.target.value);

        setPage(1);

    };


    // ==========================================================
    // Status
    // ==========================================================

    const handleStatus = (e) => {

        setStatus(e.target.value);

        setPage(1);

    };


    // ==========================================================
    // EXPORT
    //
    // IMPORTANT:
    //
    // Send the currently selected filters to backend.
    //
    // If no filters are selected, undefined values are sent
    // and backend will export ALL products.
    // ==========================================================

    const handleExport = async () => {

        try {

            const blob = await exportProducts({

                search:
                    search?.trim()
                        ? search.trim()
                        : undefined,

                category_id:
                    category
                        ? category
                        : undefined,

                brand_id:
                    brand
                        ? brand
                        : undefined,

                warehouse_id:
                    warehouse
                        ? warehouse
                        : undefined,

                status:
                    status
                        ? status
                        : undefined,

            });


            const url =
                window.URL.createObjectURL(blob);


            const a =
                document.createElement("a");


            a.href = url;


            a.download =
                `Products_${new Date()
                    .toISOString()
                    .split("T")[0]}.xlsx`;


            document.body.appendChild(a);


            a.click();


            a.remove();


            window.URL.revokeObjectURL(url);

        }
        catch (error) {

            console.error(
                "Export Products Error:",
                error
            );

            alert(
                "Failed to export products."
            );

        }

    };


    // ==========================================================
    // IMPORT BUTTON
    // ==========================================================

    const handleImportClick = () => {

        fileInputRef.current?.click();

    };


    // ==========================================================
    // IMPORT
    // ==========================================================

    const handleImport = async (e) => {

        const file =
            e.target.files?.[0];


        if (!file) {

            return;

        }


        try {

            const result =
                await importProducts(file);


            alert(
                `Import Completed\n\n` +
                `Imported : ${result.imported}\n` +
                `Failed : ${result.failed}`
            );


            await refreshProducts();

        }
        catch (error) {

            console.error(
                "Import Products Error:",
                error
            );

            alert(
                "Import failed."
            );

        }


        // Reset file input so the same file
        // can be selected again.

        e.target.value = "";

    };


    return (

        <div className="product-toolbar">


            {/* ==================================================
               LEFT SIDE
            ================================================== */}

            <div className="toolbar-left">


                {/* ==================================================
                   SEARCH
                ================================================== */}

                <div className="search-box">

                    <Search size={18} />

                    <input
                        type="text"
                        placeholder="Search for Product, Category, Brand..."
                        value={search}
                        onChange={handleSearch}
                    />

                </div>


                {/* ==================================================
                   CATEGORY
                ================================================== */}

                <select
                    value={category}
                    onChange={handleCategory}
                >

                    <option value="">
                        All Categories
                    </option>


                    {
                        categories.map((cat) => (

                            <option
                                key={cat.id}
                                value={cat.id}
                            >

                                {cat.name}

                            </option>

                        ))
                    }

                </select>


                {/* ==================================================
                   BRAND
                ================================================== */}

                <select
                    value={brand}
                    onChange={handleBrand}
                >

                    <option value="">
                        All Brands
                    </option>


                    {
                        brands.map((item) => (

                            <option
                                key={item.id}
                                value={item.id}
                            >

                                {item.name}

                            </option>

                        ))
                    }

                </select>


                {/* ==================================================
                   WAREHOUSE
                ================================================== */}

                <select
                    value={warehouse}
                    onChange={handleWarehouse}
                >

                    <option value="">
                        All Warehouses
                    </option>


                    {
                        warehouses.map((item) => (

                            <option
                                key={item.id}
                                value={item.id}
                            >

                                {item.warehouse_name}

                            </option>

                        ))
                    }

                </select>


                {/* ==================================================
                   STATUS
                ================================================== */}

                <select
                    value={status}
                    onChange={handleStatus}
                >

                    <option value="">
                        All Status
                    </option>

                    <option value="Active">
                        Active
                    </option>

                    <option value="Inactive">
                        Inactive
                    </option>

                </select>

            </div>


            {/* ==================================================
               RIGHT SIDE
            ================================================== */}

            <div className="toolbar-right">


                {/* ==================================================
                   HIDDEN FILE INPUT
                ================================================== */}

                <input
                    type="file"
                    accept=".xlsx,.xls"
                    ref={fileInputRef}
                    style={{
                        display: "none",
                    }}
                    onChange={handleImport}
                />


                {/* ==================================================
                   IMPORT
                ================================================== */}

                <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleImportClick}
                >

                    <Upload size={18} />

                    Import

                </button>


                {/* ==================================================
                   EXPORT
                ================================================== */}

                <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleExport}
                >

                    <Download size={18} />

                    Export

                </button>


                {/* ==================================================
                   REFRESH
                ================================================== */}

                <button
                    type="button"
                    className="btn btn-refresh"
                    onClick={refreshProducts}
                >

                    <RefreshCcw size={18} />

                    Refresh

                </button>


                {/* ==================================================
                   ADD PRODUCT
                ================================================== */}

                <button
                    type="button"
                    className="btn btn-primary"
                    onClick={openAddDrawer}
                >

                    <Plus size={18} />

                    Add Product

                </button>

            </div>

        </div>

    );

};


export default ProductToolbar;