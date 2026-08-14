"""Pydantic schemas for the synthetic-only public demo boundary."""

from math import isfinite
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from mindscope.quality import AudioQuality

MAX_AUDIO_SECONDS = 60
VIDEO_FEATURE_DIM = 49
MAX_VIDEO_FRAMES = 1000
_IDENTIFIER_PATTERN = r"^[A-Za-z0-9_-]{1,64}$"


class SessionRequest(BaseModel):
    """Validated in-memory session data; the demo does not accept uploads."""

    model_config = ConfigDict(extra="forbid")

    subject_id: str = Field(pattern=_IDENTIFIER_PATTERN)
    run_id: str = Field(pattern=_IDENTIFIER_PATTERN)
    sample_rate: int = Field(gt=0)
    audio_samples: list[float] = Field(default_factory=list)
    video_features: list[list[float]] = Field(default_factory=list)

    @field_validator("audio_samples")
    @classmethod
    def audio_samples_must_be_finite(cls, samples: list[float]) -> list[float]:
        if not all(isfinite(sample) for sample in samples):
            raise ValueError("audio_samples must contain only finite values")
        return samples

    @field_validator("video_features")
    @classmethod
    def video_features_must_be_well_formed(
        cls, frames: list[list[float]]
    ) -> list[list[float]]:
        if len(frames) > MAX_VIDEO_FRAMES:
            raise ValueError(f"video_features must contain at most {MAX_VIDEO_FRAMES} frames")
        for frame in frames:
            if len(frame) != VIDEO_FEATURE_DIM:
                raise ValueError(f"each video frame must contain {VIDEO_FEATURE_DIM} values")
            if not all(isfinite(value) for value in frame):
                raise ValueError("video_features must contain only finite values")
        return frames

    @model_validator(mode="after")
    def audio_must_not_exceed_demo_limit(self) -> "SessionRequest":
        if len(self.audio_samples) > self.sample_rate * MAX_AUDIO_SECONDS:
            raise ValueError(f"audio_samples must not exceed {MAX_AUDIO_SECONDS} seconds")
        return self


class TrackState(BaseModel):
    """Public model availability status without any medical output."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["not_available_in_public_demo", "skipped"]
    reason: str


class SessionResponse(BaseModel):
    """Safe demo result: quality metadata and availability-only track states."""

    model_config = ConfigDict(extra="forbid")

    audio_quality: AudioQuality
    depression_audio: TrackState
    dementia_audio: TrackState
    depression_video: TrackState
    disclaimer: str
