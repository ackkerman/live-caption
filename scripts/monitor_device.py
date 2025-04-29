import sounddevice as sd

def list_monitor_devices():
    """List all audio devices and identify monitor devices."""
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        print(f"{idx}: {dev['name']}")


if __name__ == "__main__":
    list_monitor_devices()