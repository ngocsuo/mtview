import unittest
from unittest.mock import patch, MagicMock

from hidemium_module import HidemiumClient, HidemiumAPIError, HidemiumValidationError


class TestHidemiumClient(unittest.TestCase):
    def setUp(self):
        self.client = HidemiumClient()

    @patch("hidemium_module.client.requests.request")
    def test_get_default_configs(self, mock_req):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {
            "data": {"content": [{"id": 123, "name": "Test Config"}]}
        }
        mock_req.return_value = mock_resp

        configs = self.client.get_default_configs(page=1, limit=5)
        self.assertIn("data", configs)
        self.assertEqual(configs["data"]["content"][0]["id"], 123)

    @patch("hidemium_module.client.requests.request")
    def test_create_profile_by_default(self, mock_req):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"uuid": "abc-123", "profileUUID": "abc-123"}
        mock_req.return_value = mock_resp

        result = self.client.create_profile_by_default(123, is_local=True)
        self.assertEqual(result["uuid"], "abc-123")

    @patch("hidemium_module.client.requests.request")
    def test_open_profile(self, mock_req):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"status": "opened"}
        mock_req.return_value = mock_resp

        result = self.client.open_profile("abc-123", proxy="SOCKS5|127.0.0.1|60000")
        self.assertEqual(result["status"], "opened")

    @patch("hidemium_module.client.requests.request")
    def test_close_profile(self, mock_req):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"status": "closed"}
        mock_req.return_value = mock_resp

        result = self.client.close_profile("abc-123")
        self.assertEqual(result["status"], "closed")

    @patch("hidemium_module.client.requests.request")
    def test_api_error_handling(self, mock_req):
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_req.return_value = mock_resp

        with self.assertRaises(HidemiumAPIError):
            self.client.get_default_configs()

    def test_validation_error(self):
        with self.assertRaises(HidemiumValidationError):
            self.client.create_profile_by_default(-1)

    @patch("hidemium_module.client.requests.request")
    def test_create_and_open(self, mock_req):
        # Mock create
        create_resp = MagicMock()
        create_resp.ok = True
        create_resp.json.return_value = {"uuid": "test-uuid"}

        # Mock profile info (readiness)
        info_resp = MagicMock()
        info_resp.ok = True
        info_resp.json.return_value = {"uuid": "test-uuid", "ready": True}

        # Mock open
        open_resp = MagicMock()
        open_resp.ok = True
        open_resp.json.return_value = {"status": "opened"}

        mock_req.side_effect = [create_resp, info_resp, open_resp]

        result = self.client.create_and_open(
            profile_name="Test",
            proxy="SOCKS5|127.0.0.1|60000",
            wait_ready=True,
        )
        self.assertEqual(result["uuid"], "test-uuid")
        self.assertIn("open_response", result)


if __name__ == "__main__":
    unittest.main()
