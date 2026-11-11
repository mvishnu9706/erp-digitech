import "./Select.css";

const Select = ({
    label,
    name,
    value,
    onChange,
    options = [],
    placeholder = "Select",
    required = false,
    disabled = false,
    error = ""
}) => {

    return (

        <div className="select-group">

            {
                label &&

                <label className="select-label">

                    {label}

                    {
                        required &&
                        <span className="required">*</span>
                    }

                </label>

            }

            <select

                className={

                    error

                    ?

                    "erp-select error"

                    :

                    "erp-select"

                }

                name={name}

                value={value}

                disabled={disabled}

                onChange={onChange}

            >

                <option value="">

                    {placeholder}

                </option>

                {

                    options.map((item)=>(

                        <option

                            key={item.value}

                            value={item.value}

                        >

                            {item.label}

                        </option>

                    ))

                }

            </select>

            {

                error &&

                <small className="select-error">

                    {error}

                </small>

            }

        </div>

    );

};

export default Select;
