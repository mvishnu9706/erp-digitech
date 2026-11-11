import DashboardLayout from "../../layouts/DashboardLayout";

import ProductToolbar from "../../components/product/ProductToolbar/ProductToolbar";
import ProductTable from "../../components/product/ProductTable/ProductTable";
import ProductDrawer from "../../components/product/ProductDrawer/ProductDrawer";
import ProductInventoryDrawer from "../../components/product/ProductInventoryDrawer/ProductInventoryDrawer";

import Pagination from "../../components/common/Pagination/Pagination";

import { useProducts } from "../../context/ProductContext";

import "./ProductList.css";

const ProductList = () => {

    const {
        page,
        totalPages,
        setPage,
        totalRecords,
        loading
    } = useProducts();

    return (

        <DashboardLayout>

            <div className="product-page">

                {/* ================= Header ================= */}

                <div className="page-header">

                    <div>

                        <h1>
                            Product Master
                        </h1>

                        <p>
                            Manage products, pricing, inventory and warehouse stock.
                        </p>

                    </div>

                </div>

                {/* ================= Toolbar ================= */}

                <ProductToolbar />

                {/* ================= Summary ================= */}

                <div className="product-summary">

                    <span>

                        Total Products :

                        <strong>

                            {" "}

                            {totalRecords}

                        </strong>

                    </span>

                    {
                        loading &&

                        <span className="loading-text">

                            Loading Products...

                        </span>
                    }

                </div>

                {/* ================= Table ================= */}

                <ProductTable />

                {/* ================= Pagination ================= */}

                {
                    totalPages > 1 &&

                    <Pagination

                        page={page}

                        totalPages={totalPages}

                        onPageChange={setPage}

                    />

                }

                {/* ================= Drawer ================= */}

                <ProductDrawer />
                
                <ProductInventoryDrawer />

            </div>

        </DashboardLayout>

    );

};

export default ProductList;