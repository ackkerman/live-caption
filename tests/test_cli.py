import unittest
from unittest.mock import patch
import live_caption.cli as main

class CLITest(unittest.TestCase):
    def test_cli_arguments(self):
        with patch('live_caption.cli.run_app') as run:
            main.main(['--device','2','--mic-device','3','--sample-rate','22050','--chunk-size','1024'])
            run.assert_called_once_with(2, 22050, 1024, 3)

if __name__ == '__main__':
    unittest.main()
