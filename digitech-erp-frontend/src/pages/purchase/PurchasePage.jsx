import DashboardLayout from "../../layouts/DashboardLayout";
import { usePurchase } from "../../context/PurchaseContext";

import PurchaseCards from "../../components/purchase/PurchaseCards/PurchaseCards";
import PurchaseToolbar from "../../components/purchase/PurchaseToolbar/PurchaseToolbar";
import PurchaseTable from "../../components/purchase/PurchaseTable/PurchaseTable";
import PurchaseDrawer from "../../components/purchase/PurchaseDrawer/PurchaseDrawer";

import "./PurchasePage.css";

const PurchasePage = () => {
    const {
        drawerOpen,
        closeDrawer,
    } = usePurchase();

    return (
        <DashboardLayout>
            <div className="purchase-page">
                <PurchaseCards />

                <PurchaseToolbar />

                <PurchaseTable />

                <PurchaseDrawer
                    open={drawerOpen}
                    onClose={closeDrawer}
                />
            </div>
        </DashboardLayout>
    );
};

export default PurchasePage;