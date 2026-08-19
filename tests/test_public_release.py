"""Release gate for files that would be published from this repository."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MAX_PUBLIC_FILE_BYTES = 10 * 1024 * 1024


def publishable_paths() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
    )
    return [
        Path(raw_path.decode("utf-8"))
        for raw_path in completed.stdout.split(b"\0")
        if raw_path
    ]


def unresolved_markdown_link_findings(relative_path: Path, text: str) -> list[str]:
    findings: list[str] = []
    targets = re.findall(r"!?\[[^]]*\]\(([^)]+)\)", text)
    targets.extend(
        first or second
        for first, second in re.findall(
            r"(?m)^\s*\[[^]]+\]:\s*(?:<([^>]+)>|(\S+))", text
        )
    )
    for target in targets:
        target = target.strip().strip("<>")
        if target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        local_target = target.split("#", maxsplit=1)[0].split("?", maxsplit=1)[0]
        candidate = (REPOSITORY_ROOT / relative_path.parent / local_target).resolve()
        if not candidate.is_relative_to(REPOSITORY_ROOT) or not candidate.exists():
            findings.append(
                f"{relative_path.as_posix()}: unresolved local Markdown link {target}"
            )
    return findings


def text_release_findings(relative_path: Path, text: str) -> list[str]:
    secret_assignment = re.compile(
        r"(?i)\b(?:"
        + r"(?:api|access|secret|auth|bearer|github|groq|openai)"
        + r"[ _-]*(?:api[ _-]*)?(?:key|token)|"
        + r"pass(?:word|wd)|pwd|credentials?|"
        + r"aws[ _-]*(?:access[ _-]*key[ _-]*id|secret[ _-]*access[ _-]*key)"
        + r")\b\s*[:=]\s*[^\s#]+"
    )
    secret_prefix = re.compile(
        r"(?i)\b(?:gh" + "p_|gho_|ghu_|ghs_|ghr_|gsk_|sk-" + r")[a-z0-9_-]{8,}"
    )
    bearer_value = re.compile(r"(?i)\bbear" + r"er\s+[a-z0-9._-]{8,}")
    aws_access_key_prefix = re.compile(r"\b" + "AK" + "IA" + r"[A-Z0-9]{16}\b")
    private_key_header = re.compile(
        r"-{5}BEGIN (?:[A-Z0-9 ]+ )?" + "PRIV" + "ATE KEY" + r"-{5}"
    )
    private_ipv4 = re.compile(
        r"\b(?:"
        + r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
        + r"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|"
        + r"192\.168\.\d{1,3}\.\d{1,3})\b"
    )
    windows_user_path = re.compile(r"(?i)\b[a-z]:[\\/]" + "users" + r"[\\/]")
    # Treat D: through Z: roots as potentially mapped; allow C: system paths except user homes.
    mapped_drive_path = re.compile(r"(?i)\b[d-z]:[\\/]")
    remote_path = re.compile(r"(?i)(?:" + "raidrive|webdav" + r")[\\/:]")
    text_rules = {
        "secret assignment": secret_assignment,
        "secret key/token prefix": secret_prefix,
        "bearer token": bearer_value,
        "AWS access-key prefix": aws_access_key_prefix,
        "private-key material": private_key_header,
        "RFC1918 IPv4 address": private_ipv4,
        "Windows user-home path": windows_user_path,
        "mapped-drive path": mapped_drive_path,
        "RaiDrive" + "/" + "WebDAV path": remote_path,
    }

    findings: list[str] = []
    normalized = relative_path.as_posix()
    for rule, pattern in text_rules.items():
        if pattern.search(text):
            findings.append(f"{normalized}: {rule}")
    findings.extend(unresolved_markdown_link_findings(relative_path, text))
    return findings


def release_findings(paths: list[Path]) -> list[str]:
    secret_filenames = {"." + "env", "." + "env" + ".local", "." + "env" + ".production"}
    secret_like_stems = {
        "credential",
        "credentials",
        "secret",
        "secrets",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
    }
    secret_like_extensions = {".key", ".pem"}
    forbidden_directories = {
        "received" + "_sessions",
        "da" + "ta",
        "data" + "sets",
        "ca" + "che",
        ".super" + "powers",
    }
    forbidden_extensions = {
        ".w" + "av",
        ".m" + "p3",
        ".m" + "4a",
        ".f" + "lac",
        ".o" + "gg",
        ".j" + "pg",
        ".j" + "peg",
        ".w" + "ebp",
        ".m" + "p4",
        ".m" + "ov",
        ".a" + "vi",
        ".m" + "kv",
        ".w" + "ebm",
        ".g" + "if",
        ".n" + "py",
        ".n" + "pz",
        ".p" + "t",
        ".p" + "th",
        ".c" + "kpt",
        ".o" + "nnx",
        ".h" + "5",
        ".h" + "df5",
        ".p" + "kl",
        ".p" + "ickle",
        ".j" + "oblib",
        ".t" + "ask",
        ".h" + "wp",
        ".p" + "df",
        ".x" + "lsx",
        ".z" + "ip",
        ".t" + "ar",
        ".t" + "ar.gz",
        ".t" + "gz",
        ".7" + "z",
        ".r" + "ar",
    }
    findings: list[str] = []
    for relative_path in paths:
        normalized = relative_path.as_posix()
        parts = {part.casefold() for part in relative_path.parts}
        name = relative_path.name.casefold()
        absolute_path = REPOSITORY_ROOT / relative_path

        if name in secret_filenames:
            findings.append(f"{normalized}: secret filename")
        elif (
            name.split(".", maxsplit=1)[0] in secret_like_stems
            or relative_path.suffix.casefold() in secret_like_extensions
        ):
            findings.append(f"{normalized}: secret-like filename")
        if forbidden_directories & parts:
            findings.append(f"{normalized}: sensitive directory")
        matched_extension = next(
            (
                extension
                for extension in sorted(forbidden_extensions, key=len, reverse=True)
                if name.endswith(extension)
            ),
            None,
        )
        if matched_extension is not None:
            findings.append(f"{normalized}: forbidden extension {matched_extension}")
        if relative_path.suffix.casefold() == ".png" and normalized != "assets/hero.png":
            findings.append(f"{normalized}: unexpected PNG")
        if absolute_path.stat().st_size > MAX_PUBLIC_FILE_BYTES:
            findings.append(f"{normalized}: exceeds 10 MiB")

        try:
            text = absolute_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            if normalized != "assets/hero.png":
                findings.append(f"{normalized}: unexpected binary file")
            continue

        findings.extend(text_release_findings(relative_path, text))

    return findings


def test_unresolved_local_markdown_link_is_a_release_finding() -> None:
    """A published Markdown link must resolve to a file in the repository."""
    findings = unresolved_markdown_link_findings(
        Path("README.md"), "[" + "missing" + "]" + "(" + "not-present.md" + ")"
    )
    assert findings == ["README.md: unresolved local Markdown link not-present.md"]


def test_text_rules_reject_reviewed_private_paths_and_secret_assignments() -> None:
    """Mapped drives, user homes, and provider-key assignments block a release."""
    text = "\n".join(
        [
            "Z:" + "\\" + "private-share",
            "Z:" + "/" + "share",
            "C:" + "/" + "Users" + "/" + "person",
            "C:" + "\\" + "Users" + "\\" + "person",
            "OPEN" + "AI_API_KEY=" + "example-value",
            "GROQ" + "_API_KEY=" + "example-value",
        ]
    )

    assert text_release_findings(Path("notes.md"), text) == [
        "notes.md: secret assignment",
        "notes.md: Windows user-home path",
        "notes.md: mapped-drive path",
    ]
    assert text_release_findings(Path("notes.md"), "Z:" + "\\" + "private-share") == [
        "notes.md: mapped-drive path"
    ]
    assert text_release_findings(Path("notes.md"), "Z:" + "/" + "share") == [
        "notes.md: mapped-drive path"
    ]
    assert text_release_findings(
        Path("notes.md"), "C:" + "/" + "Users" + "/" + "person"
    ) == ["notes.md: Windows user-home path"]
    assert text_release_findings(
        Path("notes.md"), "C:" + "\\" + "Users" + "\\" + "person"
    ) == ["notes.md: Windows user-home path"]
    assert text_release_findings(
        Path("notes.md"), "OPEN" + "AI_API_KEY=" + "example-value"
    ) == ["notes.md: secret assignment"]
    assert text_release_findings(
        Path("notes.md"), "GROQ" + "_API_KEY=" + "example-value"
    ) == ["notes.md: secret assignment"]


def test_text_rules_allow_relative_paths_and_system_local_c_drive_paths() -> None:
    """Relative paths and C system paths are not treated as private mapped drives."""
    text = "\n".join(
        ["docs/evaluation.md", "C:" + "\\" + "Windows" + "\\" + "System32"]
    )

    assert text_release_findings(Path("notes.md"), text) == []


@pytest.mark.parametrize(
    ("sensitive_text", "expected_rule"),
    [
        ("pass" + "word=correct-horse-battery-staple", "secret assignment"),
        (
            "AWS_ACCESS_KEY_" + "ID=" + "AK" + "IA" + "ABCDEFGHIJKLMNOP",
            "secret assignment",
        ),
        (
            "AWS_SECRET_ACCESS_" + "KEY=private-value",
            "secret assignment",
        ),
        ("creden" + "tials: private-value", "secret assignment"),
        (
            "-----BEGIN PRIVATE " + "KEY-----",
            "private-key material",
        ),
        ("AK" + "IA" + "ABCDEFGHIJKLMNOP", "AWS access-key prefix"),
    ],
)
def test_text_rules_reject_common_credentials_and_private_keys(
    sensitive_text: str, expected_rule: str
) -> None:
    """Common credentials and private-key material must block publication."""
    findings = text_release_findings(Path("notes.txt"), sensitive_text)

    assert f"notes.txt: {expected_rule}" in findings


def test_release_gate_rejects_secret_like_filenames(tmp_path, monkeypatch) -> None:
    """A force-added credential file is unsafe even when its content is harmless."""
    relative_path = Path("creden" + "tials.json")
    (tmp_path / relative_path).write_text("{}", encoding="utf-8")
    monkeypatch.setattr("test_public_release.REPOSITORY_ROOT", tmp_path)

    findings = release_findings([relative_path])

    assert findings == [f"{relative_path.as_posix()}: secret-like filename"]


@pytest.mark.parametrize(
    "relative_path",
    [
        Path("model.npy"),
        Path("model.npz"),
        Path("model.pt"),
        Path("model.pth"),
        Path("model.ckpt"),
        Path("model.onnx"),
        Path("model.h5"),
        Path("model.hdf5"),
        Path("model.pkl"),
        Path("model.pickle"),
        Path("model.joblib"),
        Path("bundle.zip"),
        Path("bundle.tar"),
        Path("bundle.tar.gz"),
        Path("bundle.tgz"),
        Path("bundle.7z"),
        Path("bundle.rar"),
    ],
)
def test_release_gate_rejects_every_ignored_model_data_and_archive_format(
    relative_path: Path, tmp_path, monkeypatch
) -> None:
    """Ignore rules are not a safety boundary for force-added artifacts."""
    (tmp_path / relative_path).write_text("synthetic", encoding="utf-8")
    monkeypatch.setattr("test_public_release.REPOSITORY_ROOT", tmp_path)

    findings = release_findings([relative_path])

    expected_suffix = ".tar.gz" if relative_path.name.endswith(".tar.gz") else relative_path.suffix
    assert f"{relative_path.as_posix()}: forbidden extension {expected_suffix}" in findings


def test_release_gate_rejects_unknown_non_utf8_binary(tmp_path, monkeypatch) -> None:
    """Unknown binary formats must fail closed even when they are under 10 MiB."""
    relative_path = Path("mystery.blob")
    (tmp_path / relative_path).write_bytes(b"\xff\xfe\x00\x80")
    monkeypatch.setattr("test_public_release.REPOSITORY_ROOT", tmp_path)

    findings = release_findings([relative_path])

    assert findings == [f"{relative_path.as_posix()}: unexpected binary file"]


def test_release_gate_allows_only_the_approved_binary_hero(tmp_path, monkeypatch) -> None:
    """The exact approved hero path remains the sole binary allowlist entry."""
    relative_path = Path("assets/hero.png")
    (tmp_path / relative_path).parent.mkdir(parents=True)
    (tmp_path / relative_path).write_bytes(b"\xff\xfe\x00\x80")
    monkeypatch.setattr("test_public_release.REPOSITORY_ROOT", tmp_path)

    assert release_findings([relative_path]) == []


def test_release_gate_allows_env_example_ordinary_prose_and_relative_paths(
    tmp_path, monkeypatch
) -> None:
    """Safe documentation and the non-secret environment template remain publishable."""
    paths_and_text = {
        Path(".env.example"): "MINDSCOPE_MODEL_DIR=./models\nOPENFACE_BIN=\n",
        Path("notes.md"): (
            "Document password rotation and credential handling without including values.\n"
            "Use docs/evaluation.md and ./models as relative paths.\n"
        ),
    }
    for relative_path, contents in paths_and_text.items():
        (tmp_path / relative_path).write_text(contents, encoding="utf-8")
    monkeypatch.setattr("test_public_release.REPOSITORY_ROOT", tmp_path)

    assert release_findings(list(paths_and_text)) == []


def test_reference_style_markdown_link_is_a_release_finding() -> None:
    """Reference-style local links must resolve just like inline Markdown links."""
    text = "[" + "guide" + "]: " + "not-present.md"

    findings = unresolved_markdown_link_findings(Path("README.md"), text)

    assert findings == ["README.md: unresolved local Markdown link not-present.md"]


def test_publishable_files_pass_public_release_gate() -> None:
    """A credential, private path, restricted asset, or oversized file blocks release."""
    findings = release_findings(publishable_paths())
    assert findings == [], "Public release findings:\n" + "\n".join(findings)
