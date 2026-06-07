from pydantic import BaseModel


class Meta(BaseModel):
    request_id: str = ""


class ApiResponse(BaseModel):
    data: dict | list | None = None
    error: dict | None = None
    meta: Meta = Meta()


class PaginationParams(BaseModel):
    limit: int = 20
    offset: int = 0


class PaginatedResponse(BaseModel):
    items: list
    total: int
    limit: int
    offset: int
