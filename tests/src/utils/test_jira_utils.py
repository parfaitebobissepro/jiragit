import unittest
from unittest.mock import patch, MagicMock
from src.utils.jira_utils import (
    jira_api_call, jira_task_exists, jira_transition, get_task_infos,
    get_current_sprint_tasks, jira_add_comment, jira_task_is_in_status
)
from src.global_const import GLOBAL_JSON_CONFIG

class TestJiraUtils(unittest.TestCase):

    @patch('src.utils.jira_utils.api_call')
    def test_jira_api_call(self, mock_api_call):
        mock_api_call.return_value = MagicMock(status_code=200, json=lambda: {"key": "value"})
        response = jira_api_call("GET", "/test-endpoint")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"key": "value"})
        mock_api_call.assert_called_once()

    @patch('src.utils.jira_utils.jira_api_call')
    def test_jira_task_exists(self, mock_jira_api_call):
        mock_jira_api_call.return_value = MagicMock(status_code=200, json=lambda: {"fields": {"issuetype": {"name": "Bug"}}})
        response = jira_task_exists("JIRA-123")
        self.assertIsNotNone(response)
        self.assertEqual(response["fields"]["issuetype"]["name"], "Bug")
        mock_jira_api_call.assert_called_once()

        mock_jira_api_call.return_value = MagicMock(status_code=404)
        response = jira_task_exists("JIRA-999")
        self.assertIsNone(response)
        mock_jira_api_call.assert_called_with("GET", "/rest/api/3/issue/JIRA-999")

    @patch('src.utils.jira_utils.jira_api_call')
    def test_jira_transition(self, mock_jira_api_call):
        mock_jira_api_call.return_value = MagicMock(status_code=204)
        status_transition_enum = MagicMock(value="31", name="Done")
        jira_transition("JIRA-123", status_transition_enum)
        mock_jira_api_call.assert_called_once_with("POST", "/rest/api/3/issue/JIRA-123/transitions", {"transition": {"id": "31"}})

        mock_jira_api_call.return_value = MagicMock(status_code=400, text="Bad Request")
        jira_transition("JIRA-123", status_transition_enum)
        mock_jira_api_call.assert_called_with("POST", "/rest/api/3/issue/JIRA-123/transitions", {"transition": {"id": "31"}})

    @patch('src.utils.jira_utils.jira_task_exists')
    @patch('src.utils.jira_utils.get_current_sprint_tasks')
    def test_get_task_infos(self, mock_get_current_sprint_tasks, mock_jira_task_exists):
        mock_get_current_sprint_tasks.return_value = [("JIRA-123", "Summary 1", "Tâche"), ("JIRA-124", "Summary 2", "Bug")]
        with patch('builtins.input', side_effect=["1"]):
            mock_jira_task_exists.return_value = {"fields": {"issuetype": {"name": "Tâche"}, "summary": "Summary 1"}}
            task_number, task_summary, task_type = get_task_infos()
            self.assertEqual(task_number, "JIRA-123")
            self.assertEqual(task_summary, "Summary 1")
            self.assertEqual(task_type, "Tâche")

        with patch('builtins.input', side_effect=["2"]):
            mock_jira_task_exists.return_value = {"fields": {"issuetype": {"name": "Bug"}, "summary": "Summary 2"}}
            task_number, task_summary, task_type = get_task_infos()
            self.assertEqual(task_number, "JIRA-124")
            self.assertEqual(task_summary, "Summary 2")
            self.assertEqual(task_type, "Bug")

        with patch('builtins.input', side_effect=["3", "JIRA-125"]):
            mock_jira_task_exists.return_value = {"fields": {"issuetype": {"name": "Tâche"}, "summary": "Summary 3"}}
            task_number, task_summary, task_type = get_task_infos()
            self.assertEqual(task_number, "JIRA-125")
            self.assertEqual(task_summary, "Summary 3")
            self.assertEqual(task_type, "Tâche")

    @patch('src.utils.jira_utils.jira_api_call')
    def test_get_current_sprint_tasks(self, mock_jira_api_call):
        mock_jira_api_call.side_effect = [
            MagicMock(status_code=200, json=lambda: {"values": [{"id": 1}]}),
            MagicMock(status_code=200, json=lambda: {"issues": [{"key": "JIRA-123", "fields": {"summary": "Summary 1", "issuetype": {"name": "Tâche"}}}]})
        ]
        tasks = get_current_sprint_tasks()
        self.assertEqual(tasks, [("JIRA-123", "Summary 1", "Tâche")])
        self.assertEqual(mock_jira_api_call.call_count, 2)

        mock_jira_api_call.side_effect = [
            MagicMock(status_code=200, json=lambda: {"values": []}),
        ]
        tasks = get_current_sprint_tasks()
        self.assertEqual(tasks, [])

    @patch('src.utils.jira_utils.jira_api_call')
    def test_jira_add_comment(self, mock_jira_api_call):
        mock_jira_api_call.return_value = MagicMock(status_code=201)
        jira_add_comment("JIRA-123", "This is a comment", "http://example.com/mr/1")
        mock_jira_api_call.assert_called_once_with("POST", "/rest/api/3/issue/JIRA-123/comment", {
            "body": {
                "content": [
                    {
                        "content": [
                            {
                                "text": "This is a comment",
                                "type": "text"
                            },
                            {
                                "text":"[Voir la merge request]",
                                "type":"text",
                                "marks":[
                                {
                                    "type":"link",
                                    "attrs":{
                                    "href": "http://example.com/mr/1"
                                    }
                                }
                                ]
                            }
                        ],
                        "type": "paragraph"
                    }
                ],
                "type": "doc",
                "version": 1
            }
        })

        mock_jira_api_call.return_value = MagicMock(status_code=400, text="Bad Request")
        jira_add_comment("JIRA-123", "This is a comment", "http://example.com/mr/1")
        mock_jira_api_call.assert_called_with("POST", "/rest/api/3/issue/JIRA-123/comment", {
            "body": {
                "content": [
                    {
                        "content": [
                            {
                                "text": "This is a comment",
                                "type": "text"
                            },
                            {
                                "text":"[Voir la merge request]",
                                "type":"text",
                                "marks":[
                                {
                                    "type":"link",
                                    "attrs":{
                                    "href": "http://example.com/mr/1"
                                    }
                                }
                                ]
                            }
                        ],
                        "type": "paragraph"
                    }
                ],
                "type": "doc",
                "version": 1
            }
        })

    @patch('src.utils.jira_utils.jira_api_call')
    def test_jira_task_is_in_status(self, mock_jira_api_call):
        mock_jira_api_call.return_value = MagicMock(status_code=200, json=lambda: {"fields": {"status": {"name": "Done"}}})
        self.assertTrue(jira_task_is_in_status("JIRA-123", "Done"))
        mock_jira_api_call.assert_called_once_with("GET", "/rest/api/3/issue/JIRA-123")

        mock_jira_api_call.return_value = MagicMock(status_code=200, json=lambda: {"fields": {"status": {"name": "In Progress"}}})
        self.assertFalse(jira_task_is_in_status("JIRA-123", "Done"))

        mock_jira_api_call.return_value = MagicMock(status_code=404)
        self.assertFalse(jira_task_is_in_status("JIRA-999", "Done"))

if __name__ == '__main__':
    unittest.main()