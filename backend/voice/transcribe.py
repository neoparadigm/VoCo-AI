"""
STT via mlx-whisper — Apple Silicon Metal, local, zero-cost.
Uses whisper-large-v3-turbo by default (~27ms on M4 for short queries).
Model is downloaded once on first use (~800MB), cached in ~/.cache/huggingface.
"""

import base64
import tempfile
import os
import time
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Lazy-loaded — model loads on first call, stays in memory after
_model = None
MLX_MODEL = "mlx-community/whisper-large-v3-turbo"


def _get_model():
    global _model
    if _model is None:
        import mlx_whisper
        logger.info(f"Loading MLX Whisper model: {MLX_MODEL}")
        # Warm up by loading (mlx_whisper loads on first transcribe call)
        _model = mlx_whisper
        logger.info("MLX Whisper ready")
    return _model


def _decode_audio_to_float32(audio_bytes: bytes) -> tuple[np.ndarray, float]:
    """
    Decode audio bytes (webm/opus/wav/any format) to float32 numpy array at 16kHz.
    Uses PyAV — no ffmpeg binary required.
    """
    import av
    import io

    container = av.open(io.BytesIO(audio_bytes))
    resampler = av.AudioResampler(format='fltp', layout='mono', rate=16000)

    samples = []
    for frame in container.decode(audio=0):
        for rf in resampler.resample(frame):
            samples.append(rf.to_ndarray()[0])

    # Flush resampler
    for rf in resampler.resample(None):
        samples.append(rf.to_ndarray()[0])

    if not samples:
        return np.zeros(1600, dtype=np.float32), 0.1

    audio = np.concatenate(samples).astype(np.float32)
    duration = len(audio) / 16000
    return audio, duration


def transcribe(audio_base64: str, language: str = "en") -> dict:
    """
    Transcribe base64-encoded audio to text using MLX Whisper on Apple Silicon.
    Handles webm (browser MediaRecorder output), wav, mp3, and other formats.
    """
    t0 = time.time()

    audio_bytes = base64.b64decode(audio_base64)

    # Decode audio to float32 numpy array at 16kHz
    audio_np, duration_s = _decode_audio_to_float32(audio_bytes)

    # Skip if audio is too short (less than 0.3s — likely accidental tap)
    if duration_s < 0.3 or len(audio_np) < 4800:
        return {"transcript": "", "confidence": 0.0, "duration_ms": 0}

    # Save to temp WAV for mlx_whisper (it accepts file paths or numpy arrays)
    mlx = _get_model()
    result = mlx.transcribe(
        audio_np,
        path_or_hf_repo=MLX_MODEL,
        language=language,
        fp16=True,
        verbose=False,
    )

    transcript = result.get("text", "").strip()
    elapsed_ms = int((time.time() - t0) * 1000)

    logger.info(f"STT: '{transcript}' ({elapsed_ms}ms, audio {duration_s:.1f}s)")

    return {
        "transcript": transcript,
        "confidence": 0.95,
        "duration_ms": elapsed_ms,
    }
