# MindScope Public Portfolio Design

## 1. Purpose

Build a public GitHub portfolio repository for **MindScope**, a team-built multimodal mental-health screening research prototype. The repository targets AI/ML recruiters and technical interviewers. It must demonstrate end-to-end engineering—from NIX edge hardware and multimodal capture to PC inference, spoken responses, and a web dashboard—without publishing restricted datasets, personal recordings, secrets, internal network details, or unsupported medical claims.

The repository is a curated portfolio, not a backup of the 17.65 GB source archive and not a clinically validated diagnostic product.

## 2. Audience and Narrative

The primary audience is an AI/ML hiring manager or technical interviewer scanning the repository for 30 seconds before deciding whether to read further.

The opening follows the approved **Systems-first** direction:

1. Hero and concise Korean summary
2. System architecture
3. Personal role and team boundaries
4. Verified results
5. Situation–Task–Action–Result case study
6. Engineering details and selected code
7. Reproduction instructions
8. Limitations, ethics, and data governance

The main README is written in English, with a short Korean summary near the top. “Simulator” is not used; the standard case-study term is **Situation**.

## 3. Brand and Naming

- Project name: **MindScope**
- Edge device name: **NIX**
- Subtitle: **Multimodal screening, from edge sensors to inference**
- NIX is introduced once as “NIX, a Jetson-based edge device.”
- All public copy uses “screening research prototype,” “risk signal,” or “model output.” It does not use “medical diagnosis,” “clinical proof,” or “ready to deploy.”

## 4. Team Attribution

The author’s public role is **ML/AI Integration Lead**.

Credited responsibilities:

- Led model experiments and model comparison
- Built multimodal audio/video data-processing paths
- Implemented or integrated the PC inference API
- Connected NIX capture, PC inference, spoken response, and dashboard output
- Contributed to product design

Explicit team boundaries:

- Product planning was led by other teammate(s)
- Physical design and 3D printing were handled by another teammate
- The README must not imply sole authorship of the complete product

## 5. Verified System Architecture

### NIX edge device

- NVIDIA Jetson Orin Nano Super
- IMX477 camera module; the README avoids a more specific manufacturer claim until the hardware label is independently confirmed
- ReSpeaker microphone array; the exact ReSpeaker SKU is not claimed
- Stereo speakers

### Data flow

1. NIX captures camera frames and microphone audio.
2. NIX sends a session payload to the MindScope PC server.
3. The PC server performs local speech-to-text, quality checks, feature extraction, and available model inference.
4. A spoken response is returned to NIX and played through stereo speakers.
5. Screening outputs are exposed separately to the project’s web dashboard.

### ML and server components

- Whisper for local speech-to-text
- HuBERT embeddings for audio tracks
- OpenFace action units, pose, and gaze for the video track
- XGBoost for the selected dementia-audio classifier
- MLP for the selected depression-audio classifier
- Mamba sequence model for the selected depression-video track
- YOLO/MediaPipe components for face localization and landmarks
- FastAPI-based PC inference service

The public architecture diagram uses a deterministic SVG or Mermaid flow rather than an AI-generated technical diagram. An optional raster hero may be AI-generated, but it must contain no labels, metrics, faces, medical symbols implying clinical certification, or fabricated hardware details.

## 6. Defensible Results

The README displays only metrics supported by machine-readable result files and the final audit. Each row includes the evaluated sample count, split description, AUC, balanced accuracy, and F1 where available.

Initial evidence set:

| Track | Selected model | Test AUC | Balanced accuracy | F1 | Evaluation note |
|---|---|---:|---:|---:|---|
| Dementia audio | HuBERT + XGBoost | 0.7651 | 0.7280 | 0.7121 | Internal held-out evaluation; sample count and split wording taken from the metrics audit |
| Depression audio | HuBERT + MLP | 0.5846 | 0.5795 | 0.7250 | Internal 56-session evaluation; threshold-selection leakage risk disclosed |
| Depression video | OpenFace + Mamba-3 | 0.5987 | 0.5782 | 0.6567 | Internal 56-session reevaluation; not the historical 0.7511 dashboard value |

The final README must reconcile exact threshold values and sample counts against the audit before publication.

Excluded claims:

- F1 or AUC of 1.0 from the synthetic 80-sample demonstration
- “Ready to Deploy” and “clinical proof” language
- Historical Mamba AUC 0.7511 as a verified headline result
- Any claim that SHAP alignment demonstrates causality or clinical validity
- Latency, throughput, or memory numbers that are not reproduced on the published code path

The README emphasizes that the strongest portfolio result is the end-to-end ML system and honest evaluation practice, not state-of-the-art medical performance.

## 7. README Content Design

### Hero

- Project name, subtitle, one-sentence research disclaimer
- Badges for Python, PyTorch, FastAPI, Jetson, HuBERT, Mamba, XGBoost, and OpenFace
- A compact Korean summary of the system and personal contribution

### Architecture

Show this flow without private IP addresses:

`Camera + ReSpeaker → NIX Edge Capture → MindScope PC Inference → Spoken Response + Web Dashboard`

Branch the PC inference stage into:

- STT and quality gate
- Audio feature extraction and two audio classifiers
- Video feature extraction and video classifier

### Personal contribution

Use a compact “Owned / Collaborated” table so attribution is visible without reading prose.

### Verified results

Use one small comparison table and link to `docs/evaluation.md` for split, threshold, leakage, and limitation details.

### STAR case study

- **Situation:** research models, edge capture, server inference, and user-facing outputs existed as disconnected concerns.
- **Task:** turn multimodal NIX sessions into an auditable edge-to-server screening workflow.
- **Action:** benchmark models; build audio/video processing; add quality gates and missing-modality handling; expose inference through FastAPI; connect NIX, spoken response, and dashboard paths.
- **Result:** integrate three analysis tracks into one session API and demonstrate an edge–server loop, while documenting model limitations and data-governance constraints.

### Engineering details

Describe:

- Minimum-duration and RMS audio quality gate
- Missing modality returns `skipped` rather than a fabricated score
- OpenFace extraction and fallback behavior
- Typed public request/response example with synthetic identifiers and values
- Configuration through environment variables, with no real host or key

### Reproduction

Provide a safe, lightweight demonstration that does not require the restricted E-DAIC/DAIC-WOZ archive, personal sessions, or unpublished model weights. The demo validates request schemas, quality-gate behavior, metric provenance, and a deterministic mock inference path. Real training and evaluation commands are documented separately and explicitly require users to obtain datasets under their original terms.

## 8. Public Repository Structure

```text
mindscope/
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── requirements.txt
├── assets/
│   ├── hero.png
│   ├── architecture.svg
│   └── verified-results.svg
├── docs/
│   ├── evaluation.md
│   ├── system-design.md
│   ├── ethics-and-limitations.md
│   └── superpowers/
│       ├── specs/
│       └── plans/
├── src/
│   └── mindscope/
│       ├── __init__.py
│       ├── schemas.py
│       ├── quality.py
│       └── demo_pipeline.py
├── results/
│   └── verified_metrics.csv
├── examples/
│   ├── session_request.json
│   └── session_response.json
└── tests/
    ├── test_quality.py
    ├── test_demo_pipeline.py
    ├── test_metrics.py
    └── test_public_release.py
```

The public code is a clean, runnable portfolio slice. Large or dependency-heavy research scripts may be summarized and linked in documentation only when they cannot be made reproducible without restricted assets. Any selected source copied from the archive is sanitized and reviewed before inclusion.

## 9. Data and Secret Exclusion Policy

Never publish:

- `.env` files, API keys, passwords, tokens, credentials, or authentication material
- `PC_server/received_sessions/**`
- WAV/MP3 recordings, face frames, participant images, transcripts, or result JSON tied to a real session
- E-DAIC, DAIC-WOZ, dementia-challenge, or custom YOLO dataset contents
- `experiments/cache/**`, NumPy caches, checkpoints, PyTorch weights, MediaPipe task files, or pretrained model binaries
- Private/internal IP addresses, hostnames, WebDAV URLs, Windows absolute paths, or user names
- HWP/PDF/XLSX submission documents and personal reports
- `.agents/**`, temporary agent workspaces, browser-brainstorm state, `__pycache__`, test caches, logs, or debug captures

The original detected Groq key must be revoked and replaced outside this repository. No secret value is copied or echoed during curation.

## 10. Safety and Ethics

- The project is not a medical device and does not provide a diagnosis.
- Metrics are internal experimental results, not external clinical validation.
- Depression-audio threshold selection has a known leakage risk and is disclosed.
- Small, imbalanced datasets limit generalization.
- Audio/video sessions are sensitive biometric and health-related data and remain outside the public repository.
- A real deployment requires consent, secure retention, access control, bias evaluation, calibration, and prospective clinical validation.

## 11. Validation and Release Gates

Publication is blocked unless all checks pass:

1. Unit tests for quality gates and missing-modality behavior
2. Metric CSV values match the cited README table
3. Public-release test rejects forbidden file extensions, large files, secret-like filenames, private hosts, absolute paths, and received-session content
4. Recursive secret-pattern scan returns no findings
5. No tracked file exceeds 10 MB
6. Markdown links and image references resolve locally
7. Python files compile and the lightweight demo runs from a clean environment
8. Git history contains only curated files; the 17.65 GB source tree is never staged
9. Final AI/ML interviewer review approves attribution, metric language, reproduction instructions, and limitations

## 12. GitHub Publication

- Preferred repository name: `mindscope`
- Visibility: public
- Default branch: `main`
- Description: `Multimodal mental-health screening research prototype connecting NIX edge capture, ML inference, and a web dashboard.`
- The first public release is pushed only after the validation gates pass.
- If `mindscope` already exists under the authenticated account, use `mindscope-nix` rather than overwriting an unrelated repository.

