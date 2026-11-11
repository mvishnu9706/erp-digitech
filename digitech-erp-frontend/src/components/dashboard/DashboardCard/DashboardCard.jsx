import "./DashboardCard.css";

const DashboardCard = ({

    title,

    value,

    change,

    color,

    icon:Icon

})=>{

    return(

        <div className="dashboard-card">

            <div className="card-top">

                <div
                    className="card-icon"
                    style={{
                        background:color+"20",
                        color:color
                    }}
                >

                    <Icon size={28}/>

                </div>

            </div>

            <h2>{value}</h2>

            <h4>{title}</h4>

            <span
                style={{
                    color:color
                }}
            >

                {change}

            </span>

        </div>

    )

}

export default DashboardCard;