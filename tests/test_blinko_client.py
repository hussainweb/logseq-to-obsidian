import json
import unittest
from unittest.mock import MagicMock, patch

from logseq_converter.blinko.client import BlinkoClient


class TestBlinkoClient(unittest.TestCase):
    def setUp(self):
        self.valid_token = "header.payload.signature"
        self.endpoint = "http://example.com"

    def test_init_validates_token(self):
        with self.assertRaises(ValueError):
            BlinkoClient(self.endpoint, "")

        with self.assertRaises(ValueError):
            BlinkoClient(self.endpoint, "invalid_token")

        # Should not raise
        BlinkoClient(self.endpoint, self.valid_token)

    @patch("urllib.request.urlopen")
    def test_upsert_note_success(self, mock_urlopen):
        client = BlinkoClient(self.endpoint, self.valid_token)

        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({"success": True}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = client.upsert_note("test content")
        self.assertEqual(result, {"success": True})

        # Verify request
        args, kwargs = mock_urlopen.call_args
        req = args[0]
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.full_url, "http://example.com/v1/note/upsert")

        headers = req.headers
        self.assertEqual(headers["Authorization"], f"Bearer {self.valid_token}")
        self.assertEqual(headers["Content-type"], "application/json")

        # Verify payload
        data = json.loads(req.data)
        self.assertEqual(data["content"], "test content")
        self.assertEqual(data["type"], 1)

    @patch("urllib.request.urlopen")
    def test_upsert_note_with_id(self, mock_urlopen):
        client = BlinkoClient(self.endpoint, self.valid_token)

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"{}"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client.upsert_note("content", original_id=123)

        req = mock_urlopen.call_args[0][0]
        data = json.loads(req.data)
        self.assertEqual(data["id"], 123)
