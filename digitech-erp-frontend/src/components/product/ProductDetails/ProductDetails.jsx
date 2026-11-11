import "./ProductDetails.css";

const ProductDetails = ({ product }) => {

    if (!product) return null;

    return (

        <div className="product-details">

            {/* Header */}

            <div className="details-header">

                <div className="product-avatar">

                    📦

                </div>

                <div>

                    <h2>

                        {product.product_name}

                    </h2>

                    <p>

                        SKU : {product.sku}

                    </p>

                    <p>

                        Barcode : {product.barcode || "-"}

                    </p>

                </div>

            </div>

            {/* Basic Information */}

            <div className="details-card">

                <h3>

                    Basic Information

                </h3>

                <div className="details-grid">

                    <Detail

                        label="Category"

                        value={product.category_name}

                    />

                    <Detail

                        label="Brand"

                        value={product.brand_name}

                    />

                    <Detail

                        label="Unit"

                        value={product.unit_name}

                    />

                    <Detail

                        label="Status"

                        value={product.status}

                    />

                </div>

            </div>

            {/* Pricing */}

            <div className="details-card">

                <h3>

                    Pricing

                </h3>

                <div className="details-grid">

                    <Detail

                        label="Purchase"

                        value={`₹ ${product.purchase_price}`}

                    />

                    <Detail

                        label="DTP"

                        value={`₹ ${product.dtp_price}`}

                    />

                    <Detail

                        label="Retail"

                        value={`₹ ${product.retail_price}`}

                    />

                    <Detail

                        label="MRP"

                        value={`₹ ${product.mrp}`}

                    />

                    <Detail

                        label="GST"

                        value={`${product.gst}%`}

                    />

                    <Detail

                        label="HSN"

                        value={product.hsn_code}

                    />

                </div>

            </div>

            {/* Inventory */}

            <div className="details-card">

                <h3>

                    Inventory

                </h3>

                <div className="details-grid">

                    <Detail

                        label="Warehouse"

                        value={product.warehouse_name}

                    />

                    <Detail

                        label="Current Stock"

                        value={product.current_stock}

                    />

                    <Detail

                        label="Minimum Stock"

                        value={product.minimum_stock}

                    />

                    <Detail

                        label="Opening Stock"

                        value={product.opening_stock}

                    />

                </div>

            </div>

            {/* Description */}

            <div className="details-card">

                <h3>

                    Description

                </h3>

                <p>

                    {product.description || "No Description"}

                </p>

            </div>

        </div>

    );

};

const Detail = ({ label, value }) => (

    <div className="detail-item">

        <span>

            {label}

        </span>

        <strong>

            {value || "-"}

        </strong>

    </div>

);

export default ProductDetails;