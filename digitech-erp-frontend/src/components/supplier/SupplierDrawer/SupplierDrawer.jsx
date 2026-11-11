import "./SupplierDrawer.css";

import { X } from "lucide-react";

import { useSupplier } from "../../../context/SupplierContext";

const SupplierDrawer = () => {

    const {
        drawerOpen,
        setDrawerOpen,
        drawerMode,
        supplierForm,
        setSupplierForm,
        createSupplier,
        updateSupplier,
        loading,
    } = useSupplier();


    if (!drawerOpen) {
        return null;
    }


    const isView = drawerMode === "view";


    // =========================================
    // Handle Input Change
    // =========================================

    const handleChange = (e) => {

        const {
            name,
            value,
        } = e.target;

        setSupplierForm((prev) => ({
            ...prev,
            [name]: value,
        }));

    };


    // =========================================
    // Handle Submit
    // =========================================

    const handleSubmit = async () => {

        // -----------------------------------------
        // Basic frontend validation
        // -----------------------------------------

        if (!supplierForm.company_name?.trim()) {

            alert("Company Name is required.");

            return;

        }


        // -----------------------------------------
        // Prepare data for backend
        // -----------------------------------------
        // Empty optional fields are converted
        // from "" to null.
        // This is important for EmailStr.
        // -----------------------------------------

        const supplierData = {

            ...supplierForm,

            company_name:
                supplierForm.company_name?.trim(),

            contact_person:
                supplierForm.contact_person?.trim()
                    ? supplierForm.contact_person.trim()
                    : null,

            phone:
                supplierForm.phone?.trim()
                    ? supplierForm.phone.trim()
                    : null,

            alternate_phone:
                supplierForm.alternate_phone?.trim()
                    ? supplierForm.alternate_phone.trim()
                    : null,

            contact_designation:
                supplierForm.contact_designation?.trim()
                    ? supplierForm.contact_designation.trim()
                    : null,

            email:
                supplierForm.email?.trim()
                    ? supplierForm.email.trim()
                    : null,

            website:
                supplierForm.website?.trim()
                    ? supplierForm.website.trim()
                    : null,

            gstin:
                supplierForm.gstin?.trim()
                    ? supplierForm.gstin.trim()
                    : null,

            pan:
                supplierForm.pan?.trim()
                    ? supplierForm.pan.trim()
                    : null,

            address:
                supplierForm.address?.trim()
                    ? supplierForm.address.trim()
                    : null,

            city:
                supplierForm.city?.trim()
                    ? supplierForm.city.trim()
                    : null,

            state:
                supplierForm.state?.trim()
                    ? supplierForm.state.trim()
                    : null,

            country:
                supplierForm.country?.trim()
                    ? supplierForm.country.trim()
                    : null,

            pincode:
                supplierForm.pincode?.trim()
                    ? supplierForm.pincode.trim()
                    : null,

            remarks:
                supplierForm.remarks?.trim()
                    ? supplierForm.remarks.trim()
                    : null,

            credit_limit:
                supplierForm.credit_limit === ""
                    ? 0
                    : Number(supplierForm.credit_limit),

            credit_days:
                supplierForm.credit_days === ""
                    ? 0
                    : Number(supplierForm.credit_days),

            opening_balance:
                supplierForm.opening_balance === ""
                    ? 0
                    : Number(supplierForm.opening_balance),

            is_active:
                supplierForm.is_active !== false,

        };


        try {

            if (drawerMode === "add") {

                await createSupplier(supplierData);

            }

            else if (drawerMode === "edit") {

                await updateSupplier(supplierData);

            }

        }

        catch (error) {

            console.error(
                "Supplier submit failed:",
                error?.response?.data || error
            );

        }

    };


    return (

        <div className="supplier-drawer-overlay">

            <div className="supplier-drawer">


                {/* =====================================
                    Header
                ===================================== */}

                <div className="supplier-drawer-header">

                    <h2>

                        {
                            drawerMode === "add"
                                ? "Add Supplier"
                                : drawerMode === "edit"
                                ? "Edit Supplier"
                                : "View Supplier"
                        }

                    </h2>


                    <button
                        type="button"
                        className="drawer-close-btn"
                        onClick={() => setDrawerOpen(false)}
                    >

                        <X size={22} />

                    </button>

                </div>


                {/* =====================================
                    Body
                ===================================== */}

                <div className="supplier-drawer-body">


                    <div className="supplier-form-grid">


                        {/* Company Name */}

                        <div className="form-group">

                            <label>

                                Company Name

                                <span className="required">
                                    *
                                </span>

                            </label>

                            <input
                                name="company_name"
                                value={
                                    supplierForm.company_name || ""
                                }
                                onChange={handleChange}
                                disabled={isView}
                            />

                        </div>


                        {/* Contact Person */}

                        <div className="form-group">

                            <label>
                                Contact Person
                            </label>

                            <input
                                name="contact_person"
                                value={
                                    supplierForm.contact_person || ""
                                }
                                onChange={handleChange}
                                disabled={isView}
                            />

                        </div>


                        {/* Phone */}

                        <div className="form-group">

                            <label>
                                Phone
                            </label>

                            <input
                                name="phone"
                                value={
                                    supplierForm.phone || ""
                                }
                                onChange={handleChange}
                                disabled={isView}
                            />

                        </div>


                        {/* Email */}

                        <div className="form-group">

                            <label>
                                Email
                            </label>

                            <input
                                type="email"
                                name="email"
                                value={
                                    supplierForm.email || ""
                                }
                                onChange={handleChange}
                                disabled={isView}
                                placeholder="supplier@example.com"
                            />

                        </div>


                        {/* GSTIN */}

                        <div className="form-group">

                            <label>
                                GSTIN
                            </label>

                            <input
                                name="gstin"
                                value={
                                    supplierForm.gstin || ""
                                }
                                onChange={handleChange}
                                disabled={isView}
                            />

                        </div>


                        {/* PAN */}

                        <div className="form-group">

                            <label>
                                PAN
                            </label>

                            <input
                                name="pan"
                                value={
                                    supplierForm.pan || ""
                                }
                                onChange={handleChange}
                                disabled={isView}
                            />

                        </div>


                        {/* City */}

                        <div className="form-group">

                            <label>
                                City
                            </label>

                            <input
                                name="city"
                                value={
                                    supplierForm.city || ""
                                }
                                onChange={handleChange}
                                disabled={isView}
                            />

                        </div>


                        {/* State */}

                        <div className="form-group">

                            <label>
                                State
                            </label>

                            <input
                                name="state"
                                value={
                                    supplierForm.state || ""
                                }
                                onChange={handleChange}
                                disabled={isView}
                            />

                        </div>


                        {/* Credit Limit */}

                        <div className="form-group">

                            <label>
                                Credit Limit
                            </label>

                            <input
                                type="number"
                                min="0"
                                name="credit_limit"
                                value={
                                    supplierForm.credit_limit ?? 0
                                }
                                onChange={handleChange}
                                disabled={isView}
                            />

                        </div>


                    </div>


                    {/* Address */}

                    <div className="form-group">

                        <label>
                            Address
                        </label>

                        <textarea
                            rows="4"
                            name="address"
                            value={
                                supplierForm.address || ""
                            }
                            onChange={handleChange}
                            disabled={isView}
                        />

                    </div>


                </div>


                {/* =====================================
                    Footer
                ===================================== */}

                <div className="supplier-drawer-footer">


                    <button
                        type="button"
                        className="btn-light"
                        onClick={() => setDrawerOpen(false)}
                        disabled={loading}
                    >

                        Cancel

                    </button>


                    {!isView && (

                        <button
                            type="button"
                            className="btn-primary"
                            onClick={handleSubmit}
                            disabled={loading}
                        >

                            {loading
                                ? "Please wait..."
                                : drawerMode === "add"
                                ? "Create Supplier"
                                : "Update Supplier"
                            }

                        </button>

                    )}


                </div>


            </div>

        </div>

    );

};


export default SupplierDrawer;