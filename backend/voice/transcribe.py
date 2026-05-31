"""
STT — multi-backend, auto-detected by platform.

Priority order (auto mode):
  1. MLX Whisper      — Apple Silicon Metal, ~27ms, fully local
  2. faster-whisper   — CPU / CUDA, Linux / Windows / Intel Mac, fully local
  3. Groq Whisper API — cloud, free tier, ~300ms  (set VOCO_GROQ_API_KEY)
  4. OpenAI Whisper   — cloud fallback            (set VOCO_OPENAI_API_KEY)

Override with env var:
  VOCO_STT_BACKEND=mlx|faster-whisper|groq|openai

Model size (local backends):
  VOCO_WHISPER_MODEL=large-v3-turbo (default) | base | small | medium | large-v3
"""

import base64
import os
import platform
import time
import logging
import numpy as np

logger = logging.getLogger(__name__)

WHISPER_MODEL  = os.getenv("VOCO_WHISPER_MODEL", "large-v3-turbo")
STT_BACKEND    = os.getenv("VOCO_STT_BACKEND", "auto")
GROQ_API_KEY   = os.getenv("VOCO_GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("VOCO_OPENAI_API_KEY", "")


def _is_apple_silicon() -> bool:
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def _detect_backend() -> str:
    if STT_BACKEND != "auto":
        return STT_BACKEND
    if _is_apple_silicon():
        return "mlx"
    if GROQ_API_KEY:
        return "groq"
    if OPENAI_API_KEY:
        return "openai"
    return "faster-whisper"


BACKEND = _detect_backend()
logger.info(f"STT backend: {BACKEND}")


# ── Shared audio decode ───────────────────────────────────────────────────────

def _decode_audio(audio_bytes: bytes) -> tuple[np.ndarray, float]:
    """Decode any audio format → float32 numpy @ 16kHz via PyAV (no ffmpeg needed)."""
    import av, io
    container = av.open(io.BytesIO(audio_bytes))
    resampler = av.AudioResampler(format="fltp", layout="mono", rate=16000)
    samples = []
    for frame in container.decode(audio=0):
        for rf in resampler.resample(frame):
            samples.append(rf.to_ndarray()[0])
    for rf in resampler.resample(None):
        samples.append(rf.to_ndarray()[0])
    if not samples:
        return np.zeros(1600, dtype=np.float32), 0.1
    audio = np.concatenate(samples).astype(np.float32)
    return audio, len(audio) / 16000


# ── MLX Whisper (Apple Silicon) ───────────────────────────────────────────────

_mlx = None

def _transcribe_mlx(audio_bytes: bytes, language: str) -> str:
    global _mlx
    import mlx_whisper
    if _mlx is None:
        _mlx = mlx_whisper
        logger.info(f"MLX Whisper ready (whisper-{WHISPER_MODEL})")
    audio_np, duration = _decode_audio(audio_bytes)
    if duration < 0.3:
        return ""
    result = _mlx.transcribe(
        audio_np,
        path_or_hf_repo=f"mlx-community/whisper-{WHISPER_MODEL}",
        language=language,
        fp16=True,
        verbose=False,
    )
    return result.get("text", "").strip()


# ── faster-whisper (CPU / CUDA) ───────────────────────────────────────────────

_fw_model = None

def _transcribe_faster_whisper(audio_bytes: bytes, language: str) -> str:
    global _fw_model
    if _fw_model is None:
        from faster_whisper import WhisperModel
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"
        compute = "float16" if device == "cuda" else "int8"
        _fw_model = WhisperModel(WHISPER_MODEL, device=device, compute_type=compute)
        logger.info(f"faster-whisper ready ({WHISPER_MODEL}, {device}/{compute})")

    audio_np, duration = _decode_audio(audio_bytes)
    if duration < 0.3:
        return ""

    import tempfile
    import soundfile as sf
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, audio_np, 16000)
        segments, _ = _fw_model.transcribe(tmp.name, language=language, beam_size=5)
        return " ".join(s.text for s in segments).strip()


# ── Groq Whisper API ──────────────────────────────────────────────────────────

def _transcribe_groq(audio_bytes: bytes, language: str) -> str:
    from groq import Groq
    import io
    client = Groq(api_key=GROQ_API_KEY)
    result = client.audio.transcriptions.create(
        model="whisper-large-v3-turbo",
        file=("audio.webm", io.BytesIO(audio_bytes), "audio/webm"),
        language=language,
    )
    return result.text.strip()


# ── OpenAI Whisper API ────────────────────────────────────────────────────────

def _transcribe_openai(audio_bytes: bytes, language: str) -> str:
    from openai import OpenAI
    import io
    client = OpenAI(api_key=OPENAI_API_KEY)
    result = client.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.webm", io.BytesIO(audio_bytes), "audio/webm"),
        language=language,
    )
    return result.text.strip()


# ── Public interface ──────────────────────────────────────────────────────────

def transcribe(audio_base64: str, language: str = "en") -> dict:
    t0 = time.time()
    audio_bytes = base64.b64decode(audio_base64)

    try:
        if BACKEND == "mlx":
            text = _transcribe_mlx(audio_bytes, language)
        elif BACKEND == "faster-whisper":
            text = _transcribe_faster_whisper(audio_bytes, language)
        elif BACKEND == "groq":
            text = _transcribe_groq(audio_bytes, language)
        elif BACKEND == "openai":
            text = _transcribe_openai(audio_bytes, language)
        else:
            raise ValueError(f"Unknown STT backend: {BACKEND}")
    except Exception as e:
        logger.error(f"STT error [{BACKEND}]: {e}")
        raise

    elapsed_ms = int((time.time() - t0) * 1000)
    logger.info(f"STT [{BACKEND}]: '{text}' ({elapsed_ms}ms)")
    return {"transcript": text, "confidence": 0.95, "duration_ms": elapsed_ms}
