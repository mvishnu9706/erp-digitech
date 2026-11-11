import "./InventoryPagination.css";

import { ChevronLeft, ChevronRight } from "lucide-react";

import { useInventory } from "../../../context/InventoryContext";

const InventoryPagination = () => {

    const {

        page,

        setPage,

        totalPages,

        totalRecords,

        size,

    } = useInventory();

    if (totalPages <= 1) {

        return null;

    }

    const startRecord = totalRecords === 0
        ? 0
        : ((page - 1) * size) + 1;

    const endRecord = Math.min(

        page * size,

        totalRecords

    );

    return (

        <div className="inventory-pagination">

            <div className="pagination-info">

                Showing

                <strong>

                    {" "} {startRecord} - {endRecord} {" "}

                </strong>

                of

                <strong>

                    {" "} {totalRecords} {" "}

                </strong>

                records

            </div>

            <div className="pagination-controls">

                <button

                    disabled={page === 1}

                    onClick={() => setPage(page - 1)}

                >

                    <ChevronLeft size={18} />

                    Previous

                </button>

                {

                    [...Array(totalPages)].map((_, index) => (

                        <button

                            key={index}

                            className={

                                page === index + 1

                                    ? "active"

                                    : ""

                            }

                            onClick={() =>

                                setPage(index + 1)

                            }

                        >

                            {index + 1}

                        </button>

                    ))

                }

                <button

                    disabled={page === totalPages}

                    onClick={() => setPage(page + 1)}

                >

                    Next

                    <ChevronRight size={18} />

                </button>

            </div>

        </div>

    );

};

export default InventoryPagination;