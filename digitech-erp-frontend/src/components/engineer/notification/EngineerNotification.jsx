import React, {
    useEffect,
    useRef,
    useState,
} from "react";

import {
    Bell,
    Check,
    CheckCheck,
    X,
} from "lucide-react";

import useNotifications from "../../../hooks/useNotifications";


/* =====================================================
   ENGINEER NOTIFICATION
===================================================== */

const EngineerNotification = ({
    onServiceOpen,
}) => {
    const {
        notifications = [],
        unreadCount = 0,
        loading,
        refreshNotifications,
        markAsRead,
        markAllAsRead,
    } = useNotifications();

    const [
        notificationsOpen,
        setNotificationsOpen,
    ] = useState(false);

    const notificationRef = useRef(null);


    /* =================================================
       CLOSE WHEN CLICKING OUTSIDE
    ================================================= */

    useEffect(() => {
        const handleOutsideClick = (event) => {
            if (
                notificationRef.current &&
                !notificationRef.current.contains(
                    event.target
                )
            ) {
                setNotificationsOpen(false);
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
    }, []);


    /* =================================================
       OPEN NOTIFICATIONS
    ================================================= */

    const handleToggle = async () => {
        const nextState =
            !notificationsOpen;

        setNotificationsOpen(nextState);

        if (nextState) {
            try {
                await refreshNotifications();
            } catch (error) {
                console.error(
                    "Notification refresh error:",
                    error
                );
            }
        }
    };


    /* =================================================
       MARK ONE AS READ
    ================================================= */

    const handleNotificationClick = async (
        notification
    ) => {
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

        /* ---------------------------------------------
           Open related service
        --------------------------------------------- */

        if (
            notification?.reference_type ===
                "SERVICE_TICKET" &&
            notification?.reference_id
        ) {
            setNotificationsOpen(false);

            if (typeof onServiceOpen === "function") {
                onServiceOpen(
                    notification.reference_id
                );
            }
        }
    };


    /* =================================================
       MARK ALL READ
    ================================================= */

    const handleMarkAllRead = async () => {
        try {
            await markAllAsRead();
        } catch (error) {
            console.error(
                "Mark all notifications error:",
                error
            );
        }
    };


    /* =================================================
       FORMAT TIME
    ================================================= */

    const formatNotificationTime = (
        value
    ) => {
        if (!value) {
            return "";
        }

        const date = new Date(value);

        if (
            Number.isNaN(
                date.getTime()
            )
        ) {
            return "";
        }

        const now = new Date();

        const difference =
            now.getTime() -
            date.getTime();

        const minutes = Math.floor(
            difference / 60000
        );

        if (minutes < 1) {
            return "Just now";
        }

        if (minutes < 60) {
            return `${minutes}m ago`;
        }

        const hours = Math.floor(
            minutes / 60
        );

        if (hours < 24) {
            return `${hours}h ago`;
        }

        const days = Math.floor(
            hours / 24
        );

        if (days < 7) {
            return `${days}d ago`;
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


    /* =================================================
       RENDER
    ================================================= */

    return (
        <div
            className="engineer-notification-wrap"
            ref={notificationRef}
        >

            {/* =========================================
                NOTIFICATION BUTTON
            ========================================= */}

            <button
                type="button"
                className="engineer-notification-btn"
                onClick={handleToggle}
                aria-label="Notifications"
                aria-expanded={
                    notificationsOpen
                }
            >
                <Bell size={20} />

                {unreadCount > 0 && (
                    <span className="engineer-notification-badge">
                        {unreadCount > 99
                            ? "99+"
                            : unreadCount}
                    </span>
                )}
            </button>


            {/* =========================================
                DROPDOWN
            ========================================= */}

            {notificationsOpen && (
                <div
                    className="engineer-notification-dropdown"
                    role="dialog"
                    aria-label="Notifications"
                >

                    {/* =================================
                        HEADER
                    ================================= */}

                    <div className="engineer-notification-header">

                        <div>
                            <strong>
                                Notifications
                            </strong>

                            <span>
                                {unreadCount > 0
                                    ? `${unreadCount} unread`
                                    : "No unread notifications"}
                            </span>
                        </div>


                        <div className="engineer-notification-header-actions">

                            {unreadCount > 0 && (
                                <button
                                    type="button"
                                    className="engineer-mark-all-btn"
                                    onClick={
                                        handleMarkAllRead
                                    }
                                >
                                    <CheckCheck
                                        size={14}
                                    />

                                    Mark all read
                                </button>
                            )}

                            <button
                                type="button"
                                className="engineer-notification-close-btn"
                                onClick={() =>
                                    setNotificationsOpen(
                                        false
                                    )
                                }
                                aria-label="Close notifications"
                            >
                                <X size={16} />
                            </button>

                        </div>

                    </div>


                    {/* =================================
                        NOTIFICATION LIST
                    ================================= */}

                    <div className="engineer-notification-list">

                        {loading &&
                        notifications.length === 0 ? (
                            <div className="engineer-notification-empty">

                                <Bell
                                    size={24}
                                />

                                <p>
                                    Loading notifications...
                                </p>

                            </div>
                        ) : notifications.length === 0 ? (
                            <div className="engineer-notification-empty">

                                <Bell
                                    size={24}
                                />

                                <p>
                                    No notifications
                                </p>

                                <span>
                                    New service updates
                                    will appear here.
                                </span>

                            </div>
                        ) : (
                            notifications
                                .slice(0, 30)
                                .map(
                                    (
                                        notification
                                    ) => {

                                        const unread =
                                            !notification?.is_read;

                                        return (
                                            <div
                                                key={
                                                    notification.id
                                                }
                                                className={
                                                    unread
                                                        ? "engineer-notification-item unread"
                                                        : "engineer-notification-item"
                                                }
                                            >

                                                {/* =========================
                                                    ICON
                                                ========================= */}

                                                <button
                                                    type="button"
                                                    className="engineer-notification-main"
                                                    onClick={() =>
                                                        handleNotificationClick(
                                                            notification
                                                        )
                                                    }
                                                >

                                                    <span className="engineer-notification-icon">
                                                        <Bell
                                                            size={16}
                                                        />
                                                    </span>


                                                    <span className="engineer-notification-content">

                                                        <strong>
                                                            {
                                                                notification.title
                                                            }
                                                        </strong>

                                                        <span>
                                                            {
                                                                notification.message
                                                            }
                                                        </span>

                                                        <small>
                                                            {formatNotificationTime(
                                                                notification.created_at
                                                            )}
                                                        </small>

                                                    </span>

                                                </button>


                                                {/* =========================
                                                    MARK ONE READ
                                                ========================= */}

                                                {unread && (
                                                    <button
                                                        type="button"
                                                        className="engineer-notification-read-btn"
                                                        onClick={async (
                                                            event
                                                        ) => {
                                                            event.stopPropagation();

                                                            try {
                                                                await markAsRead(
                                                                    notification.id
                                                                );
                                                            } catch (
                                                                error
                                                            ) {
                                                                console.error(
                                                                    "Mark notification read error:",
                                                                    error
                                                                );
                                                            }
                                                        }}
                                                        title="Mark as read"
                                                        aria-label="Mark as read"
                                                    >
                                                        <Check
                                                            size={15}
                                                        />
                                                    </button>
                                                )}

                                            </div>
                                        );
                                    }
                                )
                        )}

                    </div>

                </div>
            )}

        </div>
    );
};


export default EngineerNotification;