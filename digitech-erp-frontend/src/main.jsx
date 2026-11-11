import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";


// =====================================================
// Context Providers
// =====================================================

import { ThemeProvider } from "./context/ThemeContext";
import { ProductProvider } from "./context/ProductContext";
import { CategoryProvider } from "./context/CategoryContext";
import { BrandProvider } from "./context/BrandContext";
import { UnitProvider } from "./context/UnitContext";
import { CustomerProvider } from "./context/CustomerContext";
import { WarehouseProvider } from "./context/WarehouseContext";
import { InventoryProvider } from "./context/InventoryContext";
import { SupplierProvider } from "./context/SupplierContext";
import { PurchaseProvider } from "./context/PurchaseContext";
import { ServiceProvider } from "./context/ServiceContext";
import { AuthProvider } from "./context/AuthContext";


// =====================================================
// Application Initializer
// =====================================================

import AppInitializer from "./app/AppInitializer";


// =====================================================
// Toast Notifications
// =====================================================

import { ToastContainer } from "react-toastify";

import "react-toastify/dist/ReactToastify.css";


// =====================================================
// Global Styles
// =====================================================

import "./styles/global.css";
import "./styles/variables.css";


// =====================================================
// Application
// =====================================================

ReactDOM.createRoot(
    document.getElementById("root")
).render(

    <React.StrictMode>

        {/* =================================================
            Authentication
        ================================================= */}

        <AuthProvider>

            {/* =================================================
                Theme
            ================================================= */}

            <ThemeProvider>

                {/* =================================================
                    Category
                ================================================= */}

                <CategoryProvider>

                    {/* =================================================
                        Brand
                    ================================================= */}

                    <BrandProvider>

                        {/* =================================================
                            Unit
                        ================================================= */}

                        <UnitProvider>

                            {/* =================================================
                                Warehouse
                            ================================================= */}

                            <WarehouseProvider>

                                {/* =================================================
                                    Product
                                ================================================= */}

                                <ProductProvider>

                                    {/* =================================================
                                        Customer
                                    ================================================= */}

                                    <CustomerProvider>

                                        {/* =================================================
                                            Inventory
                                        ================================================= */}

                                        <InventoryProvider>

                                            {/* =================================================
                                                Supplier
                                            ================================================= */}

                                            <SupplierProvider>

                                                {/* =================================================
                                                    Service
                                                ================================================= */}

                                                <ServiceProvider>

                                                    {/* =================================================
                                                        Application Initializer
                                                    ================================================= */}

                                                    <AppInitializer>

                                                        {/* =================================================
                                                            Purchase
                                                        ================================================= */}

                                                        <PurchaseProvider>

                                                            <App />

                                                        </PurchaseProvider>


                                                        {/* =================================================
                                                            Toast Notifications
                                                        ================================================= */}

                                                        <ToastContainer
                                                            position="top-right"
                                                            autoClose={3000}
                                                            newestOnTop
                                                            closeOnClick
                                                            pauseOnHover
                                                        />

                                                    </AppInitializer>

                                                </ServiceProvider>

                                            </SupplierProvider>

                                        </InventoryProvider>

                                    </CustomerProvider>

                                </ProductProvider>

                            </WarehouseProvider>

                        </UnitProvider>

                    </BrandProvider>

                </CategoryProvider>

            </ThemeProvider>

        </AuthProvider>

    </React.StrictMode>

);