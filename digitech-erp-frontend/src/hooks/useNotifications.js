import {
    useCallback,
    useEffect,
    useRef,
    useState,
} from "react";

import api from "../api/axios";


const POLL_INTERVAL = 10000;


// =====================================================
// USE NOTIFICATIONS
// =====================================================

const useNotifications = () => {

    // =================================================
    // STATE
    // =================================================

    const [
        notifications,
        setNotifications,
    ] = useState([]);

    const [
        unreadCount,
        setUnreadCount,
    ] = useState(0);

    const [
        loading,
        setLoading,
    ] = useState(false);

    const [
        error,
        setError,
    ] = useState("");

    const pollingRef =
        useRef(null);


    // =================================================
    // LOAD NOTIFICATION LIST
    // =================================================
    //
    // GET /notifications/
    //
    // =================================================

    const loadNotifications =
        useCallback(
            async () => {

                try {

                    const response =
                        await api.get(
                            "/notifications/"
                        );

                    const items =
                        Array.isArray(
                            response?.data?.notifications
                        )
                            ? response.data.notifications
                            : [];

                    setNotifications(
                        items
                    );

                    setError("");

                    return items;

                } catch (err) {

                    console.error(
                        "Load Notifications Error:",
                        err
                    );

                    const message =
                        err?.response?.data?.detail ||
                        err?.response?.data?.message ||
                        "Unable to load notifications.";

                    setError(
                        message
                    );

                    // If authentication has expired,
                    // don't keep stale notification data.
                    if (
                        err?.response?.status ===
                        401
                    ) {

                        setNotifications([]);

                        setUnreadCount(0);
                    }

                    return [];

                }

            },
            []
        );


    // =================================================
    // LOAD UNREAD COUNT
    // =================================================
    //
    // GET /notifications/unread-count
    //
    // =================================================

    const loadUnreadCount =
        useCallback(
            async () => {

                try {

                    const response =
                        await api.get(
                            "/notifications/unread-count"
                        );

                    const count =
                        Number(
                            response?.data?.count || 0
                        );

                    setUnreadCount(
                        count
                    );

                    return count;

                } catch (err) {

                    console.error(
                        "Load Notification Count Error:",
                        err
                    );

                    if (
                        err?.response?.status ===
                        401
                    ) {

                        setUnreadCount(
                            0
                        );
                    }

                    return 0;
                }

            },
            []
        );


    // =================================================
    // REFRESH NOTIFICATIONS
    // =================================================
    //
    // Loads:
    //
    // 1. Notification list
    // 2. Unread count
    //
    // =================================================

    const refreshNotifications =
        useCallback(
            async () => {

                setLoading(
                    true
                );

                setError("");

                try {

                    await Promise.all([
                        loadNotifications(),
                        loadUnreadCount(),
                    ]);

                } catch (err) {

                    console.error(
                        "Refresh Notifications Error:",
                        err
                    );

                } finally {

                    setLoading(
                        false
                    );
                }

            },
            [
                loadNotifications,
                loadUnreadCount,
            ]
        );


    // =================================================
    // MARK ONE NOTIFICATION AS READ
    // =================================================
    //
    // PUT /notifications/{id}/read
    //
    // =================================================

    const markAsRead =
        useCallback(
            async (
                notificationId
            ) => {

                if (
                    notificationId ===
                    undefined ||
                    notificationId ===
                    null
                ) {

                    return;
                }

                try {

                    await api.put(
                        `/notifications/${notificationId}/read`
                    );

                    // -----------------------------------------
                    // Update local notification state
                    // -----------------------------------------

                    setNotifications(
                        (current) =>
                            current.map(
                                (notification) =>
                                    Number(
                                        notification.id
                                    ) ===
                                    Number(
                                        notificationId
                                    )
                                        ? {
                                              ...notification,
                                              is_read: true,
                                          }
                                        : notification
                            )
                    );

                    // -----------------------------------------
                    // Update local unread count
                    // -----------------------------------------

                    setUnreadCount(
                        (current) =>
                            Math.max(
                                0,
                                current - 1
                            )
                    );

                    return true;

                } catch (err) {

                    console.error(
                        "Mark Notification Read Error:",
                        err
                    );

                    throw err;
                }

            },
            []
        );


    // =================================================
    // MARK ALL NOTIFICATIONS AS READ
    // =================================================
    //
    // PUT /notifications/read-all
    //
    // =================================================

    const markAllAsRead =
        useCallback(
            async () => {

                try {

                    await api.put(
                        "/notifications/read-all"
                    );

                    // -----------------------------------------
                    // Update local notification state
                    // -----------------------------------------

                    setNotifications(
                        (current) =>
                            current.map(
                                (notification) => ({
                                    ...notification,
                                    is_read: true,
                                })
                            )
                    );

                    // -----------------------------------------
                    // Reset local count
                    // -----------------------------------------

                    setUnreadCount(
                        0
                    );

                    return true;

                } catch (err) {

                    console.error(
                        "Mark All Notifications Read Error:",
                        err
                    );

                    throw err;
                }

            },
            []
        );


    // =================================================
    // INITIAL LOAD
    // =================================================

    useEffect(
        () => {

            refreshNotifications();

        },
        [
            refreshNotifications,
        ]
    );


    // =================================================
    // POLLING
    // =================================================
    //
    // Check every 10 seconds.
    //
    // This allows the admin notification badge to update
    // automatically after a customer creates a request.
    //
    // =================================================

    useEffect(
        () => {

            pollingRef.current =
                window.setInterval(
                    () => {

                        loadUnreadCount();

                    },
                    POLL_INTERVAL
                );


            return () => {

                if (
                    pollingRef.current !==
                    null
                ) {

                    window.clearInterval(
                        pollingRef.current
                    );

                    pollingRef.current =
                        null;
                }
            };

        },
        [
            loadUnreadCount,
        ]
    );


    // =================================================
    // RETURN
    // =================================================

    return {

        notifications,

        unreadCount,

        loading,

        error,

        loadNotifications,

        loadUnreadCount,

        refreshNotifications,

        markAsRead,

        markAllAsRead,

    };
};


export default useNotifications;