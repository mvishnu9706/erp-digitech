import {
    useEffect,
    useState,
} from "react";

import Input from "../../common/Input/Input";
import Select from "../../common/Select/Select";

import {
    getCategories
} from "../../../services/categoryService";

import {
    getBrands
} from "../../../services/brandService";

import {
    getUnits
} from "../../../services/unitService";

import {
    getWarehouses
} from "../../../services/warehouseService";

import "./ProductForm.css";


const ProductForm = ({
    initialValues,
    mode,
    onSubmit
}) => {

    /* ==========================================================
       IMPORTANT:
       Keep these backend field names unchanged.

       purchase_price = Incoming Price
       dtp_price      = Retail Price
       retail_price   = Sale Price
    ========================================================== */

    const defaultValues = {

        product_name: "",

        sku: "",

        barcode: "",

        category_id: "",

        brand_id: "",

        unit_id: "",

        purchase_price: "",

        dtp_price: "",

        retail_price: "",

        mrp: "",

        gst: "18",

        hsn_code: "",

        minimum_stock: "",

        opening_stock: "",

        warehouse_id: "",

        description: "",

        status: "Active"

    };


    const [formData, setFormData] = useState(defaultValues);

    const [categories, setCategories] = useState([]);

    const [brands, setBrands] = useState([]);

    const [units, setUnits] = useState([]);

    const [warehouses, setWarehouses] = useState([]);


    /* ==========================================================
       Load Master Data
    ========================================================== */

    useEffect(() => {

        loadMasters();

    }, []);


    /* ==========================================================
       Load Existing Product
    ========================================================== */

    useEffect(() => {

        if (initialValues) {

            setFormData({

                ...defaultValues,

                ...initialValues

            });

        }

    }, [initialValues]);


    /* ==========================================================
       Load Categories / Brands / Units / Warehouses
    ========================================================== */

    const loadMasters = async () => {

        try {

            const [
                categoryRes,
                brandRes,
                unitRes,
                warehouseRes
            ] = await Promise.all([

                getCategories(),

                getBrands(),

                getUnits(),

                getWarehouses()

            ]);


            setCategories(
                categoryRes.data || []
            );

            setBrands(
                brandRes.data || []
            );

            setUnits(
                unitRes.data || []
            );

            setWarehouses(
                warehouseRes.data || []
            );

        }
        catch (error) {

            console.error(
                "Failed to load product masters:",
                error
            );

        }

    };


    /* ==========================================================
       Handle Input Changes
    ========================================================== */

    const handleChange = (e) => {

        const {
            name,
            value
        } = e.target;


        setFormData((previous) => ({

            ...previous,

            [name]: value

        }));

    };


    /* ==========================================================
       Frontend Margin Calculation
       
       Incoming Price = purchase_price
       Sale Price     = retail_price

       Margin % =
       ((Sale Price - Incoming Price) / Sale Price) * 100
    ========================================================== */

    const incomingPrice =
        parseFloat(formData.purchase_price) || 0;

    const salePrice =
        parseFloat(formData.retail_price) || 0;


    let marginPercentage = 0;


    if (salePrice > 0) {

        marginPercentage =
            ((salePrice - incomingPrice) / salePrice) * 100;

    }


    marginPercentage =
        Math.max(
            0,
            Math.round(marginPercentage * 100) / 100
        );


    /* ==========================================================
       Submit
    ========================================================== */

    const handleSubmit = (e) => {

        e.preventDefault();

        /*
         * Do NOT rename backend fields here.
         *
         * Backend continues receiving:
         *
         * purchase_price
         * dtp_price
         * retail_price
         *
         */

        onSubmit(formData);

    };


    const readOnly = mode === "view";


    return (

        <form
            id="product-form"
            className="product-form"
            onSubmit={handleSubmit}
        >


            {/* ==================================================
               BASIC INFORMATION
            ================================================== */}

            <div className="form-section">

                <h3>
                    📦 Basic Information
                </h3>


                <div className="form-grid">


                    {/* Product Name */}

                    <Input
                        label="Product Name"
                        name="product_name"
                        value={formData.product_name}
                        onChange={handleChange}
                        required
                        disabled={readOnly}
                    />


                    {/* SKU */}

                    <Input
                        label="SKU"
                        name="sku"
                        value={formData.sku}
                        onChange={handleChange}
                        disabled={readOnly}
                    />


                    {/* Barcode */}

                    <Input
                        label="Barcode"
                        name="barcode"
                        value={formData.barcode}
                        onChange={handleChange}
                        disabled={readOnly}
                    />


                    {/* Category */}

                    <Select
                        label="Category"
                        name="category_id"
                        value={formData.category_id}
                        onChange={handleChange}
                        disabled={readOnly}
                        options={[

                            {
                                value: "",
                                label: "Select Category"
                            },

                            ...categories.map(
                                (category) => ({

                                    value: category.id,

                                    label: category.name

                                })
                            )

                        ]}
                    />


                    {/* Brand */}

                    <Select
                        label="Brand"
                        name="brand_id"
                        value={formData.brand_id}
                        onChange={handleChange}
                        disabled={readOnly}
                        options={[

                            {
                                value: "",
                                label: "Select Brand"
                            },

                            ...brands.map(
                                (brand) => ({

                                    value: brand.id,

                                    label: brand.name

                                })
                            )

                        ]}
                    />


                    {/* Unit */}

                    <Select
                        label="Unit"
                        name="unit_id"
                        value={formData.unit_id}
                        onChange={handleChange}
                        disabled={readOnly}
                        options={[

                            {
                                value: "",
                                label: "Select Unit"
                            },

                            ...units.map(
                                (unit) => ({

                                    value: unit.id,

                                    label: unit.name

                                })
                            )

                        ]}
                    />

                </div>

            </div>


            {/* ==================================================
               PRICING
            ================================================== */}

            <div className="form-section">

                <h3>
                    💰 Pricing
                </h3>


                <div className="form-grid">


                    {/* ==================================================
                       Incoming Price

                       Backend field remains:
                       purchase_price
                    ================================================== */}

                    <Input
                        label="Incoming Price"
                        type="number"
                        name="purchase_price"
                        value={formData.purchase_price}
                        onChange={handleChange}
                        disabled={readOnly}
                        min="0"
                        step="0.01"
                        required
                    />


                    {/* ==================================================
                       Retail Price

                       Backend field remains:
                       dtp_price
                    ================================================== */}

                    <Input
                        label="Retail Price"
                        type="number"
                        name="dtp_price"
                        value={formData.dtp_price}
                        onChange={handleChange}
                        disabled={readOnly}
                        min="0"
                        step="0.01"
                        required
                    />


                    {/* ==================================================
                       Sale Price

                       Backend field remains:
                       retail_price
                    ================================================== */}

                    <Input
                        label="Sale Price"
                        type="number"
                        name="retail_price"
                        value={formData.retail_price}
                        onChange={handleChange}
                        disabled={readOnly}
                        min="0"
                        step="0.01"
                        required
                    />


                    {/* ==================================================
                       Margin

                       Frontend calculated only.
                       Not sent as a renamed backend field.
                    ================================================== */}

                    <Input
                        label="Margin %"
                        type="number"
                        name="frontend_margin"
                        value={marginPercentage.toFixed(2)}
                        disabled={true}
                    />


                    {/* GST */}

                    <Input
                        label="GST (%)"
                        type="number"
                        name="gst"
                        value={formData.gst}
                        onChange={handleChange}
                        disabled={readOnly}
                        min="0"
                        step="0.01"
                    />


                    {/* HSN */}

                    <Input
                        label="HSN Code"
                        name="hsn_code"
                        value={formData.hsn_code}
                        onChange={handleChange}
                        disabled={readOnly}
                    />

                </div>

            </div>


            {/* ==================================================
               INVENTORY
            ================================================== */}

            <div className="form-section">

                <h3>
                    📦 Inventory
                </h3>


                <div className="form-grid">


                    {/* Minimum Stock */}

                    <Input
                        label="Minimum Stock"
                        type="number"
                        name="minimum_stock"
                        value={formData.minimum_stock}
                        onChange={handleChange}
                        disabled={readOnly}
                        min="0"
                        step="1"
                    />


                    {/* Opening Stock */}

                    <Input
                        label="Opening Stock"
                        type="number"
                        name="opening_stock"
                        value={formData.opening_stock}
                        onChange={handleChange}
                        disabled={readOnly}
                        min="0"
                        step="1"
                    />


                    {/* Warehouse */}

                    <Select
                        label="Warehouse"
                        name="warehouse_id"
                        value={formData.warehouse_id}
                        onChange={handleChange}
                        disabled={readOnly}
                        options={[

                            {
                                value: "",
                                label: "Select Warehouse"
                            },

                            ...warehouses.map(
                                (warehouse) => ({

                                    value: warehouse.id,

                                    label:
                                        warehouse.warehouse_name ||
                                        warehouse.name

                                })
                            )

                        ]}
                    />


                    {/* Status */}

                    <Select
                        label="Status"
                        name="status"
                        value={formData.status}
                        onChange={handleChange}
                        disabled={readOnly}
                        options={[

                            {
                                value: "Active",
                                label: "Active"
                            },

                            {
                                value: "Inactive",
                                label: "Inactive"
                            }

                        ]}
                    />

                </div>

            </div>


        </form>

    );

};


export default ProductForm;