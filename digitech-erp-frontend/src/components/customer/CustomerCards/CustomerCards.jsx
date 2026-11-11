 import "./CustomerCards.css";

import {
    Users,
    UserCheck,
    UserX,
    IndianRupee,
    CreditCard,
} from "lucide-react";

import { useCustomers } from "../../../context/CustomerContext";


const CustomerCards = () => {

    const {
        dashboard,
        loading,
    } = useCustomers();


    const cards = [

        {
            title: "Total Customers",
            value: dashboard?.total_customers ?? 0,
            icon: Users,
            className: "customer-card-blue",
        },

        {
            title: "Active Customers",
            value: dashboard?.active_customers ?? 0,
            icon: UserCheck,
            className: "customer-card-green",
        },

        {
            title: "Inactive Customers",
            value: dashboard?.inactive_customers ?? 0,
            icon: UserX,
            className: "customer-card-red",
        },

        {
            title: "Total Outstanding",
            value: `₹${Number(
                dashboard?.total_outstanding ?? 0
            ).toLocaleString("en-IN", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            })}`,
            icon: IndianRupee,
            className: "customer-card-orange",
        },

        {
            title: "Total Credit Limit",
            value: `₹${Number(
                dashboard?.total_credit_limit ?? 0
            ).toLocaleString("en-IN", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            })}`,
            icon: CreditCard,
            className: "customer-card-purple",
        },

    ];


    return (

        <div className="customer-cards">

            {cards.map((card) => {

                const Icon = card.icon;

                return (

                    <div
                        key={card.title}
                        className="customer-card"
                    >

                        <div
                            className={`customer-card-icon ${card.className}`}
                        >
                            <Icon size={21} />
                        </div>

                        <div className="customer-card-content">

                            <span>
                                {card.title}
                            </span>

                            <strong>

                                {loading
                                    ? "..."
                                    : card.value
                                }

                            </strong>

                        </div>

                    </div>

                );

            })}

        </div>

    );

};


export default CustomerCards;