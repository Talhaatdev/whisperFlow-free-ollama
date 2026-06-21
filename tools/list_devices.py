"""List all audio devices so you can pick your real microphone.

Run it the SAME way you run the app (with sudo -E on Linux, so it sees the
same devices the app will):

    sudo -E .venv/bin/python tools/list_devices.py

Find the INPUT device that is your microphone, note its index number, and set
`input_device = <index>` in whisperflow/config.py.
"""

import sounddevice as sd

print("=== All audio devices ===")
print(sd.query_devices())

print("\n=== Input-capable devices (use one of these indexes) ===")
for idx, dev in enumerate(sd.query_devices()):
    if dev["max_input_channels"] > 0:
        print(
            f"  [{idx}] {dev['name']}  "
            f"(in_channels={dev['max_input_channels']}, "
            f"rate={int(dev['default_samplerate'])})"
        )

default_in = sd.default.device[0]
print(f"\nCurrent default input index: {default_in}")
