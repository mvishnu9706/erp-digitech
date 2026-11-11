import "./DataTable.css";

const DataTable = ({
    columns = [],
    data = [],
    loading = false,
    emptyMessage = "No Records Found"
}) => {

    return (

        <div className="table-container">

            <table className="erp-table">

                <thead>

                    <tr>

                        {

                            columns.map((column) => (

                                <th key={column.key}>

                                    {column.label}

                                </th>

                            ))

                        }

                    </tr>

                </thead>

                <tbody>

                    {

                        loading ? (

                            <tr>

                                <td
                                    colSpan={columns.length}
                                    className="table-center"
                                >

                                    Loading...

                                </td>

                            </tr>

                        ) : data.length === 0 ? (

                            <tr>

                                <td
                                    colSpan={columns.length}
                                    className="table-center"
                                >

                                    {emptyMessage}

                                </td>

                            </tr>

                        ) : (

                            data.map((row, index) => (

                                <tr key={index}>

                                    {

                                        columns.map((column) => (

                                            <td key={column.key}>

                                                {

                                                    column.render

                                                        ? column.render(row)

                                                        : row[column.key]

                                                }

                                            </td>

                                        ))

                                    }

                                </tr>

                            ))

                        )

                    }

                </tbody>

            </table>

        </div>

    );

};

export default DataTable;
