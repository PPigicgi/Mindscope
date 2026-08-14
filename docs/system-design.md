# MindScope public-demo system design

MindScope is a research prototype, not a diagnosis system. The public demo is
safe by construction: its FastAPI service defaults to localhost at
`http://localhost:8001`, accepts only validated in-memory numeric arrays, and
does not load trained weights, retain sessions, or produce screening scores.

## Research-system context

In the research architecture, the NIX edge device combines an NVIDIA Jetson
Orin Nano Super, an IMX477 camera module, a ReSpeaker microphone array, and
stereo speakers. NIX captures camera and microphone signals and transports the
session inputs to a PC server. The server-side research tracks include local
speech-to-text, HuBERT audio features, and OpenFace action-unit, pose, and gaze
features. Candidate modelling tracks include XGBoost, MLP, and Mamba.

The intended interaction output is a spoken response through the NIX stereo
speakers. A separate screening output is intended for a web dashboard; it is
not a diagnosis and is deliberately absent from this public demo.

Archived system work may include OpenFace extraction. If extraction is
unavailable, the research system can treat video as missing and use its defined
fallback behavior. This provides implementation context only: the public demo
does not execute archived OpenFace extraction.

## Public API behavior

The service exposes two application routes:

- `GET /health` confirms the public-demo boundary.
- `POST /analyze/session` validates a synthetic in-memory session and delegates
  quality and track-status handling to the demo pipeline.

The request uses no uploads or filenames. See the
[synthetic request contract](../examples/session_request.json) and the
[serialized response contract](../examples/session_response.json).

Before any model-track state is reported, the audio quality gate checks minimum
duration and RMS. A missing or quality-failed modality is marked `skipped` with
a reason. A usable modality remains
`not_available_in_public_demo`: this status conveys that the public demo runs
no trained research model and provides no prediction.

No storage, recordings, video frames, transcripts, weights, or real
predictions are shipped. These omissions keep the portfolio artifact
demonstrable without distributing sensitive data, model artifacts, or a
medical-looking output.
