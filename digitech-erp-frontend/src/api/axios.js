
import axios from "axios";

// =====================================================
// API INSTANCE
// =====================================================

const api = axios.create({
    baseURL: "http://localhost:8000",

    headers: {
        "Content-Type": "application/json",
    },
});

// =====================================================
// AUTH STORAGE KEYS
// =====================================================

const AUTH_SESSIONS_KEY = "auth_sessions";
const ACTIVE_SESSION_KEY = "active_session_id";
const SESSION_TOKEN_KEY = "session_token";
const SESSION_USER_KEY = "session_user";

// =====================================================
// READ REMEMBERED SESSIONS
// =====================================================

const readRememberedSessions = () => {

    const raw = localStorage.getItem(AUTH_SESSIONS_KEY);

    if (!raw) {
        return {};
    }

    try {

        const sessions = JSON.parse(raw);

        if (
            !sessions ||
            typeof sessions !== "object" ||
            Array.isArray(sessions)
        ) {
            return {};
        }

        return sessions;

    } catch (error) {

        console.error(
            "Invalid remembered auth sessions:",
            error
        );

        localStorage.removeItem(AUTH_SESSIONS_KEY);

        return {};
    }
};

// =====================================================
// WRITE REMEMBERED SESSIONS
// =====================================================

const writeRememberedSessions = (sessions) => {

    localStorage.setItem(
        AUTH_SESSIONS_KEY,
        JSON.stringify(sessions)
    );
};

// =====================================================
// GET ACTIVE TAB SESSION ID
// =====================================================

export const getActiveSessionId = () => {

    return sessionStorage.getItem(ACTIVE_SESSION_KEY);
};

// =====================================================
// CREATE UNIQUE SESSION ID
// =====================================================

const createSessionId = () => {

    if (
        typeof crypto !== "undefined" &&
        typeof crypto.randomUUID === "function"
    ) {
        return crypto.randomUUID();
    }

    return (
        "session_" +
        Date.now().toString(36) +
        "_" +
        Math.random().toString(36).slice(2)
    );
};

// =====================================================
// GET ACTIVE AUTH SESSION
// =====================================================

export const getActiveAuthSession = () => {

    const sessionId = getActiveSessionId();

    if (!sessionId) {
        return null;
    }

    // SESSION-ONLY LOGIN

    const sessionToken = sessionStorage.getItem(
        SESSION_TOKEN_KEY
    );

    if (sessionToken) {

        let user = null;

        const rawUser = sessionStorage.getItem(
            SESSION_USER_KEY
        );

        if (rawUser) {

            try {
                user = JSON.parse(rawUser);
            } catch (error) {

                console.error(
                    "Invalid session user:",
                    error
                );

                user = null;
            }
        }

        return {
            id: sessionId,
            token: sessionToken,
            user,
            persistent: false,
        };
    }

    // REMEMBERED LOGIN

    const sessions = readRememberedSessions();

    const session = sessions[sessionId];

    if (!session || !session.token) {
        return null;
    }

    return {
        id: sessionId,
        token: session.token,
        user: session.user || null,
        persistent: true,
    };
};

// =====================================================
// GET ACCESS TOKEN
// =====================================================

export const getAccessToken = () => {

    const session = getActiveAuthSession();

    return session?.token || null;
};

// =====================================================
// GET STORED USER
// =====================================================

export const getStoredUser = () => {

    const session = getActiveAuthSession();

    return session?.user || null;
};

// =====================================================
// GET ALL REMEMBERED SESSIONS
// =====================================================

export const getRememberedSessions = () => {

    const sessions = readRememberedSessions();

    return Object.entries(sessions)
        .map(([id, session]) => ({
            id,
            ...session,
        }))
        .filter((session) => Boolean(session?.token))
        .sort(
            (a, b) =>
                Number(b.lastUsedAt || 0) -
                Number(a.lastUsedAt || 0)
        );
};

// =====================================================
// SAVE AUTH SESSION
// =====================================================

export const setAuthSession = (
    token,
    user = null,
    rememberMe = true
) => {

    if (!token) {
        return null;
    }

    let sessionId = getActiveSessionId();

    if (!sessionId) {

        sessionId = createSessionId();

        sessionStorage.setItem(
            ACTIVE_SESSION_KEY,
            sessionId
        );
    }

    sessionStorage.removeItem(SESSION_TOKEN_KEY);
    sessionStorage.removeItem(SESSION_USER_KEY);

    // REMEMBER ME

    if (rememberMe) {

        const sessions = readRememberedSessions();

        sessions[sessionId] = {

            token,

            user: user || null,

            createdAt:
                sessions[sessionId]?.createdAt ||
                Date.now(),

            lastUsedAt: Date.now(),
        };

        writeRememberedSessions(sessions);

        return sessionId;
    }

    // SESSION-ONLY

    sessionStorage.setItem(
        SESSION_TOKEN_KEY,
        token
    );

    if (user) {

        sessionStorage.setItem(
            SESSION_USER_KEY,
            JSON.stringify(user)
        );
    }

    const sessions = readRememberedSessions();

    if (
        Object.prototype.hasOwnProperty.call(
            sessions,
            sessionId
        )
    ) {

        delete sessions[sessionId];

        writeRememberedSessions(sessions);
    }

    return sessionId;
};

// =====================================================
// UPDATE STORED USER
// =====================================================

export const updateAuthSessionUser = (user) => {

    const session = getActiveAuthSession();

    if (!session) {
        return null;
    }

    const sessionId = session.id;

    // PERSISTENT SESSION

    if (session.persistent) {

        const sessions = readRememberedSessions();

        if (sessions[sessionId]) {

            sessions[sessionId] = {

                ...sessions[sessionId],

                user: user || null,

                lastUsedAt: Date.now(),
            };

            writeRememberedSessions(sessions);
        }

        return sessionId;
    }

    // SESSION-ONLY

    if (user) {

        sessionStorage.setItem(
            SESSION_USER_KEY,
            JSON.stringify(user)
        );

    } else {

        sessionStorage.removeItem(SESSION_USER_KEY);
    }

    return sessionId;
};

// =====================================================
// TOUCH CURRENT SESSION
// =====================================================

export const touchAuthSession = () => {

    const session = getActiveAuthSession();

    if (!session || !session.persistent) {
        return;
    }

    const sessions = readRememberedSessions();

    if (sessions[session.id]) {

        sessions[session.id].lastUsedAt = Date.now();

        writeRememberedSessions(sessions);
    }
};

// =====================================================
// CLEAR CURRENT AUTH SESSION
// =====================================================

export const clearAuthSession = () => {

    const sessionId = getActiveSessionId();

    if (sessionId) {

        const sessions = readRememberedSessions();

        if (
            Object.prototype.hasOwnProperty.call(
                sessions,
                sessionId
            )
        ) {

            delete sessions[sessionId];

            writeRememberedSessions(sessions);
        }
    }

    sessionStorage.removeItem(SESSION_TOKEN_KEY);
    sessionStorage.removeItem(SESSION_USER_KEY);
    sessionStorage.removeItem(ACTIVE_SESSION_KEY);
};

// =====================================================
// REMOVE ONE REMEMBERED SESSION
// =====================================================

export const removeRememberedSession = (sessionId) => {

    if (!sessionId) {
        return;
    }

    const sessions = readRememberedSessions();

    if (
        Object.prototype.hasOwnProperty.call(
            sessions,
            sessionId
        )
    ) {

        delete sessions[sessionId];

        writeRememberedSessions(sessions);
    }

    if (getActiveSessionId() === sessionId) {

        sessionStorage.removeItem(ACTIVE_SESSION_KEY);
        sessionStorage.removeItem(SESSION_TOKEN_KEY);
        sessionStorage.removeItem(SESSION_USER_KEY);
    }
};

// =====================================================
// AXIOS REQUEST INTERCEPTOR
// =====================================================

api.interceptors.request.use(

    (config) => {

        const token = getAccessToken();

        config.headers = config.headers || {};

        // Remove any stale Authorization header first.
        delete config.headers.Authorization;

        if (token) {

            config.headers.Authorization =
                `Bearer ${token}`;
        }

        return config;
    },

    (error) => {
        return Promise.reject(error);
    }
);

// =====================================================
// AXIOS RESPONSE INTERCEPTOR
// =====================================================

api.interceptors.response.use(

    (response) => {
        return response;
    },

    (error) => {

        const status = error.response?.status;

        const requestUrl = error.config?.url || "";

        const requestHeaders =
            error.config?.headers || {};

        const hasAuthorization = Boolean(
            requestHeaders.Authorization ||
            requestHeaders.authorization
        );

        const isLoginRequest =
            requestUrl.includes("/auth/login");

        // Do not treat invalid login credentials
        // as an expired authenticated session.

        if (
            status === 401 &&
            !isLoginRequest &&
            hasAuthorization
        ) {

            console.warn(
                "Authenticated session is invalid or expired."
            );

            // Clear only the current tab session.
            clearAuthSession();

            // Redirect current tab only.
            if (
                window.location.pathname !== "/login"
            ) {

                window.location.replace("/login");
            }
        }

        return Promise.reject(error);
    }
);

export default api;
