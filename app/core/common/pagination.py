from pydantic import BaseModel
from typing import Optional, Type


class PaginationRequest(BaseModel):
    page_size: int
    page_number: int

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def offset(self) -> int:
        return self.page_size * (self.page_number - 1)


class PaginationResponse(BaseModel):
    total_items: int
    total_pages: int
    page_number: int
    page_size: int


class PaginatedObjects[Model: BaseModel](BaseModel):
    pagination: Optional[PaginationResponse]
    items: list[Model]

    @classmethod
    def build(
            cls,
            items: list[Model],
            total_items: int,
            request: Optional[PaginationRequest] = None,
    ) -> 'PaginatedObjects[Type[Model]]':
        return cls(
            items=items,
            pagination=PaginationResponse(
                total_items=total_items,
                total_pages=(total_items + request.page_size - 1) // request.page_size,
                page_number=request.page_number,
                page_size=request.page_size
            ) if request is not None else None
        )
