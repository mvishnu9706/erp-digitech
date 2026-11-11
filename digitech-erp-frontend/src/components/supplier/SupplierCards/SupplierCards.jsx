import "./SupplierCards.css";

import {
    Building2,
    CheckCircle2,
    XCircle,
    IndianRupee,
} from "lucide-react";

import { useSupplier } from "../../../context/SupplierContext";


const SupplierCards = () => {

    const { dashboard } = useSupplier();

    const cards = [

        {
            title: "Total Suppliers",
            value: dashboard?.total_suppliers ?? 0,
            icon: Building2,
            color: "#3b82f6",
        },

        {
            title: "Active Suppliers",
            value: dashboard?.active_suppliers ?? 0,
            icon: CheckCircle2,
            color: "#22c55e",
        },

        {
            title: "Inactive Suppliers",
            value: dashboard?.inactive_suppliers ?? 0,
            icon: XCircle,
            color: "#ef4444",
        },

        {
            title: "Outstanding Amount",
            value: `₹ ${Number(
                dashboard?.total_outstanding ?? 0
            ).toLocaleString()}`,
            icon: IndianRupee,
            color: "#f59e0b",
        },

    ];


    return (

        <div className="supplier-cards">

            {cards.map((card) => {

                const Icon = card.icon;

                return (

                    <div
                        className="supplier-card"
                        key={card.title}
                    >

                        <div className="supplier-card-left">

                            <p>
                                {card.title}
                            </p>

                            <h2>
                                {card.value}
                            </h2>

                        </div>


                        <div
                            className="supplier-card-icon"
                            style={{
                                background: `${card.color}20`,
                                color: card.color,
                            }}
                        >

                            <Icon />

                        </div>

                    </div>

                );

            })}

        </div>

    );

};


export default SupplierCards;