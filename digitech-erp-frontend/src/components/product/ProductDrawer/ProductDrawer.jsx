import "./ProductDrawer.css";

import {
    useEffect,
    useMemo,
} from "react";

import {
    X,
} from "lucide-react";

import {
    useForm,
    Controller,
} from "react-hook-form";

import CreatableSelect from "react-select/creatable";

import { useProducts } from "../../../context/ProductContext";
import { useUnits } from "../../../context/UnitContext";
import { useWarehouses } from "../../../context/WarehouseContext";
import { useCategories } from "../../../context/CategoryContext";
import { useBrands } from "../../../context/BrandContext";


const ProductDrawer = () => {

    const {
        drawerOpen,
        drawerMode,
        selectedProduct,
        closeDrawer,
        addProduct,
        editProduct,
    } = useProducts();


    const {
        units = [],
    } = useUnits();


    const {
        warehouses = [],
    } = useWarehouses();


    const {
        categories = [],
        addCategory,
        refreshCategories,
    } = useCategories();


    const {
        brands = [],
        addBrand,
        refreshBrands,
    } = useBrands();


    const isView = drawerMode === "view";
    const isEdit = drawerMode === "edit";
    const isAdd = drawerMode === "add";


    /* ==========================================================
       Form
       
       IMPORTANT:
       Backend field names are NOT changed.

       cost_price   = Incoming Price
       dtp_price    = Retail Price
       retail_price = Sale Price
    ========================================================== */

    const {
        register,
        control,
        handleSubmit,
        watch,
        reset,
        setValue,
        formState: {
            errors,
            isSubmitting,
        },
    } = useForm({

        defaultValues: {

            product_name: "",

            model_no: "",

            sku: "",

            barcode: "",

            category_name: "",

            brand_name: "",

            unit_id: "",

            warehouse_id: "",

            cost_price: 0,

            dtp_price: 0,

            retail_price: 0,

            margin_percentage: 0,

            gst_percentage: 18,

            hsn_code: "",

            minimum_stock: 0,

            status: "Active",

        },

    });


    /* ==========================================================
       PRICE VALUES
       
       Backend names:
       
       cost_price   = Incoming Price
       dtp_price    = Retail Price
       retail_price = Sale Price
    ========================================================== */

    const incomingPrice =
        Number(watch("cost_price") || 0);

    const retailPrice =
        Number(watch("dtp_price") || 0);

    const salePrice =
        Number(watch("retail_price") || 0);


    /* ==========================================================
       CORRECT MARGIN CALCULATION
       
       Margin % =
       ((Sale Price - Incoming Price) / Sale Price) × 100
       
       Example:
       
       Incoming = 50
       Retail   = 150
       Sale     = 250
       
       Margin = ((250 - 50) / 250) × 100
              = 80%
    ========================================================== */

    const margin = useMemo(() => {

        if (salePrice <= 0) {

            return "0.00";

        }


        const calculatedMargin =
            (
                (
                    salePrice -
                    incomingPrice
                ) /
                salePrice
            ) * 100;


        return Math.round(
            calculatedMargin * 100
        ) / 100;

    }, [
        incomingPrice,
        salePrice,
    ]);


    /* ==========================================================
       Update Margin Field
    ========================================================== */

    useEffect(() => {

        setValue(
            "margin_percentage",
            Number(margin)
        );

    }, [
        margin,
        setValue,
    ]);


    /* ==========================================================
       Load Selected Product
    ========================================================== */

    useEffect(() => {

        if (selectedProduct) {

            reset({

                product_name:
                    selectedProduct.product_name || "",

                model_no:
                    selectedProduct.model_no || "",

                sku:
                    selectedProduct.sku || "",

                barcode:
                    selectedProduct.barcode || "",

                category_name:
                    selectedProduct.category?.name || "",

                brand_name:
                    selectedProduct.brand?.name || "",

                unit_id:
                    selectedProduct.unit?.id || "",

                warehouse_id:
                    selectedProduct.warehouse?.id || "",


                /* ==============================================
                   Backend fields remain unchanged
                ============================================== */

                cost_price:
                    selectedProduct.cost_price || 0,

                dtp_price:
                    selectedProduct.dtp_price || 0,

                retail_price:
                    selectedProduct.retail_price || 0,


                margin_percentage:
                    selectedProduct.margin_percentage || 0,

                gst_percentage:
                    selectedProduct.gst_percentage || 18,

                hsn_code:
                    selectedProduct.hsn_code || "",

                minimum_stock:
                    selectedProduct.minimum_stock || 0,

                status:
                    selectedProduct.status || "Active",

            });

        }
        else {

            reset();

        }

    }, [
        selectedProduct,
        reset,
    ]);


    /* ==========================================================
       Submit
       
       Backend still receives:
       
       cost_price
       dtp_price
       retail_price
       
       Nothing is renamed.
    ========================================================== */

    const onSubmit = async (data) => {

        try {

            /* Make sure the calculated margin is submitted */

            data.margin_percentage =
                Number(margin);


            if (isEdit) {

                await editProduct(
                    selectedProduct.id,
                    data
                );

            }
            else {

                await addProduct(data);

            }

        }
        catch (error) {

            console.error(error);

        }

    };


    /* ==========================================================
       Don't render when closed
    ========================================================== */

    if (!drawerOpen) {

        return null;

    }


    /* ==========================================================
       Category Options
    ========================================================== */

    const categoryOptions =
        categories.map((item) => ({

            value: item.name,

            label: item.name,

        }));


    /* ==========================================================
       Brand Options
    ========================================================== */

    const brandOptions =
        brands.map((item) => ({

            value: item.name,

            label: item.name,

        }));


    return (

        <div className="drawer-overlay">

            <div className="product-drawer">


                {/* ==================================================
                   HEADER
                ================================================== */}

                <div className="drawer-header">

                    <h2>

                        {
                            isAdd
                                ? "Add Product"
                                : isEdit
                                ? "Edit Product"
                                : "View Product"
                        }

                    </h2>


                    <button
                        type="button"
                        onClick={closeDrawer}
                    >

                        <X size={22} />

                    </button>

                </div>


                {/* ==================================================
                   FORM
                ================================================== */}

                <form
                    onSubmit={handleSubmit(onSubmit)}
                >

                    <div className="drawer-body">


                        {/* ==================================================
                           BASIC INFORMATION
                        ================================================== */}

                        <div className="form-section">

                            <h3>
                                Basic Information
                            </h3>


                            <div className="form-grid">


                                {/* Product Name */}

                                <div className="form-group">

                                    <label>
                                        Product Name *
                                    </label>

                                    <input
                                        type="text"
                                        placeholder="Enter Product Name"
                                        disabled={isView}
                                        {...register(
                                            "product_name",
                                            {
                                                required:
                                                    "Product Name is required",
                                            }
                                        )}
                                    />

                                    <span className="error">
                                        {
                                            errors.product_name?.message
                                        }
                                    </span>

                                </div>


                                {/* Model */}

                                <div className="form-group">

                                    <label>
                                        Model No
                                    </label>

                                    <input
                                        type="text"
                                        placeholder="Model Number"
                                        disabled={isView}
                                        {...register("model_no")}
                                    />

                                </div>


                                {/* SKU */}

                                <div className="form-group">

                                    <label>
                                        SKU
                                    </label>

                                    <input
                                        type="text"
                                        placeholder="SKU"
                                        disabled={isView}
                                        {...register("sku")}
                                    />

                                </div>


                                {/* Barcode */}

                                <div className="form-group">

                                    <label>
                                        Barcode
                                    </label>

                                    <input
                                        type="text"
                                        placeholder="Barcode"
                                        disabled={isView}
                                        {...register("barcode")}
                                    />

                                </div>

                            </div>

                        </div>


                        {/* ==================================================
                           CLASSIFICATION
                        ================================================== */}

                        <div className="form-section">

                            <h3>
                                Classification
                            </h3>


                            <div className="form-grid">


                                {/* Category */}

                                <div className="form-group">

                                    <label>
                                        Category Name *
                                    </label>

                                    <Controller
                                        name="category_name"
                                        control={control}
                                        rules={{
                                            required:
                                                "Category is required",
                                        }}
                                        render={({ field }) => (

                                            <CreatableSelect

                                                isDisabled={isView}

                                                options={
                                                    categoryOptions
                                                }

                                                value={
                                                    categoryOptions.find(
                                                        (option) =>
                                                            option.value ===
                                                            field.value
                                                    ) || null
                                                }

                                                onChange={(option) => {

                                                    field.onChange(
                                                        option?.value || ""
                                                    );

                                                }}

                                                onCreateOption={
                                                    async (inputValue) => {

                                                        const created =
                                                            await addCategory({

                                                                name:
                                                                    inputValue,

                                                                code:
                                                                    inputValue
                                                                        .toUpperCase()
                                                                        .replace(
                                                                            /\s+/g,
                                                                            "_"
                                                                        ),

                                                            });


                                                        await refreshCategories();


                                                        field.onChange(
                                                            created.name
                                                        );

                                                    }
                                                }

                                                placeholder="Select or Create Category"

                                            />

                                        )}
                                    />

                                    <span className="error">

                                        {
                                            errors.category_name?.message
                                        }

                                    </span>

                                </div>


                                {/* Brand */}

                                <div className="form-group">

                                    <label>
                                        Brand Name *
                                    </label>

                                    <Controller
                                        name="brand_name"
                                        control={control}
                                        rules={{
                                            required:
                                                "Brand is required",
                                        }}
                                        render={({ field }) => (

                                            <CreatableSelect

                                                isDisabled={isView}

                                                options={
                                                    brandOptions
                                                }

                                                value={
                                                    brandOptions.find(
                                                        (option) =>
                                                            option.value ===
                                                            field.value
                                                    ) || null
                                                }

                                                onChange={(option) => {

                                                    field.onChange(
                                                        option?.value || ""
                                                    );

                                                }}

                                                onCreateOption={
                                                    async (inputValue) => {

                                                        const created =
                                                            await addBrand({

                                                                name:
                                                                    inputValue,

                                                                code:
                                                                    inputValue
                                                                        .toUpperCase()
                                                                        .replace(
                                                                            /\s+/g,
                                                                            "_"
                                                                        ),

                                                            });


                                                        await refreshBrands();


                                                        field.onChange(
                                                            created.name
                                                        );

                                                    }
                                                }

                                                placeholder="Select or Create Brand"

                                            />

                                        )}
                                    />

                                    <span className="error">

                                        {
                                            errors.brand_name?.message
                                        }

                                    </span>

                                </div>


                                {/* Unit */}

                                <div className="form-group">

                                    <label>
                                        Unit *
                                    </label>

                                    <select
                                        disabled={isView}
                                        {...register(
                                            "unit_id",
                                            {
                                                required:
                                                    "Unit is required",
                                            }
                                        )}
                                    >

                                        <option value="">
                                            Select Unit
                                        </option>

                                        {
                                            units.map(
                                                (unit) => (

                                                    <option
                                                        key={unit.id}
                                                        value={unit.id}
                                                    >
                                                        {unit.name}
                                                    </option>

                                                )
                                            )
                                        }

                                    </select>

                                    <span className="error">

                                        {
                                            errors.unit_id?.message
                                        }

                                    </span>

                                </div>


                                {/* Warehouse */}

                                <div className="form-group">

                                    <label>
                                        Warehouse *
                                    </label>

                                    <select
                                        disabled={isView}
                                        {...register(
                                            "warehouse_id",
                                            {
                                                required:
                                                    "Warehouse is required",
                                            }
                                        )}
                                    >

                                        <option value="">
                                            Select Warehouse
                                        </option>

                                        {
                                            warehouses.map(
                                                (warehouse) => (

                                                    <option
                                                        key={warehouse.id}
                                                        value={warehouse.id}
                                                    >
                                                        {
                                                            warehouse.warehouse_name
                                                        }
                                                    </option>

                                                )
                                            )
                                        }

                                    </select>

                                    <span className="error">

                                        {
                                            errors.warehouse_id?.message
                                        }

                                    </span>

                                </div>

                            </div>

                        </div>


                        {/* ==================================================
                           PRICING
                        ================================================== */}

                        <div className="form-section">

                            <h3>
                                Pricing
                            </h3>


                            <div className="form-grid">


                                {/* ==================================================
                                   INCOMING PRICE
                                   
                                   Backend:
                                   cost_price
                                ================================================== */}

                                <div className="form-group">

                                    <label>
                                        Incoming Price *
                                    </label>

                                    <input
                                        type="number"
                                        step="0.01"
                                        min="0"
                                        disabled={isView}
                                        {...register(
                                            "cost_price",
                                            {
                                                valueAsNumber: true,
                                            }
                                        )}
                                    />

                                </div>


                                {/* ==================================================
                                   RETAIL PRICE
                                   
                                   Backend:
                                   dtp_price
                                ================================================== */}

                                <div className="form-group">

                                    <label>
                                        Retail Price *
                                    </label>

                                    <input
                                        type="number"
                                        step="0.01"
                                        min="0"
                                        disabled={isView}
                                        {...register(
                                            "dtp_price",
                                            {
                                                valueAsNumber: true,
                                            }
                                        )}
                                    />

                                </div>


                                {/* ==================================================
                                   SALE PRICE
                                   
                                   Backend:
                                   retail_price
                                ================================================== */}

                                <div className="form-group">

                                    <label>
                                        Sale Price *
                                    </label>

                                    <input
                                        type="number"
                                        step="0.01"
                                        min="0"
                                        disabled={isView}
                                        {...register(
                                            "retail_price",
                                            {
                                                valueAsNumber: true,
                                            }
                                        )}
                                    />

                                </div>


                                {/* ==================================================
                                   MARGIN
                                ================================================== */}

                                <div className="form-group">

                                    <label>
                                        Margin %
                                    </label>

                                    <input
                                        type="number"
                                        readOnly
                                        disabled
                                        value={margin}
                                        {...register(
                                            "margin_percentage"
                                        )}
                                    />

                                </div>


                                {/* GST */}

                                <div className="form-group">

                                    <label>
                                        GST %
                                    </label>

                                    <input
                                        type="number"
                                        step="0.01"
                                        min="0"
                                        disabled={isView}
                                        {...register(
                                            "gst_percentage",
                                            {
                                                valueAsNumber: true,
                                            }
                                        )}
                                    />

                                </div>


                                {/* HSN */}

                                <div className="form-group">

                                    <label>
                                        HSN Code
                                    </label>

                                    <input
                                        type="text"
                                        disabled={isView}
                                        {...register("hsn_code")}
                                    />

                                </div>

                            </div>

                        </div>


                        {/* ==================================================
                           INVENTORY
                        ================================================== */}

                        <div className="form-section">

                            <h3>
                                Inventory
                            </h3>


                            <div className="form-grid">


                                {/* Minimum Stock */}

                                <div className="form-group">

                                    <label>
                                        Minimum Stock
                                    </label>

                                    <input
                                        type="number"
                                        min="0"
                                        disabled={isView}
                                        {...register(
                                            "minimum_stock",
                                            {
                                                valueAsNumber: true,
                                            }
                                        )}
                                    />

                                </div>


                                {/* Status */}

                                <div className="form-group">

                                    <label>
                                        Status
                                    </label>

                                    <select
                                        disabled={isView}
                                        {...register("status")}
                                    >

                                        <option value="Active">
                                            Active
                                        </option>

                                        <option value="Inactive">
                                            Inactive
                                        </option>

                                    </select>

                                </div>

                            </div>

                        </div>

                    </div>


                    {/* ==================================================
                       FOOTER
                    ================================================== */}

                    <div className="drawer-footer">

                        <button
                            type="button"
                            className="btn-cancel"
                            onClick={closeDrawer}
                        >
                            Cancel
                        </button>


                        {!isView && (

                            <button
                                type="submit"
                                className="btn-save"
                                disabled={isSubmitting}
                            >

                                {
                                    isSubmitting
                                        ? "Saving..."
                                        : "Save Product"
                                }

                            </button>

                        )}

                    </div>

                </form>

            </div>

        </div>

    );

};


export default ProductDrawer;