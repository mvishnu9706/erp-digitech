import {
    CalendarDays,
    ChevronRight,
    Cpu,
    FileText,
    ShieldCheck,
    Wrench
} from "lucide-react";
 

const CustomerMachineCard = ({
    machine,
    onRaiseService
}) => {

    const isServiceEnabled =
        machine?.service_enabled === true;


    return (

        <article className="customer-machine-card">

            {/* =================================================
                TOP
            ================================================= */}

            <div className="machine-card-top">

                <div className="machine-card-icon">

                    <Cpu size={24} />

                </div>

                <span
                    className={
                        machine?.status === "ACTIVE"
                            ? "machine-status active"
                            : "machine-status"
                    }
                >

                    {machine?.status || "UNKNOWN"}

                </span>

            </div>


            {/* =================================================
                MACHINE NAME
            ================================================= */}

            <div className="machine-card-title">

                <h3>
                    {
                        machine?.product_name ||
                        machine?.machine_name ||
                        `Machine #${machine?.id}`
                    }
                </h3>

                <p>
                    {
                        machine?.machine_number ||
                        "Machine number unavailable"
                    }
                </p>

            </div>


            {/* =================================================
                DETAILS
            ================================================= */}

            <div className="machine-card-details">

                <div className="machine-detail">

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


                <div className="machine-detail">

                    <span>
                        Asset Tag
                    </span>

                    <strong>
                        {
                            machine?.asset_tag ||
                            "-"
                        }
                    </strong>

                </div>


                <div className="machine-detail">

                    <span>
                        Current Meter
                    </span>

                    <strong>
                        {
                            machine?.current_meter ??
                            0
                        }
                    </strong>

                </div>


                <div className="machine-detail">

                    <span>
                        Warranty
                    </span>

                    <strong>

                        {machine?.warranty_end
                            ? (
                                <>

                                    <CalendarDays
                                        size={14}
                                    />

                                    {machine.warranty_end}

                                </>
                            )
                            : "Not Available"
                        }

                    </strong>

                </div>

            </div>


            {/* =================================================
                SERVICE ACCESS
            ================================================= */}

            <div
                className={
                    isServiceEnabled
                        ? "machine-service-enabled"
                        : "machine-service-disabled"
                }
            >

                <ShieldCheck size={16} />

                <span>

                    {isServiceEnabled
                        ? "Service Portal Enabled"
                        : "Service Portal Disabled"
                    }

                </span>

            </div>


            {/* =================================================
                ACTION
            ================================================= */}

            <button

                type="button"

                className="machine-service-btn"

                disabled={!isServiceEnabled}

                onClick={() =>
                    onRaiseService(machine)
                }

            >

                <Wrench size={17} />

                Raise Service Request

                <ChevronRight size={17} />

            </button>

        </article>

    );

};


export default CustomerMachineCard;