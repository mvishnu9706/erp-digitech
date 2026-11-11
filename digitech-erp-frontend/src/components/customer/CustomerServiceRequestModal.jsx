import {
    useState
} from "react";

import {
    AlertCircle,
    CalendarDays,
    Loader2,
    X
} from "lucide-react";

import {
    createCustomerServiceRequest
} from "../../services/customerPortalService";

import "./CustomerServiceRequestModal.css";


const CustomerServiceRequestModal = ({
    machine,
    onClose,
    onCreated
}) => {

    const [form, setForm] = useState({

        subject: "",

        complaint: "",

        problem_description: "",

        priority: "MEDIUM",

        ticket_type: "BREAKDOWN",

        meter_reading:
            machine?.current_meter ?? 0,

        expected_visit_date: "",

        remarks: ""

    });


    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");


    /* =====================================================
       CHANGE
    ===================================================== */

    const handleChange = (event) => {

        const {
            name,
            value
        } = event.target;

        setForm(
            previous => ({
                ...previous,
                [name]: value
            })
        );

    };


    /* =====================================================
       SUBMIT
    ===================================================== */

    const handleSubmit = async (
        event
    ) => {

        event.preventDefault();

        setError("");

        if (!form.subject.trim()) {

            setError(
                "Please enter a service subject."
            );

            return;

        }

        if (!form.complaint.trim()) {

            setError(
                "Please describe the problem."
            );

            return;

        }


        try {

            setLoading(true);

            await createCustomerServiceRequest({

                machine_id:
                    machine.id,

                ticket_type:
                    form.ticket_type,

                priority:
                    form.priority,

                subject:
                    form.subject.trim(),

                complaint:
                    form.complaint.trim(),

                problem_description:
                    form.problem_description.trim() ||
                    null,

                meter_reading:
                    Number(
                        form.meter_reading || 0
                    ),

                expected_visit_date:
                    form.expected_visit_date ||
                    null,

                remarks:
                    form.remarks.trim() ||
                    null

            });

            onCreated();

        } catch (err) {

            console.error(
                "Service request error:",
                err
            );

            setError(
                err?.message ||
                "Unable to create service request."
            );

        } finally {

            setLoading(false);

        }

    };


    return (

        <div className="customer-modal-overlay">

            <div className="customer-service-modal">

                {/* =================================================
                    HEADER
                ================================================= */}

                <div className="service-modal-header">

                    <div>

                        <h2>
                            Raise Service Request
                        </h2>

                        <p>
                            {
                                machine?.product_name ||
                                machine?.machine_name ||
                                "Machine"
                            }
                        </p>

                    </div>


                    <button
                        type="button"
                        className="service-modal-close"
                        onClick={onClose}
                        disabled={loading}
                    >

                        <X size={20} />

                    </button>

                </div>


                {/* =================================================
                    MACHINE
                ================================================= */}

                <div className="service-machine-info">

                    <div>

                        <span>
                            Machine
                        </span>

                        <strong>
                            {
                                machine?.machine_number ||
                                "-"
                            }
                        </strong>

                    </div>


                    <div>

                        <span>
                            Serial Number
                        </span>

                        <strong>
                            {
                                machine?.serial_number ||
                                "-"
                            }
                        </strong>

                    </div>

                </div>


                {/* =================================================
                    ERROR
                ================================================= */}

                {error && (

                    <div className="service-form-error">

                        <AlertCircle size={18} />

                        <span>
                            {error}
                        </span>

                    </div>

                )}


                {/* =================================================
                    FORM
                ================================================= */}

                <form
                    className="service-request-form"
                    onSubmit={handleSubmit}
                >

                    {/* Subject */}

                    <div className="form-group">

                        <label>
                            Subject
                            <span>*</span>
                        </label>

                        <input
                            type="text"
                            name="subject"
                            value={form.subject}
                            onChange={handleChange}
                            placeholder="Example: Printer not printing"
                            maxLength={200}
                        />

                    </div>


                    {/* Type + Priority */}

                    <div className="form-row">

                        <div className="form-group">

                            <label>
                                Service Type
                            </label>

                            <select
                                name="ticket_type"
                                value={form.ticket_type}
                                onChange={handleChange}
                            >

                                <option value="BREAKDOWN">
                                    Breakdown
                                </option>

                                <option value="PREVENTIVE_MAINTENANCE">
                                    Preventive Maintenance
                                </option>

                                <option value="AMC">
                                    AMC
                                </option>

                                <option value="INSTALLATION">
                                    Installation
                                </option>

                                <option value="REINSTALLATION">
                                    Reinstallation
                                </option>

                            </select>

                        </div>


                        <div className="form-group">

                            <label>
                                Priority
                            </label>

                            <select
                                name="priority"
                                value={form.priority}
                                onChange={handleChange}
                            >

                                <option value="LOW">
                                    Low
                                </option>

                                <option value="MEDIUM">
                                    Medium
                                </option>

                                <option value="HIGH">
                                    High
                                </option>

                                <option value="URGENT">
                                    Urgent
                                </option>

                            </select>

                        </div>

                    </div>


                    {/* Complaint */}

                    <div className="form-group">

                        <label>
                            Problem
                            <span>*</span>
                        </label>

                        <textarea
                            name="complaint"
                            value={form.complaint}
                            onChange={handleChange}
                            placeholder="Describe the problem..."
                            rows={4}
                            maxLength={1000}
                        />

                    </div>


                    {/* Detailed description */}

                    <div className="form-group">

                        <label>
                            Detailed Description
                        </label>

                        <textarea
                            name="problem_description"
                            value={
                                form.problem_description
                            }
                            onChange={handleChange}
                            placeholder="Add any additional information..."
                            rows={3}
                        />

                    </div>


                    {/* Meter + Visit date */}

                    <div className="form-row">

                        <div className="form-group">

                            <label>
                                Current Meter Reading
                            </label>

                            <input
                                type="number"
                                name="meter_reading"
                                min="0"
                                value={
                                    form.meter_reading
                                }
                                onChange={handleChange}
                            />

                        </div>


                        <div className="form-group">

                            <label>
                                Preferred Visit Date
                            </label>

                            <div className="input-with-icon">

                                <CalendarDays
                                    size={17}
                                />

                                <input
                                    type="date"
                                    name="expected_visit_date"
                                    value={
                                        form.expected_visit_date
                                    }
                                    onChange={
                                        handleChange
                                    }
                                />

                            </div>

                        </div>

                    </div>


                    {/* Remarks */}

                    <div className="form-group">

                        <label>
                            Remarks
                        </label>

                        <textarea
                            name="remarks"
                            value={form.remarks}
                            onChange={handleChange}
                            placeholder="Anything else we should know?"
                            rows={2}
                        />

                    </div>


                    {/* =================================================
                        ACTIONS
                    ================================================= */}

                    <div className="service-modal-actions">

                        <button
                            type="button"
                            className="service-cancel-btn"
                            onClick={onClose}
                            disabled={loading}
                        >

                            Cancel

                        </button>


                        <button
                            type="submit"
                            className="service-submit-btn"
                            disabled={loading}
                        >

                            {loading ? (

                                <>

                                    <Loader2
                                        size={17}
                                        className="button-spinner"
                                    />

                                    Submitting...

                                </>

                            ) : (

                                "Submit Service Request"

                            )}

                        </button>

                    </div>

                </form>

            </div>

        </div>

    );

};


export default CustomerServiceRequestModal;