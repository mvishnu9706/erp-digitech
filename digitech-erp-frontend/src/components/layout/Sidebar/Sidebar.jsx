import "./Sidebar.css";

import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";

import {
    LogOut,
    Headphones,
    User,
    Settings,
} from "lucide-react";

import sidebarMenu from "../../../constants/sidebarMenu";

import {
    useAuth,
} from "../../../context/AuthContext";


// =====================================================
// API BASE URL
// =====================================================

const API_BASE_URL =
    import.meta.env.VITE_API_URL ||
    "http://127.0.0.1:8000";


// =====================================================
// PAGE NAME NORMALIZER
// =====================================================

const normalizePageName = (value) => {

    if (!value) {
        return "";
    }

    return String(value)
        .trim()
        .toUpperCase()
        .replace(
            /[\/\-\s]+/g,
            "_"
        )
        .replace(
            /[^A-Z0-9_]/g,
            ""
        );
};


// =====================================================
// GET JWT TOKEN
// =====================================================

const getAuthToken = () => {

    const possibleKeys = [
        "access_token",
        "token",
        "jwt_token",
        "jwt",
        "authToken",
    ];

    for (const key of possibleKeys) {

        const value =
            localStorage.getItem(key);

        if (value) {
            return value;
        }
    }

    return null;
};


// =====================================================
// GET NORMALIZED ROLE
// =====================================================

const getUserRole = (user) => {

    return String(
        user?.role || ""
    )
        .trim()
        .toUpperCase()
        .replace(
            /\s+/g,
            "_"
        );
};


// =====================================================
// SIDEBAR
// =====================================================

const Sidebar = () => {

    const {
        user,
        logout,
    } = useAuth();


    // =================================================
    // USER ROLE
    // =================================================

    const role =
        getUserRole(user);


    // =================================================
    // PERMISSIONS
    // =================================================

    const [
        permissions,
        setPermissions,
    ] = useState([]);


    // =================================================
    // LOADING
    // =================================================

    const [
        permissionsLoading,
        setPermissionsLoading,
    ] = useState(true);


    // =================================================
    // CUSTOMER
    // =================================================
    //
    // CUSTOMER DOES NOT USE THE ERP SIDEBAR.
    //
    // Customer uses:
    //
    // /customer-portal
    //
    // Therefore:
    //
    // - Do NOT load ERP permissions
    // - Do NOT show Dashboard
    // - Do NOT show Inventory
    // - Do NOT show Sales
    // - Do NOT show Customers
    // - Do NOT show Settings
    //
    // =================================================

    const isCustomer =
        role === "CUSTOMER";


    // =================================================
    // LOAD ERP PERMISSIONS
    // =================================================

    useEffect(() => {

        let cancelled = false;


        const loadPermissions =
            async () => {

                // -------------------------------------
                // CUSTOMER
                // -------------------------------------

                if (isCustomer) {

                    if (!cancelled) {

                        setPermissions([]);

                        setPermissionsLoading(
                            false
                        );

                    }

                    return;
                }


                // -------------------------------------
                // NO USER
                // -------------------------------------

                if (!user) {

                    if (!cancelled) {

                        setPermissions([]);

                        setPermissionsLoading(
                            false
                        );

                    }

                    return;
                }


                // -------------------------------------
                // SUPER ADMIN
                // -------------------------------------

                if (
                    role === "SUPER_ADMIN"
                ) {

                    if (!cancelled) {

                        setPermissions(

                            sidebarMenu.map(
                                (menu) => ({

                                    page:
                                        normalizePageName(
                                            menu.permissionPage ||
                                            menu.permission ||
                                            menu.title
                                        ),

                                    can_access:
                                        true,

                                    can_view:
                                        true,

                                    can_create:
                                        true,

                                    can_update:
                                        true,

                                    can_delete:
                                        true,

                                })
                            )

                        );

                        setPermissionsLoading(
                            false
                        );

                    }

                    return;
                }


                // -------------------------------------
                // GET TOKEN
                // -------------------------------------

                const token =
                    getAuthToken();


                if (!token) {

                    if (!cancelled) {

                        setPermissions([]);

                        setPermissionsLoading(
                            false
                        );

                    }

                    return;
                }


                // -------------------------------------
                // START LOADING
                // -------------------------------------

                if (!cancelled) {

                    setPermissionsLoading(
                        true
                    );

                }


                try {

                    const response =
                        await fetch(
                            `${API_BASE_URL}/permissions/me`,
                            {
                                method: "GET",

                                headers: {

                                    Authorization:
                                        `Bearer ${token}`,

                                    Accept:
                                        "application/json",

                                },

                            }
                        );


                    // ---------------------------------
                    // ERROR
                    // ---------------------------------

                    if (!response.ok) {

                        const errorText =
                            await response.text();

                        console.error(
                            "Permission API error:",
                            response.status,
                            errorText
                        );

                        throw new Error(
                            `Permission request failed: ${response.status}`
                        );

                    }


                    // ---------------------------------
                    // RESPONSE
                    // ---------------------------------

                    const data =
                        await response.json();


                    const permissionList =
                        Array.isArray(
                            data?.permissions
                        )
                            ? data.permissions
                            : [];


                    if (!cancelled) {

                        setPermissions(
                            permissionList
                        );

                    }

                }

                catch (error) {

                    console.error(
                        "Failed to load permissions:",
                        error
                    );

                    if (!cancelled) {

                        setPermissions([]);

                    }

                }

                finally {

                    if (!cancelled) {

                        setPermissionsLoading(
                            false
                        );

                    }

                }

            };


        loadPermissions();


        return () => {

            cancelled = true;

        };

    }, [
        user,
        role,
        isCustomer,
    ]);


    // =================================================
    // PERMISSION MAP
    // =================================================

    const permissionMap = {};


    permissions.forEach(
        (permission) => {

            const page =
                normalizePageName(
                    permission?.page
                );


            if (!page) {
                return;
            }


            permissionMap[page] =
                permission;

        }
    );


    // =================================================
    // CUSTOMER SIDEBAR
    // =================================================
    //
    // CUSTOMER ONLY GETS CUSTOMER PORTAL.
    //
    // =================================================

    const customerMenu = [

        {
            id: "customer-portal",

            title: "Customer Portal",

            path: "/customer-portal",

            icon: Headphones,

        },

    ];


    // =================================================
    // ERP SIDEBAR
    // =================================================

    const visibleMenu =
        sidebarMenu.filter(
            (menu) => {

                // -------------------------------------
                // CUSTOMER
                // -------------------------------------
                //
                // This is a second safety layer.
                //
                // Customer must NEVER receive
                // ERP sidebar items.
                //
                // -------------------------------------

                if (isCustomer) {

                    return false;

                }


                // -------------------------------------
                // SUPER ADMIN
                // -------------------------------------

                if (
                    role === "SUPER_ADMIN"
                ) {

                    return true;

                }


                // -------------------------------------
                // PAGE
                // -------------------------------------

                const page =
                    normalizePageName(
                        menu.permissionPage ||
                        menu.permission ||
                        menu.title
                    );


                // -------------------------------------
                // PERMISSION
                // -------------------------------------

                const permission =
                    permissionMap[page];


                // -------------------------------------
                // NO PERMISSION
                // -------------------------------------

                if (!permission) {

                    return false;

                }


                // -------------------------------------
                // ACCESS
                // -------------------------------------

                const canAccess =
                    Boolean(
                        permission.can_access
                    );


                // -------------------------------------
                // VIEW
                // -------------------------------------

                const canView =
                    Boolean(
                        permission.can_view
                    );


                // -------------------------------------
                // BOTH REQUIRED
                // -------------------------------------

                return (
                    canAccess &&
                    canView
                );

            }
        );


    // =================================================
    // MENU TO DISPLAY
    // =================================================

    const menuToDisplay =
        isCustomer
            ? customerMenu
            : visibleMenu;


    // =================================================
    // LOGOUT
    // =================================================

    const handleLogout = () => {

        logout();

    };


    // =================================================
    // RENDER
    // =================================================

    return (

        <aside className="sidebar">

            {/* =================================================
                LOGO
            ================================================= */}

            <div className="sidebar-logo">

                <img
                    src="/digitechlogo.png"
                    alt="Digitech"
                />

                <div>

                    <h2>
                        Digitech
                    </h2>

                    <span>
                        Imaging Solutions
                    </span>

                </div>

            </div>


            {/* =================================================
                MENU
            ================================================= */}

            <nav className="sidebar-menu">

                {
                    permissionsLoading &&
                    !isCustomer
                        ? (

                            <div
                                style={{
                                    padding:
                                        "15px 20px",

                                    color:
                                        "#94a3b8",

                                    fontSize:
                                        "13px",
                                }}
                            >
                                Loading permissions...
                            </div>

                        )
                        : (

                            menuToDisplay.map(
                                (menu) => {

                                    const Icon =
                                        menu.icon ||
                                        User;


                                    return (

                                        <NavLink

                                            key={
                                                menu.id ||
                                                menu.path
                                            }

                                            to={
                                                menu.path
                                            }

                                            className={({
                                                isActive,
                                            }) =>
                                                isActive
                                                    ? "sidebar-link active"
                                                    : "sidebar-link"
                                            }

                                        >

                                            <Icon
                                                size={18}
                                            />

                                            <span>
                                                {
                                                    menu.title
                                                }
                                            </span>

                                        </NavLink>

                                    );

                                }
                            )

                        )
                }

            </nav>


            {/* =================================================
                CUSTOMER INFORMATION
            ================================================= */}

            {
                isCustomer && (

                    <div
                        style={{
                            padding:
                                "12px 16px",

                            margin:
                                "0 12px 12px",

                            borderRadius:
                                "10px",

                            background:
                                "rgba(255,255,255,0.04)",

                            color:
                                "#cbd5e1",

                            fontSize:
                                "12px",

                        }}
                    >

                        <div
                            style={{
                                display:
                                    "flex",

                                alignItems:
                                    "center",

                                gap:
                                    "8px",

                                marginBottom:
                                    "5px",
                            }}
                        >

                            <User
                                size={15}
                            />

                            <strong>
                                Customer Portal
                            </strong>

                        </div>

                        <div
                            style={{
                                color:
                                    "#94a3b8",
                            }}
                        >

                            Service & Machine
                            Management

                        </div>

                    </div>

                )
            }


            {/* =================================================
                USER FOOTER
            ================================================= */}

            <div className="sidebar-user">

                <div className="user-info">

                    <div className="avatar">

                        {
                            user?.full_name
                                ? user.full_name
                                    .charAt(0)
                                    .toUpperCase()
                                : "U"
                        }

                    </div>


                    <div>

                        <h4>

                            {
                                user?.full_name ||
                                "User"
                            }

                        </h4>


                        <p>

                            {
                                user?.role ||
                                "User"
                            }

                        </p>

                    </div>

                </div>


                {/* =================================================
                    LOGOUT
                ================================================= */}

                <button

                    type="button"

                    className="logout-btn"

                    onClick={
                        handleLogout
                    }

                >

                    <LogOut
                        size={18}
                    />

                    <span>
                        Logout
                    </span>

                </button>

            </div>

        </aside>

    );

};


export default Sidebar;