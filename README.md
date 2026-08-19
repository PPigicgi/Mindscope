![Abstract multimodal signal banner for MindScope](assets/hero.png)

# MindScope

**Multimodal screening, from edge sensors to inference**

> **Research prototype — not a medical diagnosis.** Results below are internal experimental benchmarks, not clinical validation.

`NIX edge capture` · `FastAPI` · `Whisper` · `HuBERT` · `OpenFace` · `XGBoost / MLP / Mamba`

## 한국어 요약

MindScope는 음성·영상 신호를 연구용 분석 흐름으로 연결한 멀티모달 프로토타입입니다.<br>
NIX는 NVIDIA Jetson Orin Nano Super, IMX477 camera module, ReSpeaker microphone array로 신호를 수집해 PC 추론 서비스로 전달합니다.<br>
PC의 별도 처리 경로는 NIX stereo speakers로 보낼 음성 응답과 웹 대시보드용 스크리닝 출력을 만듭니다.<br>
저는 ML/AI Integration Lead로서 모델 실험, 멀티모달 처리, PC 추론 API, NIX-PC-서비스 연결을 담당하고 제품 디자인에 기여했습니다.<br>
이 결과물은 임상 검증이나 진단을 위한 것이 아니며, 공개 데모에는 실제 데이터와 모델 가중치가 포함되지 않습니다.

## System Architecture

![MindScope architecture from private edge capture to PC inference and separate outputs](assets/architecture.svg)

The privacy boundary encloses NIX capture: the **IMX477 camera module** and **ReSpeaker microphone array** feed the **NVIDIA Jetson Orin Nano Super**. A validated session contract carries available modalities to PC inference, where three explicit branches handle local Whisper STT, audio quality plus HuBERT features for XGBoost/MLP, and OpenFace AU/pose/gaze features for Mamba.

Outputs remain distinct. The interaction path returns a spoken response to the NIX **stereo speakers**; the research screening path targets a web dashboard. The dashboard is an output component of the system, but its source is not included in this repository.

## My Role

| Relationship | Scope |
| --- | --- |
| **Owned — ML/AI Integration Lead** | Model experiments and benchmark comparison; multimodal audio/video processing; PC inference API and integration; NIX-PC-service connection |
| **Collaborated** | Product design decisions and integration feedback |
| **Teammate-owned** | Product planning; physical design and 3D printing |

## Verified Results

![Three verified internal benchmark rows for MindScope](assets/verified-results.svg)

Every row is an **internal benchmark**. Values are rounded to three decimals; the complete metrics, thresholds, confusion matrices, and audit caveats are in the [evaluation notes](docs/evaluation.md).

| Scope | Track | Model | Test n | ROC-AUC | Balanced accuracy | F1 | Specificity |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Internal benchmark | Dementia audio | HuBERT + XGBoost | n=412 | 0.765 | 0.728 | 0.712 | 0.686 |
| Internal benchmark | Depression audio | HuBERT + MLP | n=56 | 0.585 | 0.579 | 0.725 | 0.192 |
| Internal benchmark | Depression video | OpenFace + Mamba-3 | n=56 | 0.599 | 0.559 | 0.647 | 0.385 |

The depression-audio threshold produced low specificity (0.192), so its F1 and recall must not be read in isolation. These selected-model results are exploratory: development leakage, test-set model selection, small samples, and absent confidence intervals limit interpretation.

## STAR Case Study

### Situation

Research models, edge capture, server inference, and user-facing outputs were disconnected concerns, making session behavior and model availability difficult to audit as one system.

### Task

Turn multimodal NIX sessions into an auditable edge-to-server research workflow while keeping model limitations and missing inputs explicit.

### Action

I benchmarked candidate models; built audio and video processing paths; added audio-quality and missing-modality states; exposed the session contract through FastAPI; and connected the NIX response and dashboard paths to the PC service boundary.

### Result

Three analysis tracks were integrated into one session contract and an edge-server loop, with spoken and dashboard outputs separated and evaluation limitations disclosed.

## Engineering Highlights

- **Audio quality gate:** checks duration and RMS before any audio track can proceed.
- **Modality-aware skip:** missing or unusable modalities become explicit `skipped` states with reasons instead of fabricated predictions.
- **Public demo route boundary:** localhost FastAPI routes validate synthetic in-memory arrays and never load research weights or emit scores.
- **49-D video contract:** the public API validates fixed-width OpenFace-style AU/pose/gaze vectors; archived extraction provenance remains an evaluation caveat.
- **Synthetic-only examples:** request and response fixtures contain no recordings, frames, transcripts, personal data, or private host details.
- **Private artifacts stay private:** real datasets, trained weights, and participant-level materials are not shipped.

## Reproduction

Requirements: Python 3.11+ and a shell. The public demo is deterministic contract and quality-gate code; it does not reproduce the private research models.

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

POSIX shell:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Start the local service:

```bash
uvicorn mindscope.api:app --app-dir src --host 127.0.0.1 --port 8001
```

From another shell, post the [synthetic JSON fixture](examples/session_request.json):

```bash
curl -sS -X POST http://127.0.0.1:8001/analyze/session \
  -H "Content-Type: application/json" \
  --data-binary @examples/session_request.json
```

PowerShell-safe equivalent:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/analyze/session" `
  -Method Post -ContentType "application/json" `
  -InFile "examples/session_request.json"
```

Run the checks:

```bash
pytest -q
python -m compileall -q src tests
```

### Public release checks

Before publishing, run the full test and compilation gates:

```bash
python -m pytest -q
python -m compileall -q src tests
```

These checks reject credentials, private hosts or paths, raw media or session data, model/data artifacts, unexpected PNGs, and files over 10 MB. The public demo does not include the private training pipeline, datasets, weights, or dashboard source.

Repository map:

```text
assets/      hero and system/result visuals
docs/        system design, evaluation, ethics and limitations
examples/    synthetic request/response fixtures
results/     audited aggregate benchmark table
src/         safe public FastAPI demo
tests/       API, pipeline, metrics, quality, and README checks
```

Real datasets and pretrained models or weights must be obtained under their original terms; none are distributed here.

## Limitations & Ethics

- Internal retrospective benchmarks are exploratory, not external or prospective validation; sample sizes, threshold selection, leakage risk, and selection bias are documented in the [evaluation notes](docs/evaluation.md).
- Dataset demographic/acquisition bias, class imbalance, weak calibration, and the uncertain archived video feature contract constrain generalization.
- Any real-world study would require consent, data minimization, access controls, encryption, retention limits, auditing, and independent review. See [ethics and limitations](docs/ethics-and-limitations.md).
- The public demo keeps only synthetic numeric inputs in memory and provides track availability states, not screening predictions.

Reuse and redistribution terms are stated in [NOTICE.md](NOTICE.md).

## Team Credits

The author served as **ML/AI Integration Lead**, owning model experiments, multimodal processing, the PC inference API/integration, and the NIX-PC-service connection, while contributing to product design. Teammates owned product planning and the physical design/3D-printing work.
