"""FastAPI boundary for a synthetic sample that loads no models, persists no
sessions, and provides no diagnosis.
"""

from fastapi import FastAPI

from mindscope.demo_pipeline import analyze_demo_session
from mindscope.schemas import SessionRequest, SessionResponse


app = FastAPI(
    title="MindScope Public Demo API",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the localhost public-demo service is available."""
    return {"status": "ok", "mode": "public_demo"}


@app.post("/analyze/session", response_model=SessionResponse)
def analyze_session(request: SessionRequest) -> SessionResponse:
    """Return public-demo quality and availability metadata for in-memory input."""
    return analyze_demo_session(request)
