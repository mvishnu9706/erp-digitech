import "./SalesCards.css";

import {
    IndianRupee,
    ShoppingCart,
    Clock,
    TrendingUp,
    Package,
} from "lucide-react";

import { useSales } from "../../../context/SalesContext";


const SalesCards = () => {

    const {
        dashboard,
        updateFilter,
    } = useSales();


    // =====================================================
    // Handle Card Click
    // =====================================================

    const handleCardClick = (card) => {

        // -------------------------------------------------
        // Payment Pending
        // -------------------------------------------------

        if (
            card.filter === "PENDING"
        ) {

            updateFilter(
                "payment_status",
                "PENDING"
            );

        }

    };


    // =====================================================
    // Cards
    // =====================================================

    const cards = [

        // -------------------------------------------------
        // Today's Orders
        // -------------------------------------------------

        {
            title: "Today's Orders",

            value:
                dashboard?.todays_orders ??
                dashboard?.todays_sales_entries ??
                0,

            icon: ShoppingCart,

            color: "blue",

            clickable: false,
        },


        // -------------------------------------------------
        // Today's Items Sold
        // -------------------------------------------------

        {
            title: "Today's Items Sold",

            value:
                dashboard?.todays_items ??
                dashboard?.todays_sales_count ??
                0,

            icon: Package,

            color: "purple",

            clickable: false,
        },


        // -------------------------------------------------
        // Today's Sales Amount
        // -------------------------------------------------

        {
            title: "Today's Sales Amount",

            value:
                dashboard?.todays_sales ??
                0,

            type: "currency",

            icon: IndianRupee,

            color: "green",

            clickable: false,
        },


        // -------------------------------------------------
        // Payment Pending
        // -------------------------------------------------

        {
            title: "Payment Pending",

            value:
                dashboard?.pending_payment_amount ??
                0,

            type: "currency",

            icon: Clock,

            color: "orange",

            clickable: true,

            filter: "PENDING",
        },


        // -------------------------------------------------
        // Monthly Revenue
        // -------------------------------------------------

        {
            title: "Monthly Revenue",

            value:
                dashboard?.monthly_revenue ??
                0,

            type: "currency",

            compact: true,

            icon: TrendingUp,

            color: "teal",

            clickable: false,
        },

    ];


    // =====================================================
    // Currency Formatter
    // =====================================================

    const formatCurrency = (
        value,
        compact = false
    ) => {

        const amount =
            Number(value) || 0;


        // -------------------------------------------------
        // Lakhs
        // -------------------------------------------------

        if (
            compact &&
            amount >= 100000
        ) {

            return `₹${(
                amount / 100000
            ).toFixed(1)}L`;

        }


        // -------------------------------------------------
        // Thousands
        // -------------------------------------------------

        if (
            compact &&
            amount >= 1000
        ) {

            return `₹${(
                amount / 1000
            ).toFixed(1)}K`;

        }


        // -------------------------------------------------
        // Normal Currency
        // -------------------------------------------------

        return `₹${amount.toLocaleString(
            "en-IN",
            {
                minimumFractionDigits: 0,
                maximumFractionDigits: 2,
            }
        )}`;

    };


    // =====================================================
    // Value Formatter
    // =====================================================

    const formatValue = (card) => {

        if (
            card.type === "currency"
        ) {

            return formatCurrency(
                card.value,
                card.compact
            );

        }


        return Number(
            card.value || 0
        ).toLocaleString(
            "en-IN"
        );

    };


    // =====================================================
    // Render
    // =====================================================

    return (

        <div className="sales-cards">

            {cards.map(
                (card, index) => {

                    const Icon =
                        card.icon;


                    return (

                        <div
                            className={
                                `sales-card ${
                                    card.clickable
                                        ? "sales-card-clickable"
                                        : ""
                                }`
                            }

                            key={index}

                            onClick={() => {

                                if (
                                    card.clickable
                                ) {

                                    handleCardClick(
                                        card
                                    );

                                }

                            }}

                            role={
                                card.clickable
                                    ? "button"
                                    : undefined
                            }

                            tabIndex={
                                card.clickable
                                    ? 0
                                    : undefined
                            }

                            onKeyDown={(event) => {

                                if (
                                    card.clickable &&
                                    (
                                        event.key ===
                                            "Enter" ||
                                        event.key ===
                                            " "
                                    )
                                ) {

                                    event.preventDefault();

                                    handleCardClick(
                                        card
                                    );

                                }

                            }}
                        >

                            {/* =================================
                                Icon
                            ================================= */}

                            <div
                                className={`sales-card-icon ${card.color}`}
                            >

                                <Icon
                                    size={22}
                                />

                            </div>


                            {/* =================================
                                Content
                            ================================= */}

                            <div className="sales-card-content">

                                <p>
                                    {card.title}
                                </p>

                                <h3>
                                    {formatValue(card)}
                                </h3>

                            </div>

                        </div>

                    );

                }
            )}

        </div>

    );

};


export default SalesCards;