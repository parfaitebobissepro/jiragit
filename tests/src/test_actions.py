import unittest
from unittest.mock import patch
from src.actions import end_development, start_new_task, continue_development
from src.global_const import TaskStatus, WorkflowTransition
from src.utils.ansi import get_colored_text,YELLOW

class TestActions(unittest.TestCase):

    @patch('builtins.input', side_effect=['Commit message'])
    @patch('builtins.print')
    @patch('src.actions.commit_and_push_changes')
    @patch('src.actions.getCurrentTaskNumber', return_value='JIRA-123')
    def test_end_development(self, mock_get_task_number, mock_commit_and_push_changes, mock_print, mock_input):
        end_development()
        mock_get_task_number.assert_called_once()
        mock_print.assert_any_call(f"Le code de la tâche actuelle est le suivant : {get_colored_text('JIRA-123',YELLOW)}")
        mock_commit_and_push_changes.assert_called_once_with(
            'JIRA-123', 'Commit message', TaskStatus.IN_REVIEW, WorkflowTransition.IN_REVIEW, create_pr=True
        )

    @patch('src.actions.handle_task_creation')
    @patch('builtins.print')
    def test_start_new_task(self, mock_print, mock_handle_task_creation):
        start_new_task()
        mock_print.assert_called_once_with("Développement d'une nouvelle tâche.")
        mock_handle_task_creation.assert_called_once()

    @patch('builtins.input', side_effect=['Commit message'])
    @patch('builtins.print')
    @patch('src.actions.commit_and_push_changes')
    @patch('src.actions.getCurrentTaskNumber', return_value='JIRA-123')
    def test_continue_development(self, mock_get_task_number, mock_commit_and_push_changes, mock_print, mock_input):
        continue_development()
        mock_get_task_number.assert_called_once()
        mock_print.assert_any_call(f"Le code de la tâche actuelle est le suivant : {get_colored_text('JIRA-123',YELLOW)}")
        mock_commit_and_push_changes.assert_called_once_with(
            'JIRA-123', 'Commit message', TaskStatus.IN_PROGRESS, WorkflowTransition.IN_PROGRESS
        )

if __name__ == '__main__':
    unittest.main()