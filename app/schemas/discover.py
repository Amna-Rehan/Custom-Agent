from typing import Any
from pydantic import BaseModel


class DiscoverRequest(BaseModel):
    query: str
    category: str
    country: str | None = None


class SearchResult(BaseModel):
    name: str
    website: str
    description: str | None = None
    source: str


class DiscoverResponse(BaseModel):
    count: int
    results: list[dict[str, Any]]