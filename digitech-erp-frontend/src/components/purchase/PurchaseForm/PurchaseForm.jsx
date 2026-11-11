import "./PurchaseForm.css";
import Select from "react-select";
import { usePurchase } from "../../../context/PurchaseContext";

const PurchaseForm = () => {
    const {
        purchase,
        updateField,
        suppliers,
        warehouses,
        drawerMode,
    } = usePurchase();
    
    const disabled = drawerMode === "view";

    const supplierOptions = suppliers.map((supplier) => ({
        value: supplier.id,
        label: supplier.company_name,
    }));

    const warehouseOptions = (warehouses || []).map((warehouse) => ({
        value: warehouse.id,
        label: warehouse.warehouse_name,
    }));

    const handleChange = (e) => {
        const { name, value } = e.target;
        updateField(name, value);
    };

    return (
        <div className="purchase-form">
            <div className="purchase-form-grid">
                <div className="form-group">
                    <label>Supplier</label>
                    <Select
                        classNamePrefix="react-select"
                        options={supplierOptions}
                        isSearchable
                        isDisabled={disabled}
                        placeholder="Search Supplier..."
                        value={
                            supplierOptions.find(
                                option => option.value === purchase.supplier_id
                            ) || null
                        }
                        onChange={(selected) =>
                            updateField(
                                "supplier_id",
                                selected ? selected.value : ""
                            )
                        }
                    />
                </div>

                <div className="form-group">
                    <label>Warehouse</label>
                    <Select
                        classNamePrefix="react-select"
                        options={warehouseOptions}
                        isSearchable
                        isDisabled={disabled}
                        placeholder="Search Warehouse..."
                        value={
                            warehouseOptions.find(
                                option => option.value === purchase.warehouse_id
                            ) || null
                        }
                        onChange={(selected) =>
                            updateField(
                                "warehouse_id",
                                selected ? selected.value : ""
                            )
                        }
                    />
                </div>

                <div className="form-group">
                    <label>Purchase Date</label>
                    <input
                        type="date"
                        name="purchase_date"
                        value={purchase.purchase_date}
                        onChange={handleChange}
                        disabled={disabled}
                    />
                </div>

                <div className="form-group">
                    <label>Reference Number</label>
                    <input
                        type="text"
                        name="invoice_no"
                        value={purchase.invoice_no}
                        onChange={handleChange}
                        disabled={disabled}
                    />
                </div>

                <div className="form-group">
                    <label>Currency</label>
                    <select
                        name="currency"
                        value={purchase.currency || "INR"}
                        onChange={handleChange}
                        disabled={disabled}
                    >
                        <option value="INR">INR</option>
                        <option value="USD">USD</option>
                    </select>
                </div>
            </div>

            <div className="form-group">
                <label>Remarks</label>
                <textarea
                    name="remarks"
                    value={purchase.remarks}
                    onChange={handleChange}
                    disabled={disabled}
                    placeholder="Remarks..."
                />
            </div>
        </div>
    );
};

export default PurchaseForm;