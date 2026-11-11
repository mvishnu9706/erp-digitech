import {

    ShoppingCart,

    Wrench,

    Package,

    AlertTriangle,

    CalendarClock,

    IndianRupee

} from "lucide-react";

const dashboardCards = [

    {

        title:"Today's Sales",

        value:"₹2,35,400",

        change:"+12%",

        color:"#16a34a",

        icon:ShoppingCart

    },

    {

        title:"Pending Service",

        value:"18",

        change:"3 Urgent",

        color:"#2563eb",

        icon:Wrench

    },

    {

        title:"Active Rentals",

        value:"42",

        change:"+5",

        color:"#7c3aed",

        icon:Package

    },

    {

        title:"Low Stock",

        value:"12",

        change:"Need Purchase",

        color:"#dc2626",

        icon:AlertTriangle

    },

    {

        title:"AMC Expiring",

        value:"9",

        change:"This Month",

        color:"#ea580c",

        icon:CalendarClock

    },

    {

        title:"Monthly Revenue",

        value:"₹18.2L",

        change:"+18%",

        color:"#0f766e",

        icon:IndianRupee

    }

];

export default dashboardCards;