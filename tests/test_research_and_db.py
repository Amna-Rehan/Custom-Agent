from unittest.mock import MagicMock, patch

from app.services.database_service import DatabaseService
from app.services.ai_service import extract_json_payload, validate_ai_payload
from app.schemas.ai_extraction import OrganizationExtractionSchema


def test_opportunity_extraction_schema_validation():
    payload = {
        "organization_name": "Nest I/O",
        "organization_type": "Accelerator",
        "country": "Pakistan",
        "city": "Karachi",
        "website": "https://example.org",
        "confidence_score": "90",
        "industries": ["AI"],
        "opportunity": {
            "application_url": "https://example.org/apply",
            "eligibility": "Early-stage startups",
            "funding_amount": "$100,000",
            "equity_required": "0%",
            "benefits": "Mentorship",
            "deadline": "2026-12-01",
        },
        "fact_sources": [
            {
                "field": "funding_amount",
                "value": "$100,000",
                "source_url": "https://example.org/program",
                "source_type": "official",
                "verified": True,
            }
        ],
    }

    validated = validate_ai_payload(payload, OrganizationExtractionSchema)
    assert validated is not None
    assert validated.confidence_score == 90
    assert validated.opportunity.funding_amount == "$100,000"
    assert validated.opportunity.benefits == ["Mentorship"]


def test_malformed_ai_json_does_not_crash():
    assert extract_json_payload("not json at all") is None
    assert extract_json_payload("```json\n{bad}\n```") is None


def test_database_deduplication_updates_existing():
    service = DatabaseService()

    existing = MagicMock()
    existing.id = "org-1"
    existing.website = "https://example.org"

    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value.first.return_value = existing

    with patch(
        "app.services.database_service.SessionLocal",
        return_value=mock_db,
    ):
        with patch.object(service, "_update_organization") as update_mock:
            with patch.object(service, "_upsert_opportunity") as opp_mock:
                with patch.object(service, "_upsert_sources") as src_mock:
                    result = service.save(
                        {
                            "organization_name": "Updated Name",
                            "organization_type": "Accelerator",
                            "website": "https://example.org",
                            "country": "Pakistan",
                            "verification_status": "verified",
                            "verification_score": 90,
                            "opportunity": {
                                "application_url": "https://example.org/apply",
                                "funding_amount": "$10k",
                            },
                            "fact_sources": [],
                        }
                    )

    assert result is existing
    update_mock.assert_called_once()
    opp_mock.assert_called_once()
    src_mock.assert_called_once()
    mock_db.commit.assert_called_once()
