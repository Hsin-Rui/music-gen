"""Orchestrator helpers: run a step in its own env, measure time + peak RSS, probe WAVs."""
import json
import os
import subprocess
import threading
import time
import wave
from pathlib import Path

import numpy as np
import psutil

ROOT = Path(__file__).resolve().parent.parent
STEPS = ROOT / "steps"
PY = {
    "amt": ROOT / "envs" / "amt" / "bin" / "python",
    "pianoflow": ROOT / "envs" / "pianoflow" / "bin" / "python",
    "pianist": ROOT / "envs" / "pianist" / "bin" / "python",
}
DEFAULT_SOUNDFONT = "/Users/hsin-ruilin/dev/music_gen/magenta/sound_library/GeneralUser-GS.sf2"


def step_env(soundfont=None):
    env = dict(os.environ)
    env["HF_HOME"] = str(ROOT / "models" / "hf-cache")
    env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    env["TOKENIZERS_PARALLELISM"] = "false"
    env["PYTHONUNBUFFERED"] = "1"
    if soundfont:
        env["SOUNDFONT"] = str(soundfont)
    return env


def _tree_rss(proc):
    try:
        procs = [proc] + proc.children(recursive=True)
    except psutil.Error:
        return 0
    total = 0
    for p in procs:
        try:
            total += p.memory_info().rss
        except psutil.Error:
            pass
    return total


def run(cmd, log_path, soundfont=None, timeout=None):
    """Run cmd, tee output to log_path. Returns dict with ok, sec, peak_rss_mb,
    result (parsed 'RESULT {json}' line), warnings, error (tail of output on failure)."""
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [str(c) for c in cmd]
    t0 = time.time()
    peak = 0
    with open(log_path, "w") as log:
        log.write("$ " + " ".join(cmd) + "\n")
        log.flush()
        try:
            proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT,
                                    env=step_env(soundfont))
        except OSError as e:
            return {"ok": False, "sec": 0.0, "peak_rss_mb": 0, "result": None, "warnings": [],
                    "error": f"could not start: {e}"}
        ps = psutil.Process(proc.pid)
        stop = threading.Event()

        def poll():
            nonlocal peak
            while not stop.is_set():
                peak = max(peak, _tree_rss(ps))
                stop.wait(0.2)

        th = threading.Thread(target=poll, daemon=True)
        th.start()
        try:
            rc = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            rc = "timeout"
        stop.set()
        th.join()
    sec = time.time() - t0
    text = log_path.read_text(errors="replace")
    lines = [ln for ln in text.replace("\r", "\n").splitlines() if ln.strip()]
    result = None
    for ln in lines:
        if ln.startswith("RESULT "):
            try:
                result = json.loads(ln[7:])
            except json.JSONDecodeError:
                pass
    warnings = sorted({ln.split("WARNING:", 1)[1].strip() for ln in lines
                       if ln.startswith("WARNING:")})
    ok = rc == 0
    error = None
    if not ok:
        tail = [ln for ln in lines if "it/s]" not in ln and "s/it]" not in ln][-12:]
        error = f"exit {rc}\n" + "\n".join(tail)
    return {"ok": ok, "sec": round(sec, 1), "peak_rss_mb": round(peak / 2**20),
            "result": result, "warnings": warnings, "error": error}


def wav_stats(path):
    """Duration (s) and RMS level (dBFS) of a 16-bit WAV — an audibility probe."""
    with wave.open(str(path)) as w:
        n, ch, sw, sr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        data = np.frombuffer(w.readframes(n), dtype={2: np.int16, 4: np.int32}[sw])
    x = data.astype(np.float64) / float(2 ** (8 * sw - 1))
    rms = float(np.sqrt(np.mean(x ** 2))) if x.size else 0.0
    return {"duration_sec": round(n / sr, 1), "rms_dbfs": round(20 * np.log10(rms), 1) if rms > 0 else None,
            "audible": rms > 1e-3}


def excerpt(err, n=8):
    if not err:
        return ""
    return "\n".join(err.splitlines()[-n:])
