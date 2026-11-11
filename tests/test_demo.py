from copy import deepcopy
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.contracts.learning import LearningBundle
from app.main import app
from app.services.demo import generate_demo

client = TestClient(app)
REQUEST = {"schemaVersion": "1.0", "fixtureId": "memory-basics-v1"}


def test_fixture_and_generation_share_versioned_source_and_settings():
    fixture = client.get("/api/v1/demo/fixture").json()
    response = client.post("/api/v1/demo/generate", json=REQUEST)
    assert response.status_code == 200
    data = response.json()
    bundle = LearningBundle.model_validate(data)
    assert data["schemaVersion"] == fixture["schemaVersion"] == "1.0"
    assert data["source"] == fixture["source"]
    assert data["settings"] == fixture["settings"]
    assert str(UUID(bundle.generation_id)) == bundle.generation_id
    for section in (bundle.summary, bundle.concepts, bundle.flashcards, bundle.quiz):
        assert section
        for item in section:
            assert item.references
            for reference in item.references:
                unit = next(u for u in bundle.source.units if u.id == reference.source_unit_id)
                assert reference.label == f"Avsnitt {unit.location}"


def test_item_and_reference_ids_are_stable_but_generation_is_new():
    first, second = generate_demo(), generate_demo()
    assert first.generation_id != second.generation_id
    for section in ("summary", "concepts", "flashcards", "quiz"):
        assert getattr(first, section) == getattr(second, section)


@pytest.mark.parametrize("payload", [
    {}, {**REQUEST, "fixtureId": "unknown"}, {**REQUEST, "schemaVersion": "2.0"},
    {**REQUEST, "source": "PRIVATE_TEXT_MUST_NOT_BE_ECHOED"},
    {**REQUEST, "text": "custom source"}, {**REQUEST, "ownerId": "another-owner"},
    {**REQUEST, "settings": {"language": "en"}},
    {"schema_version": "1.0", "fixture_id": "memory-basics-v1"},
    {**REQUEST, "fixtureId": None}, {**REQUEST, "schemaVersion": 1},
])
def test_unsupported_input_is_rejected_without_echoing_source(payload):
    response = client.post("/api/v1/demo/generate", json=payload)
    assert response.status_code == 422
    assert response.json()["code"] == "unsupported_demo_input"
    assert "memory-basics-v1" in response.json()["message"]
    assert "PRIVATE_TEXT_MUST_NOT_BE_ECHOED" not in response.text
    assert UUID(response.json()["requestId"])


def test_malformed_json_is_a_safe_validation_error():
    response = client.post("/api/v1/demo/generate", content="{broken", headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert response.json()["code"] == "unsupported_demo_input"


@pytest.mark.parametrize("mutation", ["unknown_reference", "wrong_label", "duplicate_item", "empty_section", "duplicate_source"])
def test_contract_rejects_broken_bundle(mutation):
    data = deepcopy(generate_demo().model_dump(by_alias=True))
    if mutation == "unknown_reference":
        data["quiz"][0]["references"][0]["sourceUnitId"] = "nonexistent"
    elif mutation == "wrong_label":
        data["flashcards"][0]["references"][0]["label"] = "Avsnitt 99"
    elif mutation == "duplicate_item":
        data["quiz"][0]["id"] = data["flashcards"][0]["id"]
    elif mutation == "empty_section":
        data["quiz"] = []
    else:
        data["source"]["units"].append(data["source"]["units"][0])
    with pytest.raises(ValidationError):
        LearningBundle.model_validate(data)


def test_insufficient_section_has_explanation_and_no_fake_items():
    data = generate_demo().model_dump(by_alias=True)
    data["quiz"] = []
    data["insufficiency"]["quiz"] = "Materialet gir ikke nok grunnlag for denne delen."
    assert LearningBundle.model_validate(data).quiz == []


def test_public_assets_and_health():
    assert client.get("/health").json() == {"status": "ok", "mode": "demo"}
    for path, content_type in [("/", "text/html"), ("/assets/styles.css", "text/css"), ("/assets/app.js", "text/javascript")]:
        response = client.get(path)
        assert response.status_code == 200
        assert content_type in response.headers["content-type"]


@pytest.mark.parametrize("path", [
    "/.env", "/.git/config", "/README.md", "/app/main.py", "/static/index.html",
    "/assets/../main.py", "/assets/%2e%2e/main.py", "/assets/.env",
    "/assets/../../.docs/planning-artifacts/epics.md", "/api/v1/generate",
])
def test_repository_and_future_live_routes_are_not_public(path):
    assert client.get(path).status_code == 404
