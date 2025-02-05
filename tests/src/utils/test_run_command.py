import unittest
from unittest.mock import patch, MagicMock
from src.utils.run_command import run_command
import subprocess

class TestRunCommand(unittest.TestCase):

    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        # Simulate a successful command execution
        mock_run.return_value = MagicMock(stdout='success', returncode=0)
        result = run_command('echo success')
        self.assertEqual(result, 'success')

    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        # Simulate a command execution failure
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd='echo fail', stderr='error')
        result = run_command('echo fail')
        self.assertIsNone(result)

    @patch('subprocess.run')
    def test_run_command_git_status(self, mock_run):
        # Simulate a git status command
        mock_run.return_value = MagicMock(stdout='On branch main\nYour branch is up to date with \'origin/main\'.', returncode=0)
        result = run_command('git status')
        self.assertIn('On branch main', result)

    @patch('subprocess.run')
    def test_run_command_git_log(self, mock_run):
        # Simulate a git log command
        mock_run.return_value = MagicMock(stdout='commit abc123\nAuthor: Test User <test@example.com>\nDate: Mon Oct 4 12:34:56 2021 +0000\n\n    Initial commit', returncode=0)
        result = run_command('git log -1')
        self.assertIn('commit abc123', result)

    @patch('subprocess.run')
    def test_run_command_invalid_command(self, mock_run):
        # Simulate an invalid command
        mock_run.side_effect = subprocess.CalledProcessError(returncode=127, cmd='invalid_command', stderr='command not found')
        result = run_command('invalid_command')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()