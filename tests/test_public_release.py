"""Release gate for files that would be published from this repository."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


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
    for target in re.findall(r"!?\[[^]]*\]\(([^)]+)\)", text):
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


def release_findings(paths: list[Path]) -> list[str]:
    secret_filenames = {"." + "env", "." + "env" + ".local", "." + "env" + ".production"}
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
        ".n" + "py",
        ".n" + "pz",
        ".p" + "t",
        ".p" + "th",
        ".p" + "kl",
        ".t" + "ask",
        ".h" + "wp",
        ".p" + "df",
        ".x" + "lsx",
        ".z" + "ip",
    }
    secret_assignment = re.compile(
        r"(?i)\b(?:api|access|secret|auth|bearer|github|groq|openai)"
        + r"[ _-]*(?:key|token)\b\s*[:=]\s*[^\s#]+"
    )
    secret_prefix = re.compile(
        r"(?i)\b(?:gh" + "p_|gho_|ghu_|ghs_|ghr_|gsk_|sk-" + r")[a-z0-9_-]{8,}"
    )
    bearer_value = re.compile(r"(?i)\bbear" + r"er\s+[a-z0-9._-]{8,}")
    private_ipv4 = re.compile(
        r"\b(?:"
        + r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
        + r"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|"
        + r"192\.168\.\d{1,3}\.\d{1,3})\b"
    )
    windows_user_path = re.compile(r"(?i)\b[a-z]:\\" + "users" + r"\\")
    mapped_drive_path = re.compile(r"(?i)\b[a-z]:\\(?:" + "raidrive|webdav" + r")\\")
    remote_path = re.compile(r"(?i)(?:" + "raidrive|webdav" + r")[\\/:]")
    text_rules = {
        "secret assignment": secret_assignment,
        "secret key/token prefix": secret_prefix,
        "bearer token": bearer_value,
        "RFC1918 IPv4 address": private_ipv4,
        "Windows user-home path": windows_user_path,
        "mapped-drive path": mapped_drive_path,
        "RaiDrive" + "/" + "WebDAV path": remote_path,
    }

    findings: list[str] = []
    for relative_path in paths:
        normalized = relative_path.as_posix()
        parts = {part.casefold() for part in relative_path.parts}
        name = relative_path.name.casefold()
        suffix = relative_path.suffix.casefold()
        absolute_path = REPOSITORY_ROOT / relative_path

        if name in secret_filenames:
            findings.append(f"{normalized}: secret filename")
        if forbidden_directories & parts:
            findings.append(f"{normalized}: sensitive directory")
        if suffix in forbidden_extensions:
            findings.append(f"{normalized}: forbidden extension {suffix}")
        if suffix == ".png" and normalized != "assets/hero.png":
            findings.append(f"{normalized}: unexpected PNG")
        if absolute_path.stat().st_size > MAX_PUBLIC_FILE_BYTES:
            findings.append(f"{normalized}: exceeds 10 MiB")

        try:
            text = absolute_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for rule, pattern in text_rules.items():
            if pattern.search(text):
                findings.append(f"{normalized}: {rule}")
        findings.extend(unresolved_markdown_link_findings(relative_path, text))

    return findings


def test_unresolved_local_markdown_link_is_a_release_finding() -> None:
    """A published Markdown link must resolve to a file in the repository."""
    findings = unresolved_markdown_link_findings(
        Path("README.md"), "[" + "missing" + "]" + "(" + "not-present.md" + ")"
    )
    assert findings == ["README.md: unresolved local Markdown link not-present.md"]


def test_publishable_files_pass_public_release_gate() -> None:
    """A credential, private path, restricted asset, or oversized file blocks release."""
    findings = release_findings(publishable_paths())
    assert findings == [], "Public release findings:\n" + "\n".join(findings)
