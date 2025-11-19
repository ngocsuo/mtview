import unittest
from unittest.mock import patch, MagicMock

from proxy_module import ProxyManager, ProxyAPIError


class TestProxyManager(unittest.TestCase):
    def setUp(self):
        self.pm = ProxyManager(base_url="http://127.0.0.1:5000")

    @patch("proxy_module.manager.requests.request")
    def test_create_proxy_parsing(self, mock_req):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {
            "instance_id": "abc123",
            "proxy_endpoint": "127.0.0.1:60000",
            "ipv6_address": "2001:db8::1",
            "interface": "Ethernet",
            "type": "socks5",
            "created_at": 1731920000.0,
        }
        mock_req.return_value = mock_resp
        inst = self.pm.create_proxy("socks5", "Ethernet")
        self.assertEqual(inst.instance_id, "abc123")
        self.assertIn("socks5", inst.to_requests_proxies()["http"])  # scheme check

    @patch("proxy_module.manager.requests.request")
    def test_error_status(self, mock_req):
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 500
        mock_resp.text = "Server Error"
        mock_req.return_value = mock_resp
        with self.assertRaises(ProxyAPIError):
            self.pm.list_proxies()


if __name__ == "__main__":
    unittest.main()
