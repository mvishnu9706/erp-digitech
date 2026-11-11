import "./ProductTable.css";

import { useProducts } from "../../../context/ProductContext";

import ProductRow from "../ProductRow/ProductRow";


const ProductTable = () => {

    const {
        products,
        loading,
        error,
        page,
        size,
    } = useProducts();


    return (

        <div className="product-table">

            <table>

                {/* =====================================================
                    TABLE HEADER
                ===================================================== */}

                <thead>

                    <tr>

                        <th>#</th>

                        <th>Product</th>

                        <th>Brand / Model</th>

                        <th>Category</th>

                        <th>SKU</th>

                        <th>Incoming Price</th>

                        <th>Retail Price</th>

                        <th>Sale Price</th>

                        <th>GST</th>

                        <th>Actions</th>

                    </tr>

                </thead>


                {/* =====================================================
                    TABLE BODY
                ===================================================== */}

                <tbody>

                    {/* =================================================
                        Loading
                    ================================================= */}

                    {loading && (

                        <tr>

                            <td
                                colSpan="10"
                                className="table-message"
                            >
                                Loading Products...
                            </td>

                        </tr>

                    )}


                    {/* =================================================
                        Error
                    ================================================= */}

                    {!loading && error && (

                        <tr>

                            <td
                                colSpan="10"
                                className="table-message error"
                            >
                                {error}
                            </td>

                        </tr>

                    )}


                    {/* =================================================
                        No Products
                    ================================================= */}

                    {!loading &&
                        !error &&
                        products.length === 0 && (

                            <tr>

                                <td
                                    colSpan="10"
                                    className="table-message"
                                >
                                    No Products Found
                                </td>

                            </tr>

                        )}


                    {/* =================================================
                        Products
                    ================================================= */}

                    {!loading &&
                        !error &&
                        products.length > 0 &&
                        products.map(
                            (product, index) => (

                                <ProductRow

                                    key={product.id}

                                    index={
                                        (page - 1) *
                                        size +
                                        index +
                                        1
                                    }

                                    product={product}

                                />

                            )
                        )}

                </tbody>

            </table>

        </div>

    );

};


export default ProductTable;