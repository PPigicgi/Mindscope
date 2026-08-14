import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = PROJECT_ROOT / "results" / "verified_metrics.csv"
EVALUATION_PATH = PROJECT_ROOT / "docs" / "evaluation.md"


EXPECTED_METRICS = {
    "dementia_audio": {
        "n_test": "412",
        "positive_count": "183",
        "negative_count": "229",
        "threshold": "0.39",
        "roc_auc": "0.76515",
        "balanced_accuracy": "0.72804",
        "f1": "0.71212",
        "specificity": "0.68559",
    },
    "depression_audio": {
        "n_test": "56",
        "positive_count": "30",
        "negative_count": "26",
        "threshold": "0.05",
        "roc_auc": "0.58462",
        "balanced_accuracy": "0.57949",
        "f1": "0.72500",
        "specificity": "0.19231",
    },
    "depression_video": {
        "n_test": "56",
        "positive_count": "30",
        "negative_count": "26",
        "threshold": "0.81",
        "roc_auc": "0.59872",
        "balanced_accuracy": "0.55897",
        "f1": "0.64706",
        "specificity": "0.38462",
    },
}


def test_verified_metrics_are_the_audited_public_benchmarks():
    with METRICS_PATH.open(newline="", encoding="utf-8") as metrics_file:
        rows = list(csv.DictReader(metrics_file))

    metrics_by_track = {row["track_id"]: row for row in rows}
    assert set(metrics_by_track) == set(EXPECTED_METRICS)

    for track_id, expected_metrics in EXPECTED_METRICS.items():
        for metric_name, expected_value in expected_metrics.items():
            assert metrics_by_track[track_id][metric_name] == expected_value


def test_public_evidence_excludes_unsupported_claims_and_values():
    public_evidence = "\n".join(
        evidence_path.read_text(encoding="utf-8")
        for evidence_path in (METRICS_PATH, EVALUATION_PATH)
    ).lower()

    for prohibited_text in ("0.7511", "1.0000", "ready to deploy", "state of the art"):
        assert prohibited_text not in public_evidence
