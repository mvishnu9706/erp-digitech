import "./DashboardCards.css";

import dashboardCards from "../../../constants/dashboardCards";

import DashboardCard from "../DashboardCard/DashboardCard";

const DashboardCards=()=>{

    return(

        <div className="dashboard-grid">

            {

                dashboardCards.map(

                    (card,index)=>(

                        <DashboardCard

                            key={index}

                            {...card}

                        />

                    )

                )

            }

        </div>

    )

}

export default DashboardCards;