import json
import math
from pathlib import Path

from fastapi.testclient import TestClient

from mindscope.api import app


EXAMPLE_REQUEST_PATH = Path(__file__).parents[1] / "examples" / "session_request.json"
EXAMPLE_RESPONSE_PATH = Path(__file__).parents[1] / "examples" / "session_response.json"


def test_public_demo_exposes_only_its_two_contract_routes():
    """Catches generated documentation endpoints expanding the public API surface."""
    assert {route.path for route in app.routes} == {"/health", "/analyze/session"}


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

    assert response.status_code == 200
    body = response.json()
    assert body["subject_id"] == request_payload["subject_id"]
    assert body["run_id"] == request_payload["run_id"]
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


def test_analyze_session_serializes_extreme_finite_audio_without_nonfinite_json():
    """Catches finite request values overflowing the response RMS to Infinity."""
    request_payload = {
        "subject_id": "extreme-subject",
        "run_id": "extreme-run",
        "sample_rate": 10,
        "audio_samples": [1e308] * 100,
        "video_features": [],
    }
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/analyze/session", json=request_payload)

    assert response.status_code == 200
    rms = response.json()["audio_quality"]["rms"]
    assert math.isfinite(rms)
    assert rms == 1e308
    assert all(marker not in response.text for marker in ("NaN", "Infinity"))


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
