import math

import pytest
from pydantic import ValidationError

from mindscope.demo_pipeline import analyze_demo_session
from mindscope.schemas import SessionRequest


def test_usable_audio_reports_models_unavailable():
    request = SessionRequest(
        subject_id="demo-subject-001",
        run_id="demo-run-001",
        sample_rate=10,
        audio_samples=[0.01] * 100,
        video_features=[[0.0] * 49],
    )
    response = analyze_demo_session(request)
    assert response.depression_audio.status == "not_available_in_public_demo"
    assert response.dementia_audio.status == "not_available_in_public_demo"
    assert response.depression_video.status == "not_available_in_public_demo"
    assert response.disclaimer == "Research prototype — not a medical diagnosis."


def test_missing_modalities_are_skipped():
    request = SessionRequest(subject_id="demo", run_id="run", sample_rate=16_000)
    response = analyze_demo_session(request)
    assert response.depression_audio.status == "skipped"
    assert response.depression_audio.reason == "no_audio"
    assert response.depression_video.status == "skipped"
    assert response.depression_video.reason == "no_video_features"


@pytest.mark.parametrize("field,value", [("subject_id", "not valid"), ("run_id", "x" * 65)])
def test_invalid_identifiers_are_rejected(field, value):
    payload = {"subject_id": "demo", "run_id": "run", "sample_rate": 10}
    payload[field] = value

    with pytest.raises(ValidationError):
        SessionRequest(**payload)


@pytest.mark.parametrize(
    "audio_samples,video_features",
    [([math.nan], []), ([], [[math.inf] + [0.0] * 48])],
)
def test_non_finite_modality_values_are_rejected(audio_samples, video_features):
    with pytest.raises(ValidationError):
        SessionRequest(
            subject_id="demo",
            run_id="run",
            sample_rate=10,
            audio_samples=audio_samples,
            video_features=video_features,
        )


def test_video_frame_must_have_49_columns():
    with pytest.raises(ValidationError):
        SessionRequest(
            subject_id="demo",
            run_id="run",
            sample_rate=10,
            video_features=[[0.0] * 48],
        )


def test_video_frame_count_is_limited_to_1000():
    with pytest.raises(ValidationError):
        SessionRequest(
            subject_id="demo",
            run_id="run",
            sample_rate=10,
            video_features=[[0.0] * 49] * 1001,
        )


def test_audio_is_limited_to_60_seconds():
    with pytest.raises(ValidationError):
        SessionRequest(
            subject_id="demo",
            run_id="run",
            sample_rate=10,
            audio_samples=[0.0] * 601,
        )
