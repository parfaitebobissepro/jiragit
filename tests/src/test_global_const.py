import unittest
from unittest.mock import patch
from src.global_const import WorkflowTransition, TaskStatus, REMOTE_REPO_NAME

class TestGlobalConst(unittest.TestCase):

    @patch('src.global_const.load_config')
    def test_constants_from_config(self, mock_load_config):
        mock_config = {
            "jira": {
                "transitions": {
                    "IN_PROGRESS": "2",
                    "IN_REVIEW": "3"
                },
                "task_status": {
                    "IN_PROGRESS": "En cours",
                    "IN_REVIEW": "Revue en cours"
                }
            }
        }
        
        mock_load_config.return_value = mock_config

        # Test WorkflowTransition values
        self.assertEqual(WorkflowTransition.IN_PROGRESS.value, "2")
        self.assertEqual(WorkflowTransition.IN_REVIEW.value, "3")

        # Test TaskStatus values
        self.assertEqual(TaskStatus.IN_PROGRESS.value, "En cours")
        self.assertEqual(TaskStatus.IN_REVIEW.value, "Revue en cours")

        # Test REMOTE_REPO_NAME
        self.assertEqual(REMOTE_REPO_NAME, "origin")

if __name__ == '__main__':
    unittest.main()