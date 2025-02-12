import unittest
from unittest.mock import patch, MagicMock
from src.functions_utils import handle_task_creation, commit_and_push_changes
from src.global_const import TaskStatus, WorkflowTransition, REMOTE_REPO_NAME
from src.utils.gitlab_utils import create_merge_request

class TestFunctionsUtils(unittest.TestCase):

    @patch('src.functions_utils.get_task_infos')
    @patch('src.functions_utils.generate_branch_name')
    @patch('src.functions_utils.input')
    @patch('src.functions_utils.select_branch')
    @patch('src.functions_utils.stash_changes')
    @patch('src.functions_utils.run_command')
    @patch('src.functions_utils.jira_task_is_in_status')
    @patch('src.functions_utils.jira_transition')
    def test_handle_task_creation(self, mock_jira_transition, mock_jira_task_is_in_status, mock_run_command, mock_stash_changes, mock_select_branch, mock_input, mock_generate_branch_name, mock_get_task_infos):
        mock_get_task_infos.return_value = ('JIRA-123', 'Test Task', 'Feature')
        mock_generate_branch_name.return_value = 'feature/JIRA-123-test-task'
        mock_input.return_value = 'feature/JIRA-123-test-task'
        mock_select_branch.return_value = 'main'
        mock_run_command.side_effect = ['Switched to branch \'main\'', 'Already up to date.', 'Switched to a new branch \'feature/JIRA-123-test-task\'']
        mock_jira_task_is_in_status.return_value = False

        handle_task_creation()

        mock_get_task_infos.assert_called_once()
        mock_generate_branch_name.assert_called_once_with('JIRA-123', 'Test Task', type='Feature')
        mock_input.assert_called_once()
        mock_select_branch.assert_called_once()
        mock_stash_changes.assert_called_once()
        mock_run_command.assert_any_call('git checkout main')
        mock_run_command.assert_any_call(f'git pull {REMOTE_REPO_NAME} main')
        mock_run_command.assert_any_call('git checkout -b feature/JIRA-123-test-task')
        mock_jira_task_is_in_status.assert_called_once_with('JIRA-123', TaskStatus.IN_PROGRESS.value)
        mock_jira_transition.assert_called_once_with('JIRA-123', WorkflowTransition.IN_PROGRESS)

    @patch('src.functions_utils.select_files_for_commit')
    @patch('src.functions_utils.run_command')
    @patch('src.functions_utils.jira_add_comment')
    @patch('src.functions_utils.jira_task_is_in_status')
    @patch('src.functions_utils.jira_transition')
    def test_commit_and_push_changes(self, mock_jira_transition, mock_jira_task_is_in_status, mock_jira_add_comment, mock_run_command, mock_select_files_for_commit):
        mock_select_files_for_commit.return_value = True
        mock_jira_task_is_in_status.return_value = False
        mock_run_command.side_effect = ['[master 09f4acd] Updated index.html \n 1 file changed, 1 insertion(+)','current-branch', '', 'Well pushed!']

        with patch('src.functions_utils.create_merge_request') as mock_create_merge_request:
            mock_create_merge_request.return_value = 'http://example.com/mr/1'
            commit_and_push_changes('JIRA-123', 'Test commit', TaskStatus.IN_REVIEW, WorkflowTransition.IN_REVIEW, create_pr=True)

            mock_select_files_for_commit.assert_called_once()
            mock_run_command.assert_any_call('git commit -m "feat:JIRA-123 - Test commit"')
            mock_jira_add_comment.assert_called_once_with('JIRA-123', 'Test commit', 'http://example.com/mr/1')
            mock_jira_task_is_in_status.assert_called_once_with('JIRA-123', TaskStatus.IN_REVIEW.value)
            mock_jira_transition.assert_called_once_with('JIRA-123', WorkflowTransition.IN_REVIEW)
            mock_create_merge_request.assert_called_once_with('current-branch', 'Merge branch current-branch into develop')

    @patch('src.functions_utils.get_task_infos')
    @patch('src.functions_utils.generate_branch_name')
    @patch('src.functions_utils.input')
    @patch('src.functions_utils.select_branch')
    @patch('src.functions_utils.stash_changes')
    @patch('src.functions_utils.run_command')
    @patch('src.functions_utils.jira_task_is_in_status')
    @patch('src.functions_utils.jira_transition')
    def test_handle_task_creation_with_bug(self, mock_jira_transition, mock_jira_task_is_in_status, mock_run_command, mock_stash_changes, mock_select_branch, mock_input, mock_generate_branch_name, mock_get_task_infos):
        mock_get_task_infos.return_value = ('JIRA-456', 'Fix Bug', 'Bug')
        mock_generate_branch_name.return_value = 'fix/JIRA-456-fix-bug'
        mock_input.return_value = 'fix/JIRA-456-fix-bug'
        mock_run_command.side_effect = ['Switched to branch \'develop\'', 'Already up to date.', 'Switched to a new branch \'fix/JIRA-456-fix-bug\'']
        mock_jira_task_is_in_status.return_value = False

        handle_task_creation()

        mock_get_task_infos.assert_called_once()
        mock_generate_branch_name.assert_called_once_with('JIRA-456', 'Fix Bug', type='Bug')
        mock_input.assert_called_once()
        mock_select_branch.assert_not_called()
        mock_stash_changes.assert_called_once()
        mock_run_command.assert_any_call('git checkout develop')
        mock_run_command.assert_any_call(f'git pull {REMOTE_REPO_NAME} develop')
        mock_run_command.assert_any_call('git checkout -b fix/JIRA-456-fix-bug')
        mock_jira_task_is_in_status.assert_called_once_with('JIRA-456', TaskStatus.IN_PROGRESS.value)
        mock_jira_transition.assert_called_once_with('JIRA-456', WorkflowTransition.IN_PROGRESS)

    @patch('src.functions_utils.select_files_for_commit')
    @patch('src.functions_utils.run_command')
    @patch('src.functions_utils.jira_add_comment')
    @patch('src.functions_utils.jira_task_is_in_status')
    @patch('src.functions_utils.jira_transition')
    def test_commit_and_push_changes_no_files_selected(self, mock_jira_transition, mock_jira_task_is_in_status, mock_jira_add_comment, mock_run_command, mock_select_files_for_commit):
        mock_select_files_for_commit.return_value = False

        with patch('src.functions_utils.create_merge_request') as mock_create_merge_request:
            commit_and_push_changes('JIRA-789', 'Test commit', TaskStatus.IN_REVIEW, WorkflowTransition.IN_REVIEW, create_pr=True)

            mock_select_files_for_commit.assert_called_once()
            mock_run_command.assert_not_called()
            mock_jira_add_comment.assert_not_called()
            mock_jira_task_is_in_status.assert_not_called()
            mock_jira_transition.assert_not_called()
            mock_create_merge_request.assert_not_called()

    if __name__ == '__main__':
        unittest.main()