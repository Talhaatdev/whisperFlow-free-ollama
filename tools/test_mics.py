"""Record a few seconds from each candidate input device and report the peak
amplitude, so you can tell which device actually hears your voice.

Run it EXACTLY like the app (sudo -E on Linux), and TALK the whole time:

    sudo -E .venv/bin/python tools/test_mics.py

The device with a high peak (e.g. > 0.05) is your microphone. Put its index in
whisperflow/config.py as `input_device = <index>`.
"""

import time

import numpy as np
import sounddevice as sd

# Candidate hardware input devices (skip the ALSA "default"/plugin pseudo-devices).
CANDIDATES = [0, 4, 5]
SECONDS = 3

for idx in CANDIDATES:
    try:
        info = sd.query_devices(idx, "input")
    except Exception as exc:
        print(f"[{idx}] not an input device: {exc}")
        continue

    rate = int(info["default_samplerate"])
    ch = max(1, int(info["max_input_channels"]))
    print(f"\n[{idx}] {info['name']} — recording {SECONDS}s at {rate}Hz… TALK NOW!")
    try:
        rec = sd.rec(int(SECONDS * rate), samplerate=rate, channels=ch, device=idx)
        sd.wait()
        peak = float(np.abs(rec).max())
        rms = float(np.sqrt(np.mean(rec**2)))
        verdict = "  <-- LOUD (likely your mic)" if peak > 0.05 else ""
        print(f"     peak={peak:.4f}  rms={rms:.4f}{verdict}")
    except Exception as exc:
        print(f"     failed: {exc}")
    time.sleep(0.3)

print("\nPick the index with the highest peak and set input_device in config.py.")
