import "./PurchaseCards.css";

import {
    ShoppingCart,
    Clock3,
    CheckCircle2,
    IndianRupee,
} from "lucide-react";

import { usePurchase } from "../../../context/PurchaseContext";

const PurchaseCards = () => {

    const { dashboard } = usePurchase();

    const cards = [
        {
            title: "Total Purchases",
            value: dashboard?.total_purchases ?? 0,
            icon: ShoppingCart,
            color: "#2563eb",
            bg: "#DBEAFE",
        },
        {
            title: "Today's Entries",
            value: dashboard?.today_entries ?? 0,
            icon: Clock3,
            color: "#F59E0B",
            bg: "#FEF3C7",
        },
        {
            title: "Today's Purchases",
            value: dashboard?.today_purchases ?? 0,
            icon: Clock3,
            color: "#D97706",
            bg: "#FDE68A",
        },
        {
            title: "This Month Entries",
            value: dashboard?.month_entries ?? 0,
            icon: CheckCircle2,
            color: "#10B981",
            bg: "#D1FAE5",
        },
        {
            title: "This Month Purchases",
            value: dashboard?.month_purchases ?? 0,
            icon: CheckCircle2,
            color: "#059669",
            bg: "#A7F3D0",
        },
        {
            title: "Today's Entry Value",
            value: `₹ ${Number(
                dashboard?.today_entry_value ?? 0
            ).toLocaleString()}`,
            icon: IndianRupee,
            color: "#EA580C",
            bg: "#FFEDD5",
        },
        {
            title: "Today's Purchase Value",
            value: `₹ ${Number(
                dashboard?.today_purchase_value ?? 0
            ).toLocaleString()}`,
            icon: IndianRupee,
            color: "#C2410C",
            bg: "#FED7AA",
        },
        {
            title: "Total Purchase Value",
            value: `₹ ${Number(
                dashboard?.total_purchase_value ?? 0
            ).toLocaleString()}`,
            icon: IndianRupee,
            color: "#7C3AED",
            bg: "#EDE9FE",
        },
    ];

    return (
        <div className="purchase-cards">
            {
                cards.map((card, index) => {
                    const Icon = card.icon;

                    return (
                        <div
                            className="purchase-card"
                            key={index}
                        >
                            <div>
                                <h4>
                                    {card.title}
                                </h4>
                                <h2>
                                    {card.value}
                                </h2>
                            </div>
                            <div
                                className="purchase-card-icon"
                                style={{
                                    background: card.bg,
                                    color: card.color,
                                }}
                            >
                                <Icon size={28} />
                            </div>
                        </div>
                    );
                })
            }
        </div>
    );
};

export default PurchaseCards;