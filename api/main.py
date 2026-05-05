import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from api.agent import analyze
from api.governance import validate_request, detect_pii, log_request, get_audit_log

app = FastAPI(
    title="TradeSense AI",
    description="Enterprise-grade AI trading research with RAG, agents, and governance",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    query: str
    session_id: str = "default"


class AnalysisResponse(BaseModel):
    answer: str
    session_id: str
    flagged: bool = False
    warning: str = ""


@app.get("/")
def root():
    return {
        "name": "TradeSense AI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model": "llama-3.3-70b-versatile",
        "governance": "enabled",
        "tracing": "langsmith",
        "tools": 7
    }


@app.post("/analyze", response_model=AnalysisResponse)
def analyze_stock(request: AnalysisRequest):
    is_valid, error_msg = validate_request(request.query)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    pii_found = detect_pii(request.query)
    warning = f"PII detected: {', '.join(pii_found)}." if pii_found else ""

    answer = analyze(request.query, request.session_id)

    log_request(
        session_id=request.session_id,
        query=request.query,
        response=answer,
        pii_detected=pii_found,
        injection_detected=False
    )

    return AnalysisResponse(
        answer=answer,
        session_id=request.session_id,
        flagged=bool(pii_found),
        warning=warning
    )


@app.get("/audit-log")
def audit():
    return {
        "total_requests": len(get_audit_log()),
        "log": get_audit_log()
    }


@app.get("/sessions")
def sessions():
    from api.agent import store
    return {
        "active_sessions": len(store),
        "session_ids": list(store.keys())
    }
