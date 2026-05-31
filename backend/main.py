"""
VoCo FastAPI Backend
Voice-Native Enterprise Intelligence Platform

Stack:
- FastAPI (async API)
- CrewAI (multi-agent orchestration: 4 agents)
- Ollama gemma4 (local LLM — change OLLAMA_MODEL to swap)
- Parakeet.cpp STT (mocked for MVP — see voice/transcribe.py)
- Kokoro TTS (mocked for MVP — see voice/speak.py)

All data anonymized. Zero cloud dependencies.
"""

import logging
import httpx
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.tools import servicenow_tool, m365_tool, intune_tool, metrics_tool, context_tool
from backend.voice.transcribe import transcribe
from backend.voice.speak import speak
from backend.memory.episodic import save_episode

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

OLLAMA_MODEL    = os.getenv("VOCO_MODEL",       "mistral:latest")
OLLAMA_BASE_URL = os.getenv("VOCO_LLM_URL",    "http://localhost:11434")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────

app = FastAPI(
    title="VoCo",
    description="Voice-native enterprise intelligence — local, zero-cost, fully private",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────────

class TranscribeRequest(BaseModel):
    audio_base64: str
    language: str = "en"

class TranscribeResponse(BaseModel):
    transcript: str
    confidence: float
    duration_ms: int

class ReasonRequest(BaseModel):
    question: str
    user_role: str = "architect"
    model: Optional[str] = None  # Override OLLAMA_MODEL per-request

class ReasonResponse(BaseModel):
    summary: str
    root_cause: str
    contributing_factors: List[str]
    reasoning_chain: List[Dict[str, str]]
    actions: List[Dict[str, str]]
    confidence_score: float
    business_impact: str
    raw_output: str

class SpeakRequest(BaseModel):
    text: str
    voice: str = "default"

class SpeakResponse(BaseModel):
    audio_base64: str
    duration_ms: int

# ─────────────────────────────────────────────
# DATA PRE-FETCH (no LLM — direct tool calls)
# ─────────────────────────────────────────────

def prefetch_data(question: str) -> str:
    """Fetch all enterprise data synchronously. No LLM overhead."""
    sections = {
        "ServiceNow Incidents": servicenow_tool.run(question),
        "M365 Enrollment Metrics": m365_tool.run(question),
        "Intune Device Status": intune_tool.run(question),
        "Infrastructure Metrics": metrics_tool.run(question),
        "Incident Context": context_tool.run(question),
    }
    return "\n\n".join(f"=== {k} ===\n{v}" for k, v in sections.items())


# ─────────────────────────────────────────────
# SINGLE-SHOT LLM CALL (replaces 3-agent chain)
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are an enterprise intelligence analyst. Given a question and enterprise data, produce a structured analysis in EXACTLY this format — no deviations, no extra text before or after:

SUMMARY: [1-2 sentences. What happened and what is the root cause.]

ROOT_CAUSE: [One clear sentence identifying the primary cause.]

CONTRIBUTING_FACTORS:
- [Factor 1]
- [Factor 2]
- [Factor 3]

REASONING_CHAIN:
- OBSERVE: [What the data shows]
- CORRELATE: [How signals connect]
- ANALYZE: [What it means]
- CONCLUDE: [Final determination]

ACTIONS:
- IMMEDIATE (within 1h): [Specific action]
- SHORT_TERM (within 24h): [Specific action]
- LONG_TERM (within 1 week): [Specific action]

CONFIDENCE: [0.0-1.0]
BUSINESS_IMPACT: [One sentence on business risk if not resolved]"""


async def call_ollama(question: str, data: str, model: str) -> str:
    """Single Ollama chat call — no agent overhead."""
    user_msg = f"Question: {question}\n\nEnterprise data:\n{data}"
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_msg},
                ],
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 800},
            }
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]


def parse_crew_output(raw: str) -> Dict[str, Any]:
    """
    Parse structured output from FormatterAgent.
    Uses regex to handle LLMs that collapse newlines or vary formatting.
    """
    import re

    result: Dict[str, Any] = {
        "summary": "",
        "root_cause": "",
        "contributing_factors": [],
        "reasoning_chain": [],
        "actions": [],
        "confidence_score": 0.85,
        "business_impact": "",
        "raw_output": raw
    }

    # ── Single-value fields (regex extract) ──────────────────────────────────
    def extract(pattern: str, text: str) -> str:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if not m:
            return ""
        val = m.group(1).strip()
        # Trim at next ALL-CAPS section header
        val = re.split(r'\n[A-Z_]{4,}:', val)[0].strip()
        return val

    result["summary"]         = extract(r'SUMMARY:\s*(.+?)(?=\n[A-Z_]{3,}:|$)', raw)
    result["root_cause"]      = extract(r'ROOT_CAUSE:\s*(.+?)(?=\n[A-Z_]{3,}:|$)', raw)
    result["business_impact"] = extract(r'BUSINESS_IMPACT:\s*(.+?)(?=\n[A-Z_]{3,}:|$)', raw)

    conf_match = re.search(r'CONFIDENCE:\s*([0-9.]+)', raw, re.IGNORECASE)
    if conf_match:
        try:
            result["confidence_score"] = float(conf_match.group(1))
        except ValueError:
            pass

    # ── List fields ──────────────────────────────────────────────────────────
    def extract_list(section: str, text: str) -> list:
        block = extract(rf'{section}:\s*(.+?)(?=\n[A-Z_]{{3,}}:|$)', text)
        if not block:
            return []
        items = []
        for line in re.split(r'\n|(?<=\w)\s*-\s+', block):
            line = re.sub(r'^[-•*\d]+[.)]\s*', '', line).strip()
            if line:
                items.append(line)
        return items

    result["contributing_factors"] = extract_list("CONTRIBUTING_FACTORS", raw)

    # Actions — preserve timeframe labels
    result["actions"] = [{"action": a} for a in extract_list("ACTIONS", raw)]

    # Reasoning chain — split on step labels (OBSERVE, CORRELATE, etc.)
    reasoning_block = extract(r'REASONING_CHAIN:\s*(.+?)(?=\n[A-Z_]{3,}:|$)', raw)
    if reasoning_block:
        for line in re.split(r'\n|(?<=\w)\s*-\s+', reasoning_block):
            line = re.sub(r'^[-•*]\s*', '', line).strip()
            if not line:
                continue
            m = re.match(r'^(OBSERVE|CORRELATE|ANALYZE|CONCLUDE|RECOMMEND)[:\s]+(.+)', line, re.IGNORECASE)
            if m:
                result["reasoning_chain"].append({"step": m.group(1).upper(), "detail": m.group(2).strip()})
            elif result["reasoning_chain"]:
                # append continuation to last step
                result["reasoning_chain"][-1]["detail"] += " " + line

    # ── Fallback: nothing parsed → use raw as summary ─────────────────────────
    if not result["summary"] and not result["root_cause"]:
        result["summary"] = raw[:600].strip()

    return result

# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "components": {
            "api": "up",
            "ollama": f"local ({OLLAMA_MODEL})",
            "crew": "crewai (4 agents: fetch, analyze, reason, format)",
            "tts": "kokoro (local, mocked in MVP)",
            "stt": "parakeet (local, mocked in MVP)",
        }
    }


@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_endpoint(request: TranscribeRequest):
    logger.info(f"Transcribe request ({len(request.audio_base64)} chars)")
    result = transcribe(request.audio_base64, request.language)
    return TranscribeResponse(**result)


@app.post("/reason", response_model=ReasonResponse)
async def reason_endpoint(request: ReasonRequest):
    logger.info(f"Reason: '{request.question}' (role: {request.user_role})")
    try:
        model = request.model or OLLAMA_MODEL
        data = prefetch_data(request.question)
        raw = await call_ollama(request.question, data, model)
        parsed = parse_crew_output(raw)

        # Persist to episodic memory
        save_episode(
            question=request.question,
            summary=parsed["summary"],
            root_cause=parsed["root_cause"],
            confidence=parsed["confidence_score"]
        )

        logger.info(f"Crew complete. Confidence: {parsed['confidence_score']}")
        return ReasonResponse(**parsed)
    except Exception as e:
        logger.error(f"Crew error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/speak", response_model=SpeakResponse)
async def speak_endpoint(request: SpeakRequest):
    logger.info(f"Speak: {len(request.text)} chars")
    result = speak(request.text, request.voice)
    return SpeakResponse(**result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True)
