import "./DashboardHeader.css";

import {

    Bell,

    Plus

} from "lucide-react";

const DashboardHeader = () => {

    const today = new Date();

    const formattedDate = today.toLocaleDateString(

        "en-IN",

        {

            weekday:"long",

            day:"numeric",

            month:"long",

            year:"numeric"

        }

    );

    return(

        <div className="dashboard-header">

            <div>

                <h1>

                    Good Morning, Admin 👋

                </h1>

                <p>

                    Administrator —

                    {formattedDate}

                </p>

            </div>

            <div className="dashboard-actions">

                <button className="alert-btn">

                    <Bell size={18}/>

                    Alerts

                    <span>

                        5

                    </span>

                </button>

                <button className="quick-btn">

                    <Plus size={18}/>

                    Quick Add

                </button>

            </div>

        </div>

    )

}

export default DashboardHeader;