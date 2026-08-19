"""Synthetic-only public pipeline with no model execution or file writes."""

from mindscope.quality import AudioQuality, assess_audio
from mindscope.schemas import SessionRequest, SessionResponse, TrackState

_UNAVAILABLE = "not_available_in_public_demo"
_DISCLAIMER = "Research prototype — not a medical diagnosis."


def _audio_track(quality: AudioQuality) -> TrackState:
    if quality.usable:
        return TrackState(status=_UNAVAILABLE, reason=_UNAVAILABLE)
    return TrackState(status="skipped", reason=quality.reason)


def analyze_demo_session(request: SessionRequest) -> SessionResponse:
    """Report input quality and public-demo model availability only."""
    audio_quality = assess_audio(request.audio_samples, request.sample_rate)
    audio_track = _audio_track(audio_quality)
    video_track = (
        TrackState(status=_UNAVAILABLE, reason=_UNAVAILABLE)
        if request.video_features
        else TrackState(status="skipped", reason="no_video_features")
    )
    return SessionResponse(
        subject_id=request.subject_id,
        run_id=request.run_id,
        audio_quality=audio_quality,
        depression_audio=audio_track,
        dementia_audio=audio_track,
        depression_video=video_track,
        disclaimer=_DISCLAIMER,
    )
