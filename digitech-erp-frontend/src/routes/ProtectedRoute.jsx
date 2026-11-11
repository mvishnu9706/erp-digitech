import {
    Navigate,
    Outlet,
    useLocation,
} from "react-router-dom";

import { useAuth } from "../context/AuthContext";


// =====================================================
// PROTECTED ROUTE
// =====================================================
//
// Usage:
//
// <ProtectedRoute>
//     <Dashboard />
// </ProtectedRoute>
//
// OR:
//
// <ProtectedRoute
//     allowedRoles={[
//         "ADMIN",
//         "SUPER_ADMIN"
//     ]}
// >
//     <Dashboard />
// </ProtectedRoute>
//
// =====================================================

const ProtectedRoute = ({
    children,
    allowedRoles = null,
}) => {

    const location = useLocation();

    const {
        user,
        loading,
        isAuthenticated,
    } = useAuth();


    // =====================================================
    // WAIT FOR AUTHENTICATION CHECK
    // =====================================================

    if (loading) {

        return (
            <div
                style={{
                    minHeight: "100vh",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "16px",
                }}
            >
                Loading...
            </div>
        );

    }


    // =====================================================
    // NOT LOGGED IN
    // =====================================================

    if (!isAuthenticated || !user) {

        return (
            <Navigate
                to="/login"
                replace
                state={{
                    from: location,
                }}
            />
        );

    }


    // =====================================================
    // GET USER ROLE
    // =====================================================

    const userRole =
        (user.role || "")
            .toString()
            .trim()
            .toUpperCase();


    // =====================================================
    // ROLE CHECK
    // =====================================================
    //
    // If allowedRoles is provided, user must have one
    // of those roles.
    //
    // =====================================================

    if (
        Array.isArray(allowedRoles) &&
        allowedRoles.length > 0
    ) {

        const normalizedRoles =
            allowedRoles.map(
                (role) =>
                    role
                        .toString()
                        .trim()
                        .toUpperCase()
            );


        // ---------------------------------------------
        // User does not have permission
        // ---------------------------------------------

        if (
            !normalizedRoles.includes(
                userRole
            )
        ) {

            // -----------------------------------------
            // CUSTOMER
            // -----------------------------------------

            if (
                userRole === "CUSTOMER"
            ) {

                return (
                    <Navigate
                        to="/customer-portal"
                        replace
                    />
                );

            }


            // -----------------------------------------
            // ENGINEER
            // -----------------------------------------

            if (
                userRole === "ENGINEER"
            ) {

                return (
                    <Navigate
                        to="/engineer-portal"
                        replace
                    />
                );

            }


            // -----------------------------------------
            // SALES PERSON
            // -----------------------------------------

            if (
                userRole === "SALES_PERSON"
            ) {

                return (
                    <Navigate
                        to="/sales"
                        replace
                    />
                );

            }


            // -----------------------------------------
            // ADMIN / SUPER ADMIN
            // -----------------------------------------

            return (
                <Navigate
                    to="/dashboard"
                    replace
                />
            );

        }

    }


    // =====================================================
    // ACCESS GRANTED
    // =====================================================

    if (children) {

        return children;

    }


    return (
        <Outlet />
    );

};


export default ProtectedRoute;