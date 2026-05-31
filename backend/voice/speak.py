"""
TTS via Kokoro (local, open-source, free).
MVP: Returns silent WAV stub.
Production: Uncomment subprocess block.
"""

import base64


# Minimal valid WAV (silent, 44 bytes)
_SILENT_WAV_B64 = "UklGRiYAAABXQVZFZm10IBAAAAABAAEAQB8AAAB9AAACABAAZGF0YQIAAAAAAA=="


def speak(text: str, voice: str = "default") -> dict:
    """
    Convert text to speech audio.

    Production (Kokoro TTS):
        import subprocess, tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            out_path = f.name
        subprocess.run([
            "python", "-m", "kokoro",
            "--text", text,
            "--output", out_path,
            "--voice", voice
        ], check=True)
        with open(out_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        os.unlink(out_path)
        return {"audio_base64": audio_b64, "duration_ms": len(text) * 50}
    """
    return {
        "audio_base64": _SILENT_WAV_B64,
        "duration_ms": int(len(text) * 50)
    }
