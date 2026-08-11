"""Pydantic schemas for validating Vertex AI / Gemini JSON outputs."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class SearchIntentSchema(BaseModel):
    entity_type: str | None = None
    country: str | None = None
    city: str | None = None
    industry: str | None = None
    startup_stage: str | None = None
    investment_stage: str | None = None
    limit: int = 10
    funding_requirement: str | None = None
    opportunity_intent: bool = False

    @field_validator("limit", mode="before")
    @classmethod
    def coerce_limit(cls, value: Any) -> int:
        if value is None or value == "":
            return 10
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return 10
        return max(1, min(parsed, 50))


class OpportunityExtractionSchema(BaseModel):
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

    @field_validator("benefits", mode="before")
    @classmethod
    def coerce_benefits(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value.strip() else []
        if isinstance(value, list):
            return [str(item) for item in value if item]
        return []


class FactSourceSchema(BaseModel):
    field: str | None = None
    value: str | None = None
    source_url: str | None = None
    source_type: str | None = "official"
    verified: bool = False


class OrganizationExtractionSchema(BaseModel):
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
    confidence_score: int = 0
    opportunity: OpportunityExtractionSchema | None = None
    fact_sources: list[FactSourceSchema] = Field(default_factory=list)

    @field_validator("industries", "portfolio_examples", mode="before")
    @classmethod
    def coerce_str_lists(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value.strip() else []
        if isinstance(value, list):
            return [str(item) for item in value if item]
        return []

    @field_validator("confidence_score", mode="before")
    @classmethod
    def coerce_confidence(cls, value: Any) -> int:
        if value is None or value == "":
            return 0
        try:
            score = int(float(value))
        except (TypeError, ValueError):
            return 0
        return max(0, min(score, 100))
