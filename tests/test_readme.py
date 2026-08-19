import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

import pytest


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
EXPECTED_VERIFIED_RESULT_ROWS = (
    (
        "Internal benchmark",
        "Dementia audio",
        "HuBERT + XGBoost",
        "n=412",
        "0.765",
        "0.728",
        "0.712",
        "0.686",
    ),
    (
        "Internal benchmark",
        "Depression audio",
        "HuBERT + MLP",
        "n=56",
        "0.585",
        "0.579",
        "0.725",
        "0.192",
    ),
    (
        "Internal benchmark",
        "Depression video",
        "OpenFace + Mamba-3",
        "n=56",
        "0.599",
        "0.559",
        "0.647",
        "0.385",
    ),
)


def readme_text() -> str:
    return README.read_text(encoding="utf-8") if README.exists() else ""


def assert_verified_results_contract(text: str) -> None:
    """Bind every published metric to its scope, track, and selected model."""
    header = (
        "| Scope | Track | Model | Test n | ROC-AUC | Balanced accuracy | F1 |"
        " Specificity |"
    )
    lines = text.splitlines()
    assert header in lines, "README is missing the Verified Results table header"
    header_index = lines.index(header)

    parsed_rows = []
    for line in lines[header_index + 2 :]:
        if not line.startswith("|"):
            break
        cells = tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
        assert len(cells) == 8, f"unexpected Verified Results row shape: {line}"
        parsed_rows.append(cells)

    assert tuple(parsed_rows) == EXPECTED_VERIFIED_RESULT_ROWS


def test_required_sections_appear_in_recruiter_first_order() -> None:
    text = readme_text()
    headings = [
        "한국어 요약",
        "System Architecture",
        "My Role",
        "Verified Results",
        "STAR Case Study",
        "Engineering Highlights",
        "Reproduction",
        "Limitations & Ethics",
        "Team Credits",
    ]

    positions = []
    for heading in headings:
        marker = f"## {heading}"
        assert marker in text, f"missing required heading: {marker}"
        positions.append(text.index(marker))

    assert positions == sorted(positions), "required headings are out of order"


def test_first_screen_stack_and_nix_introduction_match_the_brand_contract() -> None:
    """Catches missing stack signals or an unexplained first use of the device name."""
    text = readme_text()
    first_screen = text.split("## 한국어 요약", maxsplit=1)[0]

    for technology in (
        "Python",
        "PyTorch",
        "FastAPI",
        "Jetson",
        "HuBERT",
        "Mamba",
        "XGBoost",
        "OpenFace",
    ):
        assert technology in first_screen, f"first-screen stack is missing {technology}"

    first_nix_index = text.index("NIX")
    assert text[first_nix_index:].startswith("NIX, a Jetson-based edge device")


def test_required_scope_hardware_role_and_metrics_are_present() -> None:
    text = readme_text()
    required_literals = [
        "ML/AI Integration Lead",
        "NVIDIA Jetson Orin Nano Super",
        "IMX477 camera module",
        "ReSpeaker microphone array",
        "stereo speakers",
        "Research prototype — not a medical diagnosis.",
    ]

    missing = [literal for literal in required_literals if literal not in text]
    assert not missing, f"README is missing required literals: {missing}"
    assert_verified_results_contract(text)


def test_verified_results_contract_rejects_auc_values_swapped_between_models() -> None:
    """Catches intact metric literals attached to the wrong benchmark row."""
    text = readme_text()
    mutated = text.replace("| n=412 | 0.765 |", "| n=412 | 0.585 |").replace(
        "| n=56 | 0.585 |", "| n=56 | 0.765 |", 1
    )
    assert mutated != text

    with pytest.raises(AssertionError):
        assert_verified_results_contract(mutated)


def test_every_local_markdown_target_exists() -> None:
    text = readme_text()
    assert README.exists(), "README.md does not exist"

    targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text)
    missing = []
    for raw_target in targets:
        target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
        if target.startswith(("http://", "https://", "#")):
            continue
        local_path = ROOT / unquote(target.split("#", maxsplit=1)[0])
        if not local_path.exists():
            missing.append(target)

    assert not missing, f"missing local Markdown targets: {missing}"


def test_readme_avoids_unsupported_or_clinical_claims() -> None:
    text = readme_text()
    lowered = text.casefold()

    for forbidden in ["0.7511", "ready to deploy", "state of the art", "clinically proven"]:
        assert forbidden not in lowered, f"unsupported claim found: {forbidden}"

    medical_device_claims = lowered.replace("not a medical device", "")
    assert "medical device" not in medical_device_claims


def test_architecture_input_connectors_enter_nix_top_edge() -> None:
    tree = ET.parse(ROOT / "assets" / "architecture.svg")
    paths = {
        path.get("data-flow"): path
        for path in tree.findall(".//{http://www.w3.org/2000/svg}path")
        if path.get("data-flow") in {"camera-to-nix", "microphone-to-nix"}
    }

    assert set(paths) == {"camera-to-nix", "microphone-to-nix"}
    for connector_name, path in paths.items():
        assert path.get("marker-end") == "url(#arrow)", connector_name
        route = re.fullmatch(
            r"M[\d.]+ 210 V(?P<bend_y>[\d.]+) H(?P<x>[\d.]+) V(?P<y>[\d.]+)",
            path.get("d", ""),
        )
        assert route is not None, f"{connector_name} lacks a final vertical segment"
        assert float(route.group("bend_y")) < 258
        assert 85 <= float(route.group("x")) <= 315
        assert float(route.group("y")) == 258
