
import "./Button.css";

const Button = ({
    children,
    variant = "primary",
    size = "md",
    icon = null,
    loading = false,
    disabled = false,
    fullWidth = false,
    type = "button",
    onClick
}) => {

    const className = `
        btn
        btn-${variant}
        btn-${size}
        ${fullWidth ? "btn-full" : ""}
    `;

    return (

        <button
            type={type}
            className={className}
            disabled={disabled || loading}
            onClick={onClick}
        >

            {
                loading &&
                <span className="btn-loader"></span>
            }

            {
                !loading && icon
            }

            <span>

                {children}

            </span>

        </button>

    );

};

export default Button;