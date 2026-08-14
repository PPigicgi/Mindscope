"""Quality checks for synthetic in-memory audio samples."""

from dataclasses import dataclass
from math import sqrt
from typing import Sequence


@dataclass(frozen=True)
class AudioQuality:
    """Immutable metadata describing whether audio meets demo thresholds."""

    duration_seconds: float
    rms: float
    usable: bool
    reason: str


def assess_audio(
    samples: Sequence[float],
    sample_rate: int,
    min_duration_seconds: float = 10.0,
    min_rms: float = 0.001,
) -> AudioQuality:
    """Assess duration and RMS without persisting samples or producing scores."""
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")

    sample_count = len(samples)
    raw_duration_seconds = sample_count / sample_rate
    raw_rms = sqrt(sum(sample * sample for sample in samples) / sample_count) if samples else 0.0
    duration_seconds = round(raw_duration_seconds, 3)
    rms = round(raw_rms, 6)

    if not samples:
        reason = "no_audio"
    elif raw_duration_seconds < min_duration_seconds:
        reason = "audio_too_short"
    elif raw_rms < min_rms:
        reason = "audio_too_quiet"
    else:
        reason = "ok"

    return AudioQuality(
        duration_seconds=duration_seconds,
        rms=rms,
        usable=reason == "ok",
        reason=reason,
    )
