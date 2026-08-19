import csv
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = PROJECT_ROOT / "results" / "verified_metrics.csv"
EVALUATION_PATH = PROJECT_ROOT / "docs" / "evaluation.md"


EXPECTED_METRIC_ROWS = [
    {
        "track_id": "dementia_audio",
        "modality": "audio",
        "model": "HuBERT + XGBoost",
        "n_test": "412",
        "positive_count": "183",
        "negative_count": "229",
        "threshold": "0.39",
        "roc_auc": "0.76515",
        "balanced_accuracy": "0.72804",
        "f1": "0.71212",
        "precision": "0.66197",
        "recall": "0.77049",
        "specificity": "0.68559",
        "scope": "internal held-out test benchmark",
    },
    {
        "track_id": "depression_audio",
        "modality": "audio",
        "model": "HuBERT + MLP",
        "n_test": "56",
        "positive_count": "30",
        "negative_count": "26",
        "threshold": "0.05",
        "roc_auc": "0.58462",
        "balanced_accuracy": "0.57949",
        "f1": "0.72500",
        "precision": "0.58000",
        "recall": "0.96667",
        "specificity": "0.19231",
        "scope": "internal test benchmark with evaluation caveats",
    },
    {
        "track_id": "depression_video",
        "modality": "video",
        "model": "OpenFace + Mamba-3",
        "n_test": "56",
        "positive_count": "30",
        "negative_count": "26",
        "threshold": "0.81",
        "roc_auc": "0.59872",
        "balanced_accuracy": "0.55897",
        "f1": "0.64706",
        "precision": "0.57895",
        "recall": "0.73333",
        "specificity": "0.38462",
        "scope": "internal test benchmark recomputed from predictions",
    },
]


def assert_metrics_match_audited_contract(rows: list[dict[str, str]]) -> None:
    assert len(rows) == len(EXPECTED_METRIC_ROWS), "unexpected physical CSV row count"
    track_ids = [row["track_id"] for row in rows]
    assert len(track_ids) == len(set(track_ids)), "duplicate track_id rows"
    assert rows == EXPECTED_METRIC_ROWS


def test_verified_metrics_are_the_audited_public_benchmarks():
    with METRICS_PATH.open(newline="", encoding="utf-8") as metrics_file:
        rows = list(csv.DictReader(metrics_file))

    assert_metrics_match_audited_contract(rows)


def test_metric_contract_rejects_duplicate_track_ids() -> None:
    """Catches duplicate physical rows that dictionary conversion would hide."""
    with METRICS_PATH.open(newline="", encoding="utf-8") as metrics_file:
        rows = list(csv.DictReader(metrics_file))
    duplicated_rows = [*rows, dict(rows[0])]

    with pytest.raises(AssertionError):
        assert_metrics_match_audited_contract(duplicated_rows)


def test_public_evidence_excludes_unsupported_claims_and_values():
    public_evidence = "\n".join(
        evidence_path.read_text(encoding="utf-8")
        for evidence_path in (METRICS_PATH, EVALUATION_PATH)
    ).lower()

    for prohibited_text in ("0.7511", "1.0000", "ready to deploy", "state of the art"):
        assert prohibited_text not in public_evidence
