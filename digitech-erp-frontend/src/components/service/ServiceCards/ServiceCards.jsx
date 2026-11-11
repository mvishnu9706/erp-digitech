import React from "react";
import {
    Wrench,
    AlertTriangle,
    UserCheck,
    Clock3,
    CheckCircle2,
    CircleAlert,
    IndianRupee,
    CalendarCheck2,
} from "lucide-react";

import "./ServiceCards.css";


// =====================================================
// SERVICE DASHBOARD CARDS
// =====================================================

const ServiceCards = ({
    totalTickets = 0,
    openTickets = 0,
    assignedTickets = 0,
    inProgressTickets = 0,
    completedTickets = 0,
    pendingTickets = 0,
    totalServiceValue = 0,
    monthlyCompletedTickets = 0,
}) => {

    // =================================================
    // SAFE NUMBER
    // =================================================

    const safeNumber = (value) => {
        if (
            value === null ||
            value === undefined ||
            value === ""
        ) {
            return 0;
        }

        const number =
            typeof value === "number"
                ? value
                : Number(
                    String(value)
                        .replace(/[₹,\s]/g, "")
                        .trim()
                );

        return Number.isFinite(number)
            ? number
            : 0;
    };


    // =================================================
    // FORMAT SERVICE VALUE
    // =================================================

    const formattedServiceValue =
        new Intl.NumberFormat(
            "en-IN",
            {
                maximumFractionDigits: 2,
            }
        ).format(
            safeNumber(
                totalServiceValue
            )
        );


    // =================================================
    // CARDS
    // =================================================

    const cards = [
        {
            key: "total",
            title: "Total Tickets",
            value: safeNumber(totalTickets),
            icon: Wrench,
            color: "blue",
        },
        {
            key: "open",
            title: "Open",
            value: safeNumber(openTickets),
            icon: AlertTriangle,
            color: "orange",
        },
        {
            key: "assigned",
            title: "Assigned",
            value: safeNumber(assignedTickets),
            icon: UserCheck,
            color: "cyan",
        },
        {
            key: "in-progress",
            title: "In Progress",
            value: safeNumber(inProgressTickets),
            icon: Clock3,
            color: "purple",
        },
        {
            key: "completed",
            title: "Completed",
            value: safeNumber(completedTickets),
            icon: CheckCircle2,
            color: "green",
        },
        {
            key: "pending",
            title: "Pending",
            value: safeNumber(pendingTickets),
            icon: CircleAlert,
            color: "red",
        },
        {
            key: "service-value",
            title: "Service Value",
            value: `₹ ${formattedServiceValue}`,
            icon: IndianRupee,
            color: "teal",
        },
        {
            key: "monthly-completed",
            title: "Monthly Completed",
            value: safeNumber(
                monthlyCompletedTickets
            ),
            icon: CalendarCheck2,
            color: "indigo",
        },
    ];


    // =================================================
    // RENDER
    // =================================================

    return (
        <div className="service-cards">

            {cards.map(
                (card) => {

                    const Icon =
                        card.icon;

                    return (
                        <div
                            key={
                                card.key
                            }
                            className="service-card"
                        >

                            <div
                                className={
                                    `service-card-icon ${card.color}`
                                }
                            >
                                <Icon
                                    size={21}
                                    strokeWidth={2}
                                />
                            </div>


                            <div
                                className="service-card-content"
                            >
                                <p>
                                    {
                                        card.title
                                    }
                                </p>

                                <h2>
                                    {
                                        card.value
                                    }
                                </h2>
                            </div>

                        </div>
                    );
                }
            )}

        </div>
    );
};


export default ServiceCards;
