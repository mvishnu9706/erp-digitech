from math import ceil


class Pagination:

    @staticmethod
    def response(
        items,
        total: int,
        page: int,
        page_size: int
    ):

        return {

            "items": items,

            "page": page,

            "page_size": page_size,

            "total": total,

            "total_pages": ceil(total / page_size) if page_size else 1,

            "has_next": page * page_size < total,

            "has_previous": page > 1

        }