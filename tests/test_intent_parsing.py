from app.services.ai_service import AIService, extract_json_payload


def test_parse_startups_in_pakistan():
    ai = AIService()
    ai._generate_json = lambda prompt: None  # force deterministic path

    intent = ai.parse_search_intent("Find startups in Pakistan")

    assert intent["entity_type"] == "Startup"
    assert intent["country"] == "Pakistan"
    assert intent["opportunity_intent"] is False


def test_parse_ai_accelerators_limit():
    ai = AIService()
    ai._generate_json = lambda prompt: None

    intent = ai.parse_search_intent("Find 10 AI accelerators in Pakistan")

    assert intent["entity_type"] == "Accelerator"
    assert intent["country"] == "Pakistan"
    assert intent["industry"] == "AI"
    assert intent["limit"] == 10
    assert intent["opportunity_intent"] is True


def test_parse_apply_programs_opportunity_intent():
    ai = AIService()
    ai._generate_json = lambda prompt: None

    intent = ai.parse_search_intent(
        "Find programs I can apply to as an early-stage startup in Pakistan"
    )

    assert intent["entity_type"] == "Program"
    assert intent["country"] == "Pakistan"
    assert intent["startup_stage"] == "Early-stage"
    assert intent["opportunity_intent"] is True


def test_parse_investors_for_fintech():
    ai = AIService()
    ai._generate_json = lambda prompt: None

    intent = ai.parse_search_intent(
        "Find investors for fintech startups in Pakistan"
    )

    assert intent["entity_type"] == "Investor"
    assert intent["country"] == "Pakistan"
    assert intent["industry"] == "Fintech"


def test_extract_json_from_fenced_payload():
    payload = extract_json_payload(
        """```json
{"entity_type": "Startup", "country": "Pakistan", "limit": 5}
```"""
    )
    assert payload["entity_type"] == "Startup"
    assert payload["limit"] == 5


def test_extract_json_from_malformed_wrapper():
    payload = extract_json_payload(
        'Here is the result:\n{"organization_name": "Acme", "confidence_score": 80}\nThanks'
    )
    assert payload["organization_name"] == "Acme"
