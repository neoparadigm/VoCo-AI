<div align="center">

<br />

<img width="1027" height="420" alt="image" src="https://github.com/user-attachments/assets/73866e85-0da7-4028-b0b6-06f6466d16a3" />


<br /><br />

**Voice-Native Enterprise Intelligence — local, zero-cost, fully private**

Ask questions about your infrastructure, incidents, and systems by voice or text.
Get structured root-cause analysis in seconds. No data leaves your machine.

<br />

[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-3b82f6?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-16-white?style=flat-square&logo=next.js&logoColor=black)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Ollama](https://img.shields.io/badge/Ollama-local-f59e0b?style=flat-square)](https://ollama.com)
[![Whisper STT](https://img.shields.io/badge/STT-Whisper_multi--platform-000000?style=flat-square&logo=apple&logoColor=white)](https://github.com/ml-explore/mlx)

<br />

[Quick Start](#-quick-start) · [BYO LLM](#-bring-your-own-llm) · [BYO Data](#-bring-your-own-data) · [Architecture](#-architecture) · [Demo Scenarios](#-demo-scenarios)

<br />

</div>

---

## What is VoCo?

VoCo is an open-source, voice-first intelligence layer for enterprise operations teams. You speak (or type) a question — VoCo fetches live data from your connected systems, runs it through a local LLM, and returns a structured briefing: root cause, contributing factors, recommended actions, and confidence score.

Everything runs on your hardware. No subscriptions. No data egress.

<br />

## Feature highlights

| | |
|---|---|
| **Voice input** | Speak naturally — Whisper STT runs locally on Apple Silicon, CPU, or CUDA; cloud fallback via Groq |
| **Structured output** | Every response: summary, root cause, factors, actions, business impact |
| **BYO LLM** | Ollama, OpenAI, Azure, LM Studio, llama.cpp — one env var to swap |
| **BYO data** | Plug in any API in a single file — ships with ServiceNow, Intune, M365, infra metrics |
| **Adaptive UI** | Desktop and mobile layouts, light/dark mode, smooth model toggle |
| **Zero cloud** | Fully local inference, no telemetry, no external calls |

<br />

## Quick start

> **Prerequisites:** Python 3.11 · Node 18+ · [Ollama](https://ollama.com) running with at least one model pulled

```bash
# 1. Clone and run setup (installs all deps, creates .env)
git clone https://github.com/neoparadigm/VoCo-AI.git && cd VoCo-AI && bash setup.sh

# 2. Pull a model if you haven't already
ollama pull mistral

# 3. Start the backend (Terminal 1)
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

# 4. Start the frontend (Terminal 2)
cd frontend && npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)**

Total time from clone to running: **under 5 minutes** on a fast connection.

<br />

## Bring your own LLM

Edit `.env` — one line to switch providers:

```bash
# Default: Ollama (local)
VOCO_LLM_URL=http://localhost:11434
VOCO_MODEL=mistral:latest

# Swap to any of these:
VOCO_MODEL=gemma4:latest          # Ollama — deeper reasoning
VOCO_MODEL=llama3.3:70b           # Ollama — highest quality local

VOCO_LLM_URL=https://api.openai.com/v1
VOCO_MODEL=openai/gpt-4o          # OpenAI

VOCO_LLM_URL=https://YOUR.openai.azure.com
VOCO_MODEL=azure/gpt-4o           # Azure OpenAI

VOCO_LLM_URL=http://localhost:1234/v1
VOCO_MODEL=openai/local           # LM Studio / llama.cpp
```

The model selector in the UI maps to Ollama models by default. To change the options shown, edit `MODELS` in `frontend/app/page.tsx`.

<br />

## Bring your own data

All connectors live in **`backend/tools/__init__.py`**. Each tool is a plain Python function — replace the mock reads with real API calls:

```python
@tool("ServiceNow")
def servicenow_tool(query: str) -> str:
    """Query ServiceNow for incidents and SLA data."""
    # Drop in your real call:
    resp = requests.get(f"{SN_INSTANCE}/api/now/table/incident",
                        auth=(SN_USER, SN_PASS), params={"sysparm_limit": 10})
    return json.dumps(resp.json()["result"])
```

<details>
<summary><strong>Built-in tool slots (click to expand)</strong></summary>

<br />

| Tool | Default mock | Replace with |
|---|---|---|
| `ServiceNow` | Incident + SLA data | ServiceNow REST API |
| `M365Metrics` | Enrollment failure rates | Microsoft Graph API |
| `IntuneStatus` | Device provisioning state | Intune Graph API |
| `InfraMetrics` | DNS latency, network health | Datadog / Prometheus / CloudWatch |
| `IncidentContext` | Timeline and alerts | PagerDuty / OpsGenie / Splunk |

Add as many additional tools as you need — each tool's output is automatically injected into the LLM context.

</details>

<br />

## Architecture

```
User (voice or text)
        │
        ▼
 [MLX Whisper STT]          Apple Silicon Metal · ~27ms · whisper-large-v3-turbo
        │
        ▼
 [FastAPI /reason]
   prefetch_data()  ──────► [ServiceNow] [M365] [Intune] [Infra] [Context]
                                          ↓ all results merged
   call_ollama()    ──────► [Local LLM]  system prompt + data + question → structured text
   parse_output()   ──────► regex parser → typed JSON
        │
        ▼
 [Next.js frontend]         Adaptive layout · glass morphism · Framer Motion
```

**Context engineering** happens in `backend/main.py`:
- `SYSTEM_PROMPT` — role definition + exact output schema (structured contract)
- `prefetch_data()` — pulls all tool outputs synchronously, no LLM overhead
- `call_ollama()` — single-shot `[system, user]` prompt at `temperature=0.1`

<br />

## Demo scenarios

Three anonymised enterprise incidents are included to try immediately:

<details>
<summary><strong>Scenario 1 — Device provisioning failures</strong></summary>

> "Why is device provisioning failing?"

87 devices stuck in provisioning. Root cause: DNS latency spike (3200ms vs 45ms baseline) causing resolution failures during Intune enrollment. Contributing: misconfigured upstream router, no DNS failover configured.

</details>

<details>
<summary><strong>Scenario 2 — Cloud migration blocker</strong></summary>

> "What's blocking the cloud migration?"

34 exposed service account credentials found in migration scripts. 817M API calls at risk. Immediate action: rotate credentials and audit IAM policies before proceeding.

</details>

<details>
<summary><strong>Scenario 3 — DNS failover incident</strong></summary>

> "Tell me about the DNS failover issue"

Remote datacenter DNS failover triggered. 2847 devices affected. Primary DNS unreachable for 47 minutes. Secondary DNS resolved within SLA but latency elevated for 3h post-failover.

</details>

<br />

## Voice — works on all platforms

`setup.sh` detects your hardware and installs the right STT backend automatically. No manual configuration needed.

| Platform | Backend | Latency | Install |
|---|---|---|---|
| Apple Silicon (M1–M4) | MLX Whisper | ~27ms | auto |
| CPU — Linux / Windows / Intel Mac | faster-whisper int8 | ~2–8s | auto |
| CUDA GPU | faster-whisper float16 | ~300ms | auto |
| Any — cloud fallback | Groq Whisper API | ~300ms | set `VOCO_GROQ_API_KEY` |
| Any — cloud fallback | OpenAI Whisper API | ~500ms | set `VOCO_OPENAI_API_KEY` |

Override via `.env`:

```bash
VOCO_STT_BACKEND=auto            # default — detects platform
VOCO_STT_BACKEND=faster-whisper  # force CPU/CUDA
VOCO_STT_BACKEND=groq            # force Groq cloud (free tier)
VOCO_STT_BACKEND=openai          # force OpenAI cloud
VOCO_WHISPER_MODEL=base          # smaller/faster: base | small | medium | large-v3-turbo
```

All backends use the same Whisper model family — output quality is consistent. Audio path: browser `MediaRecorder` → webm → PyAV decode → float32 16kHz → your chosen backend.

<br />

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16 · React 19 · Tailwind v4 · Framer Motion |
| Backend | FastAPI · Python 3.11 · httpx |
| LLM | Ollama / LiteLLM (any OpenAI-compatible endpoint) |
| STT | MLX Whisper (Apple Silicon) · faster-whisper (CPU/CUDA) · Groq/OpenAI API |
| Data | Mock JSON → swap with real APIs in `backend/tools/__init__.py` |

<br />

## Project structure

```
VoCo-AI/
├── backend/
│   ├── main.py              # FastAPI app, LLM call, response parser
│   ├── tools/__init__.py    # Enterprise data connectors (replace mocks here)
│   ├── voice/
│   │   ├── transcribe.py    # MLX Whisper STT
│   │   └── speak.py         # TTS (mock — swap with Kokoro/ElevenLabs)
│   ├── agents/              # CrewAI agent definitions (used in extended mode)
│   └── memory/episodic.py   # SQLite query history
├── frontend/
│   ├── app/page.tsx         # Main UI — voice orb, input, results
│   ├── app/components/      # VoiceOrb, OutputPanel, WaveformViz
│   └── lib/api.ts           # Backend API client
├── mock_data/incidents.json # 3 demo scenarios
├── setup.sh                 # One-command setup
└── docker-compose.yml       # Docker alternative
```

<br />

## License

MIT — use it, fork it, build on it.

---

<div align="center">

Built with [Claude Code](https://claude.ai/code) · Running on Apple Silicon · Zero cloud dependencies

</div>
