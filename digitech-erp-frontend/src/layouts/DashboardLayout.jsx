import Sidebar from "../components/layout/Sidebar/Sidebar";
import Navbar from "../components/layout/Navbar/Navbar";
import Footer from "../components/layout/Footer/Footer";

import "../styles/layout.css";

const DashboardLayout = ({ children }) => {

    return (

        <div className="dashboard-layout">

            <Sidebar />

            <div className="dashboard-main">

                <Navbar />

                <div className="dashboard-content">

                    {children}

                </div>

                <Footer />

            </div>

        </div>

    );

};

export default DashboardLayout;