from pydantic import BaseModel


class PaginationQueryParams:
    __slots__ = ("page", "limit")

    def __init__(self, page: int = 1, limit: int = 100):
        self.page = page
        self.limit = limit


class Pagination(BaseModel):
    page: int
    limit: int
    count: int
