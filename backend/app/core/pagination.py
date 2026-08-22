import math
from typing import Any, Generic, List, Sequence, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number starting from 1")
    per_page: int = Field(15, ge=1, le=100, description="Number of items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int = 1
    per_page: int = 15
    total_pages: int = 0
    has_more: bool = False


def paginate_response(
    items: Sequence[Any],
    total: int,
    page: int = 1,
    per_page: int = 15,
) -> PaginatedResponse[Any]:
    """Helper to construct a standardized PaginatedResponse with computed pagination metrics."""
    total_pages = math.ceil(total / per_page) if total > 0 and per_page > 0 else 0
    has_more = page < total_pages

    return PaginatedResponse(
        items=list(items),
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_more=has_more,
    )
