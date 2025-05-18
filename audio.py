import sys
import threading

try:
    import sounddevice as sd
except Exception:  # pragma: no cover - dependency may be missing during tests
    sd = None


def audio_capture_worker(queue, stop_event, device_index=0, sample_rate=48000, chunk_size=4000):
    """Capture audio from the monitor device and put chunks into a queue."""
    if sd is None:
        raise ImportError("sounddevice is required to use audio_capture_worker")
    def callback(indata, frames, time, status):
        if status:
            print(f"Audio Callback Status: {status}", file=sys.stderr)
        queue.put(indata.copy())

    stream = sd.InputStream(
        device=device_index,
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        blocksize=chunk_size,
        callback=callback,
    )

    with stream:
        stop_event.wait()
