import unittest
from unittest.mock import patch, MagicMock
from src.utils.gitlab_utils import get_gitlab_token, get_remote_url, extract_project_path, get_project_id, create_merge_request
from src.global_const import GLOBAL_JSON_CONFIG, REMOTE_REPO_NAME

class TestGitlabUtils(unittest.TestCase):

    @patch('src.utils.gitlab_utils.GLOBAL_JSON_CONFIG', {
        "gitlab": {
            "token": "main_token",
            "tokens": [{"project1": "token1"}, {"project2": "token2"}],
            "url": "https://gitlab.com"
        }
    })
    def test_get_gitlab_token_main_token(self):
        token = get_gitlab_token("project1")
        self.assertEqual(token, "main_token")

    @patch('src.utils.gitlab_utils.GLOBAL_JSON_CONFIG', {
        "gitlab": {
            "tokens": [{"project1": "token1"}, {"project2": "token2"}],
            "url": "https://gitlab.com"
        }
    })
    def test_get_gitlab_token_project_token(self):
        token = get_gitlab_token("project1")
        self.assertEqual(token, "token1")

    @patch('src.utils.gitlab_utils.GLOBAL_JSON_CONFIG', {
        "gitlab": {
            "tokens": [{"project1": "token1"}, {"project2": "token2"}],
            "url": "https://gitlab.com"
        }
    })

    def test_get_gitlab_token_no_token(self):
        token = get_gitlab_token("unknown_project")
        self.assertIsNone(token)

    @patch('src.utils.gitlab_utils.run_command')
    def test_get_remote_url_success(self, mock_run_command):
        mock_run_command.return_value = "https://gitlab.com/user/repo.git"
        remote_url = get_remote_url()
        self.assertEqual(remote_url, "https://gitlab.com/user/repo.git")

    @patch('src.utils.gitlab_utils.run_command')
    def test_get_remote_url_failure(self, mock_run_command):
        mock_run_command.return_value = ""
        remote_url = get_remote_url()
        self.assertIsNone(remote_url)

    def test_extract_project_path_success(self):
        remote_url = "https://gitlab.com/user/repo.git"
        project_path = extract_project_path(remote_url)
        self.assertEqual(project_path, "user/repo")

    def test_extract_project_path_failure(self):
        remote_url = "https://github.com/user/repo.git" # Not a GitLab URL, Github will be developed in the future
        project_path = extract_project_path(remote_url)
        self.assertIsNone(project_path)

    @patch('src.utils.gitlab_utils.get_remote_url')
    @patch('src.utils.gitlab_utils.extract_project_path')
    @patch('src.utils.gitlab_utils.api_call')
    def test_get_project_id_success(self, mock_api_call, mock_extract_project_path, mock_get_remote_url):
        mock_get_remote_url.return_value = "https://gitlab.com/user/repo.git"
        mock_extract_project_path.return_value = "user/repo"
        mock_api_call.return_value = MagicMock(json=lambda: {"id": 123})

        project_id, project_path = get_project_id("valid_token")
        self.assertEqual(project_id, 123)
        self.assertEqual(project_path, "user/repo")

    @patch('src.utils.gitlab_utils.get_remote_url')
    @patch('src.utils.gitlab_utils.extract_project_path')
    @patch('src.utils.gitlab_utils.api_call')
    def test_get_project_id_failure(self, mock_api_call, mock_extract_project_path, mock_get_remote_url):
        mock_get_remote_url.return_value = None
        project_id, project_path = get_project_id("valid_token")
        self.assertIsNone(project_id)
        self.assertIsNone(project_path)

    @patch('src.utils.gitlab_utils.get_project_id')
    @patch('src.utils.gitlab_utils.get_gitlab_token')
    @patch('src.utils.gitlab_utils.api_call')
    @patch('builtins.input', lambda _: "Test description")
    def test_create_merge_request_success(self, mock_api_call, mock_get_gitlab_token, mock_get_project_id):
        mock_get_project_id.return_value = (123, "user/repo")
        mock_get_gitlab_token.return_value = "valid_token"
        mock_api_call.return_value = MagicMock(json=lambda: {"web_url": "https://gitlab.com/user/repo/merge_requests/1"})

        with patch('builtins.print') as mocked_print:
            create_merge_request("feature_branch", "Test MR")
            mocked_print.assert_any_call("✅ Merge Request créée avec succès :", "https://gitlab.com/user/repo/merge_requests/1")

    @patch('src.utils.gitlab_utils.get_project_id')
    @patch('src.utils.gitlab_utils.get_gitlab_token')
    @patch('src.utils.gitlab_utils.api_call')
    @patch('builtins.input', lambda _: "Test description")
    def test_create_merge_request_failure(self, mock_api_call, mock_get_gitlab_token, mock_get_project_id):
        mock_get_project_id.return_value = (None, None)
        mock_get_gitlab_token.return_value = "valid_token"
        mock_api_call.return_value = None

        with patch('builtins.print') as mocked_print:
            create_merge_request("feature_branch", "Test MR")
            mocked_print.assert_any_call("❌ Impossible de récupérer l'ID du projet. Annulation de la MR.")

if __name__ == '__main__':
    unittest.main()
