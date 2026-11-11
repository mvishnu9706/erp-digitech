import React from "react";
import { usePurchase } from "../../../context/PurchaseContext";
import PurchaseForm from "../PurchaseForm/PurchaseForm";
import PurchaseItemsTable from "../PurchaseItemsTable/PurchaseItemsTable";
import PurchaseSummary from "../PurchaseSummary/PurchaseSummary";
import "./PurchaseDrawer.css";

const PurchaseDrawer = () => {
    const { drawerOpen, closeDrawer, drawerMode, savePurchase } = usePurchase();

    if (!drawerOpen) return null;

    const getTitle = () => {
        if (drawerMode === "create") return "New Purchase Order";
        if (drawerMode === "edit") return "Edit Purchase Order";
        return "View Purchase Order";
    };

    return (
        <>
            <div className="purchase-overlay" onClick={closeDrawer}></div>
            <div className={`purchase-drawer ${drawerOpen ? "open" : ""}`}>
                <div className="drawer-header">
                    <h2>{getTitle()}</h2>
                    <button className="close-btn" onClick={closeDrawer}>&times;</button>
                </div>
                
                <div className="drawer-body">
                    <PurchaseForm />
                    
                    <div className="purchase-content">
                        <div className="purchase-items">
                            <PurchaseItemsTable />
                        </div>
                        <div className="purchase-summary-container">
                            <PurchaseSummary />
                        </div>
                    </div>
                </div>

                <div className="drawer-footer">
                    <button className="cancel-btn" onClick={closeDrawer}>Cancel</button>
                    {drawerMode !== "view" && (
                        <button className="save-btn" onClick={savePurchase}>Save</button>
                    )}
                </div>
            </div>
        </>
    );
};

export default PurchaseDrawer;