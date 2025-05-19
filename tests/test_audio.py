import queue
import threading
import time
import unittest
from unittest.mock import patch

from live_caption.audio import audio_capture_worker, microphone_capture_worker


class DummyArray(list):
    def copy(self):
        return DummyArray(self)


class DummyInputStream:
    def __init__(self, *args, callback=None, **kwargs):
        self.callback = callback

    def __enter__(self):
        if self.callback:
            data = DummyArray([1, 2, 3, 4])
            self.callback(data, len(data), None, None)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class AudioCaptureWorkerTest(unittest.TestCase):
    def test_worker_puts_audio_in_queue(self):
        q = queue.Queue()
        stop = threading.Event()

        dummy_sd = type('DummySD', (), {'InputStream': DummyInputStream})
        with patch('live_caption.audio.sd', dummy_sd):
            t = threading.Thread(target=audio_capture_worker, args=(q, stop, 0, 48000, 4))
            t.start()
            time.sleep(0.1)
            stop.set()
            t.join()

        self.assertFalse(q.empty())
        data = q.get_nowait()
        self.assertEqual(data, DummyArray([1, 2, 3, 4]))


class MicrophoneCaptureWorkerTest(unittest.TestCase):
    def test_worker_captures_when_enabled(self):
        q = queue.Queue()
        stop = threading.Event()
        enable = threading.Event()
        enable.set()

        dummy_sd = type('DummySD', (), {'InputStream': DummyInputStream})
        with patch('live_caption.audio.sd', dummy_sd):
            t = threading.Thread(target=microphone_capture_worker, args=(q, stop, enable, 0, 48000, 4))
            t.start()
            time.sleep(0.1)
            stop.set()
            t.join()

        self.assertFalse(q.empty())

    def test_worker_ignores_when_disabled(self):
        q = queue.Queue()
        stop = threading.Event()
        enable = threading.Event()

        dummy_sd = type('DummySD', (), {'InputStream': DummyInputStream})
        with patch('live_caption.audio.sd', dummy_sd):
            t = threading.Thread(target=microphone_capture_worker, args=(q, stop, enable, 0, 48000, 4))
            t.start()
            time.sleep(0.1)
            stop.set()
            t.join()

        self.assertTrue(q.empty())


if __name__ == '__main__':
    unittest.main()
