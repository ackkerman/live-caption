import types
import threading
import unittest
from unittest.mock import Mock

import main

class MainSignalTest(unittest.TestCase):
    def test_handle_sigint_twice_sets_stop_event(self):
        main.ctrl_c_count = 0
        main.stop_event = threading.Event()
        dummy_app = types.SimpleNamespace(quit=Mock())
        main.QtWidgets = types.SimpleNamespace(QApplication=dummy_app)

        main.handle_sigint(None, None)
        self.assertEqual(main.ctrl_c_count, 1)
        self.assertFalse(main.stop_event.is_set())

        main.handle_sigint(None, None)
        self.assertEqual(main.ctrl_c_count, 2)
        self.assertTrue(main.stop_event.is_set())
        dummy_app.quit.assert_called_once()

    def test_periodic_check_triggers_quit_when_stopped(self):
        dummy_app = types.SimpleNamespace(quit=Mock())
        main.QtWidgets = types.SimpleNamespace(QApplication=dummy_app)
        main.stop_event = threading.Event()
        main.stop_event.set()

        main.periodic_check()
        dummy_app.quit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
