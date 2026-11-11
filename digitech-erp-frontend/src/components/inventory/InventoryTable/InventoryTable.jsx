import "./InventoryTable.css";

import { useInventory } from "../../../context/InventoryContext";

import InventoryRow from "../InventoryRow/InventoryRow";
import InventoryPagination from "../InventoryPagination/InventoryPagination";


const InventoryTable = () => {

    const {
        inventory,
        loading,
    } = useInventory();


    return (

        <div className="inventory-table-wrapper">

            <table className="inventory-table">

                {/* =====================================================
                    Table Header
                ===================================================== */}

                <thead>

                    <tr>

                        <th>#</th>

                        <th>Product</th>

                        <th>Warehouse</th>

                        <th>Rack</th>

                        <th>Available</th>

                        <th>Purchase Price</th>

                        <th>Status</th>

                        <th>Actions</th>

                    </tr>

                </thead>


                {/* =====================================================
                    Table Body
                ===================================================== */}

                <tbody>

                    {/* =================================================
                        Loading
                    ================================================= */}

                    {loading ? (

                        <tr>

                            <td
                                colSpan="8"
                                className="inventory-loading-cell"
                            >

                                <div className="inventory-table-loading">

                                    <div className="inventory-spinner"></div>

                                    <span className="inventory-loading-text">
                                        Searching inventory...
                                    </span>

                                </div>

                            </td>

                        </tr>

                    ) : inventory.length === 0 ? (

                        /* =============================================
                           No Data
                        ============================================= */

                        <tr>

                            <td
                                colSpan="8"
                                className="no-data"
                            >
                                No Inventory Found
                            </td>

                        </tr>

                    ) : (

                        /* =============================================
                           Inventory Rows
                        ============================================= */

                        inventory.map(
                            (item, index) => (

                                <InventoryRow
                                    key={item.id}
                                    index={index}
                                    item={item}
                                />

                            )
                        )

                    )}

                </tbody>

            </table>


            {/* =========================================================
                Pagination
            ========================================================= */}

            {!loading && (
                <InventoryPagination />
            )}

        </div>

    );

};


export default InventoryTable;