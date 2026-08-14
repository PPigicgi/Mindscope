# MindScope Public Portfolio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a small, credible, public MindScope repository that demonstrates the NIX edge-to-server ML workflow with synthetic-only runnable code, audited metrics, recruiter-first documentation, and automated privacy/release gates.

**Architecture:** Create a clean public slice instead of copying the 17.65 GB research archive. The slice implements request validation, audio quality gating, modality-aware orchestration, and a FastAPI demo endpoint without shipping trained weights or private data; documentation links this safe demo to the audited research system and discloses evaluation limitations.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, pytest, standard-library CSV/JSON/WAV processing, SVG, Git, GitHub.

## Global Constraints

- Project name is `MindScope`; edge-device name is `NIX` in uppercase.
- Main README is English with a short Korean summary near the top.
- Position the system as a `screening research prototype`, never a diagnosis or clinically validated product.
- Personal role is `ML/AI Integration Lead`; product planning and physical design/3D printing are credited to teammates.
- Hardware wording is exactly: NVIDIA Jetson Orin Nano Super, IMX477 camera module, ReSpeaker microphone array, and stereo speakers.
- Never publish `.env`, keys, credentials, session recordings, face images, transcripts, participant data, model weights, caches, internal IPs, WebDAV hosts, Windows absolute paths, or personal documents.
- No tracked file may exceed 10 MB.
- Do not copy archived server or benchmark files wholesale; publish a synthetic-only clean-room portfolio slice because the audited originals require security hardening and provenance review.
- Verified public metrics are internal benchmarks only: dementia audio AUC `0.76515`, balanced accuracy `0.72804`, F1 `0.71212`, `n=412`, threshold `0.39`; depression audio AUC `0.58462`, balanced accuracy `0.57949`, F1 `0.72500`, specificity `0.19231`, `n=56`, threshold `0.05`; depression video AUC `0.59872`, balanced accuracy `0.55897`, F1 `0.64706`, `n=56`, threshold `0.81`.
- Exclude synthetic-demo F1/AUC `1.0`, historical Mamba AUC `0.7511`, and contradictory `organized_results/best/*.csv` values from public claims.
- Hero art contains no text, human face, patient data, medical-certification imagery, metric gauge, or fabricated hardware detail.
- Architecture and results graphics are deterministic SVG files, not AI-generated technical diagrams.
- The public sample stores no uploads and runs no medical model; it validates inputs and reports model states as `not_available_in_public_demo`.
- Default server binding shown in docs is `127.0.0.1:8001`.
- Repository is public on GitHub with default branch `main`; prefer `mindscope`, fall back to `mindscope-nix` if the former already exists.

---

### Task 1: Build the synthetic-only core and quality gate

**Files:**
- Create: `.gitignore`
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `src/mindscope/__init__.py`
- Create: `src/mindscope/schemas.py`
- Create: `src/mindscope/quality.py`
- Create: `src/mindscope/demo_pipeline.py`
- Create: `tests/test_quality.py`
- Create: `tests/test_demo_pipeline.py`

**Interfaces:**
- Produces: `assess_audio(samples: Sequence[float], sample_rate: int, min_duration_seconds: float = 10.0, min_rms: float = 0.001) -> AudioQuality`
- Produces: `analyze_demo_session(request: SessionRequest) -> SessionResponse`
- `SessionRequest` accepts `subject_id`, `run_id`, `sample_rate`, `audio_samples`, and `video_features`; IDs match `[A-Za-z0-9_-]{1,64}`, video frames have exactly 49 floats, and at most 1,000 frames are accepted.
- `SessionResponse` contains quality metadata and three track states; it never contains a medical score.

- [ ] **Step 1: Write failing quality tests**

Create `tests/test_quality.py` with tests that assert: 10 seconds of amplitude `0.01` at 10 Hz is usable; 9.9 seconds is rejected with reason `audio_too_short`; 10 seconds of amplitude `0.0001` is rejected with reason `audio_too_quiet`; empty samples produce duration and RMS `0.0`; sample rate `0` raises `ValueError("sample_rate must be positive")`.

- [ ] **Step 2: Run the quality tests and verify failure**

Run: `python -m pytest tests/test_quality.py -q`

Expected: collection or import fails because `mindscope.quality` does not exist.

- [ ] **Step 3: Implement the quality gate**

Implement `AudioQuality` as an immutable dataclass with `duration_seconds`, `rms`, `usable`, and `reason`. Compute RMS using `sqrt(sum(x*x)/len(samples))`. Reason precedence is `no_audio`, `audio_too_short`, `audio_too_quiet`, then `ok`. Round public duration to three decimals and RMS to six decimals.

- [ ] **Step 4: Write failing orchestration tests**

Create `tests/test_demo_pipeline.py` with exact cases:

```python
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
```

Also assert invalid identifiers, a 48-column video frame, more than 1,000 frames, and more than 60 seconds of audio are rejected by Pydantic validation.

- [ ] **Step 5: Implement schemas and orchestration**

Use Pydantic v2 models with `extra="forbid"`. Set `MAX_AUDIO_SECONDS = 60`, `VIDEO_FEATURE_DIM = 49`, and `MAX_VIDEO_FRAMES = 1000`. Track objects have only `status` and `reason`. For usable input, return `not_available_in_public_demo`; for absent or failed-quality modalities, return `skipped` with the exact quality or missing reason. Never write files and never calculate a screening score.

- [ ] **Step 6: Add dependency and ignore configuration**

Create `requirements.txt`:

```text
fastapi>=0.115,<1
pydantic>=2.9,<3
uvicorn>=0.30,<1
httpx>=0.27,<1
pytest>=8,<10
```

Create `pyproject.toml` with project name `mindscope-public-demo`, version `0.1.0`, Python requirement `>=3.11`, setuptools package discovery under `src`, and pytest option `pythonpath = ["src"]` so every documented test command works from a clean checkout without an editable install.

Create `.gitignore` that blocks Python caches and virtual environments plus `.env*` with an explicit `!.env.example` exception, audio/video/image formats with an explicit `!assets/hero.png` exception, NumPy caches, model/checkpoint formats, `data/`, `datasets/`, `received_sessions/`, `experiments/cache/`, `.superpowers/`, and archive formats.

- [ ] **Step 7: Run core tests**

Run: `python -m pytest tests/test_quality.py tests/test_demo_pipeline.py -q`

Expected: all tests pass.

- [ ] **Step 8: Commit the core**

```bash
git add .gitignore pyproject.toml requirements.txt src/mindscope tests/test_quality.py tests/test_demo_pipeline.py
git commit -m "feat: add safe public demo pipeline"
```

---

### Task 2: Add audited evidence and evaluation documentation

**Files:**
- Create: `results/verified_metrics.csv`
- Create: `docs/evaluation.md`
- Create: `tests/test_metrics.py`

**Interfaces:**
- `results/verified_metrics.csv` is the single source for public numeric claims.
- `docs/evaluation.md` cites each row and explains split, threshold, class balance, specificity, leakage, model-selection bias, and internal-benchmark scope.

- [ ] **Step 1: Write the failing evidence test**

Create `tests/test_metrics.py` that loads the CSV using `csv.DictReader`, requires exactly the track IDs `dementia_audio`, `depression_audio`, and `depression_video`, and asserts exact decimal strings for `n_test`, `threshold`, `roc_auc`, `balanced_accuracy`, `f1`, `specificity`, `positive_count`, and `negative_count`. It must also assert the repository’s public evidence files do not contain `0.7511`, `1.0000`, `Ready to Deploy`, or `state of the art`.

- [ ] **Step 2: Run the evidence test and verify failure**

Run: `python -m pytest tests/test_metrics.py -q`

Expected: failure because `results/verified_metrics.csv` does not exist.

- [ ] **Step 3: Create the canonical metric CSV**

Use this header:

```text
track_id,modality,model,n_test,positive_count,negative_count,threshold,roc_auc,balanced_accuracy,f1,precision,recall,specificity,scope
```

Use exact audited rows:

```text
dementia_audio,audio,HuBERT + XGBoost,412,183,229,0.39,0.76515,0.72804,0.71212,0.66197,0.77049,0.68559,internal held-out test benchmark
depression_audio,audio,HuBERT + MLP,56,30,26,0.05,0.58462,0.57949,0.72500,0.58000,0.96667,0.19231,internal test benchmark with evaluation caveats
depression_video,video,OpenFace + Mamba-3,56,30,26,0.81,0.59872,0.55897,0.64706,0.57895,0.73333,0.38462,internal test benchmark recomputed from predictions
```

- [ ] **Step 4: Write evaluation documentation**

Document the source evidence without publishing private absolute paths. Include confusion matrices, threshold-selection procedure, the HuBERT train-plus-development leakage, test-set model selection, depression-audio low specificity, video 31-versus-49 feature provenance uncertainty, and YOLO validation-only status. State that no confidence interval or external validation is available. Do not headline YOLO results because data provenance and grouping are not publication-ready.

- [ ] **Step 5: Run evidence tests**

Run: `python -m pytest tests/test_metrics.py -q`

Expected: pass.

- [ ] **Step 6: Commit evidence**

```bash
git add results/verified_metrics.csv docs/evaluation.md tests/test_metrics.py
git commit -m "docs: publish audited internal benchmarks"
```

---

### Task 3: Expose a safe API contract and system documentation

**Files:**
- Create: `src/mindscope/api.py`
- Create: `examples/session_request.json`
- Create: `examples/session_response.json`
- Create: `docs/system-design.md`
- Create: `docs/ethics-and-limitations.md`
- Create: `.env.example`
- Create: `tests/test_api.py`

**Interfaces:**
- FastAPI app title is `MindScope Public Demo API`.
- `GET /health` returns `{"status": "ok", "mode": "public_demo"}`.
- `POST /analyze/session` accepts `SessionRequest` and returns `SessionResponse`.
- The public app stores no uploads, accepts no filenames, and binds to localhost in the documented command.

- [ ] **Step 1: Write failing API tests**

Use `fastapi.testclient.TestClient` and assert the health response exactly. Post `examples/session_request.json`, assert HTTP 200, exact IDs, the research disclaimer, audio quality, and three `not_available_in_public_demo` statuses. Assert unknown fields and invalid IDs return HTTP 422.

- [ ] **Step 2: Run API tests and verify failure**

Run: `python -m pytest tests/test_api.py -q`

Expected: import failure because `mindscope.api` does not exist.

- [ ] **Step 3: Implement the API wrapper**

Create a FastAPI app with only `/health` and `/analyze/session`. Delegate all orchestration to `analyze_demo_session`. Add module docstring warning that this synthetic public sample does not load models, persist sessions, or provide a diagnosis.

- [ ] **Step 4: Create synthetic examples**

Use IDs `demo-subject-001` and `demo-run-001`, sample rate `10`, 100 audio values of `0.01`, and one 49-zero video frame. Serialize the actual Pydantic response to produce `examples/session_response.json`; do not hand-edit a divergent example.

- [ ] **Step 5: Write system and ethics docs**

`docs/system-design.md` documents NIX hardware, edge capture, PC STT/feature/model paths, spoken response, web dashboard, quality gate, OpenFace fallback, missing-modality behavior, and why the public demo omits storage and weights. Use `http://localhost:8001` only.

`docs/ethics-and-limitations.md` covers non-diagnostic use, consent, biometric/health-data sensitivity, retention, access control, bias, calibration, leakage, model-selection bias, external validation, and teammate attribution.

`.env.example` contains only non-secret sample values: `MINDSCOPE_HOST=127.0.0.1`, `MINDSCOPE_PORT=8001`, `MINDSCOPE_MODEL_DIR=./models`, and `OPENFACE_BIN=`.

- [ ] **Step 6: Run API tests and compile**

Run: `python -m pytest tests/test_api.py -q`

Run: `python -m compileall -q src`

Expected: both pass.

- [ ] **Step 7: Commit API and documentation**

```bash
git add src/mindscope/api.py examples docs/system-design.md docs/ethics-and-limitations.md .env.example tests/test_api.py
git commit -m "feat: document edge to server demo API"
```

---

### Task 4: Build portfolio visuals and recruiter-first README

**Files:**
- Create: `assets/hero.png`
- Create: `assets/architecture.svg`
- Create: `assets/verified-results.svg`
- Create: `README.md`
- Create: `NOTICE.md`
- Create: `tests/test_readme.py`

**Interfaces:**
- `README.md` follows the approved Systems-first order.
- Every README image uses a repository-relative path.
- SVG metric values are read from or checked against `results/verified_metrics.csv`.
- `NOTICE.md` states that the public demo code is provided for portfolio and research-reference purposes, that third-party models/datasets are not redistributed, and that the repository does not grant rights to team-owned physical/product designs.

- [ ] **Step 1: Generate and inspect the abstract hero**

Use the built-in image-generation tool with this exact design intent: dark navy technical-editorial abstract composition; indigo and cyan multimodal waveform, feature-vector dots, and data ribbons converging toward a neutral insight panel; wide GitHub README banner; no text, no person, no face, no eye, no brain, no medical cross, no risk gauge, no score, no logo, no watermark. Copy the selected project-bound output to `assets/hero.png` and inspect it before use.

- [ ] **Step 2: Write failing README tests**

Create `tests/test_readme.py` to assert all required headings exist in order: `한국어 요약`, `System Architecture`, `My Role`, `Verified Results`, `STAR Case Study`, `Engineering Highlights`, `Reproduction`, `Limitations & Ethics`, `Team Credits`. Assert the README contains `ML/AI Integration Lead`, all four NIX hardware strings, all three sample counts, the exact AUC and balanced-accuracy values rounded to three decimals, and the non-diagnostic disclaimer. Resolve every local Markdown link/image and fail on missing targets.

- [ ] **Step 3: Create deterministic SVG visuals**

`assets/architecture.svg` is a 1,200-pixel-wide horizontal diagram with a dashed privacy boundary around NIX capture, PC inference branches, and separate arrows to NIX speakers and the web dashboard. Use palette `#0B1020`, `#4F46E5`, `#22D3EE`, `#CBD5E1`, with amber only for quality/uncertainty.

`assets/verified-results.svg` is an accessible three-row evidence graphic containing model name, `n`, ROC-AUC, balanced accuracy, and a visible `Internal benchmark` label. It must not use red/green clinical-risk styling.

- [ ] **Step 4: Write the README**

Use the approved order and exact positioning from the design spec. Keep the first screen concise. Include an “Owned / Collaborated” table, the STAR narrative, API curl examples using `localhost`, a compact file tree, installation/run/test commands, links to the three docs, a dataset/weights non-redistribution note, and explicit team credits. Describe the web dashboard as a system output without claiming its source is included. Do not claim real-time latency unless a published reproducible benchmark supports it.

- [ ] **Step 5: Add the rights notice**

Use a conservative no-open-source-license notice because the original project was team work and third-party provenance is incomplete. State: source is visible for portfolio review; no dataset, pretrained model, hardware design, or teammate contribution is relicensed; contact the repository owner before reuse. Do not add MIT, Apache, or another permissive license.

- [ ] **Step 6: Run README tests**

Run: `python -m pytest tests/test_readme.py -q`

Expected: pass.

- [ ] **Step 7: Commit the portfolio presentation**

```bash
git add README.md NOTICE.md assets tests/test_readme.py
git commit -m "docs: present MindScope engineering case study"
```

---

### Task 5: Add public-release gates and validate the repository

**Files:**
- Create: `tests/test_public_release.py`
- Modify: `.gitignore`
- Modify: `README.md`

**Interfaces:**
- Release tests scan tracked/public files without embedding a self-matching secret or private-path literal.
- Release tests fail on forbidden extensions, secret-like filenames, session-data paths, internal hosts, Windows user paths, WebDAV strings, unresolved links, or files larger than 10 MB.

- [ ] **Step 1: Write the failing release test**

Create `tests/test_public_release.py` using `git ls-files --cached --others --exclude-standard -z` to enumerate every publishable tracked or untracked file. Build sensitive patterns from concatenated fragments so the test does not flag its own source. Reject:

- filenames `.env`, `.env.local`, `.env.production`
- directories `received_sessions`, `data`, `datasets`, `cache`, `.superpowers`
- extensions `.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`, `.jpg`, `.jpeg`, `.webp`, `.mp4`, `.npy`, `.npz`, `.pt`, `.pth`, `.pkl`, `.task`, `.hwp`, `.pdf`, `.xlsx`, `.zip`
- any tracked file over `10 * 1024 * 1024` bytes
- common secret assignments and key prefixes
- RFC1918 IPv4 addresses
- Windows user-home, mapped-drive, RaiDrive, or WebDAV path fragments

Allow only `assets/hero.png` among PNG files.

- [ ] **Step 2: Run the release test and inspect every finding**

Run: `python -m pytest tests/test_public_release.py -q`

Expected before final adjustments: either pass or report exact tracked-file findings; do not weaken a rule to silence a real finding.

- [ ] **Step 3: Fix release findings and document the gate**

Remove or sanitize every real finding. Add a “Public release checks” subsection to the README with exact commands. Extend `.gitignore` for any newly discovered sensitive pattern.

- [ ] **Step 4: Run the complete validation suite**

Run:

```bash
python -m pytest -q
python -m compileall -q src tests
git status --short
git ls-files
```

Expected: all tests pass, compilation passes, status contains only intended Task 5 files before commit, and the tracked list contains no source-archive content.

- [ ] **Step 5: Commit release gates**

```bash
git add .gitignore README.md tests/test_public_release.py
git commit -m "test: enforce public portfolio safety"
```

- [ ] **Step 6: Final local release audit**

Run the full suite again from the committed tree, verify `git status -sb` is clean, verify no tracked file exceeds 10 MB, and compare README metrics to `results/verified_metrics.csv` programmatically. Record commands and output in the implementation report.
