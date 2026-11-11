
import "./Input.css";

const Input = ({
    label,
    type = "text",
    placeholder = "",
    value,
    onChange,
    name,
    required = false,
    disabled = false,
    error = "",
    icon = null
}) => {

    return (

        <div className="input-group">

            {
                label &&

                <label className="input-label">

                    {label}

                    {
                        required &&
                        <span className="required">*</span>
                    }

                </label>
            }

            <div className="input-wrapper">

                {
                    icon &&
                    <span className="input-icon">
                        {icon}
                    </span>
                }

                <input

                    className={error ? "erp-input error" : "erp-input"}

                    type={type}

                    placeholder={placeholder}

                    value={value}

                    name={name}

                    disabled={disabled}

                    onChange={onChange}

                />

            </div>

            {
                error &&
                <small className="input-error">

                    {error}

                </small>
            }

        </div>

    );

};

export default Input;