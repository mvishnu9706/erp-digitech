import "./Drawer.css";
import { X } from "lucide-react";

const Drawer = ({
    open,
    title,
    children,
    width = "700px",
    onClose,
    footer
}) => {

    if (!open) return null;

    return (

        <div className="drawer-overlay">

            <div
                className="drawer"
                style={{ width }}
            >

                <div className="drawer-header">

                    <h2>{title}</h2>

                    <button
                        className="drawer-close"
                        onClick={onClose}
                    >
                        <X size={22} />
                    </button>

                </div>

                <div className="drawer-body">

                    {children}

                </div>

                {
                    footer &&
                    <div className="drawer-footer">

                        {footer}

                    </div>
                }

            </div>

        </div>

    );

};

export default Drawer;