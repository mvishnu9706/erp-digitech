import "./InventoryCards.css";

import {
    Boxes,
    PackageCheck,
    AlertTriangle,
    XCircle,
    Truck,
    IndianRupee,
} from "lucide-react";

import { useInventory } from "../../../context/InventoryContext";


const InventoryCards = () => {

    const {
        dashboard,

        setStatus,

        setPage,

        setSearch,

        setWarehouse,

        setProduct,

    } = useInventory();


    // =====================================================
    // Handle Card Click
    // =====================================================

    const handleCardClick = (type) => {

        // Always start from page 1
        setPage(1);


        // =================================================
        // Total Products
        // =================================================

        if (type === "TOTAL") {

            setStatus("");

            return;
        }


        // =================================================
        // Available Stock
        // =================================================

        if (type === "AVAILABLE") {

            setStatus("IN_STOCK");

            return;
        }


        // =================================================
        // Low Stock
        // =================================================

        if (type === "LOW_STOCK") {

            setStatus("LOW_STOCK");

            return;
        }


        // =================================================
        // Out Of Stock
        // =================================================

        if (type === "OUT_OF_STOCK") {

            setStatus("OUT_OF_STOCK");

            return;
        }


        // =================================================
        // Incoming Stock
        // =================================================

        if (type === "INCOMING") {

            setStatus("INCOMING");

            return;
        }

    };


    const cards = [

        // =================================================
        // Total Products
        // =================================================

        {
            title: "Total Products",

            type: "TOTAL",

            value:
                dashboard?.total_products ?? 0,

            icon:
                <Boxes size={22} />,

            color: "blue",
        },


        // =================================================
        // Available Stock
        // =================================================

        {
            title: "Available Stock",

            type: "AVAILABLE",

            value:
                dashboard?.stock ?? 0,

            icon:
                <PackageCheck size={22} />,

            color: "cyan",
        },


        // =================================================
        // Low Stock
        // =================================================

        {
            title: "Low Stock",

            type: "LOW_STOCK",

            value:
                dashboard?.low_stock ?? 0,

            icon:
                <AlertTriangle size={22} />,

            color: "orange",
        },


        // =================================================
        // Out Of Stock
        // =================================================

        {
            title: "Out Of Stock",

            type: "OUT_OF_STOCK",

            value:
                dashboard?.out_of_stock ?? 0,

            icon:
                <XCircle size={22} />,

            color: "red",
        },


        // =================================================
        // Incoming Stock
        // =================================================

        {
            title: "Incoming Stock",

            type: "INCOMING",

            value:
                dashboard?.incoming_stock ?? 0,

            icon:
                <Truck size={22} />,

            color: "teal",
        },


        // =================================================
        // Inventory Value
        // =================================================

        {
            title: "Inventory Value",

            type: null,

            value:
                `₹ ${Number(
                    dashboard?.inventory_value ?? 0
                ).toLocaleString()}`,

            icon:
                <IndianRupee size={22} />,

            color: "gold",
        },

    ];


    return (

        <div className="inventory-cards">

            {cards.map((card) => (

                <div
                    key={card.title}
                    className={
                        `inventory-card ${
                            card.type
                                ? "inventory-card-clickable"
                                : ""
                        }`
                    }

                    onClick={() => {

                        if (card.type) {

                            handleCardClick(
                                card.type
                            );

                        }

                    }}

                    role={
                        card.type
                            ? "button"
                            : undefined
                    }

                    tabIndex={
                        card.type
                            ? 0
                            : undefined
                    }

                    onKeyDown={(e) => {

                        if (
                            card.type &&
                            (
                                e.key === "Enter" ||
                                e.key === " "
                            )
                        ) {

                            e.preventDefault();

                            handleCardClick(
                                card.type
                            );

                        }

                    }}

                >

                    {/* =================================================
                        Icon
                    ================================================= */}

                    <div
                        className={
                            `inventory-icon ${card.color}`
                        }
                    >

                        {card.icon}

                    </div>


                    {/* =================================================
                        Content
                    ================================================= */}

                    <div className="inventory-content">

                        <h4>
                            {card.title}
                        </h4>

                        <h2>
                            {card.value}
                        </h2>

                    </div>

                </div>

            ))}

        </div>

    );

};


export default InventoryCards;