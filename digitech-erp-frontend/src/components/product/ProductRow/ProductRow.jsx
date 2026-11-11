import "./ProductRow.css";

import {
    Edit,
    Trash2,
    Eye,
    Package,
    PackagePlus,
} from "lucide-react";

import { useProducts } from "../../../context/ProductContext";


const ProductRow = ({ product, index }) => {

    const {
        openEditDrawer,
        openViewDrawer,
        removeProduct,
        openInventoryDrawer,
    } = useProducts();


    return (

        <tr>

            {/* =====================================================
                #
            ===================================================== */}

            <td>
                {index}
            </td>


            {/* =====================================================
                Product
            ===================================================== */}

            <td>

                <div className="product-info">

                    <div className="product-image">

                        {product.image_url ? (

                            <img
                                src={product.image_url}
                                alt={product.product_name}
                            />

                        ) : (

                            <Package size={22} />

                        )}

                    </div>


                    <div>

                        <h4>
                            {product.product_name}
                        </h4>

                        <p>
                            {product.barcode || "No Barcode"}
                        </p>

                    </div>

                </div>

            </td>


            {/* =====================================================
                Brand / Model
            ===================================================== */}

            <td>

                <strong>
                    {product.brand?.name || "-"}
                </strong>

                <br />

                <span>
                    {product.model_no || "-"}
                </span>

            </td>


            {/* =====================================================
                Category
            ===================================================== */}

            <td>

                <span className="category">

                    {product.category?.name || "-"}

                </span>

            </td>


            {/* =====================================================
                SKU
            ===================================================== */}

            <td>

                {product.sku || "-"}

            </td>


            {/* =====================================================
                Incoming Price
                Backend field: cost_price
            ===================================================== */}

            <td>

                ₹
                {Number(
                    product.cost_price ?? 0
                ).toLocaleString("en-IN")}

            </td>


            {/* =====================================================
                Retail Price
                Backend field: dtp_price
            ===================================================== */}

            <td>

                ₹
                {Number(
                    product.dtp_price ?? 0
                ).toLocaleString("en-IN")}

            </td>


            {/* =====================================================
                Sale Price
                Backend field: retail_price
            ===================================================== */}

            <td>

                ₹
                {Number(
                    product.retail_price ?? 0
                ).toLocaleString("en-IN")}

            </td>


            {/* =====================================================
                GST
            ===================================================== */}

            <td>

                {Number(
                    product.gst_percentage ?? 0
                ).toLocaleString("en-IN")}
                %

            </td>


            {/* =====================================================
                Actions
            ===================================================== */}

            <td>

                <div className="actions">

                    {/* -----------------------------------------
                        View
                    ----------------------------------------- */}

                    <button
                        type="button"
                        className="action-btn view"
                        onClick={() =>
                            openViewDrawer(product)
                        }
                        title="View"
                    >

                        <Eye size={18} />

                    </button>


                    {/* -----------------------------------------
                        Add To Inventory
                    ----------------------------------------- */}

                    <button
                        type="button"
                        className="action-btn btn-add-stock"
                        title="Add To Inventory"
                        onClick={() =>
                            openInventoryDrawer(product)
                        }
                    >

                        <PackagePlus size={18} />

                    </button>


                    {/* -----------------------------------------
                        Edit
                    ----------------------------------------- */}

                    <button
                        type="button"
                        className="action-btn edit"
                        onClick={() =>
                            openEditDrawer(product)
                        }
                        title="Edit"
                    >

                        <Edit size={18} />

                    </button>


                    {/* -----------------------------------------
                        Delete
                    ----------------------------------------- */}

                    <button
                        type="button"
                        className="action-btn delete"
                        onClick={() =>
                            removeProduct(product.id)
                        }
                        title="Delete"
                    >

                        <Trash2 size={18} />

                    </button>

                </div>

            </td>

        </tr>

    );

};


export default ProductRow;