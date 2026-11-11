import "./SalesDrawer.css";

import { X } from "lucide-react";

import { useSales } from "../../../context/SalesContext";

import SalesForm from "../SalesForm/SalesForm";
import SalesDetails from "../SalesDetails/SalesDetails";

const SalesDrawer = () => {

    const {
        drawerOpen,
        drawerMode,
        closeDrawer,
    } = useSales();


    if (!drawerOpen) {
        return null;
    }


    const isViewMode =
        drawerMode === "view";


    return (

        <div className="sales-drawer-overlay">

            <div className="sales-drawer">

                {/* =====================================
                    CLOSE
                ===================================== */}

                <button
                    type="button"
                    onClick={closeDrawer}
                    className="sales-drawer-close"
                    aria-label="Close sales"
                >
                    <X size={20} />
                </button>


                {/* =====================================
                    SALES CONTENT
                ===================================== */}

                <div className="sales-drawer-body">

                    {isViewMode ? (

                        <SalesDetails />

                    ) : (

                        <SalesForm />

                    )}

                </div>

            </div>

        </div>

    );
};


export default SalesDrawer;