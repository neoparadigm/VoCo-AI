# VoCo Demo Script

## Setup (5 min before)

```bash
# Terminal 1 - Backend
cd /path/to/VoCo
pip install -r backend/requirements.txt
python mock_data/generate.py
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm run dev

# Verify
curl http://localhost:8000/health
# Open: http://localhost:3000
```

## Demo (5 min)

### Opening
"This is VoCo — a voice-native enterprise intelligence platform. Runs completely locally,
zero cloud dependencies, zero cost. You speak a question. Four AI agents analyze your
systems. You get answers."

### Demo 1: Device Provisioning (2 min)
1. Click microphone
2. Speak: "Why is device provisioning failing?"
3. Show waveform visualization
4. Show answer appearing
5. Click "Show reasoning chain" — walk through each step
6. Point to action items (immediate, same-day, sprint)
7. Click volume icon — TTS plays locally

Key points:
- "Voice input — hands-free, faster than typing"
- "Four agents ran in sequence — fetch, analyze, reason, format"
- "Root cause, not just symptoms"
- "Actionable at three time horizons"

### Demo 2: Migration Blocker (1.5 min)
1. Click mic
2. Speak: "What's blocking the cloud migration project?"
3. Show output — 817M API calls at risk
4. Point to critical path milestones

Key points:
- "Same platform, different question, completely different analysis"
- "Business impact quantified automatically"

### Demo 3: DNS Issue (1.5 min)
1. Click mic
2. Speak: "Tell me about the DNS issues in the remote datacenter"
3. Show DNS correlation analysis

### Closing
"All of this runs on your laptop. Ollama for LLM, Parakeet for voice, Kokoro for TTS.
CrewAI orchestrates the agents — designed to scale to LangGraph. Docker — runs on Mac,
Linux, Windows, or any cloud."

## Q&A Talking Points

**"Can it connect to real systems?"**
Yes — replace mock tool functions with real API calls. Same architecture.

**"What LLM does it use?"**
Gemma 4 via Ollama. Swap any model — llama3.3:70b, Mistral, Qwen. One config line.

**"How do you extend it?"**
Add an agent, define a task, add it to the crew. CrewAI handles orchestration.

**"Is the data private?"**
Completely. Nothing leaves your machine. Zero cloud calls at runtime.

**"What's the latency?"**
3-8 seconds on M3/M4 Mac. Parakeet transcription: 27ms.
