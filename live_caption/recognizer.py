import json
import queue

try:
    from vosk import Model, KaldiRecognizer
except Exception:  # pragma: no cover - dependency may be missing during tests
    Model = None
    KaldiRecognizer = None


class SpeechRecognizer:
    """Simple wrapper around Vosk recognizer"""
    def __init__(self, lang="en-us", sample_rate=48000):
        if Model is None or KaldiRecognizer is None:
            raise ImportError("Vosk is required to use SpeechRecognizer")
        self.model = Model(lang=lang)
        self.rec = KaldiRecognizer(self.model, sample_rate)
        self.final_text = ""

    def process(self, indata, window):
        bytes_data = indata.tobytes()
        if self.rec.AcceptWaveform(bytes_data):
            result = self.rec.Result()
            text = json.loads(result).get("text", "")
            if text:
                self.final_text = text
                window.update_caption(self.final_text)
                print(f"[CAPTION] {self.final_text}")
        else:
            partial_result = self.rec.PartialResult()
            partial_text = json.loads(partial_result).get("partial", "")
            if partial_text:
                caption_text = f"{self.final_text} {partial_text}"
                window.update_caption(caption_text)
                print(f"[CAPTION] {caption_text}")


def recognize_worker(window, q: queue.Queue, stop_event, recognizer=None, lang="en-us", sample_rate=48000):
    """Read audio chunks from the queue and update window captions."""
    if recognizer is None:
        recognizer = SpeechRecognizer(lang=lang, sample_rate=sample_rate)

    while not stop_event.is_set():
        try:
            indata = q.get(timeout=0.1)
        except queue.Empty:
            continue
        recognizer.process(indata, window)
