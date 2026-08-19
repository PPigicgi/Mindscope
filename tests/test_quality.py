import math

import pytest

from mindscope.quality import assess_audio


def test_ten_seconds_of_clear_audio_is_usable():
    quality = assess_audio([0.01] * 100, sample_rate=10)

    assert quality.duration_seconds == 10.0
    assert quality.rms == 0.01
    assert quality.usable is True
    assert quality.reason == "ok"


def test_short_audio_is_rejected():
    quality = assess_audio([0.01] * 99, sample_rate=10)

    assert quality.usable is False
    assert quality.reason == "audio_too_short"


def test_duration_rounding_does_not_make_short_audio_usable():
    quality = assess_audio([0.01] * 24_999, sample_rate=2_500)

    assert quality.duration_seconds == 10.0
    assert quality.usable is False
    assert quality.reason == "audio_too_short"


def test_quiet_audio_is_rejected():
    quality = assess_audio([0.0001] * 100, sample_rate=10)

    assert quality.usable is False
    assert quality.reason == "audio_too_quiet"


def test_empty_audio_has_zero_measurements():
    quality = assess_audio([], sample_rate=10)

    assert quality.duration_seconds == 0.0
    assert quality.rms == 0.0
    assert quality.usable is False
    assert quality.reason == "no_audio"


def test_extreme_finite_audio_has_finite_representable_rms():
    """Catches overflow from squaring large finite samples directly."""
    quality = assess_audio([1e308] * 100, sample_rate=10)

    assert math.isfinite(quality.rms)
    assert quality.rms == 1e308
    assert quality.usable is True
    assert quality.reason == "ok"


def test_non_positive_sample_rate_is_rejected():
    with pytest.raises(ValueError, match="^sample_rate must be positive$"):
        assess_audio([], sample_rate=0)
