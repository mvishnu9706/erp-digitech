import React, {
    useEffect,
    useState,
} from "react";

import {
    ShieldCheck,
    Shield,
    Wrench,
    Users,
    BadgeDollarSign,
    UserPlus,
    Loader2,
    LockKeyhole,
    Eye,
    EyeOff,
    X,
    Pencil,
    Check,
    Square,
    Mail,
    Search,
    UserRoundCheck,
    Power,
    PowerOff,
    KeyRound,
} from "lucide-react";

import { toast } from "react-toastify";

import api from "../../../api/axios";

import "./RoleCards.css";


// =====================================================
// ROLE DEFINITIONS
// =====================================================

const ROLES = [
    {
        key: "SUPER_ADMIN",
        title: "Super Admin",
        description: "Full system access",
        icon: ShieldCheck,
        className: "super-admin",
    },

    {
        key: "ADMIN",
        title: "Admin",
        description: "Administrative access",
        icon: Shield,
        className: "admin",
    },

    {
        key: "ENGINEER",
        title: "Engineer",
        description: "Service and engineer access",
        icon: Wrench,
        className: "engineer",
    },

    {
        key: "SALES_PERSON",
        title: "Sales Person",
        description: "Sales operation access",
        icon: BadgeDollarSign,
        className: "sales-person",
    },
];


// =====================================================
// PERMISSION PAGES
// =====================================================

const PERMISSION_PAGES = [
    { key: "DASHBOARD", label: "Dashboard" },
    { key: "PRODUCT_MASTER", label: "Product Master" },
    { key: "CUSTOMERS", label: "Customers" },
    { key: "SUPPLIERS", label: "Suppliers" },
    { key: "PURCHASE", label: "Purchase" },
    { key: "SALES", label: "Sales" },
    { key: "INVENTORY", label: "Inventory" },
    { key: "SERVICE", label: "Service" },
    { key: "RENTAL_AMC", label: "Rental / AMC" },
    { key: "REPORTS", label: "Reports" },
    { key: "SETTINGS", label: "Settings" },
];

const PERMISSION_ACTIONS = [
    { key: "can_access", label: "Access" },
    { key: "can_view", label: "View" },
    { key: "can_create", label: "Create" },
    { key: "can_update", label: "Update" },
    { key: "can_delete", label: "Delete" },
];

/*
 * SUPER_ADMIN is intentionally excluded from the permission
 * management table. SUPER_ADMIN always has full system access
 * and does not need individual permission records.
 */
const PERMISSION_ROLES = ROLES.filter(
    (role) => role.key !== "SUPER_ADMIN"
);

// SUPER_ADMIN intentionally has no editable permission rows.
// The backend should treat SUPER_ADMIN as having full access
// to every page and every action by default.


// =====================================================
// NORMALIZE ROLE
// =====================================================

const normalizeRole = (role) => {
    if (!role) {
        return "";
    }

    return role
        .toString()
        .trim()
        .toUpperCase()
        .replace(/\s+/g, "_");
};


// =====================================================
// GET API ERROR MESSAGE
// =====================================================

const getApiErrorMessage = (error, fallback) => {
    const detail = error?.response?.data?.detail;

    if (Array.isArray(detail)) {
        return detail
            .map((item) => {
                if (typeof item === "string") {
                    return item;
                }

                return (
                    item?.msg ||
                    item?.message ||
                    "Invalid value"
                );
            })
            .join(", ");
    }

    if (typeof detail === "string") {
        return detail;
    }

    if (typeof error?.response?.data?.message === "string") {
        return error.response.data.message;
    }

    if (typeof error?.message === "string") {
        return error.message;
    }

    return fallback;
};


// =====================================================
// ROLE CARDS
// =====================================================

const RoleCards = ({
    onAddUser,
}) => {

    // =================================================
    // USERS
    // =================================================

    const [users, setUsers] = useState([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");


    // =================================================
    // SELECTED ROLE
    // =================================================

    // Role used for the user list.
    const [selectedRole, setSelectedRole] =
        useState("SUPER_ADMIN");

    // IMPORTANT:
    // This state belongs ONLY to the permission table dropdown.
    // Clicking a role card changes the user list only.
    // It MUST NOT change the role whose permissions are being edited.
    //
    // SUPER_ADMIN is intentionally excluded because it always has
    // full access and is not editable in this table.
    const [selectedPermissionRole, setSelectedPermissionRole] =
        useState("ADMIN");

    // =================================================
    // SETTINGS TABS
    // =================================================
    // Roles: manage/view users by role
    // Permission Control: manage page permissions by role
    const [activeSettingsTab, setActiveSettingsTab] =
        useState("roles");

    // =================================================
    // CUSTOMER PORTAL MANAGEMENT
    // =================================================

    const [portalCustomers, setPortalCustomers] = useState([]);
    const [portalLoading, setPortalLoading] = useState(false);
    const [portalError, setPortalError] = useState("");
    const [portalSearch, setPortalSearch] = useState("");
    const [portalModalOpen, setPortalModalOpen] = useState(false);
    const [portalEditMode, setPortalEditMode] = useState(false);
    const [selectedPortalCustomer, setSelectedPortalCustomer] = useState(null);

    const [portalEmail, setPortalEmail] = useState("");
    const [portalPassword, setPortalPassword] = useState("");
    const [portalConfirmPassword, setPortalConfirmPassword] = useState("");

    // Password confirmation status for Customer Portal access.
    const [portalPasswordMatch, setPortalPasswordMatch] = useState(null);

    const [portalActive, setPortalActive] = useState(true);

    // Customer Portal module access.
    // These values are persisted on the CUSTOMER user account.
    // Service and Rental access are independent.
    const [portalServiceAccess, setPortalServiceAccess] = useState(true);
    const [portalRentalAccess, setPortalRentalAccess] = useState(false);

    const [showPortalPassword, setShowPortalPassword] = useState(false);
    const [showPortalConfirmPassword, setShowPortalConfirmPassword] = useState(false);
    const [savingPortal, setSavingPortal] = useState(false);

    // =================================================
    // ROLE PERMISSIONS
    // =================================================

    const [permissions, setPermissions] = useState([]);

    const [permissionsLoading, setPermissionsLoading] =
        useState(false);

    const [permissionsError, setPermissionsError] =
        useState("");

    const [savingPermissionId, setSavingPermissionId] =
        useState(null);

    const [savingPermissionKey, setSavingPermissionKey] =
        useState(null);


    // =================================================
    // EDIT USER MODAL
    // =================================================

    const [editModalOpen, setEditModalOpen] = useState(false);

    const [selectedUser, setSelectedUser] = useState(null);


    // =================================================
    // EDIT USER FIELDS
    // =================================================

    const [editFullName, setEditFullName] = useState("");

    const [editEmail, setEditEmail] = useState("");

    const [editPhone, setEditPhone] = useState("");


    // =================================================
    // PASSWORD FIELDS
    // =================================================

    const [newPassword, setNewPassword] = useState("");

    const [confirmPassword, setConfirmPassword] = useState("");

    const [showPassword, setShowPassword] = useState(false);

    const [showConfirmPassword, setShowConfirmPassword] =
        useState(false);


    // =================================================
    // SAVING EDIT USER
    // =================================================

    const [savingUser, setSavingUser] = useState(false);


    // =================================================
    // ADD USER MODAL
    // =================================================

    const [addModalOpen, setAddModalOpen] = useState(false);

    const [addCompanyName, setAddCompanyName] = useState("");

    const [addContactPersonName, setAddContactPersonName] =
        useState("");

    const [addEmail, setAddEmail] = useState("");

    const [addPhone, setAddPhone] = useState("");

    const [addPassword, setAddPassword] = useState("");

    const [addConfirmPassword, setAddConfirmPassword] =
        useState("");

    const [showAddPassword, setShowAddPassword] =
        useState(false);

    const [showAddConfirmPassword, setShowAddConfirmPassword] =
        useState(false);

    const [savingAddUser, setSavingAddUser] = useState(false);


    // =================================================
    // LOAD USERS
    // =================================================

    const loadUsers = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await api.get("/users/");

            const data = response.data;

            if (!Array.isArray(data)) {
                throw new Error(
                    "Invalid users response from server"
                );
            }

            setUsers(data);
        }

        catch (err) {
            console.error(
                "Role Management - Load Users Error:",
                err
            );

            console.error(
                "Status:",
                err.response?.status
            );

            console.error(
                "Response:",
                err.response?.data
            );

            setUsers([]);

            setError(
                getApiErrorMessage(
                    err,
                    "Unable to load users"
                )
            );
        }

        finally {
            setLoading(false);
        }
    };


    // =================================================
    // LOAD USERS ON PAGE OPEN
    // =================================================

    useEffect(() => {
        loadUsers();
    }, []);

    // =================================================
    // LOAD CUSTOMER PORTAL DATA
    // =================================================

    const loadPortalCustomers = async () => {
        try {
            setPortalLoading(true);
            setPortalError("");

            // -------------------------------------------------
            // CUSTOMER PORTAL MANAGEMENT
            // -------------------------------------------------
            // Customers come from the existing customers table.
            // Machines come from the existing machines table.
            //
            // IMPORTANT:
            // We do NOT create another machine/customer structure
            // for the portal. Machines are linked to customers by:
            //
            //     machines.customer_id = customers.id
            //
            // The admin machine API supports filtering and returns
            // the machine records, including machine_name and
            // serial_number.
            // -------------------------------------------------

            const [customersResponse, usersResponse, machinesResponse] =
                await Promise.all([
                    api.get("/customers/", {
                        params: {
                            page: 1,
                            page_size: 100,
                        },
                    }),
                    api.get("/users/"),
                    api.get("/machines/", {
                        params: {
                            page: 1,
                            page_size: 100,
                        },
                    }),
                ]);

            const customers = Array.isArray(customersResponse.data)
                ? customersResponse.data
                : Array.isArray(customersResponse.data?.customers)
                    ? customersResponse.data.customers
                    : Array.isArray(customersResponse.data?.items)
                        ? customersResponse.data.items
                        : [];

            const users = Array.isArray(usersResponse.data)
                ? usersResponse.data
                : [];

            // -------------------------------------------------
            // GET MACHINES
            // -------------------------------------------------

            const machineData = machinesResponse.data;

            const machines = Array.isArray(machineData)
                ? machineData
                : Array.isArray(machineData?.machines)
                    ? machineData.machines
                    : Array.isArray(machineData?.items)
                        ? machineData.items
                        : [];

            // -------------------------------------------------
            // GROUP MACHINES BY CUSTOMER
            // -------------------------------------------------
            //
            // One customer can have many machines.
            // Do NOT use find() here because that would return
            // only one machine.
            // -------------------------------------------------

            const customerMachineMap = new Map();

            machines.forEach((machine) => {
                const customerId = machine?.customer_id;

                if (customerId == null) {
                    return;
                }

                const numericCustomerId = Number(customerId);

                if (!customerMachineMap.has(numericCustomerId)) {
                    customerMachineMap.set(numericCustomerId, []);
                }

                customerMachineMap
                    .get(numericCustomerId)
                    .push(machine);
            });

            // -------------------------------------------------
            // BUILD CUSTOMER PORTAL DATA
            // -------------------------------------------------
            //
            // Each customer now contains:
            //
            //     portal_user
            //     machines: [...]
            //
            // Therefore multiple machines belonging to the same
            // customer are available to the Customer Portal
            // Management UI.
            // -------------------------------------------------

            const customerUserMap = new Map();

            users.forEach((user) => {
                if (
                    String(user?.role || "").toUpperCase() === "CUSTOMER" &&
                    user?.customer_id != null
                ) {
                    customerUserMap.set(
                        Number(user.customer_id),
                        user
                    );
                }
            });

            const mergedCustomers = customers.map((customer) => ({
                ...customer,

                portal_user:
                    customerUserMap.get(Number(customer.id)) || null,

                machines:
                    customerMachineMap.get(Number(customer.id)) || [],
            }));

            setPortalCustomers(mergedCustomers);
        } catch (err) {
            console.error("Customer Portal - Load Error:", err);
            console.error("Status:", err.response?.status);
            console.error("Response:", err.response?.data);

            setPortalCustomers([]);

            setPortalError(
                getApiErrorMessage(
                    err,
                    "Unable to load customer portal data"
                )
            );
        } finally {
            setPortalLoading(false);
        }
    };

    useEffect(() => {
        if (activeSettingsTab === "customer-portal") {
            loadPortalCustomers();
        }
    }, [activeSettingsTab]);


    const openPortalAccessModal = (customer, editMode = false) => {
        setSelectedPortalCustomer(customer);
        setPortalEditMode(editMode);

        const account =
            customer?.portal_user ||
            customer?.portalUser ||
            customer?.portal_account ||
            customer?.portalAccount ||
            null;

        // Customer master email is the ONLY source of truth for
        // the customer portal login email.
        setPortalEmail(
            customer?.email || ""
        );
        setPortalPassword("");
        setPortalConfirmPassword("");
        setPortalPasswordMatch(null);
        setPortalActive(
            account?.is_active !== undefined
                ? Boolean(account.is_active)
                : customer?.portal_active !== undefined
                    ? Boolean(customer.portal_active)
                    : true
        );

        // Read module access when the backend already exposes these fields.
        // Existing portal users remain service-enabled by default so this
        // frontend change does not unexpectedly hide the existing service area.
        setPortalServiceAccess(
            account?.service_access !== undefined
                ? Boolean(account.service_access)
                : account?.service_portal_access !== undefined
                    ? Boolean(account.service_portal_access)
                    : customer?.service_access !== undefined
                        ? Boolean(customer.service_access)
                        : true
        );

        setPortalRentalAccess(
            account?.rental_access !== undefined
                ? Boolean(account.rental_access)
                : account?.rental_portal_access !== undefined
                    ? Boolean(account.rental_portal_access)
                    : customer?.rental_access !== undefined
                        ? Boolean(customer.rental_access)
                        : false
        );

        setShowPortalPassword(false);
        setShowPortalConfirmPassword(false);
        setPortalModalOpen(true);
    };

    const closePortalAccessModal = () => {
        if (savingPortal) return;

        setPortalModalOpen(false);
        setPortalEditMode(false);
        setSelectedPortalCustomer(null);
        setPortalEmail("");
        setPortalPassword("");
        setPortalConfirmPassword("");
        setPortalPasswordMatch(null);
        setPortalActive(true);
        setPortalServiceAccess(true);
        setPortalRentalAccess(false);
        setShowPortalPassword(false);
        setShowPortalConfirmPassword(false);
    };

    const handleSavePortalAccess = async (event) => {
        event.preventDefault();

        if (!selectedPortalCustomer?.id) {
            toast.error("Customer not selected");
            return;
        }

        const email = String(
            selectedPortalCustomer?.email || ""
        ).trim().toLowerCase();

        if (!email) {
            toast.error(
                "Customer email is required. Add an email in the Customers page first."
            );
            return;
        }

        // Keep the displayed form value aligned with the customer master.
        setPortalEmail(email);

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {
            toast.error("Please enter a valid email address");
            return;
        }

        if (!portalEditMode && !portalPassword) {
            toast.error("Password is required");
            return;
        }

        if (portalPassword || portalConfirmPassword) {
            if (portalPassword.length < 6) {
                setPortalPasswordMatch(false);
                toast.error("Password must be at least 6 characters");
                return;
            }

            if (portalPassword !== portalConfirmPassword) {
                setPortalPasswordMatch(false);
                toast.error("Passwords do not match");
                return;
            }

            setPortalPasswordMatch(true);
        } else {
            // In edit mode, blank password fields mean keep the
            // existing password, so no match indicator is needed.
            setPortalPasswordMatch(null);
        }

        try {
            setSavingPortal(true);

            // CUSTOMER PORTAL LOGIN USES THE EXISTING USERS TABLE.
            //
            // Create:
            //   POST /users/with-role
            //
            // Edit:
            //   PUT /users/{user_id}
            //
            // The user is linked to the selected customer with:
            //   role = CUSTOMER
            //   customer_id = selectedPortalCustomer.id

            const customerName =
                selectedPortalCustomer?.customer_name ||
                selectedPortalCustomer?.company_name ||
                selectedPortalCustomer?.name ||
                "Customer";

            const customerPhone =
                selectedPortalCustomer?.phone ||
                selectedPortalCustomer?.mobile ||
                selectedPortalCustomer?.mobile_number ||
                "";

            if (portalEditMode) {
                const portalUser =
                    selectedPortalCustomer?.portal_user ||
                    selectedPortalCustomer?.portalUser ||
                    null;

                const userId =
                    portalUser?.id ||
                    selectedPortalCustomer?.portal_user_id ||
                    selectedPortalCustomer?.user_id;

                if (!userId) {
                    throw new Error(
                        "Customer portal user ID is missing. Refresh the Customer Portal list and try again."
                    );
                }

                const updatePayload = {
                    full_name: customerName,
                    email,
                    phone: customerPhone || null,
                    role: "CUSTOMER",
                    customer_id: selectedPortalCustomer.id,
                    is_active: portalActive,

                    // Customer Portal module access.
                    // Service and Rental are independent permissions.
                    service_access: portalServiceAccess,
                    rental_access: portalRentalAccess,

                    // Save the separate portal password only
                    // when the admin entered a new password.
                    ...(portalPassword
                        ? {
                              portal_password: portalPassword,
                          }
                        : {}),
                };

                await api.put(
                    `/users/${userId}`,
                    updatePayload
                );

                if (portalPassword) {
                    await api.put(
                        `/users/${userId}/password`,
                        {
                            new_password: portalPassword,
                            confirm_password: portalConfirmPassword,
                        }
                    );
                }

                toast.success(
                    "Customer portal access updated successfully"
                );
            } else {
                const createPayload = {
                    full_name: customerName,
                    contact_person_name:
                        selectedPortalCustomer?.contact_person ||
                        customerName,
                    email,
                    phone: customerPhone || null,

                    // Authentication password.
                    password: portalPassword,

                    // Separate portal password value requested
                    // for Customer Portal management.
                    portal_password: portalPassword,

                    role: "CUSTOMER",
                    customer_id: selectedPortalCustomer.id,

                    // Customer Portal module access.
                    // Service and Rental are independent permissions.
                    service_access: portalServiceAccess,
                    rental_access: portalRentalAccess,
                };

                await api.post(
                    "/users/with-role",
                    createPayload
                );

                toast.success(
                    "Customer portal access created successfully"
                );
            }

            await loadPortalCustomers();
            closePortalAccessModal();
        } catch (err) {
            console.error("Customer Portal - Save Error:", err);
            toast.error(
                getApiErrorMessage(
                    err,
                    portalEditMode
                        ? "Failed to update customer portal access"
                        : "Failed to create customer portal access"
                )
            );
        } finally {
            setSavingPortal(false);
        }
    };

    // =================================================
    // CUSTOMER PORTAL TABLE FILTER
    // =================================================
    //
    // Default:
    //   Show ONLY customers who already have portal access.
    //
    // When searching:
    //   Search across ALL existing customers so the admin
    //   can find a customer who does not have access yet
    //   and give them access.
    //
    // =================================================

    const normalizedPortalSearch = portalSearch.trim().toLowerCase();

    const getPortalAccount = (customer) =>
        customer?.portal_user ||
        customer?.portalUser ||
        customer?.portal_account ||
        customer?.portalAccount ||
        null;

    const customerHasPortalAccess = (customer) => {
        const account = getPortalAccount(customer);

        return Boolean(
            account ||
            customer?.portal_access ||
            customer?.portal_access_enabled ||
            customer?.has_portal_access
        );
    };


    // Customer Portal module access display.
    // Values come from the CUSTOMER portal user's saved access flags.
    const getPortalModuleAccess = (customer) => {
        const account = getPortalAccount(customer);

        const serviceAccess =
            account?.service_access !== undefined
                ? Boolean(account.service_access)
                : account?.service_portal_access !== undefined
                    ? Boolean(account.service_portal_access)
                    : customer?.service_access !== undefined
                        ? Boolean(customer.service_access)
                        : true;

        const rentalAccess =
            account?.rental_access !== undefined
                ? Boolean(account.rental_access)
                : account?.rental_portal_access !== undefined
                    ? Boolean(account.rental_portal_access)
                    : customer?.rental_access !== undefined
                        ? Boolean(customer.rental_access)
                        : false;

        return { serviceAccess, rentalAccess };
    };

    const getPortalAccessLabel = (customer) => {
        const { serviceAccess, rentalAccess } = getPortalModuleAccess(customer);

        if (rentalAccess && serviceAccess) return "Rental + Service";
        if (rentalAccess) return "Rental";
        if (serviceAccess) return "Service";
        return "—";
    };

    const filteredPortalCustomers = portalCustomers.filter((customer) => {
        const account = getPortalAccount(customer);

        const searchable = [
            customer?.customer_name,
            customer?.name,
            customer?.company_name,
            customer?.contact_person,
            customer?.customer_code,
            customer?.code,
            customer?.phone,
            customer?.mobile,
            customer?.mobile_number,
            customer?.email,
            account?.email,
            customer?.portal_email,

            // Search by machine name and serial number as well.
            ...(Array.isArray(customer?.machines)
                ? customer.machines.flatMap((machine) => [
                      machine?.machine_name,
                      machine?.serial_number,
                      machine?.machine_number,
                  ])
                : []),
        ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();

        // No search:
        // Only show customers who already have portal access.
        if (!normalizedPortalSearch) {
            return customerHasPortalAccess(customer);
        }

        // Search:
        // Search ALL customers, including customers without access.
        return searchable.includes(normalizedPortalSearch);
    });


    // =================================================
    // LOAD ROLE PERMISSIONS
    // =================================================

    const loadPermissions = async (role) => {
        if (!role) {
            setPermissions([]);
            setPermissionsError("");
            return;
        }

        // SUPER_ADMIN always has full access and is not stored
        // in the editable role permission table.
        if (role === "SUPER_ADMIN") {
            setPermissions([]);
            setPermissionsError("");
            return;
        }

        try {
            setPermissionsLoading(true);
            setPermissionsError("");

            const response = await api.get(
                `/permissions/${role}`
            );

            const data = response.data;

            const permissionRows = Array.isArray(
                data?.permissions
            )
                ? data.permissions
                : [];

            setPermissions(permissionRows);
        } catch (err) {
            console.error(
                "Role Management - Load Permissions Error:",
                err
            );

            setPermissions([]);

            setPermissionsError(
                getApiErrorMessage(
                    err,
                    "Unable to load role permissions"
                )
            );
        } finally {
            setPermissionsLoading(false);
        }
    };


    // =================================================
    // LOAD PERMISSIONS WHEN ROLE CHANGES
    // =================================================

    useEffect(() => {
        loadPermissions(selectedPermissionRole);
    }, [selectedPermissionRole]);


    // =================================================
    // GET PERMISSION FOR PAGE
    // =================================================

    const getPermissionForPage = (pageKey) => {
        return permissions.find(
            (permission) =>
                permission.page === pageKey
        );
    };


    // =================================================
    // CREATE / UPDATE PERMISSION
    // =================================================
    //
    // If the permission row already exists:
    //     PUT /permissions/{permission_id}
    //
    // If the row does not exist yet:
    //     POST /permissions/
    //
    // This is important because a newly-created
    // role_permissions table may initially be empty.
    //
    // =================================================

    const handlePermissionChange = async (
        permission,
        pageKey,
        action
    ) => {
        if (selectedPermissionRole === "SUPER_ADMIN") {
            toast.info("Super Admin already has full access.");
            return;
        }

        const permissionKey =
            `${selectedPermissionRole}:${pageKey}`;

        // -------------------------------------------------
        // CREATE MISSING PERMISSION RECORD
        // -------------------------------------------------

        if (!permission?.id) {
            try {
                setSavingPermissionKey(permissionKey);

                const payload = {
                    role: selectedPermissionRole,
                    page: pageKey,
                    can_access: false,
                    can_view: false,
                    can_create: false,
                    can_update: false,
                    can_delete: false,
                };

                // The clicked checkbox becomes TRUE.
                payload[action] = true;

                const response = await api.post(
                    "/permissions/",
                    payload
                );

                const createdPermission =
                    response.data;

                setPermissions((currentPermissions) => {
                    const alreadyExists =
                        currentPermissions.some(
                            (item) =>
                                item.id ===
                                createdPermission.id
                        );

                    if (alreadyExists) {
                        return currentPermissions;
                    }

                    return [
                        ...currentPermissions,
                        createdPermission,
                    ];
                });

                toast.success(
                    `${pageKey.replaceAll("_", " ")} ${
                        action.replace("can_", "")
                    } permission enabled`
                );
            } catch (err) {
                console.error(
                    "Create Permission Error:",
                    err
                );

                toast.error(
                    getApiErrorMessage(
                        err,
                        "Failed to create permission"
                    )
                );
            } finally {
                setSavingPermissionKey(null);
            }

            return;
        }

        // -------------------------------------------------
        // UPDATE EXISTING PERMISSION
        // -------------------------------------------------

        const currentValue = Boolean(
            permission[action]
        );

        const updatedValue = !currentValue;

        // Page Access controls whether the role can enter/use that page.
        // If Access is switched OFF, clear all page actions as well.
        const updatePayload =
            action === "can_access" && updatedValue === false
                ? {
                      can_access: false,
                      can_view: false,
                      can_create: false,
                      can_update: false,
                      can_delete: false,
                  }
                : {
                      [action]: updatedValue,
                  };

        // -------------------------------------------------
        // Keep a snapshot so a failed request can be reverted.
        // -------------------------------------------------

        const previousPermission = { ...permission };

        // -------------------------------------------------
        // Optimistic UI update
        // -------------------------------------------------

        setPermissions((currentPermissions) =>
            currentPermissions.map((item) =>
                item.id === permission.id
                    ? {
                          ...item,
                          ...updatePayload,
                      }
                    : item
            )
        );

        try {
            setSavingPermissionId(permission.id);

            const response = await api.put(
                `/permissions/${permission.id}`,
                updatePayload
            );

            const updatedPermission =
                response.data;

            setPermissions((currentPermissions) =>
                currentPermissions.map((item) =>
                    item.id === permission.id
                        ? updatedPermission
                        : item
                )
            );

            toast.success(
                action === "can_access" && !updatedValue
                    ? `${permission.page.replaceAll("_", " ")} access disabled`
                    : `${permission.page.replaceAll("_", " ")} ${
                          action.replace("can_", "")
                      } permission ${
                          updatedValue
                              ? "enabled"
                              : "disabled"
                      }`
            );
        } catch (err) {
            console.error(
                "Update Permission Error:",
                err
            );

            // -------------------------------------------------
            // Revert optimistic update
            // -------------------------------------------------

            setPermissions((currentPermissions) =>
                currentPermissions.map((item) =>
                    item.id === permission.id
                        ? previousPermission
                        : item
                )
            );

            toast.error(
                getApiErrorMessage(
                    err,
                    "Failed to update permission"
                )
            );
        } finally {
            setSavingPermissionId(null);
        }
    };


    // =================================================
    // SELECTED ROLE DATA
    // =================================================

    const selectedRoleData = ROLES.find(
        (role) =>
            role.key === selectedRole
    );


    // =================================================
    // USERS FOR SELECTED ROLE
    // =================================================

    const selectedRoleUsers = users.filter(
        (user) =>
            normalizeRole(user.role) === selectedRole
    );


    // =================================================
    // OPEN EDIT USER MODAL
    // =================================================

    const openEditUserModal = (user) => {
        setSelectedUser(user);

        setEditFullName(
            user.full_name || ""
        );

        setEditEmail(
            user.email || ""
        );

        setEditPhone(
            user.phone || ""
        );

        setNewPassword("");

        setConfirmPassword("");

        setShowPassword(false);

        setShowConfirmPassword(false);

        setEditModalOpen(true);
    };


    // =================================================
    // CLOSE EDIT USER MODAL
    // =================================================

    const closeEditUserModal = () => {
        if (savingUser) {
            return;
        }

        setEditModalOpen(false);

        setSelectedUser(null);

        setEditFullName("");

        setEditEmail("");

        setEditPhone("");

        setNewPassword("");

        setConfirmPassword("");

        setShowPassword(false);

        setShowConfirmPassword(false);
    };


    // =================================================
    // SAVE USER
    // =================================================

    const handleSaveUser = async (event) => {
        event.preventDefault();

        if (!selectedUser) {
            toast.error("User not selected");
            return;
        }


        // =================================================
        // BASIC VALIDATION
        // =================================================

        const fullName = editFullName.trim();

        const email = editEmail
            .trim()
            .toLowerCase();

        const phone = editPhone.trim();


        if (fullName.length < 2) {
            toast.error(
                "Name must contain at least 2 characters"
            );
            return;
        }


        if (!email) {
            toast.error("Email is required");
            return;
        }


        // =================================================
        // EMAIL VALIDATION
        // =================================================

        const emailRegex =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {
            toast.error("Please enter a valid email address");
            return;
        }


        // =================================================
        // PHONE VALIDATION
        // =================================================

        if (phone) {
            const phoneDigits =
                phone.replace(/\D/g, "");

            if (
                phoneDigits.length < 10 ||
                phoneDigits.length > 15
            ) {
                toast.error(
                    "Please enter a valid mobile number"
                );
                return;
            }
        }


        // =================================================
        // PASSWORD VALIDATION
        // =================================================

        if (
            newPassword.trim() ||
            confirmPassword.trim()
        ) {
            if (!newPassword.trim()) {
                toast.error(
                    "Please enter a new password"
                );
                return;
            }

            if (newPassword.length < 6) {
                toast.error(
                    "Password must be at least 6 characters"
                );
                return;
            }

            if (!confirmPassword.trim()) {
                toast.error(
                    "Please confirm the password"
                );
                return;
            }

            if (
                newPassword !==
                confirmPassword
            ) {
                toast.error(
                    "Passwords do not match"
                );
                return;
            }
        }


        try {
            setSavingUser(true);


            // =================================================
            // UPDATE USER INFORMATION
            // =================================================

            await api.put(
                `/users/${selectedUser.id}`,
                {
                    full_name: fullName,
                    email: email,
                    phone: phone || null,
                }
            );


            // =================================================
            // CHANGE PASSWORD
            // =================================================

            if (newPassword.trim()) {
                await api.put(
                    `/users/${selectedUser.id}/password`,
                    {
                        new_password: newPassword,
                        confirm_password:
                            confirmPassword,
                    }
                );
            }


            // =================================================
            // SUCCESS
            // =================================================

            toast.success(
                `${fullName} updated successfully`
            );


            // =================================================
            // REFRESH USERS
            // =================================================

            await loadUsers();


            // =================================================
            // CLOSE MODAL
            // =================================================

            closeEditUserModal();
        }

        catch (err) {
            console.error(
                "Update User Error:",
                err
            );

            console.error(
                "Status:",
                err.response?.status
            );

            console.error(
                "Response:",
                err.response?.data
            );

            toast.error(
                getApiErrorMessage(
                    err,
                    "Failed to update user"
                )
            );
        }

        finally {
            setSavingUser(false);
        }
    };


    // =================================================
    // OPEN ADD USER MODAL
    // =================================================

    const handleAddUser = () => {
        if (!selectedRole) {
            toast.error(
                "Please select a role first"
            );
            return;
        }

        setAddCompanyName("");

        setAddContactPersonName("");

        setAddEmail("");

        setAddPhone("");

        setAddPassword("");

        setAddConfirmPassword("");

        setShowAddPassword(false);

        setShowAddConfirmPassword(false);

        setAddModalOpen(true);
    };


    // =================================================
    // CLOSE ADD USER MODAL
    // =================================================

    const closeAddUserModal = () => {
        if (savingAddUser) {
            return;
        }

        setAddModalOpen(false);

        setAddCompanyName("");

        setAddContactPersonName("");

        setAddEmail("");

        setAddPhone("");

        setAddPassword("");

        setAddConfirmPassword("");

        setShowAddPassword(false);

        setShowAddConfirmPassword(false);
    };


    // =================================================
    // CREATE USER
    // =================================================

    const handleCreateUser = async (event) => {
        event.preventDefault();


        // =================================================
        // ROLE VALIDATION
        // =================================================

        if (!selectedRole) {
            toast.error(
                "Please select a role first"
            );
            return;
        }


        // =================================================
        // GET FORM VALUES
        // =================================================

        const companyName =
            addCompanyName.trim();

        const contactPersonName =
            addContactPersonName.trim();

        const email =
            addEmail.trim().toLowerCase();

        const phone =
            addPhone.trim();

        const password =
            addPassword;

        const confirmPassword =
            addConfirmPassword;


        // =================================================
        // IMPORTANT FIX
        //
        // Previously code used:
        //
        // if (fullName.length < 2)
        //
        // But fullName did not exist.
        //
        // We now correctly use:
        //
        // contactPersonName
        // =================================================

        if (contactPersonName.length < 2) {
            toast.error(
                "Contact person name must contain at least 2 characters"
            );
            return;
        }


        // =================================================
        // COMPANY VALIDATION
        // =================================================

        if (!companyName) {
            toast.error(
                "Company name is required"
            );
            return;
        }


        // =================================================
        // EMAIL VALIDATION
        // =================================================

        if (!email) {
            toast.error(
                "Email is required"
            );
            return;
        }


        const emailRegex =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {
            toast.error(
                "Please enter a valid email address"
            );
            return;
        }


        // =================================================
        // PHONE VALIDATION
        // =================================================

        if (!phone) {
            toast.error(
                "Mobile number is required"
            );
            return;
        }


        const phoneDigits =
            phone.replace(/\D/g, "");

        if (
            phoneDigits.length < 10 ||
            phoneDigits.length > 15
        ) {
            toast.error(
                "Please enter a valid mobile number"
            );
            return;
        }


        // =================================================
        // PASSWORD VALIDATION
        // =================================================

        if (!password) {
            toast.error(
                "Password is required"
            );
            return;
        }


        if (password.length < 6) {
            toast.error(
                "Password must be at least 6 characters"
            );
            return;
        }


        if (!confirmPassword) {
            toast.error(
                "Please confirm the password"
            );
            return;
        }


        if (password !== confirmPassword) {
            toast.error(
                "Passwords do not match"
            );
            return;
        }


        // =================================================
        // CREATE USER
        // =================================================

        try {
            setSavingAddUser(true);

            console.log(
                "Creating user with:",
                {
                    full_name: contactPersonName,
                    company_name: companyName,
                    contact_person_name:
                        contactPersonName,
                    email,
                    phone,
                    role: selectedRole,
                }
            );


            // =================================================
            // API REQUEST
            // =================================================

            const response = await api.post(
                "/users/with-role",
                {
                    full_name: contactPersonName,

                    company_name:
                        companyName,

                    contact_person_name:
                        contactPersonName,

                    email: email,

                    phone: phone,

                    password: password,

                    // Always send the exact role selected in the Role Management UI.
                    role: normalizeRole(selectedRole),
                }
            );


            console.log(
                "Create User Response:",
                response.data
            );


            // =================================================
            // SUCCESS
            // =================================================

            toast.success(
                `${contactPersonName} created successfully`
            );


            // =================================================
            // PARENT CALLBACK
            // =================================================

            if (onAddUser) {
                onAddUser(
                    selectedRole,
                    response.data
                );
            }


            // =================================================
            // REFRESH USERS
            // =================================================

            await loadUsers();


            // =================================================
            // CLOSE MODAL
            // =================================================

            closeAddUserModal();
        }

        catch (err) {
            console.error(
                "Create User Error:",
                err
            );

            console.error(
                "Status:",
                err.response?.status
            );

            console.error(
                "Response:",
                err.response?.data
            );

            toast.error(
                getApiErrorMessage(
                    err,
                    "Failed to create user"
                )
            );
        }

        finally {
            setSavingAddUser(false);
        }
    };


    // =====================================================
    // RENDER
    // =====================================================

    return (
        <div className="role-management">


            {/* =================================================
                PAGE HEADER
            ================================================= */}

            <div className="role-management-header">

                <div>

                    <h1>
                        Role Management
                    </h1>

                    <p>
                        Manage users according to their
                        system roles.
                    </p>

                </div>

            </div>


            {/* =================================================
                SETTINGS TABS
            ================================================= */}

            <div
                className="role-management-tabs"
                style={{
                    display: "flex",
                    gap: "8px",
                    marginBottom: "14px",
                    padding: "5px",
                    background: "#ffffff",
                    border: "1px solid #dbe4f0",
                    borderRadius: "10px",
                    width: "fit-content",
                }}
            >
                <button
                    type="button"
                    onClick={() => setActiveSettingsTab("roles")}
                    style={{
                        border: "1px solid",
                        borderColor: activeSettingsTab === "roles" ? "#2563eb" : "transparent",
                        background: activeSettingsTab === "roles" ? "#eff6ff" : "transparent",
                        color: activeSettingsTab === "roles" ? "#1d4ed8" : "#475569",
                        padding: "9px 18px",
                        borderRadius: "7px",
                        fontWeight: 700,
                        cursor: "pointer",
                    }}
                >
                    Roles
                </button>

                <button
                    type="button"
                    onClick={() => setActiveSettingsTab("permissions")}
                    style={{
                        border: "1px solid",
                        borderColor: activeSettingsTab === "permissions" ? "#2563eb" : "transparent",
                        background: activeSettingsTab === "permissions" ? "#eff6ff" : "transparent",
                        color: activeSettingsTab === "permissions" ? "#1d4ed8" : "#475569",
                        padding: "9px 18px",
                        borderRadius: "7px",
                        fontWeight: 700,
                        cursor: "pointer",
                    }}
                >
                    Permission Control
                </button>

                <button
                    type="button"
                    onClick={() => setActiveSettingsTab("customer-portal")}
                    style={{
                        border: "1px solid",
                        borderColor: activeSettingsTab === "customer-portal" ? "#2563eb" : "transparent",
                        background: activeSettingsTab === "customer-portal" ? "#eff6ff" : "transparent",
                        color: activeSettingsTab === "customer-portal" ? "#1d4ed8" : "#475569",
                        padding: "9px 18px",
                        borderRadius: "7px",
                        fontWeight: 700,
                        cursor: "pointer",
                    }}
                >
                    Customer Portal
                </button>
            </div>

            {/* =================================================
                CUSTOMER PORTAL
            ================================================= */}

            {activeSettingsTab === "customer-portal" && (
                <div
                    style={{
                        background: "#ffffff",
                        border: "1px solid #dbe4f0",
                        borderRadius: "12px",
                        overflow: "hidden",
                    }}
                >
                    <div
                        style={{
                            padding: "18px 20px",
                            borderBottom: "1px solid #e5e7eb",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            gap: "16px",
                            flexWrap: "wrap",
                        }}
                    >
                        <div>
                            <h2 style={{ margin: 0, color: "#0f172a", fontSize: "18px", fontWeight: 800 }}>
                                Customer Portal Management
                            </h2>
                            <p style={{ margin: "5px 0 0", color: "#64748b", fontSize: "13px" }}>
                                Give existing customers secure login access to the customer portal.
                            </p>
                        </div>
                    </div>

                    <div style={{ padding: "14px 20px", display: "flex", alignItems: "center", gap: "10px", borderBottom: "1px solid #e5e7eb" }}>
                        <div style={{ position: "relative", flex: 1, maxWidth: "430px" }}>
                            <Search size={16} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "#64748b" }} />
                            <input
                                type="text"
                                value={portalSearch}
                                onChange={(event) => setPortalSearch(event.target.value)}
                                placeholder="Search all customers to give or manage access..."
                                style={{ width: "100%", boxSizing: "border-box", height: "38px", border: "1px solid #cbd5e1", borderRadius: "7px", padding: "0 12px 0 36px", outline: "none", fontSize: "13px" }}
                            />
                        </div>
                        <button
                            type="button"
                            onClick={loadPortalCustomers}
                            disabled={portalLoading}
                            style={{ height: "38px", border: "1px solid #cbd5e1", background: "#ffffff", color: "#334155", borderRadius: "7px", padding: "0 13px", fontWeight: 700, cursor: portalLoading ? "not-allowed" : "pointer" }}
                        >
                            {portalLoading ? "Loading..." : "Refresh"}
                        </button>

                        <span style={{ color: "#64748b", fontSize: "11px", marginLeft: "2px" }}>
                            {normalizedPortalSearch
                                ? "Showing matching customers"
                                : "Showing customers with portal access"}
                        </span>
                    </div>

                    {portalLoading ? (
                        <div style={{ padding: "55px 20px", textAlign: "center", color: "#64748b" }}>
                            <Loader2 size={28} className="role-loading-icon" />
                            <p style={{ marginTop: "10px" }}>Loading customers...</p>
                        </div>
                    ) : portalError ? (
                        <div style={{ padding: "40px 20px", textAlign: "center", color: "#b91c1c" }}>
                            <p>{portalError}</p>
                            <button type="button" onClick={loadPortalCustomers} className="retry-users-btn">
                                Try Again
                            </button>
                        </div>
                    ) : (
                        <div style={{ overflowX: "auto" }}>
                            <table style={{ width: "100%", borderCollapse: "collapse", minWidth: "850px" }}>
                                <thead>
                                    <tr style={{ background: "#f8fafc" }}>
                                        {["Customer", "Mobile Number", "Login Email", "Machines", "Access", "Portal Access", "Status", "Last Login", "Action"].map((heading) => (
                                            <th
                                                key={heading}
                                                style={{
                                                    textAlign: "left",
                                                    padding: "12px 14px",
                                                    borderBottom: "1px solid #e2e8f0",
                                                    color: "#475569",
                                                    fontSize: "12px",
                                                    fontWeight: 800,
                                                    whiteSpace: "nowrap",
                                                }}
                                            >
                                                {heading}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredPortalCustomers.length === 0 ? (
                                        <tr>
                                            <td colSpan={9} style={{ padding: "50px 20px", textAlign: "center", color: "#64748b" }}>
                                                No customers with portal access found. Use search to find a customer and give access.
                                            </td>
                                        </tr>
                                    ) : (
                                        filteredPortalCustomers.map((customer) => {
                                            const account =
                                                customer?.portal_user ||
                                                customer?.portalUser ||
                                                customer?.portal_account ||
                                                customer?.portalAccount ||
                                                null;
                                            const hasAccess = Boolean(account) || Boolean(customer?.portal_access);
                                            const isActive = account?.is_active !== undefined
                                                ? Boolean(account.is_active)
                                                : Boolean(customer?.portal_active);
                                            const customerName = customer?.customer_name || customer?.company_name || customer?.name || customer?.full_name || "Unnamed Customer";
                                            const phone = customer?.phone || customer?.mobile || customer?.mobile_number || "—";
                                            const loginEmail =
                                                customer?.email ||
                                                "—";
                                            const lastLogin = account?.last_login || customer?.last_login || null;
                                            const portalAccessLabel = getPortalAccessLabel(customer);

                                            const customerMachines = Array.isArray(
                                                customer?.machines
                                            )
                                                ? customer.machines
                                                : [];

                                            return (
                                                <tr key={customer.id}>
                                                    <td style={{ padding: "14px", borderBottom: "1px solid #eef2f7" }}>
                                                        <div style={{ fontWeight: 800, color: "#0f172a" }}>{customerName}</div>
                                                        {(customer?.customer_code || customer?.code) && (
                                                            <div style={{ marginTop: "3px", fontSize: "11px", color: "#64748b" }}>
                                                                {customer.customer_code || customer.code}
                                                            </div>
                                                        )}
                                                    </td>
                                                    <td style={{ padding: "14px", borderBottom: "1px solid #eef2f7", color: "#475569", fontSize: "13px" }}>{phone}</td>
                                                    <td style={{ padding: "14px", borderBottom: "1px solid #eef2f7", color: "#334155", fontSize: "13px" }}>{loginEmail}</td>

                                                    {/* =================================================
                                                        MACHINES
                                                        =================================================
                                                        Show EVERY machine belonging to this customer.
                                                        Each machine is displayed as:
                                                        Machine Name
                                                        Serial No: XXXXX
                                                    ================================================= */}
                                                    <td
                                                        style={{
                                                            padding: "12px 14px",
                                                            borderBottom: "1px solid #eef2f7",
                                                            minWidth: "220px",
                                                            verticalAlign: "top",
                                                        }}
                                                    >
                                                        {customerMachines.length === 0 ? (
                                                            <span
                                                                style={{
                                                                    color: "#94a3b8",
                                                                    fontSize: "12px",
                                                                }}
                                                            >
                                                                —
                                                            </span>
                                                        ) : (
                                                            <div
                                                                style={{
                                                                    display: "flex",
                                                                    flexDirection: "column",
                                                                    gap: "8px",
                                                                }}
                                                            >
                                                                {customerMachines.map(
                                                                    (machine, machineIndex) => {
                                                                        const machineName =
                                                                            machine?.machine_name ||
                                                                            machine?.name ||
                                                                            "Unnamed Machine";

                                                                        const serialNumber =
                                                                            machine?.serial_number ||
                                                                            "—";

                                                                        const machineNumber =
                                                                            machine?.machine_number ||
                                                                            "";

                                                                        return (
                                                                            <div
                                                                                key={
                                                                                    machine?.id ||
                                                                                    `${customer.id}-${machineIndex}`
                                                                                }
                                                                                style={{
                                                                                    padding: "7px 9px",
                                                                                    border: "1px solid #e2e8f0",
                                                                                    borderRadius: "7px",
                                                                                    background: "#f8fafc",
                                                                                }}
                                                                            >
                                                                                <div
                                                                                    style={{
                                                                                        fontWeight: 800,
                                                                                        color: "#0f172a",
                                                                                        fontSize: "13px",
                                                                                        lineHeight: "18px",
                                                                                    }}
                                                                                >
                                                                                    {machineName}
                                                                                </div>

                                                                                <div
                                                                                    style={{
                                                                                        marginTop: "2px",
                                                                                        color: "#64748b",
                                                                                        fontSize: "11px",
                                                                                        lineHeight: "16px",
                                                                                    }}
                                                                                >
                                                                                    Serial No:{" "}
                                                                                    <strong
                                                                                        style={{
                                                                                            color: "#334155",
                                                                                        }}
                                                                                    >
                                                                                        {serialNumber}
                                                                                    </strong>
                                                                                </div>

                                                                                {machineNumber && (
                                                                                    <div
                                                                                        style={{
                                                                                            marginTop: "1px",
                                                                                            color: "#94a3b8",
                                                                                            fontSize: "10px",
                                                                                            lineHeight: "15px",
                                                                                        }}
                                                                                    >
                                                                                        Machine No:{" "}
                                                                                        {machineNumber}
                                                                                    </div>
                                                                                )}
                                                                            </div>
                                                                        );
                                                                    }
                                                                )}
                                                            </div>
                                                        )}
                                                    </td>

                                                    <td style={{ padding: "14px", borderBottom: "1px solid #eef2f7", verticalAlign: "top" }}>
                                                         <span
                                                             style={{
                                                                 display: "inline-flex",
                                                                 alignItems: "center",
                                                                 padding: "5px 9px",
                                                                 borderRadius: "20px",
                                                                 background: portalAccessLabel === "Rental + Service" ? "#eff6ff" : portalAccessLabel === "Rental" ? "#fff7ed" : portalAccessLabel === "Service" ? "#ecfdf5" : "#f1f5f9",
                                                                 color: portalAccessLabel === "Rental + Service" ? "#1d4ed8" : portalAccessLabel === "Rental" ? "#c2410c" : portalAccessLabel === "Service" ? "#047857" : "#64748b",
                                                                 fontSize: "11px",
                                                                 fontWeight: 800,
                                                                 whiteSpace: "nowrap",
                                                             }}
                                                         >
                                                             {portalAccessLabel}
                                                         </span>
                                                     </td>

                                                     <td style={{ padding: "14px", borderBottom: "1px solid #eef2f7" }}>
                                                        <span style={{ display: "inline-flex", alignItems: "center", padding: "5px 9px", borderRadius: "20px", background: hasAccess ? "#ecfdf5" : "#f1f5f9", color: hasAccess ? "#047857" : "#64748b", fontSize: "11px", fontWeight: 800 }}>
                                                            {hasAccess ? "Enabled" : "Not Given"}
                                                        </span>
                                                    </td>
                                                    <td style={{ padding: "14px", borderBottom: "1px solid #eef2f7" }}>
                                                        <span style={{ display: "inline-flex", alignItems: "center", gap: "5px", fontSize: "12px", fontWeight: 700, color: !hasAccess ? "#94a3b8" : isActive ? "#047857" : "#b45309" }}>
                                                            <span style={{ width: "7px", height: "7px", borderRadius: "50%", background: !hasAccess ? "#cbd5e1" : isActive ? "#10b981" : "#f59e0b" }} />
                                                            {!hasAccess ? "—" : isActive ? "Active" : "Disabled"}
                                                        </span>
                                                    </td>
                                                    <td style={{ padding: "14px", borderBottom: "1px solid #eef2f7", color: "#64748b", fontSize: "12px" }}>
                                                        {lastLogin ? new Date(lastLogin).toLocaleString() : "Never"}
                                                    </td>
                                                    <td style={{ padding: "14px", borderBottom: "1px solid #eef2f7" }}>
                                                        <button
                                                            type="button"
                                                            onClick={() => openPortalAccessModal(customer, hasAccess)}
                                                            style={{ display: "inline-flex", alignItems: "center", gap: "6px", border: "1px solid #bfdbfe", background: "#eff6ff", color: "#1d4ed8", borderRadius: "6px", padding: "7px 10px", fontSize: "12px", fontWeight: 800, cursor: "pointer" }}
                                                        >
                                                            {hasAccess ? <><KeyRound size={14} /> Edit Access</> : <><UserRoundCheck size={14} /> Give Access</>}
                                                        </button>
                                                    </td>
                                                </tr>
                                            );
                                        })
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {/* =================================================
                ROLE TABS
            ================================================= */}

            {activeSettingsTab === "roles" && (
                <div>
                    <div className="role-tabs">

                {ROLES.map((role) => {

                    const Icon = role.icon;

                    const roleUserCount =
                        users.filter(
                            (user) =>
                                normalizeRole(
                                    user.role
                                ) === role.key
                        ).length;

                    return (
                        <button
                            key={role.key}
                            type="button"
                            className={
                                selectedRole === role.key
                                    ? `role-tab active ${role.className}`
                                    : `role-tab ${role.className}`
                            }
                            onClick={() =>
                                setSelectedRole(
                                    role.key
                                )
                            }
                        >

                            <span className="role-tab-icon">
                                <Icon size={20} />
                            </span>

                            <span className="role-tab-content">

                                <strong>
                                    {role.title}
                                </strong>

                                <small>
                                    {role.description}
                                </small>

                            </span>

                            <span className="role-tab-count">
                                {loading
                                    ? "..."
                                    : roleUserCount}
                            </span>

                            <span
                                className="role-tab-hover-text"
                                aria-hidden="true"
                            >
                                Click to view details
                            </span>

                        </button>
                    );
                })}

            </div>

                </div>
            )}


            {/* =================================================
                ROLE PERMISSIONS
            ================================================= */}

            {activeSettingsTab === "permissions" && (
                <div className="role-permissions-panel">

                    <div className="role-permissions-header">
                        <div className="role-permissions-title">
                            <h3>Role Permissions</h3>

                            <p>
                                Manage which pages and actions the selected role can access.
                                {permissionsLoading && (
                                    <span className="role-permissions-loading-text">
                                        Loading...
                                    </span>
                                )}
                            </p>
                        </div>

                        <div className="role-permissions-controls">

                            {/* =================================================
                                ROLE SELECT DROPDOWN
                            ================================================= */}

                            <div className="role-permission-role-selector">

                                <label htmlFor="permission-role-select">
                                    Select Role
                                </label>

                                <select
                                    id="permission-role-select"
                                    value={selectedPermissionRole}
                                    onChange={(event) => {
                                        setSelectedPermissionRole(
                                            event.target.value
                                        );
                                    }}
                                >
                                    {PERMISSION_ROLES.map((role) => (
                                        <option
                                            key={role.key}
                                            value={role.key}
                                        >
                                            {role.title}
                                        </option>
                                    ))}
                                </select>

                                <span className="role-permission-selected-role">
                                    Editing: <strong>
                                        {PERMISSION_ROLES.find(
                                            (role) =>
                                                role.key === selectedPermissionRole
                                        )?.title || selectedPermissionRole}
                                    </strong>
                                </span>

                            </div>

                            {/* =================================================
                                LEGEND
                            ================================================= */}

                            <div className="role-permissions-legend">

                                <span>
                                    <Check size={14} />
                                    Permission
                                </span>

                                <span>
                                    <Square size={14} />
                                    No Permission
                                </span>

                            </div>

                        </div>
                    </div>

                    {!permissionsLoading && permissionsError && (
                        <div className="role-permissions-state error role-permissions-error-bar">
                            <span>{permissionsError}</span>
                            <button
                                type="button"
                                onClick={() =>
                                    loadPermissions(
                                        selectedPermissionRole
                                    )
                                }
                                className="retry-users-btn"
                            >
                                Try Again
                            </button>
                        </div>
                    )}

                    <div className="role-permissions-table-wrapper">
                                <table className="role-permissions-table">
                                    <thead>
                                        <tr>
                                            <th>Page</th>
                                            {PERMISSION_ACTIONS.map(
                                                (action) => (
                                                    <th key={action.key}>
                                                        {action.label}
                                                    </th>
                                                )
                                            )}
                                        </tr>
                                    </thead>

                                    <tbody>
                                        {PERMISSION_PAGES.map(
                                            (page) => {
                                                const permission =
                                                    getPermissionForPage(
                                                        page.key
                                                    );

                                                return (
                                                    <tr key={page.key}>
                                                        <td className="permission-page-name">
                                                            {page.label}
                                                        </td>

                                                        {PERMISSION_ACTIONS.map(
                                                            (action) => {
                                                                const enabled = Boolean(
                                                                    permission &&
                                                                    permission[action.key]
                                                                );

                                                                const permissionKey =
                                                                    `${selectedPermissionRole}:${page.key}`;

                                                                const saving =
                                                                    savingPermissionId ===
                                                                        permission?.id ||
                                                                    savingPermissionKey ===
                                                                        permissionKey;

                                                                return (
                                                                    <td
                                                                        key={
                                                                            action.key
                                                                        }
                                                                        className="permission-checkbox-cell"
                                                                    >
                                                                        <button
                                                                            type="button"
                                                                            className={
                                                                                enabled
                                                                                    ? "permission-checkbox checked"
                                                                                    : "permission-checkbox"
                                                                            }
                                                                            onClick={() =>
                                                                                handlePermissionChange(
                                                                                    permission,
                                                                                    page.key,
                                                                                    action.key
                                                                                )
                                                                            }
                                                                            disabled={saving}
                                                                            title={
                                                                                enabled
                                                                                    ? `Remove ${action.label} permission`
                                                                                    : `Give ${action.label} permission`
                                                                            }
                                                                            aria-label={`${page.label} ${action.label} permission`}
                                                                        >
                                                                            {saving ? (
                                                                                <Loader2
                                                                                    size={16}
                                                                                    className="role-loading-icon"
                                                                                />
                                                                            ) : enabled ? (
                                                                                <Check
                                                                                    size={17}
                                                                                />
                                                                            ) : (
                                                                                <Square
                                                                                    size={17}
                                                                                />
                                                                            )}
                                                                        </button>
                                                                    </td>
                                                                );
                                                            }
                                                        )}
                                                    </tr>
                                                );
                                            }
                                        )}
                                    </tbody>
                                </table>
                            </div>
                </div>
            )}


            {/* =================================================
                SELECTED ROLE HEADER
            ================================================= */}

            {activeSettingsTab === "roles" && selectedRoleData && (

                <div
                    className={
                        `selected-role-header ${selectedRoleData.className}`
                    }
                >

                    <div className="selected-role-info">

                        <div className="selected-role-icon">

                            {React.createElement(
                                selectedRoleData.icon,
                                {
                                    size: 26,
                                }
                            )}

                        </div>

                        <div>

                            <h2>
                                {selectedRoleData.title}
                            </h2>

                            <p>
                                {selectedRoleData.description}
                            </p>

                        </div>

                    </div>


                    <div className="selected-role-actions">

                        <span className="selected-role-count">

                            {loading
                                ? "..."
                                : `${selectedRoleUsers.length} ${
                                    selectedRoleUsers.length === 1
                                        ? "User"
                                        : "Users"
                                }`}

                        </span>

                        <button
                            type="button"
                            className="role-add-user-btn"
                            onClick={handleAddUser}
                        >

                            <UserPlus size={17} />

                            Add User

                        </button>

                    </div>

                </div>
            )}


            {/* =================================================
                USERS
            ================================================= */}

            {activeSettingsTab === "roles" && selectedRole && (

                <div className="selected-role-panel">


                    {/* =================================================
                        LOADING
                    ================================================= */}

                    {loading && (

                        <div className="role-panel-state">

                            <Loader2
                                size={34}
                                className="role-loading-icon"
                            />

                            <h3>
                                Loading users...
                            </h3>

                            <p>
                                Please wait while users are loaded.
                            </p>

                        </div>
                    )}


                    {/* =================================================
                        ERROR
                    ================================================= */}

                    {!loading && error && (

                        <div className="role-panel-state error">

                            <Users
                                size={36}
                                strokeWidth={1.5}
                            />

                            <h3>
                                Unable to load users
                            </h3>

                            <p>
                                {error}
                            </p>

                            <button
                                type="button"
                                onClick={loadUsers}
                                className="retry-users-btn"
                            >
                                Try Again
                            </button>

                        </div>
                    )}


                    {/* =================================================
                        NO USERS
                    ================================================= */}

                    {!loading &&
                        !error &&
                        selectedRoleUsers.length === 0 && (

                            <div className="role-panel-state">

                                <Users
                                    size={42}
                                    strokeWidth={1.5}
                                />

                                <h3>
                                    No {selectedRoleData?.title} Users
                                </h3>

                                <p>
                                    Users assigned to this role
                                    will appear here.
                                </p>

                                <button
                                    type="button"
                                    className="empty-add-user-btn"
                                    onClick={handleAddUser}
                                >

                                    <UserPlus size={16} />

                                    Add User

                                </button>

                            </div>
                        )
                    }


                    {/* =================================================
                        REAL USERS
                    ================================================= */}

                    {!loading &&
                        !error &&
                        selectedRoleUsers.length > 0 && (

                            <div className="selected-role-users">

                                {selectedRoleUsers.map(
                                    (user) => (

                                        <div
                                            key={user.id}
                                            className="selected-role-user"
                                        >

                                            {/* =================================
                                                USER DETAILS
                                            ================================= */}

                                            <div className="role-user-details">

                                                <strong>
                                                    {user.full_name}
                                                </strong>

                                                {user.company_name && (
                                                    <span>
                                                        {user.company_name}
                                                    </span>
                                                )}

                                                {user.contact_person_name &&
                                                    user.contact_person_name !==
                                                    user.full_name && (
                                                        <span>
                                                            {user.contact_person_name}
                                                        </span>
                                                    )}

                                                <span>
                                                    {user.email}
                                                </span>

                                            </div>


                                            {/* =================================
                                                USER CONTACT / PASSWORD
                                            ================================= */}

                                            <div className="role-user-extra">

                                                <span className="role-user-password">

                                                    Password:

                                                    <span className="password-hidden">
                                                        ********
                                                    </span>

                                                </span>

                                                {user.phone && (
                                                    <small>
                                                        {user.phone}
                                                    </small>
                                                )}

                                            </div>


                                            {/* =================================
                                                EDIT USER
                                            ================================= */}

                                            <button
                                                type="button"
                                                className="change-password-btn"
                                                onClick={() =>
                                                    openEditUserModal(
                                                        user
                                                    )
                                                }
                                            >

                                                <Pencil
                                                    size={16}
                                                />

                                                <span>
                                                    Edit User
                                                </span>

                                            </button>

                                        </div>
                                    )
                                )}

                            </div>
                        )
                    }

                </div>
            )}


            {/* =================================================
                CUSTOMER PORTAL ACCESS MODAL
            ================================================= */}

            {portalModalOpen && selectedPortalCustomer && (
                <div className="password-modal-overlay" onMouseDown={closePortalAccessModal}>
                    <div className="password-modal edit-user-modal" onMouseDown={(event) => event.stopPropagation()}>
                        <div className="password-modal-header">
                            <div>
                                <h2>{portalEditMode ? "Edit Customer Portal Access" : "Give Customer Portal Access"}</h2>
                                <p>Manage login credentials for this existing customer.</p>
                            </div>
                            <button type="button" className="password-modal-close" onClick={closePortalAccessModal} disabled={savingPortal}>
                                <X size={20} />
                            </button>
                        </div>

                        <div className="password-modal-user">
                            <div className="password-modal-avatar">
                                {(selectedPortalCustomer?.customer_name || selectedPortalCustomer?.company_name || selectedPortalCustomer?.name || "C").charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <strong>{selectedPortalCustomer?.customer_name || selectedPortalCustomer?.company_name || selectedPortalCustomer?.name || "Customer"}</strong>
                                <span>Customer ID: {selectedPortalCustomer.id}</span>
                            </div>
                        </div>

                        <form onSubmit={handleSavePortalAccess}>
                            <div className="password-field">
                                <label>Email</label>
                                <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
                                    <Mail size={16} style={{ position: "absolute", left: "12px", color: "#64748b" }} />
                                    <input
                                        type="email"
                                        value={portalEmail}
                                        readOnly
                                        disabled={savingPortal}
                                        placeholder="Customer email"
                                        autoComplete="email"
                                        title="Portal login email comes from the customer master record."
                                        style={{
                                            paddingLeft: "38px",
                                            background: "#f8fafc",
                                            color: "#475569",
                                            cursor: "not-allowed",
                                        }}
                                    />
                                </div>
                                <small style={{ display: "block", marginTop: "5px", color: "#64748b", fontSize: "10px" }}>
                                    Portal login email is taken from the customer master. Change the email in the Customers page to update it.
                                </small>
                            </div>

                            <div className="password-field">
                                <label>Mobile Number</label>
                                <input
                                    type="tel"
                                    value={
                                        selectedPortalCustomer?.phone ||
                                        selectedPortalCustomer?.mobile ||
                                        selectedPortalCustomer?.mobile_number ||
                                        ""
                                    }
                                    readOnly
                                    disabled
                                    placeholder="Customer mobile number"
                                    style={{
                                        background: "#f8fafc",
                                        color: "#475569",
                                        cursor: "not-allowed",
                                    }}
                                />
                            </div>

                            <div className="password-field">
                                <label>{portalEditMode ? "New Password" : "Password"}</label>
                                <div className="password-input-wrapper">
                                    <input
                                        type={showPortalPassword ? "text" : "password"}
                                        value={portalPassword}
                                        onChange={(event) => {
                                            const value = event.target.value;

                                            setPortalPassword(value);

                                            if (!value && !portalConfirmPassword) {
                                                setPortalPasswordMatch(null);
                                            } else if (!portalConfirmPassword) {
                                                setPortalPasswordMatch(null);
                                            } else {
                                                setPortalPasswordMatch(
                                                    value === portalConfirmPassword
                                                );
                                            }
                                        }}
                                        placeholder={portalEditMode ? "Leave blank to keep current password" : "Enter portal password"}
                                        autoComplete="new-password"
                                        disabled={savingPortal}
                                    />
                                    <button type="button" className="password-eye-btn" onClick={() => setShowPortalPassword((value) => !value)} disabled={savingPortal}>
                                        {showPortalPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                                    </button>
                                </div>
                            </div>

                            <div className="password-field">
                                <label>Confirm Password</label>
                                <div className="password-input-wrapper">
                                    <input
                                        type={showPortalConfirmPassword ? "text" : "password"}
                                        value={portalConfirmPassword}
                                        onChange={(event) => {
                                            const value = event.target.value;

                                            setPortalConfirmPassword(value);

                                            if (!portalPassword && !value) {
                                                setPortalPasswordMatch(null);
                                            } else if (!value) {
                                                setPortalPasswordMatch(null);
                                            } else {
                                                setPortalPasswordMatch(
                                                    value === portalPassword
                                                );
                                            }
                                        }}
                                        placeholder={portalEditMode ? "Confirm new password" : "Re-enter password"}
                                        autoComplete="new-password"
                                        disabled={savingPortal}
                                    />
                                    <button type="button" className="password-eye-btn" onClick={() => setShowPortalConfirmPassword((value) => !value)} disabled={savingPortal}>
                                        {showPortalConfirmPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                                    </button>
                                </div>
                            </div>

                            {portalPasswordMatch !== null && portalConfirmPassword && (
                                <div
                                    style={{
                                        marginTop: "-6px",
                                        marginBottom: "4px",
                                        fontSize: "11px",
                                        fontWeight: 700,
                                        color: portalPasswordMatch
                                            ? "#15803d"
                                            : "#dc2626",
                                    }}
                                >
                                    {portalPasswordMatch
                                        ? "✓ Password matched"
                                        : "✕ Password does not match"}
                                </div>
                            )}

                            <div className="customer-portal-module-access">
                                <div className="customer-portal-module-access-header">
                                    <div>
                                        <strong>Portal Module Access</strong>
                                        <span>Choose which sections this customer can see after login.</span>
                                    </div>
                                    <Shield size={17} />
                                </div>

                                <label
                                    className={`customer-portal-module-option ${portalServiceAccess ? "selected" : ""}`}
                                >
                                    <input
                                        type="checkbox"
                                        checked={portalServiceAccess}
                                        onChange={(event) => setPortalServiceAccess(event.target.checked)}
                                        disabled={savingPortal}
                                    />
                                    <span className="customer-portal-module-check">
                                        {portalServiceAccess ? <Check size={14} /> : null}
                                    </span>
                                    <span className="customer-portal-module-icon service">
                                        <Wrench size={16} />
                                    </span>
                                    <span className="customer-portal-module-content">
                                        <strong>Service Access</strong>
                                        <small>
                                            Customer can view service information and raise service requests.
                                        </small>
                                    </span>
                                </label>

                                <label
                                    className={`customer-portal-module-option ${portalRentalAccess ? "selected rental" : ""}`}
                                >
                                    <input
                                        type="checkbox"
                                        checked={portalRentalAccess}
                                        onChange={(event) => setPortalRentalAccess(event.target.checked)}
                                        disabled={savingPortal}
                                    />
                                    <span className="customer-portal-module-check">
                                        {portalRentalAccess ? <Check size={14} /> : null}
                                    </span>
                                    <span className="customer-portal-module-icon rental">
                                        <Users size={16} />
                                    </span>
                                    <span className="customer-portal-module-content">
                                        <strong>Rental Access</strong>
                                        <small>
                                            Customer can view rental machines, enter meter readings and see rental history and amounts.
                                        </small>
                                    </span>
                                </label>

                                <div className="customer-portal-access-toggle">
                                    <div className="customer-portal-access-toggle-content">
                                        <strong>Portal Login</strong>
                                        <span>Enable or disable the customer's portal account.</span>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => setPortalActive((value) => !value)}
                                        disabled={savingPortal}
                                        className={`customer-portal-access-toggle-btn ${portalActive ? "active" : ""}`}
                                    >
                                        {portalActive ? <><Power size={14} /> Active</> : <><PowerOff size={14} /> Disabled</>}
                                    </button>
                                </div>

                                <div className="customer-portal-access-selection-note">
                                    <span>
                                        {portalServiceAccess && portalRentalAccess
                                            ? "Service + Rental access enabled."
                                            : portalServiceAccess
                                                ? "Service access only."
                                                : portalRentalAccess
                                                    ? "Rental access only."
                                                    : "No portal module access selected."}
                                    </span>
                                </div>
                            </div>

                            <div className="password-info-note">
                                <LockKeyhole size={15} />
                                <span>The password will be stored securely by the backend as a password hash. The actual password will not be stored as plain text.</span>
                            </div>

                            <div className="password-modal-actions">
                                <button type="button" className="password-cancel-btn" onClick={closePortalAccessModal} disabled={savingPortal}>Cancel</button>
                                <button type="submit" className="password-save-btn" disabled={savingPortal}>
                                    {savingPortal ? <><Loader2 size={15} className="role-loading-icon" /> Saving...</> : <><UserRoundCheck size={15} /> {portalEditMode ? "Save Access" : "Give Access"}</>}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* =================================================
                ADD USER MODAL
            ================================================= */}

            {addModalOpen &&
                selectedRoleData && (

                    <div
                        className="password-modal-overlay"
                        onMouseDown={closeAddUserModal}
                    >

                        <div
                            className="password-modal edit-user-modal"
                            onMouseDown={(event) =>
                                event.stopPropagation()
                            }
                        >

                            {/* =================================
                                HEADER
                            ================================= */}

                            <div className="password-modal-header">

                                <div>

                                    <h2>
                                        Add User
                                    </h2>

                                    <p>
                                        Create a new user for this role.
                                    </p>

                                </div>

                                <button
                                    type="button"
                                    className="password-modal-close"
                                    onClick={closeAddUserModal}
                                    disabled={savingAddUser}
                                >

                                    <X size={20} />

                                </button>

                            </div>


                            {/* =================================
                                SELECTED ROLE
                            ================================= */}

                            <div className="password-modal-user">

                                <div>

                                    <strong>
                                        {selectedRoleData.title}
                                    </strong>

                                    <span>
                                        {selectedRoleData.description}
                                    </span>

                                </div>

                            </div>


                            {/* =================================
                                ADD USER FORM
                            ================================= */}

                            <form
                                onSubmit={handleCreateUser}
                            >


                                {/* =================================
                                    COMPANY NAME
                                ================================= */}

                                <div className="password-field">

                                    <label>
                                        Company Name
                                    </label>

                                    <input
                                        type="text"
                                        value={addCompanyName}
                                        onChange={(event) =>
                                            setAddCompanyName(
                                                event.target.value
                                            )
                                        }
                                        placeholder="Enter company name"
                                        autoComplete="organization"
                                        disabled={savingAddUser}
                                    />

                                </div>


                                {/* =================================
                                    CONTACT PERSON NAME
                                ================================= */}

                                <div className="password-field">

                                    <label>
                                        Contact Person Name
                                    </label>

                                    <input
                                        type="text"
                                        value={addContactPersonName}
                                        onChange={(event) =>
                                            setAddContactPersonName(
                                                event.target.value
                                            )
                                        }
                                        placeholder="Enter contact person name"
                                        autoComplete="name"
                                        disabled={savingAddUser}
                                    />

                                </div>


                                {/* =================================
                                    EMAIL
                                ================================= */}

                                <div className="password-field">

                                    <label>
                                        Email
                                    </label>

                                    <input
                                        type="email"
                                        value={addEmail}
                                        onChange={(event) =>
                                            setAddEmail(
                                                event.target.value
                                            )
                                        }
                                        placeholder="Enter email address"
                                        autoComplete="email"
                                        disabled={savingAddUser}
                                    />

                                </div>


                                {/* =================================
                                    MOBILE NUMBER
                                ================================= */}

                                <div className="password-field">

                                    <label>
                                        Mobile Number
                                    </label>

                                    <input
                                        type="tel"
                                        value={addPhone}
                                        onChange={(event) =>
                                            setAddPhone(
                                                event.target.value
                                            )
                                        }
                                        placeholder="Enter mobile number"
                                        autoComplete="tel"
                                        inputMode="numeric"
                                        disabled={savingAddUser}
                                    />

                                </div>


                                {/* =================================
                                    PASSWORD
                                ================================= */}

                                <div className="password-field">

                                    <label>
                                        Password
                                    </label>

                                    <div className="password-input-wrapper">

                                        <input
                                            type={
                                                showAddPassword
                                                    ? "text"
                                                    : "password"
                                            }
                                            value={addPassword}
                                            onChange={(event) =>
                                                setAddPassword(
                                                    event.target.value
                                                )
                                            }
                                            placeholder="Enter password"
                                            autoComplete="new-password"
                                            disabled={savingAddUser}
                                        />

                                        <button
                                            type="button"
                                            className="password-eye-btn"
                                            onClick={() =>
                                                setShowAddPassword(
                                                    (value) =>
                                                        !value
                                                )
                                            }
                                            disabled={savingAddUser}
                                        >

                                            {showAddPassword ? (
                                                <EyeOff size={17} />
                                            ) : (
                                                <Eye size={17} />
                                            )}

                                        </button>

                                    </div>

                                </div>


                                {/* =================================
                                    CONFIRM PASSWORD
                                ================================= */}

                                <div className="password-field">

                                    <label>
                                        Confirm Password
                                    </label>

                                    <div className="password-input-wrapper">

                                        <input
                                            type={
                                                showAddConfirmPassword
                                                    ? "text"
                                                    : "password"
                                            }
                                            value={
                                                addConfirmPassword
                                            }
                                            onChange={(event) =>
                                                setAddConfirmPassword(
                                                    event.target.value
                                                )
                                            }
                                            placeholder="Re-enter password"
                                            autoComplete="new-password"
                                            disabled={savingAddUser}
                                        />

                                        <button
                                            type="button"
                                            className="password-eye-btn"
                                            onClick={() =>
                                                setShowAddConfirmPassword(
                                                    (value) =>
                                                        !value
                                                )
                                            }
                                            disabled={savingAddUser}
                                        >

                                            {showAddConfirmPassword ? (
                                                <EyeOff size={17} />
                                            ) : (
                                                <Eye size={17} />
                                            )}

                                        </button>

                                    </div>

                                </div>


                                {/* =================================
                                    INFO
                                ================================= */}

                                <div className="password-info-note">

                                    <LockKeyhole size={15} />

                                    <span>
                                        This user will be created
                                        with the selected role:
                                        {" "}
                                        <strong>
                                            {selectedRoleData.title}
                                        </strong>
                                    </span>

                                </div>


                                {/* =================================
                                    ACTIONS
                                ================================= */}

                                <div className="password-modal-actions">

                                    <button
                                        type="button"
                                        className="password-cancel-btn"
                                        onClick={closeAddUserModal}
                                        disabled={savingAddUser}
                                    >
                                        Cancel
                                    </button>


                                    <button
                                        type="submit"
                                        className="password-save-btn"
                                        disabled={savingAddUser}
                                    >

                                        {savingAddUser ? (
                                            <>
                                                <Loader2
                                                    size={15}
                                                    className="role-loading-icon"
                                                />

                                                Creating...
                                            </>
                                        ) : (
                                            <>
                                                <UserPlus size={15} />

                                                Create User
                                            </>
                                        )}

                                    </button>

                                </div>

                            </form>

                        </div>

                    </div>
                )
            }


            {/* =================================================
                EDIT USER MODAL
            ================================================= */}

            {editModalOpen &&
                selectedUser && (

                    <div
                        className="password-modal-overlay"
                        onMouseDown={closeEditUserModal}
                    >

                        <div
                            className="password-modal edit-user-modal"
                            onMouseDown={(event) =>
                                event.stopPropagation()
                            }
                        >

                            {/* =================================
                                HEADER
                            ================================= */}

                            <div className="password-modal-header">

                                <div>

                                    <h2>
                                        Edit User
                                    </h2>

                                    <p>
                                        Update user information
                                        and password.
                                    </p>

                                </div>

                                <button
                                    type="button"
                                    className="password-modal-close"
                                    onClick={closeEditUserModal}
                                    disabled={savingUser}
                                >

                                    <X size={20} />

                                </button>

                            </div>


                            {/* =================================
                                USER INFORMATION
                            ================================= */}

                            <div className="password-modal-user">

                                <div className="password-modal-avatar">

                                    {
                                        selectedUser.full_name
                                            ?.charAt(0)
                                            ?.toUpperCase() ||
                                        "U"
                                    }

                                </div>

                                <div>

                                    <strong>
                                        {selectedUser.full_name}
                                    </strong>

                                    <span>
                                        {selectedUser.role}
                                    </span>

                                </div>

                            </div>


                            {/* =================================
                                EDIT FORM
                            ================================= */}

                            <form
                                onSubmit={handleSaveUser}
                            >


                                {/* =================================
                                    FULL NAME
                                ================================= */}

                                <div className="password-field">

                                    <label>
                                        Full Name
                                    </label>

                                    <input
                                        type="text"
                                        value={editFullName}
                                        onChange={(event) =>
                                            setEditFullName(
                                                event.target.value
                                            )
                                        }
                                        placeholder="Enter full name"
                                        disabled={savingUser}
                                    />

                                </div>


                                {/* =================================
                                    EMAIL
                                ================================= */}

                                <div className="password-field">

                                    <label>
                                        Email
                                    </label>

                                    <input
                                        type="email"
                                        value={editEmail}
                                        onChange={(event) =>
                                            setEditEmail(
                                                event.target.value
                                            )
                                        }
                                        placeholder="Enter email address"
                                        disabled={savingUser}
                                    />

                                </div>


                                {/* =================================
                                    MOBILE
                                ================================= */}

                                <div className="password-field">

                                    <label>
                                        Mobile Number
                                    </label>

                                    <input
                                        type="tel"
                                        value={editPhone}
                                        onChange={(event) =>
                                            setEditPhone(
                                                event.target.value
                                            )
                                        }
                                        placeholder="Enter mobile number"
                                        disabled={savingUser}
                                    />

                                </div>


                                {/* =================================
                                    NEW PASSWORD
                                ================================= */}

                                <div className="password-field">

                                    <label>
                                        New Password
                                    </label>

                                    <div className="password-input-wrapper">

                                        <input
                                            type={
                                                showPassword
                                                    ? "text"
                                                    : "password"
                                            }
                                            value={newPassword}
                                            onChange={(event) =>
                                                setNewPassword(
                                                    event.target.value
                                                )
                                            }
                                            placeholder="Leave blank to keep current password"
                                            autoComplete="new-password"
                                            disabled={savingUser}
                                        />

                                        <button
                                            type="button"
                                            className="password-eye-btn"
                                            onClick={() =>
                                                setShowPassword(
                                                    (value) =>
                                                        !value
                                                )
                                            }
                                            disabled={savingUser}
                                        >

                                            {showPassword ? (
                                                <EyeOff size={18} />
                                            ) : (
                                                <Eye size={18} />
                                            )}

                                        </button>

                                    </div>

                                </div>


                                {/* =================================
                                    CONFIRM PASSWORD
                                ================================= */}

                                <div className="password-field">

                                    <label>
                                        Confirm Password
                                    </label>

                                    <div className="password-input-wrapper">

                                        <input
                                            type={
                                                showConfirmPassword
                                                    ? "text"
                                                    : "password"
                                            }
                                            value={confirmPassword}
                                            onChange={(event) =>
                                                setConfirmPassword(
                                                    event.target.value
                                                )
                                            }
                                            placeholder="Confirm new password"
                                            autoComplete="new-password"
                                            disabled={savingUser}
                                        />

                                        <button
                                            type="button"
                                            className="password-eye-btn"
                                            onClick={() =>
                                                setShowConfirmPassword(
                                                    (value) =>
                                                        !value
                                                )
                                            }
                                            disabled={savingUser}
                                        >

                                            {showConfirmPassword ? (
                                                <EyeOff size={18} />
                                            ) : (
                                                <Eye size={18} />
                                            )}

                                        </button>

                                    </div>

                                </div>


                                {/* =================================
                                    PASSWORD NOTE
                                ================================= */}

                                <div className="password-info-note">

                                    <LockKeyhole size={16} />

                                    <span>
                                        Leave the password fields
                                        empty to keep the existing
                                        password unchanged.
                                    </span>

                                </div>


                                {/* =================================
                                    ACTIONS
                                ================================= */}

                                <div className="password-modal-actions">

                                    <button
                                        type="button"
                                        className="password-cancel-btn"
                                        onClick={closeEditUserModal}
                                        disabled={savingUser}
                                    >
                                        Cancel
                                    </button>


                                    <button
                                        type="submit"
                                        className="password-save-btn"
                                        disabled={savingUser}
                                    >

                                        {savingUser ? (
                                            <>
                                                <Loader2
                                                    size={16}
                                                    className="role-loading-icon"
                                                />

                                                Saving...
                                            </>
                                        ) : (
                                            <>
                                                <Pencil size={16} />

                                                Save Changes
                                            </>
                                        )}

                                    </button>

                                </div>

                            </form>

                        </div>

                    </div>
                )
            }

        </div>
    );
};


export default RoleCards;