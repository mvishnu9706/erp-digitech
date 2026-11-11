import "./QuickActions.css";

import {
    PackagePlus,
    UserPlus,
    ShoppingCart,
    Receipt,
    Wrench,
    ArrowLeftRight
} from "lucide-react";

const actions = [

    {
        title: "Add Product",
        icon: PackagePlus
    },

    {
        title: "Add Customer",
        icon: UserPlus
    },

    {
        title: "Purchase Order",
        icon: ShoppingCart
    },

    {
        title: "Sales Invoice",
        icon: Receipt
    },

    {
        title: "Service Ticket",
        icon: Wrench
    },

    {
        title: "Stock Transfer",
        icon: ArrowLeftRight
    }

];

const QuickActions = () => {

    return (

        <div className="quick-actions">

            <h2>Quick Actions</h2>

            <div className="quick-grid">

                {

                    actions.map((item, index) => {

                        const Icon = item.icon;

                        return (

                            <button
                                key={index}
                                className="quick-card"
                            >

                                <Icon size={30} />

                                <span>

                                    {item.title}

                                </span>

                            </button>

                        );

                    })

                }

            </div>

        </div>

    );

};

export default QuickActions;