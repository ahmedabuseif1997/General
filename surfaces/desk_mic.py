"""Desk-mic surface: push-to-talk voice loop on your own machine.

Loop: Enter -> record until Enter -> transcribe -> brain -> speak reply.

Degrades gracefully:
  recording   — needs `arecord` (Linux/ALSA) or `rec` (sox) or `sox -d`
  transcribe  — needs `pip install faster-whisper` (first run downloads
                the model); without it, falls back to typed input
  speak       — uses `espeak-ng` / `say` (macOS) if present, else prints

Run:  python3 -m surfaces.desk_mic
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from brain.claude_client import BrainUnavailable, run_brain

_whisper_model = None


def record_wav() -> Path | None:
    wav = Path(tempfile.mkstemp(suffix=".wav")[1])
    if shutil.which("arecord"):
        cmd = ["arecord", "-q", "-f", "S16_LE", "-r", "16000", str(wav)]
    elif shutil.which("rec"):
        cmd = ["rec", "-q", "-r", "16000", "-c", "1", str(wav)]
    elif shutil.which("sox"):
        cmd = ["sox", "-q", "-d", "-r", "16000", "-c", "1", str(wav)]
    else:
        return None
    input("press Enter to talk … ")
    proc = subprocess.Popen(cmd)
    input("recording — press Enter to stop … ")
    proc.terminate()
    proc.wait()
    return wav


def transcribe(wav: Path) -> str | None:
    global _whisper_model
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    if _whisper_model is None:
        print("(loading whisper model …)")
        _whisper_model = WhisperModel("base", compute_type="int8")
    segments, _ = _whisper_model.transcribe(str(wav))
    return " ".join(s.text.strip() for s in segments).strip()


def speak(text: str) -> None:
    if shutil.which("espeak-ng"):
        subprocess.run(["espeak-ng", text[:2000]], check=False)
    elif shutil.which("say"):
        subprocess.run(["say", text[:2000]], check=False)


def main() -> None:
    print("desk-mic surface — Ctrl-C to quit")
    while True:
        try:
            wav = record_wav()
            text = transcribe(wav) if wav else None
            if wav:
                wav.unlink(missing_ok=True)
            if not text:
                if wav is None:
                    print("(no recorder found — install alsa-utils or sox; "
                          "typing mode)")
                else:
                    print("(no transcription — pip install faster-whisper; "
                          "typing mode)")
                text = input("you> ").strip()
            if not text:
                continue
            print(f"you: {text}")
            try:
                reply = run_brain(f"[surface: desk-mic] {text}")
            except BrainUnavailable as exc:
                reply = f"brain error: {exc}"
            print(f"brain: {reply}")
            speak(reply)
        except (KeyboardInterrupt, EOFError):
            print("\nbye")
            sys.exit(0)


if __name__ == "__main__":
    main()
