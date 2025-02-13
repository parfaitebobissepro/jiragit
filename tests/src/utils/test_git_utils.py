import unittest
from unittest.mock import patch
from src.utils.git_utils import generate_branch_name, stash_changes, apply_stashed_changes, list_remote_branches, select_branch, getCurrentTaskNumber, select_files_for_commit

class TestGitUtils(unittest.TestCase):

    @patch('src.utils.git_utils.run_command')
    def test_generate_branch_name(self, mock_run_command):
        mock_run_command.return_value = None
        GLOBAL_JSON_CONFIG = {
            "jira": {
                "task_type_mapping": {
                    "Bug": "fix",
                    "Tâche": "feature"
                }
            }
        }
        
        # Valid cases
        self.assertEqual(generate_branch_name("JIRA-123", "Fix login issue", "Bug"), "fix/JIRA-123_fix_login_issue")
        self.assertEqual(generate_branch_name("JIRA-456", "Add new feature", "Tâche"), "feature/JIRA-456_add_new_feature")
        
        # Title with special characters
        self.assertEqual(generate_branch_name("JIRA-789", "Fix issue #1", "Bug"), "fix/JIRA-789_fix_issue_1")
        
        # Title exceeding 80 characters
        long_title = "This is a very long title that should be truncated to fit within the branch name limit"
        self.assertTrue(len(generate_branch_name("JIRA-101", long_title, "Tâche")) <= 80)

    @patch('src.utils.git_utils.run_command')
    def test_stash_changes(self, mock_run_command):
        mock_run_command.side_effect = ["M  file1.txt", "Saved working directory"]
        
        with patch('builtins.input', return_value='y'):
            result = stash_changes()
            self.assertTrue(result)
            self.assertEqual(mock_run_command.call_count, 2)

    @patch('src.utils.git_utils.run_command')
    def test_apply_stashed_changes(self, mock_run_command):
        mock_run_command.return_value = None
        
        with patch('builtins.input', return_value='y'):
            apply_stashed_changes()
            mock_run_command.assert_called_once_with('git stash apply')
        
        mock_run_command.reset_mock()
        with patch('builtins.input', return_value='n'):
            apply_stashed_changes()
            mock_run_command.assert_not_called()

    @patch('src.utils.git_utils.run_command')
    def test_list_remote_branches(self, mock_run_command):
        mock_run_command.return_value = "  remotes/origin/branch1\n  remotes/origin/branch2\n  remotes/origin/branch3"
        REMOTE_REPO_NAME = "origin"
        branches = list_remote_branches()
        self.assertEqual(branches, ["branch1", "branch2", "branch3"])

    @patch('src.utils.git_utils.run_command')
    def test_select_branch(self, mock_run_command):
        mock_run_command.return_value = "  remotes/origin/branch1\n  remotes/origin/branch2\n  remotes/origin/branch3"
        REMOTE_REPO_NAME = "origin"
        
        with patch('builtins.input', side_effect=["1"]):
            selected_branch = select_branch()
            self.assertEqual(selected_branch, "branch1")
        
        with patch('builtins.input', side_effect=["2"]):
            selected_branch = select_branch()
            self.assertEqual(selected_branch, "branch2")
        
        with patch('builtins.input', side_effect=["3"]):
            selected_branch = select_branch()
            self.assertEqual(selected_branch, "branch3")
        
        with patch('builtins.input', side_effect=["4", "1"]):
            selected_branch = select_branch()
            self.assertEqual(selected_branch, "branch1")

    @patch('src.utils.git_utils.run_command')
    def test_getCurrentTaskNumber(self, mock_run_command):
        mock_run_command.return_value = "feature/JIRA-123_fix_login_issue"
        self.assertEqual(getCurrentTaskNumber(), "JIRA-123")
        
        mock_run_command.return_value = "fix/JIRA-456_fix_bug"
        self.assertEqual(getCurrentTaskNumber(), "JIRA-456")
        
        mock_run_command.return_value = "develop"
        with self.assertRaises(SystemExit):
            getCurrentTaskNumber()

    @patch('src.utils.git_utils.run_command')
    def test_select_files_for_commit(self, mock_run_command):
        mock_run_command.return_value = " M test file1.txt\n M file2.txt\n D file3.txt\n?? file4.txt"
        
        with patch('builtins.input', side_effect=["1", "f", "y"]):
            selected_files = select_files_for_commit()
            self.assertEqual(selected_files, ["test file1.txt"])
        
        with patch('builtins.input', side_effect=[".", "y"]):
            selected_files = select_files_for_commit()
            self.assertEqual(selected_files, ["test file1.txt", "file2.txt", "file4.txt"])
        
        with patch('builtins.input', side_effect=["0"]):
            selected_files = select_files_for_commit()
            self.assertIsNone(selected_files)
        
        with patch('builtins.input', side_effect=["1", "2", "f", "y"]):
            selected_files = select_files_for_commit()
            self.assertEqual(selected_files, ["test file1.txt", "file2.txt"])

if __name__ == '__main__':
    unittest.main()
