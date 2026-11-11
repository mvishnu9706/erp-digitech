import {
    createContext,
    useContext,
    useState,
    useEffect,
    useCallback,
} from "react";

import api, {
    getAccessToken,
    getStoredUser,
    setAuthSession,
    updateAuthSessionUser,
    clearAuthSession,
    touchAuthSession,
} from "../api/axios";


const AuthContext = createContext(null);


// =====================================================
// ACCESS VALUE HELPER
// =====================================================

const getBooleanAccess = (value) => {

    if (value === true || value === 1) {
        return true;
    }

    if (typeof value === "string") {

        const normalized =
            value.trim().toLowerCase();

        return (
            normalized === "true" ||
            normalized === "1"
        );
    }

    return false;
};


// =====================================================
// NORMALIZE USER
// =====================================================
//
// Makes sure the Customer Portal always receives:
//
//     service_access: true / false
//     rental_access: true / false
//
// =====================================================

const normalizeUser = (user) => {

    if (!user) {
        return null;
    }

    return {
        ...user,

        service_access:
            getBooleanAccess(
                user.service_access
            ),

        rental_access:
            getBooleanAccess(
                user.rental_access
            ),
    };
};


// =====================================================
// AUTH PROVIDER
// =====================================================

export const AuthProvider = ({
    children,
}) => {

    const [user, setUser] =
        useState(() => {

            const storedUser =
                getStoredUser();

            return normalizeUser(
                storedUser
            );
        });


    const [loading, setLoading] =
        useState(true);


    // =====================================================
    // LOAD CURRENT USER
    // =====================================================

    const loadUser = useCallback(
        async () => {

            const token =
                getAccessToken();


            // -------------------------------------------------
            // No active session
            // -------------------------------------------------

            if (!token) {

                setUser(null);

                setLoading(false);

                return null;
            }


            try {

                setLoading(true);


                // -------------------------------------------------
                // Backend is the source of truth
                // -------------------------------------------------

                const response =
                    await api.get(
                        "/auth/me"
                    );


                const backendUser =
                    response.data;


                if (!backendUser?.id) {

                    throw new Error(
                        "Invalid authenticated user response"
                    );
                }


                // -------------------------------------------------
                // Normalize access flags
                // -------------------------------------------------

                const currentUser =
                    normalizeUser(
                        backendUser
                    );


                console.log(
                    "CURRENT USER:",
                    currentUser
                );


                console.log(
                    "SERVICE ACCESS:",
                    currentUser.service_access
                );


                console.log(
                    "RENTAL ACCESS:",
                    currentUser.rental_access
                );


                // -------------------------------------------------
                // Update React state
                // -------------------------------------------------

                setUser(
                    currentUser
                );


                // -------------------------------------------------
                // Update this tab's session
                // -------------------------------------------------

                updateAuthSessionUser(
                    currentUser
                );


                touchAuthSession();


                return currentUser;

            } catch (err) {

                console.error(
                    "LOAD USER ERROR:",
                    err
                );


                // -------------------------------------------------
                // Invalid / expired JWT
                // -------------------------------------------------

                if (
                    err?.response?.status ===
                    401
                ) {

                    clearAuthSession();

                    setUser(null);

                    return null;
                }


                // -------------------------------------------------
                // Server/network error
                //
                // Keep existing valid session.
                // -------------------------------------------------

                const storedUser =
                    getStoredUser();


                if (!storedUser) {

                    setUser(null);

                    return null;
                }


                const normalizedStoredUser =
                    normalizeUser(
                        storedUser
                    );


                setUser(
                    normalizedStoredUser
                );


                return normalizedStoredUser;

            } finally {

                setLoading(false);

            }

        },
        []
    );


    // =====================================================
    // LOGIN
    // =====================================================

    const login = async (
        token,
        rememberMe = true
    ) => {

        if (!token) {

            throw new Error(
                "Access token is required"
            );
        }


        // -------------------------------------------------
        // Create session for this browser tab
        // -------------------------------------------------

        setAuthSession(
            token,
            null,
            rememberMe
        );


        try {

            // -------------------------------------------------
            // Load user from backend
            // -------------------------------------------------

            const currentUser =
                await loadUser();


            if (!currentUser) {

                clearAuthSession();

                setUser(null);

                throw new Error(
                    "Unable to load authenticated user"
                );
            }


            return currentUser;

        } catch (error) {

            clearAuthSession();

            setUser(null);

            throw error;
        }
    };


    // =====================================================
    // LOGOUT
    // =====================================================

    const logout = async () => {

        try {

            await api.post(
                "/auth/logout"
            );

        } catch (error) {

            console.warn(
                "Logout API call failed:",
                error
            );
        }


        // -------------------------------------------------
        // Remove only current tab session
        // -------------------------------------------------

        clearAuthSession();


        setUser(null);


        window.location.href =
            "/login";
    };


    // =====================================================
    // INITIAL AUTH CHECK
    // =====================================================

    useEffect(
        () => {

            loadUser();

        },
        [loadUser]
    );


    // =====================================================
    // CONTEXT
    // =====================================================

    return (

        <AuthContext.Provider
            value={{

                user,

                loading,

                isAuthenticated:
                    !!user,

                login,

                logout,

                loadUser,

            }}
        >

            {children}

        </AuthContext.Provider>

    );
};


// =====================================================
// USE AUTH
// =====================================================

export const useAuth = () => {

    return useContext(
        AuthContext
    );
};


export default AuthContext;