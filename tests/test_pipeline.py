from unittest.mock import MagicMock, patch

from app.services.discovery_service import DiscoveryService
from app.services.filters import is_blocked_domain, is_blocked_path, is_blocked_text
from app.services.verification_service import VerificationService
from app.schemas.discover import SearchResult


def test_filter_helpers_reject_bad_domains_paths_and_noise():
    assert is_blocked_domain("https://linkedin.com/in/example") is True
    assert is_blocked_domain("https://example.org/about") is False
    assert is_blocked_path("https://example.org/blog/post") is True
    assert is_blocked_path("https://example.org/about") is False
    assert is_blocked_text("This is a top 10 startup list") is True
    assert is_blocked_text("Official accelerator program") is False


def test_verification_does_not_use_confidence_alone():
    verifier = VerificationService()

    with patch("app.services.verification_service.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = verifier.verify(
            url="https://example.org",
            title="Example Accelerator",
            description="A short description of the accelerator program.",
            linkedin="",
            fact_sources=[],
            opportunity={},
        )

    assert result["status"] in {
        "verified",
        "partially_verified",
        "unverified",
    }
    assert "score" in result
    assert result["source"] == "https://example.org"


def test_verification_boosts_official_facts():
    verifier = VerificationService()

    with patch("app.services.verification_service.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = verifier.verify(
            url="https://example.org",
            title="Example Accelerator",
            description="Official accelerator supporting early-stage startups.",
            linkedin="https://linkedin.com/company/example",
            fact_sources=[
                {
                    "field": "funding_amount",
                    "value": "$100,000",
                    "source_url": "https://example.org/program",
                    "source_type": "official",
                    "verified": True,
                }
            ],
            opportunity={
                "funding_amount": "$100,000",
                "application_url": "https://example.org/apply",
                "eligibility": "Early-stage startups in Pakistan",
            },
        )

    assert result["score"] >= 50
    assert result["status"] in {"verified", "partially_verified"}
    assert result["source"] == "https://example.org/program"


def test_candidate_ranking_prefers_entity_and_country():
    discovery = DiscoveryService()
    intent = {
        "entity_type": "Accelerator",
        "country": "Pakistan",
        "industry": "AI",
        "opportunity_intent": True,
    }

    relevant = SearchResult(
        name="Pakistan AI Accelerator",
        website="https://aiaccel.pk",
        description="Official AI accelerator program in Pakistan. Apply now.",
        source="Discovery Engine",
    )
    irrelevant = SearchResult(
        name="Top 10 startups news article",
        website="https://news.example.com/top-10",
        description="A blog article about startups around the world",
        source="Discovery Engine",
    )

    assert discovery.score_candidate(relevant, intent) > discovery.score_candidate(
        irrelevant, intent
    )


def test_search_failure_handling_returns_partial_results():
    from app.services.search_service import SearchService

    service = SearchService()

    service.ai.parse_search_intent = MagicMock(
        return_value={
            "entity_type": "Accelerator",
            "country": "Pakistan",
            "city": None,
            "industry": "AI",
            "startup_stage": None,
            "investment_stage": None,
            "limit": 2,
            "funding_requirement": None,
            "opportunity_intent": True,
        }
    )

    service.discovery.search = MagicMock(
        return_value=[
            SearchResult(
                name="Good Accel",
                website="https://good.example",
                description="Accelerator in Pakistan",
                source="Discovery Engine",
            ),
            SearchResult(
                name="Bad Accel",
                website="https://bad.example",
                description="Accelerator in Pakistan",
                source="Discovery Engine",
            ),
        ]
    )
    service.discovery.score_candidate = MagicMock(return_value=80)

    service.research.crawl_many = MagicMock(
        return_value=[
            {
                "raw": {
                    "name": "Good Accel",
                    "website": "https://good.example",
                    "description": "Accelerator",
                    "email": None,
                    "phone": None,
                    "linkedin": None,
                },
                "ai_analysis": {
                    "organization_name": "Good Accel",
                    "organization_type": "Accelerator",
                    "country": "Pakistan",
                    "city": "Lahore",
                    "industries": ["AI"],
                    "summary": "AI accelerator",
                    "confidence_score": 80,
                    "opportunity": {
                        "application_url": "https://good.example/apply",
                        "funding_amount": "$50,000",
                        "benefits": ["Mentorship"],
                    },
                    "fact_sources": [],
                },
                "opportunity": {
                    "application_url": "https://good.example/apply",
                    "funding_amount": "$50,000",
                    "benefits": ["Mentorship"],
                },
                "sources": [],
                "verification": {
                    "score": 85,
                    "status": "verified",
                    "source": "https://good.example",
                },
                "database": {
                    "saved": True,
                    "id": "11111111-1111-1111-1111-111111111111",
                    "verification_status": "verified",
                    "verification_source": "https://good.example",
                    "verification_score": 85,
                },
            },
            {
                "raw": {"website": "https://bad.example"},
                "ai_analysis": {"error": "timeout"},
                "opportunity": None,
                "sources": [],
                "verification": {
                    "score": 0,
                    "status": "unverified",
                    "source": None,
                },
                "database": {"saved": False},
                "error": "timeout",
            },
        ]
    )

    response = service.search("Find 2 AI accelerators in Pakistan")

    assert response["count"] >= 1
    assert response["parsed_intent"]["entity_type"] == "Accelerator"
    assert response["results"][0]["organization_name"] == "Good Accel"
    assert response["results"][0]["opportunity"]["application_url"]


def test_csv_headers_include_opportunity_fields():
    from app.api.export import CSV_HEADERS, export_csv

    with patch("app.api.export.SessionLocal") as mock_session_local:
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.options.return_value.order_by.return_value.all.return_value = []
        response = export_csv()

    assert response.media_type == "text/csv"
    assert "application_url" in CSV_HEADERS
    assert "funding_amount" in CSV_HEADERS
    assert "verification_status" in CSV_HEADERS
    assert "id" in CSV_HEADERS
    assert "name" in CSV_HEADERS
