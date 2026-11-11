import "./Navbar.css";

import {
    Bell,
    Search,
    UserCircle,
    Moon,
    Sun,
    Check,
    ExternalLink,
} from "lucide-react";

import {
    useEffect,
    useRef,
    useState,
} from "react";

import { useTheme } from "../../../context/ThemeContext";
import useNotifications from "../../../hooks/useNotifications";


const formatNotificationTime = (value) => {

    if (!value) {
        return "";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "";
    }

    const now = new Date();

    const diffMs =
        now.getTime() -
        date.getTime();

    const diffMinutes =
        Math.floor(
            diffMs / 60000
        );

    if (diffMinutes < 1) {
        return "Just now";
    }

    if (diffMinutes < 60) {
        return `${diffMinutes}m ago`;
    }

    const diffHours =
        Math.floor(
            diffMinutes / 60
        );

    if (diffHours < 24) {
        return `${diffHours}h ago`;
    }

    const diffDays =
        Math.floor(
            diffHours / 24
        );

    if (diffDays < 7) {
        return `${diffDays}d ago`;
    }

    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric",
        }
    );
};


const Navbar = () => {

    const {
        theme,
        toggleTheme,
    } = useTheme();

    const {
        notifications,
        unreadCount,
        loading: notificationsLoading,
        refreshNotifications,
        markAsRead,
        markAllAsRead,
    } = useNotifications();

    const [
        notificationsOpen,
        setNotificationsOpen,
    ] = useState(false);

    const notificationRef =
        useRef(null);


    // =====================================================
    // CLOSE DROPDOWN WHEN CLICKING OUTSIDE
    // =====================================================

    useEffect(
        () => {

            const handleOutsideClick =
                (event) => {

                    if (
                        notificationRef.current &&
                        !notificationRef.current.contains(
                            event.target
                        )
                    ) {

                        setNotificationsOpen(
                            false
                        );
                    }
                };


            document.addEventListener(
                "mousedown",
                handleOutsideClick
            );


            return () => {

                document.removeEventListener(
                    "mousedown",
                    handleOutsideClick
                );
            };

        },
        []
    );


    // =====================================================
    // OPEN NOTIFICATIONS
    // =====================================================

    const handleOpenNotifications =
        async () => {

            const willOpen =
                !notificationsOpen;

            setNotificationsOpen(
                willOpen
            );

            if (willOpen) {

                await refreshNotifications();
            }
        };


    // =====================================================
    // HANDLE NOTIFICATION CLICK
    // =====================================================

    const handleNotificationClick =
        async (notification) => {

            try {

                if (!notification?.is_read) {

                    await markAsRead(
                        notification.id
                    );
                }

            } catch (error) {

                console.error(
                    "Notification read error:",
                    error
                );
            }


            // -------------------------------------------------
            // Open related service ticket.
            // -------------------------------------------------

            if (
                notification?.reference_type ===
                    "SERVICE_TICKET" &&
                notification?.reference_id
            ) {

                setNotificationsOpen(
                    false
                );

                window.location.href =
                    `/service?ticket=${notification.reference_id}`;

                return;
            }


            setNotificationsOpen(
                false
            );
        };


    return (

        <header className="navbar">

            <div className="navbar-search">

                <Search size={18} />

                <input
                    type="text"
                    placeholder="Search..."
                />

            </div>


            <div className="navbar-right">

                {/* =================================================
                    THEME
                ================================================= */}

                <button
                    className="theme-toggle"
                    onClick={toggleTheme}
                    aria-label="Toggle theme"
                    title={
                        theme === "dark"
                            ? "Switch to light mode"
                            : "Switch to dark mode"
                    }
                >

                    {theme === "dark"
                        ? <Sun size={18} />
                        : <Moon size={18} />
                    }

                </button>


                {/* =================================================
                    NOTIFICATIONS
                ================================================= */}

                <div
                    ref={notificationRef}
                    className="navbar-notification-wrapper"
                >

                    <button
                        className="navbar-icon-btn navbar-notification-btn"
                        aria-label="Notifications"
                        title="Notifications"
                        onClick={
                            handleOpenNotifications
                        }
                    >

                        <Bell size={22} />

                        {unreadCount > 0 && (

                            <span className="navbar-notification-badge">

                                {unreadCount > 99
                                    ? "99+"
                                    : unreadCount}

                            </span>

                        )}

                    </button>


                    {notificationsOpen && (

                        <div className="navbar-notification-dropdown">

                            <div className="navbar-notification-header">

                                <div>

                                    <h3>
                                        Notifications
                                    </h3>

                                    <span>
                                        {unreadCount > 0
                                            ? `${unreadCount} unread`
                                            : "No unread notifications"}
                                    </span>

                                </div>


                                <div className="navbar-notification-header-actions">

                                    <button
                                        type="button"
                                        onClick={
                                            refreshNotifications
                                        }
                                        disabled={
                                            notificationsLoading
                                        }
                                        title="Refresh notifications"
                                    >
                                        ↻
                                    </button>


                                    {unreadCount > 0 && (

                                        <button
                                            type="button"
                                            onClick={
                                                async () => {

                                                    try {

                                                        await markAllAsRead();

                                                    } catch (error) {

                                                        console.error(
                                                            "Mark all read error:",
                                                            error
                                                        );
                                                    }
                                                }
                                            }
                                        >
                                            Mark all read
                                        </button>

                                    )}

                                </div>

                            </div>


                            <div className="navbar-notification-list">

                                {notificationsLoading &&
                                notifications.length === 0 ? (

                                    <div className="navbar-notification-state">
                                        Loading notifications...
                                    </div>

                                ) : notifications.length === 0 ? (

                                    <div className="navbar-notification-state">

                                        <Bell size={25} />

                                        <span>
                                            No notifications
                                        </span>

                                    </div>

                                ) : (

                                    notifications.map(
                                        (notification) => (

                                            <div
                                                key={
                                                    notification.id
                                                }
                                                className={
                                                    notification.is_read
                                                        ? "navbar-notification-item"
                                                        : "navbar-notification-item unread"
                                                }
                                            >

                                                <div className="navbar-notification-item-icon">

                                                    {notification.is_read
                                                        ? (
                                                            <Check
                                                                size={15}
                                                            />
                                                        )
                                                        : (
                                                            <Bell
                                                                size={15}
                                                            />
                                                        )}

                                                </div>


                                                <div
                                                    className="navbar-notification-item-content"
                                                    role="button"
                                                    tabIndex={0}
                                                    onClick={() =>
                                                        handleNotificationClick(
                                                            notification
                                                        )
                                                    }
                                                    onKeyDown={(event) => {
                                                        if (
                                                            event.key === "Enter" ||
                                                            event.key === " "
                                                        ) {
                                                            event.preventDefault();

                                                            handleNotificationClick(
                                                                notification
                                                            );
                                                        }
                                                    }}
                                                >

                                                    <div className="navbar-notification-item-top">

                                                        <strong>
                                                            {
                                                                notification.title
                                                            }
                                                        </strong>

                                                        {!notification.is_read && (
                                                            <span className="navbar-notification-unread-dot" />
                                                        )}

                                                    </div>


                                                    <p>
                                                        {
                                                            notification.message
                                                        }
                                                    </p>


                                                    <small>
                                                        {
                                                            formatNotificationTime(
                                                                notification.created_at
                                                            )
                                                        }
                                                    </small>

                                                </div>


                                                <div className="navbar-notification-item-actions">

                                                    {!notification.is_read && (
                                                        <button
                                                            type="button"
                                                            className="navbar-notification-mark-read"
                                                            onClick={async (event) => {
                                                                event.stopPropagation();

                                                                try {
                                                                    await markAsRead(
                                                                        notification.id
                                                                    );
                                                                } catch (error) {
                                                                    console.error(
                                                                        "Mark notification as read error:",
                                                                        error
                                                                    );
                                                                }
                                                            }}
                                                            title="Mark as read"
                                                        >
                                                            Mark as read
                                                        </button>
                                                    )}

                                                    <button
                                                        type="button"
                                                        className="navbar-notification-open"
                                                        onClick={() =>
                                                            handleNotificationClick(
                                                                notification
                                                            )
                                                        }
                                                        title="Open service request"
                                                        aria-label="Open service request"
                                                    >
                                                        <ExternalLink
                                                            size={14}
                                                        />
                                                    </button>

                                                </div>

                                            </div>

                                        )
                                    )

                                )}

                            </div>


                            {notifications.length > 0 && (

                                <div className="navbar-notification-footer">

                                    <button
                                        type="button"
                                        onClick={() => {

                                            setNotificationsOpen(
                                                false
                                            );

                                            window.location.href =
                                                "/service";

                                        }}
                                    >
                                        View Service Management
                                    </button>

                                </div>

                            )}

                        </div>

                    )}

                </div>


                {/* =================================================
                    ACCOUNT
                ================================================= */}

                <button
                    className="navbar-icon-btn"
                    aria-label="User account"
                    title="Account"
                >

                    <UserCircle size={24} />

                </button>

            </div>

        </header>

    );
};


export default Navbar;