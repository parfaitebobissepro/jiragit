import os
import sys
import json
import unittest
from unittest.mock import patch, mock_open

# Assuming the load_config function is imported from the correct module
from src.utils.load_config import load_config

class TestLoadConfig(unittest.TestCase):

    @patch('os.getenv')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_load_config_success(self, mock_open, mock_exists, mock_getenv):
        mock_getenv.return_value = os.path.join('fake', 'path')
        mock_exists.return_value = True

        config = load_config()
        self.assertEqual(config, {"key": "value"})
        mock_open.assert_called_once_with(os.path.join('fake', 'path', 'config.json'), 'r')

    @patch('os.getenv')
    def test_load_config_no_env_var(self, mock_getenv):
        mock_getenv.return_value = None

        with self.assertRaises(SystemExit) as cm:
            load_config()
        self.assertEqual(cm.exception.code, 1)

    @patch('os.getenv')
    @patch('os.path.exists')
    def test_load_config_file_not_found(self, mock_exists, mock_getenv):
        mock_getenv.return_value = '/fake/path'
        mock_exists.return_value = False

        with self.assertRaises(SystemExit) as cm:
            load_config()
        self.assertEqual(cm.exception.code, 1)

    @patch('os.getenv')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_load_config_invalid_json(self, mock_open, mock_exists, mock_getenv):
        mock_getenv.return_value = '/fake/path'
        mock_exists.return_value = True

        with self.assertRaises(json.JSONDecodeError):
            load_config()

if __name__ == '__main__':
    unittest.main()
