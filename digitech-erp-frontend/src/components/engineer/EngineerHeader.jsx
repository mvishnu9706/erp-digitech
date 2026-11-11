import React, { useState } from "react";
import {
    Bell,
    CheckCheck,
    LogOut,
    UserRound,
    X,
} from "lucide-react";

import useNotifications from "../../hooks/useNotifications";

import "./EngineerHeader.css";

const formatNotificationTime = (value) => {
    if (!value) return "";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "";
    }

    const diff = Date.now() - date.getTime();
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) {
        return "Just now";
    }

    if (minutes < 60) {
        return `${minutes} min ago`;
    }

    const hours = Math.floor(minutes / 60);

    if (hours < 24) {
        return `${hours} hr ago`;
    }

    const days = Math.floor(hours / 24);

    if (days < 7) {
        return `${days} day${days > 1 ? "s" : ""} ago`;
    }

    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
};

const EngineerHeader = ({
    engineerName = "Service Engineer",
    logout,
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

    const [notificationOpen, setNotificationOpen] = useState(false);

    const handleNotificationToggle = async () => {
        const nextState = !notificationOpen;

        setNotificationOpen(nextState);

        if (nextState) {
            try {
                await refreshNotifications();
            } catch (error) {
                console.error(
                    "Failed to refresh notifications:",
                    error
                );
            }
        }
    };

    const handleNotificationClick = async (notification) => {
        try {
            if (!notification?.is_read) {
                await markAsRead(notification.id);
            }
        } catch (error) {
            console.error(
                "Failed to mark notification as read:",
                error
            );
        }

        if (notification?.reference_id && onServiceOpen) {
            setNotificationOpen(false);

            onServiceOpen(notification.reference_id);
        }
    };

    const handleSingleMarkAsRead = async (event, notificationId) => {
        event.stopPropagation();

        try {
            await markAsRead(notificationId);
        } catch (error) {
            console.error(
                "Failed to mark notification as read:",
                error
            );
        }
    };

    const handleMarkAllAsRead = async () => {
        try {
            await markAllAsRead();
        } catch (error) {
            console.error(
                "Failed to mark all notifications as read:",
                error
            );
        }
    };

    const handleLogout = () => {
        setNotificationOpen(false);

        if (typeof logout === "function") {
            logout();
        }
    };

    return (
        <header className="engineer-header">
            <div className="engineer-header-inner">
                {/* =====================================================
                    BRAND
                ===================================================== */}
                <div className="engineer-brand">
                    <img
                        src="/digitechlogo.png"
                        alt="Digitech"
                        className="engineer-logo"
                    />

                    <div className="engineer-brand-text">
                        <strong>Digitech</strong>
                        <span>Service Engineer Portal</span>
                    </div>
                </div>

                {/* =====================================================
                    RIGHT SIDE (Icons only on mobile)
                ===================================================== */}
                <div className="engineer-header-right">
                    {/* =================================================
                        NOTIFICATION
                    ================================================= */}
                    <div className="engineer-notification-container">
                        <button
                            type="button"
                            className={`engineer-notification-button ${
                                notificationOpen ? "active" : ""
                            }`}
                            onClick={handleNotificationToggle}
                            aria-label="Notifications"
                        >
                            <Bell size={20} />

                            {unreadCount > 0 && (
                                <span className="engineer-notification-count">
                                    {unreadCount > 99
                                        ? "99+"
                                        : unreadCount}
                                </span>
                            )}
                        </button>

                        {/* NOTIFICATION PANEL */}
                        {notificationOpen && (
                            <div className="engineer-notification-panel">
                                {/* HEADER */}
                                <div className="engineer-notification-panel-header">
                                    <div>
                                        <h3>Notifications</h3>
                                        <span>
                                            {unreadCount > 0
                                                ? `${unreadCount} unread`
                                                : "All caught up"}
                                        </span>
                                    </div>

                                    <button
                                        type="button"
                                        className="engineer-notification-close"
                                        onClick={() =>
                                            setNotificationOpen(false)
                                        }
                                        aria-label="Close notifications"
                                    >
                                        <X size={17} />
                                    </button>
                                </div>

                                {/* MARK ALL */}
                                {unreadCount > 0 && (
                                    <div className="engineer-notification-actions">
                                        <button
                                            type="button"
                                            onClick={handleMarkAllAsRead}
                                        >
                                            <CheckCheck size={14} />
                                            Mark all as read
                                        </button>
                                    </div>
                                )}

                                {/* NOTIFICATION LIST */}
                                <div className="engineer-notification-list">
                                    {loading && notifications.length === 0 ? (
                                        <div className="engineer-notification-empty">
                                            <Bell size={26} />
                                            <strong>Loading notifications...</strong>
                                        </div>
                                    ) : notifications.length === 0 ? (
                                        <div className="engineer-notification-empty">
                                            <Bell size={28} />
                                            <strong>No notifications</strong>
                                            <span>New service updates will appear here.</span>
                                        </div>
                                    ) : (
                                        notifications.slice(0, 30).map((notification) => {
                                            const unread = !notification?.is_read;

                                            return (
                                                <div
                                                    key={notification.id}
                                                    className={`engineer-notification-row ${
                                                        unread ? "unread" : "read"
                                                    }`}
                                                >
                                                    <button
                                                        type="button"
                                                        className="engineer-notification-content"
                                                        onClick={() =>
                                                            handleNotificationClick(
                                                                notification
                                                            )
                                                        }
                                                    >
                                                        <div className="engineer-notification-icon">
                                                            <Bell size={16} />
                                                        </div>

                                                        <div className="engineer-notification-text">
                                                            <strong>{notification?.title}</strong>
                                                            <p>{notification?.message}</p>
                                                            <small>
                                                                {formatNotificationTime(
                                                                    notification?.created_at
                                                                )}
                                                            </small>
                                                        </div>
                                                    </button>

                                                    {unread && (
                                                        <button
                                                            type="button"
                                                            className="engineer-single-read-button"
                                                            onClick={(event) =>
                                                                handleSingleMarkAsRead(
                                                                    event,
                                                                    notification.id
                                                                )
                                                            }
                                                        >
                                                            <CheckCheck size={14} />
                                                            <span>Mark as read</span>
                                                        </button>
                                                    )}
                                                </div>
                                            );
                                        })
                                    )}
                                </div>

                                {/* FOOTER */}
                                {notifications.length > 0 && (
                                    <div className="engineer-notification-footer">
                                        Showing latest{" "}
                                        {Math.min(notifications.length, 30)}{" "}
                                        notifications
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* =================================================
                        ENGINEER PROFILE
                    ================================================= */}
                    <div className="engineer-user-profile">
                        <div className="engineer-user-avatar">
                            <UserRound size={18} />
                        </div>
                        <div className="engineer-user-details">
                            <strong>{engineerName}</strong>
                            <span>SERVICE ENGINEER</span>
                        </div>
                    </div>

                    {/* =================================================
                        LOGOUT
                    ================================================= */}
                    <button
                        type="button"
                        className="engineer-logout-button"
                        onClick={handleLogout}
                        title="Logout"
                    >
                        <LogOut size={17} />
                        <span>Logout</span>
                    </button>
                </div>
            </div>
        </header>
    );
};

export default EngineerHeader;