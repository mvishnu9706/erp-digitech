import {
    BrowserRouter,
    Routes,
    Route,
    Navigate,
} from "react-router-dom";


// =====================================================
// AUTH
// =====================================================

import Login from "../pages/auth/Login";

import EngineerPortal
    from "../pages/engineer/EngineerPortal";

import {
    useAuth,
} from "../context/AuthContext";


// =====================================================
// DASHBOARD
// =====================================================

import Dashboard
    from "../pages/dashboard/Dashboard";


// =====================================================
// CUSTOMER PORTAL
// =====================================================

import CustomerPortal
    from "../pages/CustomerPortal/CustomerPortal";


// =====================================================
// PRODUCTS
// =====================================================

import ProductList
    from "../pages/products/ProductList";


// =====================================================
// INVENTORY
// =====================================================

import InventoryPage
    from "../pages/inventory/InventoryPage";


// =====================================================
// SUPPLIERS
// =====================================================

import SupplierPage
    from "../pages/supplier/SupplierPage";


// =====================================================
// PURCHASE
// =====================================================

import PurchasePage
    from "../pages/purchase/PurchasePage";


// =====================================================
// SALES
// =====================================================

import SalesPage
    from "../pages/sales/SalesPage";


// =====================================================
// CUSTOMERS
// =====================================================

import CustomerPage
    from "../pages/customers/CustomerPage";


// =====================================================
// SERVICE
// =====================================================

import ServicePage
    from "../pages/service/ServicePage";

// =====================================================
// RENTAL / AMC
// =====================================================

import RentalPage
    from "../pages/rental/RentalPage";


// =====================================================
// SETTINGS
// =====================================================

import SettingRoles
    from "../pages/Settings/SettingRoles";


// =====================================================
// EXISTING ROUTE PROTECTION
// =====================================================

import ProtectedRoute
    from "./ProtectedRoute";

import PublicRoute
    from "./PublicRoute";


// =====================================================
// ROLE NORMALIZER
// =====================================================

const normalizeRole = (role) => {

    return String(role || "")
        .trim()
        .toUpperCase()
        .replace(
            /\s+/g,
            "_"
        );

};


// =====================================================
// CUSTOMER ONLY ROUTE
// =====================================================
//
// CUSTOMER can access:
//
// /customer-portal
//
// Nobody else is sent here.
//
// =====================================================

const CustomerOnlyRoute = ({
    children,
}) => {

    const {
        user,
        loading,
        isAuthenticated,
    } = useAuth();


    // ---------------------------------------------
    // Authentication Loading
    // ---------------------------------------------

    if (loading) {

        return null;

    }


    // ---------------------------------------------
    // Not Logged In
    // ---------------------------------------------

    if (
        !isAuthenticated ||
        !user
    ) {

        return (
            <Navigate
                to="/login"
                replace
            />
        );

    }


    // ---------------------------------------------
    // Role
    // ---------------------------------------------

    const role =
        normalizeRole(
            user.role
        );


    // ---------------------------------------------
    // CUSTOMER ONLY
    // ---------------------------------------------

    if (role !== "CUSTOMER") {

        return (
            <Navigate
                to="/dashboard"
                replace
            />
        );

    }


    return children;

};


// =====================================================
// ENGINEER ONLY ROUTE
// =====================================================
//
// Only ENGINEER users can access:
//
// /engineer-portal
//
// ADMIN / SUPER_ADMIN / CUSTOMER / SALES_PERSON
// cannot access the Engineer Portal.
//
// =====================================================

const EngineerOnlyRoute = ({
    children,
}) => {

    const {
        user,
        loading,
        isAuthenticated,
    } = useAuth();


    // ---------------------------------------------
    // Authentication Loading
    // ---------------------------------------------

    if (loading) {

        return null;

    }


    // ---------------------------------------------
    // Not Logged In
    // ---------------------------------------------

    if (
        !isAuthenticated ||
        !user
    ) {

        return (
            <Navigate
                to="/login"
                replace
            />
        );

    }


    // ---------------------------------------------
    // Normalize Role
    // ---------------------------------------------

    const role =
        normalizeRole(
            user.role
        );


    // ---------------------------------------------
    // ENGINEER ONLY
    // ---------------------------------------------

    if (role !== "ENGINEER") {

        return (
            <Navigate
                to="/dashboard"
                replace
            />
        );

    }


    return children;

};


// =====================================================
// ERP ROUTE
// =====================================================
//
// ADMIN / SUPER_ADMIN / ENGINEER / SALES_PERSON
//
// can enter the ERP.
//
// CUSTOMER CANNOT.
//
// IMPORTANT:
//
// This is separate from sidebar permissions.
//
// Even if CUSTOMER manually types:
//
// /dashboard
// /inventory
// /sales
// /customers
//
// they will be redirected to:
//
// /customer-portal
//
// =====================================================

const ERPRoute = ({
    children,
}) => {

    const {
        user,
        loading,
        isAuthenticated,
    } = useAuth();


    // ---------------------------------------------
    // Authentication Loading
    // ---------------------------------------------

    if (loading) {

        return null;

    }


    // ---------------------------------------------
    // Not Logged In
    // ---------------------------------------------

    if (
        !isAuthenticated ||
        !user
    ) {

        return (
            <Navigate
                to="/login"
                replace
            />
        );

    }


    // ---------------------------------------------
    // Role
    // ---------------------------------------------

    const role =
        normalizeRole(
            user.role
        );


    // ---------------------------------------------
    // CUSTOMER BLOCK
    // ---------------------------------------------

    if (role === "CUSTOMER") {

        return (
            <Navigate
                to="/customer-portal"
                replace
            />
        );

    }


    // ---------------------------------------------
    // ENGINEER BLOCK
    // ---------------------------------------------
    //
    // Engineers must use the Engineer Portal.
    // They cannot access normal ERP pages such as
    // /dashboard, /service, /customers, etc.
    //
    // ---------------------------------------------

    if (role === "ENGINEER") {

        return (
            <Navigate
                to="/engineer-portal"
                replace
            />
        );

    }


    // ---------------------------------------------
    // ERP USERS
    // ---------------------------------------------
    //
    // SUPER_ADMIN
    // ADMIN
    // ENGINEER
    // SALES_PERSON
    //
    // are allowed through this route.
    //
    // Individual page permissions are handled by
    // the sidebar / permission system.
    //
    // ---------------------------------------------

    return children;

};


// =====================================================
// DEFAULT ROUTE
// =====================================================
//
// We use the logged-in user's role instead of only
// checking whether a token exists.
//
// CUSTOMER
//      ↓
// /customer-portal
//
// ADMIN / ENGINEER / SALES
//      ↓
// /dashboard
//
// =====================================================

const DefaultRoute = () => {

    const {
        user,
        loading,
        isAuthenticated,
    } = useAuth();


    // ---------------------------------------------
    // Loading
    // ---------------------------------------------

    if (loading) {

        return null;

    }


    // ---------------------------------------------
    // Not Logged In
    // ---------------------------------------------

    if (
        !isAuthenticated ||
        !user
    ) {

        return (
            <Navigate
                to="/login"
                replace
            />
        );

    }


    // ---------------------------------------------
    // CUSTOMER
    // ---------------------------------------------

    const role =
        normalizeRole(
            user.role
        );


    if (role === "CUSTOMER") {

        return (
            <Navigate
                to="/customer-portal"
                replace
            />
        );

    }


    // ---------------------------------------------
    // ENGINEER
    // ---------------------------------------------

    if (role === "ENGINEER") {

        return (
            <Navigate
                to="/engineer-portal"
                replace
            />
        );

    }


    // ---------------------------------------------
    // ERP USER
    // ---------------------------------------------

    return (
        <Navigate
            to="/dashboard"
            replace
        />
    );

};


// =====================================================
// APP ROUTES
// =====================================================

const AppRoutes = () => {

    return (

        <BrowserRouter>

            <Routes>


                {/* =================================================
                    DEFAULT
                ================================================= */}

                <Route
                    path="/"
                    element={
                        <DefaultRoute />
                    }
                />


                {/* =================================================
                    PUBLIC
                ================================================= */}

                <Route
                    element={
                        <PublicRoute />
                    }
                >

                    <Route
                        path="/login"
                        element={
                            <Login />
                        }
                    />

                </Route>


                {/* =================================================
                    CUSTOMER PORTAL
                ================================================= */}

                <Route
                    path="/customer-portal"
                    element={

                        <CustomerOnlyRoute>

                            <CustomerPortal />

                        </CustomerOnlyRoute>

                    }
                />


                {/* =================================================
                    ENGINEER PORTAL
                ================================================= */}

                <Route
                    path="/engineer-portal"
                    element={

                        <EngineerOnlyRoute>

                            <EngineerPortal />

                        </EngineerOnlyRoute>

                    }
                />


                {/* =================================================
                    DASHBOARD
                ================================================= */}

                <Route
                    path="/dashboard"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    PRODUCTS
                ================================================= */}

                <Route
                    path="/products"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <ProductList />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    CATEGORIES
                ================================================= */}

                <Route
                    path="/categories"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    BRANDS
                ================================================= */}

                <Route
                    path="/brands"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    UNITS
                ================================================= */}

                <Route
                    path="/units"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    CUSTOMERS
                ================================================= */}

                <Route
                    path="/customers"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <CustomerPage />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    SUPPLIERS
                ================================================= */}

                <Route
                    path="/suppliers"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <SupplierPage />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    WAREHOUSES
                ================================================= */}

                <Route
                    path="/warehouses"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    INVENTORY
                ================================================= */}

                <Route
                    path="/inventory"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <InventoryPage />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    PURCHASE
                ================================================= */}

                <Route
                    path="/purchase"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <PurchasePage />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    PURCHASE INVOICES
                ================================================= */}

                <Route
                    path="/purchase-invoices"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    SALES
                ================================================= */}

                <Route
                    path="/sales"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <SalesPage />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    SALES ORDERS
                ================================================= */}

                <Route
                    path="/sales-orders"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <SalesPage />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    SALES INVOICES
                ================================================= */}

                <Route
                    path="/sales-invoices"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    MACHINES
                ================================================= */}

                <Route
                    path="/machines"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    SERVICE
                ================================================= */}

                <Route
                    path="/service"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <ServicePage />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    SERVICE TICKETS
                ================================================= */}

                <Route
                    path="/service-tickets"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    SERVICE VISITS
                ================================================= */}

                <Route
                    path="/service-visits"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    AMC
                ================================================= */}

                <Route
                    path="/amc"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <RentalPage />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    PREVENTIVE MAINTENANCE
                ================================================= */}

                <Route
                    path="/pm"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    RENTAL
                ================================================= */}

                <Route
                    path="/rental"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <RentalPage />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    FINANCE
                ================================================= */}

                <Route
                    path="/finance"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    JOURNAL
                ================================================= */}

                <Route
                    path="/journal"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    LEDGER
                ================================================= */}

                <Route
                    path="/ledger"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    TRIAL BALANCE
                ================================================= */}

                <Route
                    path="/trial-balance"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    PROFIT & LOSS
                ================================================= */}

                <Route
                    path="/profit-loss"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    BALANCE SHEET
                ================================================= */}

                <Route
                    path="/balance-sheet"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    CASH FLOW
                ================================================= */}

                <Route
                    path="/cash-flow"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    REPORTS
                ================================================= */}

                <Route
                    path="/reports"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <Dashboard />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    SETTINGS
                ================================================= */}

                <Route
                    path="/settings"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <SettingRoles />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    SETTINGS - ROLES
                ================================================= */}

                <Route
                    path="/settings/roles"
                    element={

                        <ERPRoute>

                            <ProtectedRoute>

                                <SettingRoles />

                            </ProtectedRoute>

                        </ERPRoute>

                    }
                />


                {/* =================================================
                    UNKNOWN ROUTE
                ================================================= */}

                <Route
                    path="*"
                    element={
                        <DefaultRoute />
                    }
                />


            </Routes>

        </BrowserRouter>

    );

};


export default AppRoutes;