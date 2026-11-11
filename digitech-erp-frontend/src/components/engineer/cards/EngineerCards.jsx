import React from "react";
import {
    Ticket,
    CircleCheck,
    Wrench,
    CheckCircle2,
} from "lucide-react";

import "./EngineerCards.css";


const EngineerCards = ({
    assignedCount = 0,
    acceptedCount = 0,
    inProgressCount = 0,
    completedCount = 0,
}) => {

    const cards = [
        {
            key: "assigned",
            title: "Assigned Services",
            count: assignedCount,
            description: "Awaiting your acceptance",
            icon: Ticket,
            className: "assigned",
        },
        {
            key: "accepted",
            title: "Accepted",
            count: acceptedCount,
            description: "Accepted service requests",
            icon: CircleCheck,
            className: "accepted",
        },
        {
            key: "progress",
            title: "In Progress",
            count: inProgressCount,
            description: "Currently being serviced",
            icon: Wrench,
            className: "progress",
        },
        {
            key: "completed",
            title: "Completed",
            count: completedCount,
            description: "Completed this month",
            icon: CheckCircle2,
            className: "completed",
        },
    ];


    return (
        <section
            className="engineer-stat-grid"
            aria-label="Engineer service statistics"
        >

            {cards.map((card) => {

                const Icon = card.icon;

                return (
                    <article
                        key={card.key}
                        className={`engineer-stat-card ${card.className}`}
                    >

                        <div className="engineer-stat-icon">
                            <Icon
                                size={20}
                                strokeWidth={2.2}
                            />
                        </div>


                        <div className="engineer-stat-content">

                            <span className="engineer-stat-label">
                                {card.title}
                            </span>

                            <strong className="engineer-stat-value">
                                {Number(card.count) || 0}
                            </strong>

                            <small className="engineer-stat-description">
                                {card.description}
                            </small>

                        </div>

                    </article>
                );
            })}

        </section>
    );
};


export default EngineerCards;