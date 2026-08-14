import json
from pathlib import Path

from fastapi.testclient import TestClient

from mindscope.api import app


EXAMPLE_REQUEST_PATH = Path(__file__).parents[1] / "examples" / "session_request.json"
EXAMPLE_RESPONSE_PATH = Path(__file__).parents[1] / "examples" / "session_response.json"


def test_health_reports_the_public_demo_contract():
    """Catches a route that exposes the wrong mode or health payload."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "public_demo"}


def test_analyze_session_returns_availability_only_for_the_synthetic_example():
    """Catches routes that bypass the safe demo orchestration response."""
    request_payload = json.loads(EXAMPLE_REQUEST_PATH.read_text(encoding="utf-8"))
    client = TestClient(app)

    response = client.post("/analyze/session", json=request_payload)

    assert request_payload["subject_id"] == "demo-subject-001"
    assert request_payload["run_id"] == "demo-run-001"
    assert response.status_code == 200
    body = response.json()
    assert body["disclaimer"] == "Research prototype — not a medical diagnosis."
    assert body["audio_quality"]["usable"] is True
    assert body["depression_audio"]["status"] == "not_available_in_public_demo"
    assert body["dementia_audio"]["status"] == "not_available_in_public_demo"
    assert body["depression_video"]["status"] == "not_available_in_public_demo"


def test_serialized_example_response_matches_the_api_response():
    """Catches documentation examples that drift from the live response contract."""
    request_payload = json.loads(EXAMPLE_REQUEST_PATH.read_text(encoding="utf-8"))
    expected_response = json.loads(EXAMPLE_RESPONSE_PATH.read_text(encoding="utf-8"))
    client = TestClient(app)

    response = client.post("/analyze/session", json=request_payload)

    assert response.status_code == 200
    assert response.json() == expected_response


def test_analyze_session_rejects_unknown_fields():
    """Catches accidental expansion of the public request surface."""
    request_payload = json.loads(EXAMPLE_REQUEST_PATH.read_text(encoding="utf-8"))
    request_payload["filename"] = "recording.wav"
    client = TestClient(app)

    response = client.post("/analyze/session", json=request_payload)

    assert response.status_code == 422


def test_analyze_session_rejects_invalid_subject_ids():
    """Catches routes that skip the existing request identifier validation."""
    request_payload = json.loads(EXAMPLE_REQUEST_PATH.read_text(encoding="utf-8"))
    request_payload["subject_id"] = "not valid"
    client = TestClient(app)

    response = client.post("/analyze/session", json=request_payload)

    assert response.status_code == 422
