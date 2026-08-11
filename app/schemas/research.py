from typing import Any

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    url: str


class WebsiteData(BaseModel):
    name: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    description: str | None = None
    pages_scraped: list[str] = Field(default_factory=list)


class OpportunityData(BaseModel):
    application_url: str | None = None
    eligibility: str | None = None
    startup_stage: str | None = None
    investment_stage: str | None = None
    funding_amount: str | None = None
    funding_currency: str | None = None
    equity_required: str | None = None
    program_duration: str | None = None
    benefits: list[str] = Field(default_factory=list)
    application_process: str | None = None
    deadline: str | None = None
    geographic_focus: str | None = None
    sector_focus: str | None = None
    mentorship: str | None = None
    investor_access: str | None = None
    network_access: str | None = None
    office_space: str | None = None
    grants: str | None = None
    credits: str | None = None
    cohort_information: str | None = None
    required_documents: str | None = None
    selection_process: str | None = None
    program_status: str | None = None


class FactSource(BaseModel):
    field: str | None = None
    value: str | None = None
    source_url: str | None = None
    source_type: str | None = None
    verified: bool = False


class AIAnalysis(BaseModel):
    organization_name: str | None = None
    organization_type: str | None = None
    country: str | None = None
    city: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    founding_year: str | None = None
    industries: list[str] = Field(default_factory=list)
    investment_stage: list[str] | str | None = None
    startup_stage: str | None = None
    ticket_size: str | None = None
    portfolio_examples: list[str] = Field(default_factory=list)
    summary: str | None = None
    confidence_score: int | None = None
    verification_status: str | None = None
    verification_source: str | None = None
    opportunity: OpportunityData | dict[str, Any] | None = None
    fact_sources: list[FactSource] | list[dict[str, Any]] = Field(
        default_factory=list
    )
    error: str | None = None


class ResearchResponse(BaseModel):
    raw: WebsiteData | dict[str, Any]
    ai_analysis: AIAnalysis | dict[str, Any]
    database: dict[str, Any] | None = None
    verification: dict[str, Any] | None = None
    opportunity: OpportunityData | dict[str, Any] | None = None
    sources: list[FactSource] | list[dict[str, Any]] = Field(
        default_factory=list
    )
