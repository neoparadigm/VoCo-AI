# VoCo AI — Voice-Native Enterprise Intelligence

Ask questions about your enterprise data by voice or text. Get structured analysis: root cause, contributing factors, recommended actions, and business impact — in seconds, running entirely on your machine.

Built for IT operations, security, and infrastructure teams who need fast answers without sending data to the cloud.

---

## What it does

- **Voice or text input** — speak your question or type it; Whisper transcribes locally on Apple Silicon
- **Structured analysis** — every response gives you summary, root cause, contributing factors, actions, and confidence score
- **BYO LLM** — works with any Ollama model, or any OpenAI-compatible endpoint (OpenAI, Anthropic, Azure, Together, local llama.cpp servers)
- **BYO data** — plug in your own enterprise sources in one file; ships with realistic mock scenarios (ServiceNow, Intune, M365, DNS/infra metrics)
- **Fully local** — no telemetry, no cloud calls, no data leaves your machine

---

## One-command setup (~3 min)

**Prerequisites:** Python 3.11, Node 18+, and your LLM running (see below)

```bash
git clone https://github.com/YOUR_USERNAME/voco.git && cd voco && bash setup.sh
```

Then start two terminals:

```bash
# Terminal 1 — backend
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 — frontend
cd frontend && npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## BYO LLM

Edit `.env` (created by setup.sh):

```bash
# Ollama (default) — run: ollama pull mistral
VOCO_LLM_URL=http://localhost:11434
VOCO_MODEL=mistral:latest

# Other Ollama models
VOCO_MODEL=gemma4:latest
VOCO_MODEL=llama3.3:70b

# OpenAI
VOCO_LLM_URL=https://api.openai.com/v1
VOCO_MODEL=openai/gpt-4o

# Azure OpenAI
VOCO_LLM_URL=https://YOUR_RESOURCE.openai.azure.com
VOCO_MODEL=azure/gpt-4o

# Any llama.cpp / LM Studio / Ollama-compatible server
VOCO_LLM_URL=http://localhost:1234/v1
VOCO_MODEL=openai/local-model
```

The model toggle in the UI maps to Ollama models by default. To change the options, edit `MODELS` in `frontend/app/page.tsx`.

---

## BYO enterprise data

All data connectors live in **`backend/tools/__init__.py`**. Each tool is a plain function decorated with `@tool`. Replace the mock JSON reads with real API calls:

```python
@tool("ServiceNow")
def servicenow_tool(query: str) -> str:
    """Query ServiceNow for incidents, tickets, SLA data."""
    # Replace with your real ServiceNow API call:
    # resp = requests.get(f"{SN_URL}/api/now/table/incident", ...)
    # return json.dumps(resp.json()["result"])
    ...

@tool("Splunk")
def splunk_tool(query: str) -> str:
    """Query Splunk for log anomalies and alert counts."""
    ...
```

**Built-in mock tools** (swap any or all):

| Tool | What it returns |
|---|---|
| `ServiceNow` | Incidents, SLA breaches, ticket metadata |
| `M365Metrics` | Enrollment failure rates, error distribution |
| `IntuneStatus` | Device provisioning state, retry counts |
| `InfraMetrics` | DNS latency, network health, failover state |
| `IncidentContext` | Timeline, alerts, team sentiment |

Add as many tools as you like — each one's output is injected into the LLM context automatically.

---

## Demo scenarios (included)

Three anonymized enterprise incidents to try immediately:

- *"Why is device provisioning failing?"* — DNS latency cascade affecting 87 devices
- *"What's blocking the cloud migration?"* — 34 exposed credentials, 817M API calls at risk
- *"Tell me about the DNS failover issue"* — remote datacenter, 2847 devices affected

---

## Architecture

```
Voice/Text input
      |
      v
[MLX Whisper STT]  — Apple Silicon Metal, ~27ms
      |
      v
[FastAPI /reason]
  prefetch_data()  — parallel tool calls, no LLM overhead
  call_ollama()    — single-shot structured prompt to your LLM
  parse_output()   — regex parser → typed JSON response
      |
      v
[Next.js frontend] — adaptive layout, glass morphism UI
```

**Stack:** FastAPI · Next.js 16 · MLX Whisper · Ollama/LiteLLM · Tailwind v4 · Framer Motion

---

## Voice (Apple Silicon only)

STT uses [mlx-whisper](https://github.com/ml-explore/mlx-examples) (whisper-large-v3-turbo) on Apple Metal. The model (~800MB) downloads automatically on first voice query and is cached in `~/.cache/huggingface`.

On non-Apple hardware, voice input falls back to an error — text input works on all platforms.

---

## License

MIT
