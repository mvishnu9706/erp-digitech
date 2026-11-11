import "./SearchableProduct.css";

import {
    Search,
    Package,
    ChevronDown,
    ChevronUp,
    Check,
} from "lucide-react";

import {
    useEffect,
    useRef,
    useState,
} from "react";

const SearchableProduct = ({
    products = [],
    value,
    onChange,
}) => {

    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState("");

    const containerRef = useRef(null);
    const searchInputRef = useRef(null);


    // =========================================
    // Selected Product
    // =========================================

    const selectedProduct = products.find(
        (product) =>
            String(product.id) === String(value)
    );


    // =========================================
    // Product Name
    // =========================================

    const getProductName = (product) => {

        return (
            product.product_name ||
            product.name ||
            product.title ||
            "Unnamed Product"
        );

    };


    // =========================================
    // SKU
    // =========================================

    const getSku = (product) => {

        return (
            product.sku ||
            product.product_code ||
            ""
        );

    };


    // =========================================
    // Model
    // =========================================

    const getModel = (product) => {

        return (
            product.model_no ||
            product.model_number ||
            product.model ||
            ""
        );

    };


    // =========================================
    // Search
    // =========================================

    const filteredProducts = products.filter(
        (product) => {

            const searchText =
                search.trim().toLowerCase();

            if (!searchText) {
                return true;
            }

            const productName =
                getProductName(product)
                    .toLowerCase();

            const sku =
                getSku(product)
                    .toLowerCase();

            const model =
                getModel(product)
                    .toLowerCase();

            return (
                productName.includes(searchText) ||
                sku.includes(searchText) ||
                model.includes(searchText)
            );

        }
    );


    // =========================================
    // Outside Click
    // =========================================

    useEffect(() => {

        const handleClickOutside = (event) => {

            if (
                containerRef.current &&
                !containerRef.current.contains(
                    event.target
                )
            ) {

                setOpen(false);
                setSearch("");

            }

        };


        document.addEventListener(
            "mousedown",
            handleClickOutside
        );


        return () => {

            document.removeEventListener(
                "mousedown",
                handleClickOutside
            );

        };

    }, []);


    // =========================================
    // Open
    // =========================================

    const handleOpen = () => {

        setOpen(
            (previous) => !previous
        );

        setTimeout(() => {

            searchInputRef.current?.focus();

        }, 50);

    };


    // =========================================
    // Select
    // =========================================

    const handleSelect = (product) => {

        onChange(product);

        setOpen(false);

        setSearch("");

    };


    return (

        <div
            className="searchable-product"
            ref={containerRef}
        >

            {/* =====================================
                Selected Product
            ===================================== */}

            <button
                type="button"
                className={`searchable-product-control ${
                    open ? "open" : ""
                }`}
                onClick={handleOpen}
            >

                <div className="product-control-left">

                    <Package
                        size={16}
                        className="product-control-icon"
                    />

                    <div className="product-control-text">

                        {selectedProduct ? (

                            <>
                                <span className="product-selected-name">

                                    {getProductName(
                                        selectedProduct
                                    )}

                                </span>

                                {getSku(
                                    selectedProduct
                                ) && (

                                    <span className="product-selected-sku">

                                        {getSku(
                                            selectedProduct
                                        )}

                                    </span>

                                )}

                            </>

                        ) : (

                            <span className="product-placeholder">

                                Select Product

                            </span>

                        )}

                    </div>

                </div>


                <div className="product-control-arrow">

                    {open ? (
                        <ChevronUp size={16} />
                    ) : (
                        <ChevronDown size={16} />
                    )}

                </div>

            </button>


            {/* =====================================
                Dropdown
            ===================================== */}

            {open && (

                <div className="searchable-product-dropdown">

                    {/* Search */}

                    <div className="product-search-box">

                        <Search
                            size={17}
                            className="product-search-icon"
                        />

                        <input
                            ref={searchInputRef}
                            type="text"
                            value={search}
                            placeholder="Search product, SKU or model..."
                            onChange={(e) =>
                                setSearch(
                                    e.target.value
                                )
                            }
                        />

                        {search && (

                            <button
                                type="button"
                                className="product-search-clear"
                                onClick={() =>
                                    setSearch("")
                                }
                            >
                                ×
                            </button>

                        )}

                    </div>


                    {/* Results Header */}

                    <div className="product-results-header">

                        <span>
                            Products
                        </span>

                        <span>
                            {filteredProducts.length}
                        </span>

                    </div>


                    {/* Products */}

                    <div className="product-results">

                        {filteredProducts.length > 0 ? (

                            filteredProducts.map(
                                (product) => {

                                    const isSelected =
                                        String(product.id) ===
                                        String(value);

                                    return (

                                        <button
                                            type="button"
                                            key={product.id}
                                            className={`product-option ${
                                                isSelected
                                                    ? "selected"
                                                    : ""
                                            }`}
                                            onClick={() =>
                                                handleSelect(
                                                    product
                                                )
                                            }
                                        >

                                            {/* Icon */}

                                            <div className="product-avatar">

                                                <Package
                                                    size={17}
                                                />

                                            </div>


                                            {/* Details */}

                                            <div className="product-option-content">

                                                <div className="product-option-top">

                                                    <span className="product-name">

                                                        {getProductName(
                                                            product
                                                        )}

                                                    </span>

                                                </div>


                                                <div className="product-option-details">

                                                    {getSku(
                                                        product
                                                    ) && (

                                                        <span>

                                                            SKU:{" "}
                                                            {
                                                                getSku(
                                                                    product
                                                                )
                                                            }

                                                        </span>

                                                    )}

                                                    {getModel(
                                                        product
                                                    ) && (

                                                        <span>

                                                            Model:{" "}
                                                            {
                                                                getModel(
                                                                    product
                                                                )
                                                            }

                                                        </span>

                                                    )}

                                                </div>

                                            </div>


                                            {/* Selected */}

                                            {isSelected && (

                                                <div className="product-selected-check">

                                                    <Check
                                                        size={16}
                                                    />

                                                </div>

                                            )}

                                        </button>

                                    );

                                }
                            )

                        ) : (

                            <div className="product-empty">

                                <div className="product-empty-icon">

                                    <Search
                                        size={22}
                                    />

                                </div>

                                <strong>
                                    No products found
                                </strong>

                                <span>
                                    Try searching by product
                                    name, SKU or model.
                                </span>

                            </div>

                        )}

                    </div>

                </div>

            )}

        </div>

    );

};

export default SearchableProduct;