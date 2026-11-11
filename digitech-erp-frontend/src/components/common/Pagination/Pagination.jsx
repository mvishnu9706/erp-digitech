import "./Pagination.css";

import {
    ChevronLeft,
    ChevronRight
} from "lucide-react";

const Pagination = ({

    page,

    totalPages,

    onPageChange

}) => {

    const pages = [];

    for (let i = 1; i <= totalPages; i++) {

        pages.push(i);

    }

    return (

        <div className="pagination">

            <button

                disabled={page === 1}

                onClick={() => onPageChange(page - 1)}

            >

                <ChevronLeft size={18} />

            </button>

            {

                pages.map(number => (

                    <button

                        key={number}

                        className={

                            page === number

                                ? "active"

                                : ""

                        }

                        onClick={() => onPageChange(number)}

                    >

                        {number}

                    </button>

                ))

            }

            <button

                disabled={page === totalPages}

                onClick={() => onPageChange(page + 1)}

            >

                <ChevronRight size={18} />

            </button>

        </div>

    );

};

export default Pagination;