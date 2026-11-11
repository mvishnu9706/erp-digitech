import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

import logo from "/digitechlogo.png";

import { login } from "../../services/authService";
import {
    getRememberedSessions,
    removeRememberedSession,
} from "../../api/axios";
import { useAuth } from "../../context/AuthContext";


const Login = () => {

    const navigate = useNavigate();

    const {
        login: authLogin
    } = useAuth();


    // =====================================================
    // LOGIN STATE
    // =====================================================

    const [identifier, setIdentifier] = useState("");

    const [password, setPassword] = useState("");

    const [showPassword, setShowPassword] =
        useState(false);

    const [rememberMe, setRememberMe] =
        useState(true);

    const [rememberedSessions, setRememberedSessions] =
        useState([]);

    const [showRememberedAccounts, setShowRememberedAccounts] =
        useState(true);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");


    // =====================================================
    // LOAD REMEMBERED ACCOUNTS
    // =====================================================

    useEffect(() => {

        const sessions =
            getRememberedSessions();

        setRememberedSessions(
            sessions
        );

        // -------------------------------------------------
        // If there is exactly one remembered account,
        // pre-fill its login identifier.
        // -------------------------------------------------

        if (
            sessions.length === 1 &&
            sessions[0]?.user?.email
        ) {

            setIdentifier(
                sessions[0].user.email
            );
        }

    }, []);


    // =====================================================
    // CONTINUE REMEMBERED ACCOUNT
    // =====================================================

    const continueRememberedSession = async (
        rememberedSession
    ) => {

        if (
            !rememberedSession?.id ||
            !rememberedSession?.token
        ) {

            setError(
                "Remembered login session is unavailable."
            );

            return;
        }

        try {

            setLoading(true);
            setError("");

            // -------------------------------------------------
            // Activate this remembered session ONLY in the
            // current browser tab.
            // -------------------------------------------------

            sessionStorage.setItem(
                "active_session_id",
                rememberedSession.id
            );

            const loggedInUser =
                await authLogin(
                    rememberedSession.token,
                    true
                );

            redirectByRole(
                loggedInUser
            );

        } catch (err) {

            console.error(
                "REMEMBERED LOGIN ERROR:",
                err
            );

            // -------------------------------------------------
            // Remove a stale saved session if its JWT is
            // rejected by the backend.
            // -------------------------------------------------

            if (
                err?.response?.status === 401
            ) {

                removeRememberedSession(
                    rememberedSession.id
                );

                setRememberedSessions(
                    getRememberedSessions()
                );
            }

            setError(
                err?.response?.data?.detail ||
                err?.message ||
                "Unable to restore saved login"
            );

        } finally {

            setLoading(false);
        }

    };


    // =====================================================
    // FORGET REMEMBERED ACCOUNT
    // =====================================================

    const forgetRememberedAccount = (
        event,
        rememberedSession
    ) => {

        event.stopPropagation();

        removeRememberedSession(
            rememberedSession.id
        );

        const updatedSessions =
            getRememberedSessions();

        setRememberedSessions(
            updatedSessions
        );

        if (
            identifier ===
            rememberedSession?.user?.email
        ) {

            setIdentifier("");
        }
    };


    // =====================================================
    // ROLE BASED REDIRECT
    // =====================================================

    const redirectByRole = (user) => {

        const role =
            (user?.role || "")
                .toString()
                .trim()
                .toUpperCase();


        console.log(
            "LOGGED IN USER:",
            user
        );

        console.log(
            "USER ROLE:",
            role
        );


        // =================================================
        // SUPER ADMIN
        // =================================================

        if (role === "SUPER_ADMIN") {

            navigate(
                "/dashboard",
                {
                    replace: true
                }
            );

            return;
        }


        // =================================================
        // ADMIN
        // =================================================

        if (role === "ADMIN") {

            navigate(
                "/dashboard",
                {
                    replace: true
                }
            );

            return;
        }


        // =================================================
        // CUSTOMER
        // =================================================

        if (role === "CUSTOMER") {

            navigate(
                "/customer-portal",
                {
                    replace: true
                }
            );

            return;
        }


        // =================================================
        // ENGINEER
        // =================================================

        if (role === "ENGINEER") {

            navigate(
                "/engineer-portal",
                {
                    replace: true
                }
            );

            return;
        }


        // =================================================
        // SALES PERSON
        // =================================================

        if (role === "SALES_PERSON") {

            navigate(
                "/sales",
                {
                    replace: true
                }
            );

            return;
        }


        // =================================================
        // UNKNOWN ROLE
        // =================================================

        console.warn(
            "Unknown user role:",
            role
        );


        navigate(
            "/dashboard",
            {
                replace: true
            }
        );

    };


    // =====================================================
    // HANDLE LOGIN
    // =====================================================

    const handleLogin = async (e) => {

        e.preventDefault();


        // =================================================
        // VALIDATION
        // =================================================

        if (!identifier.trim()) {

            setError(
                "Please enter your email or mobile number"
            );

            return;
        }


        if (!password) {

            setError(
                "Please enter your password"
            );

            return;
        }


        try {

            setLoading(true);

            setError("");


            // =================================================
            // LOGIN API
            // =================================================

            const response = await login(
                identifier.trim(),
                password
            );


            console.log(
                "LOGIN RESPONSE:",
                response
            );


            // =================================================
            // CHECK TOKEN
            // =================================================

            if (!response?.access_token) {

                throw new Error(
                    "Access token was not returned"
                );

            }


            // =================================================
            // SAVE TOKEN + LOAD USER
            // =================================================
            //
            // authLogin should:
            //
            // 1. Create/activate this tab's session
            // 2. Save JWT according to Remember Me
            // 3. Call /auth/me
            // 4. Store current user
            // 5. Return current user
            //
            // =================================================

            const loggedInUser =
                await authLogin(
                    response.access_token,
                    rememberMe
                );


            console.log(
                "AUTHENTICATED USER:",
                loggedInUser
            );


            // =================================================
            // ROLE BASED REDIRECT
            // =================================================

            redirectByRole(
                loggedInUser
            );

        }
        catch (err) {

            console.error(
                "LOGIN ERROR:",
                err
            );


            setError(

                err?.response?.data?.detail ||

                err?.message ||

                "Invalid Email/Mobile or Password"

            );

        }
        finally {

            setLoading(false);

        }

    };


    // =====================================================
    // UI
    // =====================================================

    return (

        <div className="login-container">

            <div className="login-card">


                {/* =========================================
                    HEADER
                ========================================= */}

                <div className="login-header">

                    <img
                        src={logo}
                        alt="Digitech ERP"
                    />

                    <h2>
                        Digitech ERP
                    </h2>

                    <p>
                        Imaging Solutions
                    </p>

                </div>


                {/* =========================================
                    LOGIN FORM
                ========================================= */}

                {rememberedSessions.length > 0 && showRememberedAccounts && (
                    <div
                        style={{
                            margin: "0 0 18px",
                            padding: "12px",
                            border: "1px solid #dbe3ee",
                            borderRadius: "9px",
                            background: "#f8fafc",
                        }}
                    >
                        <div
                            style={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                gap: "10px",
                                marginBottom: "9px",
                            }}
                        >
                            <div>
                                <strong
                                    style={{
                                        display: "block",
                                        color: "#071a33",
                                        fontSize: "13px",
                                    }}
                                >
                                    Remembered Accounts
                                </strong>

                                <span
                                    style={{
                                        display: "block",
                                        marginTop: "2px",
                                        color: "#71839a",
                                        fontSize: "10px",
                                    }}
                                >
                                    Continue with a saved login on this device.
                                </span>
                            </div>

                            <button
                                type="button"
                                onClick={() =>
                                    setShowRememberedAccounts(false)
                                }
                                style={{
                                    border: 0,
                                    background: "transparent",
                                    color: "#64748b",
                                    fontSize: "11px",
                                    fontWeight: 700,
                                    cursor: "pointer",
                                }}
                            >
                                Hide
                            </button>
                        </div>

                        <div
                            style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: "7px",
                            }}
                        >
                            {rememberedSessions.map((session) => {

                                const savedUser =
                                    session?.user || {};

                                const displayName =
                                    savedUser.full_name ||
                                    savedUser.contact_person_name ||
                                    "Saved Account";

                                const displayRole =
                                    (
                                        savedUser.role ||
                                        "USER"
                                    )
                                        .toString()
                                        .replace(/_/g, " ");

                                const displayEmail =
                                    savedUser.email ||
                                    "Saved login";

                                return (
                                    <button
                                        key={session.id}
                                        type="button"
                                        onClick={() =>
                                            continueRememberedSession(
                                                session
                                            )
                                        }
                                        disabled={loading}
                                        style={{
                                            width: "100%",
                                            padding: "10px 11px",
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "space-between",
                                            gap: "10px",
                                            border: "1px solid #dbe3ee",
                                            borderRadius: "8px",
                                            background: "#ffffff",
                                            textAlign: "left",
                                            cursor: loading
                                                ? "not-allowed"
                                                : "pointer",
                                        }}
                                    >
                                        <span
                                            style={{
                                                minWidth: 0,
                                                display: "flex",
                                                flexDirection: "column",
                                            }}
                                        >
                                            <strong
                                                style={{
                                                    color: "#071a33",
                                                    fontSize: "12px",
                                                    whiteSpace: "nowrap",
                                                    overflow: "hidden",
                                                    textOverflow: "ellipsis",
                                                }}
                                            >
                                                {displayName}
                                            </strong>

                                            <span
                                                style={{
                                                    marginTop: "2px",
                                                    color: "#526b87",
                                                    fontSize: "10px",
                                                    whiteSpace: "nowrap",
                                                    overflow: "hidden",
                                                    textOverflow: "ellipsis",
                                                }}
                                            >
                                                {displayEmail} · {displayRole}
                                            </span>
                                        </span>

                                        <span
                                            style={{
                                                display: "inline-flex",
                                                alignItems: "center",
                                                gap: "7px",
                                                flexShrink: 0,
                                            }}
                                        >
                                            <span
                                                style={{
                                                    color: "#2563eb",
                                                    fontSize: "11px",
                                                    fontWeight: 800,
                                                }}
                                            >
                                                Continue
                                            </span>

                                            <span
                                                role="button"
                                                tabIndex={0}
                                                onClick={(event) =>
                                                    forgetRememberedAccount(
                                                        event,
                                                        session
                                                    )
                                                }
                                                onKeyDown={(event) => {
                                                    if (
                                                        event.key ===
                                                        "Enter"
                                                    ) {
                                                        forgetRememberedAccount(
                                                            event,
                                                            session
                                                        );
                                                    }
                                                }}
                                                style={{
                                                    color: "#94a3b8",
                                                    fontSize: "10px",
                                                    fontWeight: 700,
                                                    padding: "2px 4px",
                                                }}
                                                title="Forget this account"
                                            >
                                                Forget
                                            </span>
                                        </span>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                )}

                <form
                    onSubmit={handleLogin}
                >


                    {/* =====================================
                        EMAIL / MOBILE
                    ===================================== */}

                    <div className="form-group">

                        <label>
                            Email or Mobile Number
                        </label>

                        <input
                            type="text"
                            placeholder="Enter Email or Mobile Number"
                            value={identifier}
                            onChange={(e) =>
                                setIdentifier(
                                    e.target.value
                                )
                            }
                            autoComplete="username"
                            required
                        />

                    </div>


                    {/* =====================================
                        PASSWORD
                    ===================================== */}

                    <div className="form-group">

                        <label>
                            Password
                        </label>

                        <input
                            type={
                                showPassword
                                    ? "text"
                                    : "password"
                            }
                            placeholder="Enter Password"
                            value={password}
                            onChange={(e) =>
                                setPassword(
                                    e.target.value
                                )
                            }
                            autoComplete="current-password"
                            required
                        />

                    </div>


                    {/* =====================================
                        LOGIN OPTIONS
                    ===================================== */}

                    <div className="login-options">

                        <label>

                            <input
                                type="checkbox"
                                checked={rememberMe}
                                onChange={(e) =>
                                    setRememberMe(
                                        e.target.checked
                                    )
                                }
                            />

                            Remember Me

                        </label>


                        <button
                            type="button"
                            className="show-password"
                            onClick={() =>
                                setShowPassword(
                                    !showPassword
                                )
                            }
                        >

                            {
                                showPassword
                                    ? "Hide"
                                    : "Show"
                            }

                        </button>

                    </div>


                    {/* =====================================
                        ERROR
                    ===================================== */}

                    {error && (

                        <p className="login-error">

                            {error}

                        </p>

                    )}


                    {/* =====================================
                        LOGIN BUTTON
                    ===================================== */}

                    <button
                        type="submit"
                        className="login-btn"
                        disabled={loading}
                    >

                        {
                            loading
                                ? "Logging..."
                                : "Login"
                        }

                    </button>

                </form>

            </div>

        </div>

    );

};


export default Login;