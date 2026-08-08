from typing import Any

from pydantic import BaseModel


class ResearchRequest(BaseModel):
    url: str


class WebsiteData(BaseModel):
    name: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    description: str | None = None


class AIAnalysis(BaseModel):
    organization_name: str | None = None
    organization_type: str | None = None
    country: str | None = None
    city: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str |None = None
    linkedin: str | None = None
    founding_year: str | None = None
    industries: list[str] = []
    investment_stage: list[str] = []
    startup_stage: str | None = None
    ticket_size: str | None = None
    portfolio_examples: list[str] = []
    summary: str | None = None
    confidence_score: int | None = None
    error: str | None = None


class ResearchResponse(BaseModel):
    raw: WebsiteData
    ai_analysis: AIAnalysis | dict[str, Any]