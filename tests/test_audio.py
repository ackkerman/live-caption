import queue
import threading
import time
import unittest
from unittest.mock import patch

from audio import audio_capture_worker


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
        with patch('audio.sd', dummy_sd):
            t = threading.Thread(target=audio_capture_worker, args=(q, stop, 0, 48000, 4))
            t.start()
            time.sleep(0.1)
            stop.set()
            t.join()

        self.assertFalse(q.empty())
        data = q.get_nowait()
        self.assertEqual(data, DummyArray([1, 2, 3, 4]))


if __name__ == '__main__':
    unittest.main()
