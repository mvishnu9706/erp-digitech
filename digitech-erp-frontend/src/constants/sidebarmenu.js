import {
    LayoutDashboard,
    Package,
    Users,
    Truck,
    ShoppingCart,
    ReceiptText,
    Boxes,
    Wrench,
    ClipboardList,
    BarChart3,
    Settings
} from "lucide-react";

const sidebarMenu = [

    {
        id: 1,
        title: "Dashboard",
        icon: LayoutDashboard,
        path: "/dashboard"
    },

    {
        id: 2,
        title: "Product Master",
        icon: Package,
        path: "/products"
    },

    {
        id: 3,
        title: "Customers",
        icon: Users,
        path: "/customers"
    },

    {
        id: 4,
        title: "Suppliers",
        icon: Truck,
        path: "/suppliers"
    },

    {
        id: 5,
        title: "Purchase",
        icon: ShoppingCart,
        path: "/purchase"
    },

    {
        id: 6,
        title: "Sales",
        icon: ReceiptText,
        path: "/sales"
    },

    {
        id: 7,
        title: "Inventory",
        icon: Boxes,
        path: "/inventory"
    },

    {
        id: 8,
        title: "Service",
        icon: Wrench,
        path: "/service"
    },

    {
        id: 9,
        title: "Rental / AMC",
        icon: ClipboardList,
        path: "/rental"
    },

    {
        id: 10,
        title: "Reports",
        icon: BarChart3,
        path: "/reports"
    },

    {
        id: 11,
        title: "Settings",
        icon: Settings,
        path: "/settings"
    }

];

export default sidebarMenu;