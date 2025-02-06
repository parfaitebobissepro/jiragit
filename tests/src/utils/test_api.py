import unittest
from unittest.mock import patch, Mock
from src.utils.api import api_call

class TestApiCall(unittest.TestCase):

    @patch('requests.get')
    def test_api_call_get_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        url = "http://example.com"
        method = "GET"
        endpoint = "/api/test"
        response = api_call(url, method, endpoint)

        mock_get.assert_called_once_with(f"{url}{endpoint}", auth=None, headers=None)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"key": "value"})

    @patch('requests.post')
    def test_api_call_post_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "value"}
        mock_post.return_value = mock_response

        url = "http://example.com"
        method = "POST"
        endpoint = "/api/test"
        payload = {"data": "test"}
        response = api_call(url, method, endpoint, payload=payload)

        mock_post.assert_called_once_with(f"{url}{endpoint}", json=payload, auth=None, headers=None)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"key": "value"})

    @patch('requests.get')
    def test_api_call_get_with_auth(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        url = "http://example.com"
        method = "GET"
        endpoint = "/api/test"
        auth = ('user', 'pass')
        response = api_call(url, method, endpoint, auth=auth)

        mock_get.assert_called_once_with(f"{url}{endpoint}", auth=auth, headers=None)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"key": "value"})

    @patch('requests.post')
    def test_api_call_post_with_headers(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "value"}
        mock_post.return_value = mock_response

        url = "http://example.com"
        method = "POST"
        endpoint = "/api/test"
        headers = {'Content-Type': 'application/json'}
        payload = {"data": "test"}
        response = api_call(url, method, endpoint, headers=headers, payload=payload)

        mock_post.assert_called_once_with(f"{url}{endpoint}", json=payload, auth=None, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"key": "value"})

    def test_api_call_invalid_method(self):
        url = "http://example.com"
        method = "PUT"
        endpoint = "/api/test"
        
        with self.assertRaises(ValueError) as context:
            api_call(url, method, endpoint)
        
        self.assertEqual(str(context.exception), "Unsupported HTTP method")

if __name__ == '__main__':
    unittest.main()