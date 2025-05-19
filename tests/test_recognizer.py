import queue
import threading
import time
import unittest

from live_caption.recognizer import recognize_worker


class DummyRecognizer:
    def __init__(self):
        self.processed = []

    def process(self, indata, window):
        self.processed.append(indata)
        window.update_caption("dummy")


class DummyWindow:
    def __init__(self):
        self.texts = []

    def update_caption(self, text):
        self.texts.append(text)


class RecognizerWorkerTest(unittest.TestCase):
    def test_worker_updates_caption(self):
        q = queue.Queue()
        stop = threading.Event()
        dummy_rec = DummyRecognizer()
        dummy_window = DummyWindow()

        q.put(b"abc")

        t = threading.Thread(target=recognize_worker, args=(dummy_window, q, stop, dummy_rec))
        t.start()
        time.sleep(0.2)
        stop.set()
        t.join()

        self.assertEqual(dummy_window.texts[-1], "dummy")
        self.assertTrue(dummy_rec.processed)


if __name__ == "__main__":
    unittest.main()
