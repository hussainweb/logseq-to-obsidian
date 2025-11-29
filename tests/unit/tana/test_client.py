from unittest.mock import patch

import pytest

from logseq_converter.tana.client import TanaClient
from logseq_converter.tana.models import TanaNode


@pytest.fixture
def tana_client():
    return TanaClient(api_key="test_key")


def test_init_raises_error_without_api_key(monkeypatch):
    monkeypatch.delenv("TANA_API_KEY", raising=False)
    with pytest.raises(ValueError):
        TanaClient()


def test_send_nodes_success(tana_client):
    nodes = [TanaNode(name="Test Node")]
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {}

        tana_client.send_nodes(nodes, target_node_id="INBOX")

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer test_key"
        assert kwargs["json"]["targetNodeId"] == "INBOX"
        assert len(kwargs["json"]["nodes"]) == 1


def test_send_nodes_batches_requests(tana_client):
    # Create 150 nodes
    nodes = [TanaNode(name=f"Node {i}") for i in range(150)]

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200

        tana_client.send_nodes(nodes, target_node_id="INBOX")

        assert mock_post.call_count == 2
        # First batch 100, second batch 50
        first_call_json = mock_post.call_args_list[0][1]["json"]
        second_call_json = mock_post.call_args_list[1][1]["json"]
        assert len(first_call_json["nodes"]) == 100
        assert len(second_call_json["nodes"]) == 50


def test_send_nodes_respects_rate_limit(tana_client):
    nodes = [TanaNode(name=f"Node {i}") for i in range(150)]

    with patch("requests.post") as mock_post, patch("time.sleep") as mock_sleep:
        mock_post.return_value.status_code = 200

        tana_client.send_nodes(nodes, target_node_id="INBOX")

        assert mock_sleep.called
