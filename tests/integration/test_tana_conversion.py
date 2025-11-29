from unittest.mock import patch

import pytest

from logseq_converter.logseq.models import Block, Page
from logseq_converter.tana.models import TanaNode


@pytest.fixture
def mock_logseq_dir(tmp_path):
    """Create a mock LogSeq directory structure."""
    pages_dir = tmp_path / "pages"
    journals_dir = tmp_path / "journals"
    pages_dir.mkdir()
    journals_dir.mkdir()

    # Create a sample page
    (pages_dir / "test_page.md").write_text("- Test content\n  - Nested content")

    # Create a sample journal
    (journals_dir / "2024_01_01.md").write_text("- Journal entry")

    return tmp_path


def test_tana_conversion_integration(mock_logseq_dir):
    """Test the full conversion flow from LogSeq to Tana."""
    with (
        patch("logseq_converter.tana.client.TanaClient") as MockClient,
        patch("logseq_converter.logseq.parser.LogSeqParser") as MockParser,
        patch("logseq_converter.tana.converter.TanaConverter") as MockConverter,
    ):
        # Setup mocks
        mock_client_instance = MockClient.return_value
        mock_parser_instance = MockParser.return_value
        mock_converter_instance = MockConverter.return_value

        # Mock parser to return a page with blocks
        mock_page = Page(filename="test_page.md", content="- Test content", blocks=[Block(content="Test content")])
        mock_parser_instance.parse.return_value = mock_page

        # Mock converter to return a TanaNode
        mock_node = TanaNode(name="Test content")
        mock_converter_instance.convert_block.return_value = mock_node

        # Import here after mocks are set up
        from logseq_converter.cli import convert_to_tana

        # Run the conversion
        result = convert_to_tana(mock_logseq_dir, "INBOX", verbose=False, dry_run=False)

        # Verify the conversion succeeded
        assert result == 0

        # Verify the client was called with nodes
        mock_client_instance.send_nodes.assert_called_once()
        call_args = mock_client_instance.send_nodes.call_args
        assert call_args[1]["target_node_id"] == "INBOX"
        assert len(call_args[0][0]) > 0  # At least one node was sent


def test_tana_conversion_dry_run(mock_logseq_dir):
    """Test that dry run doesn't actually send data."""
    with patch("logseq_converter.tana.client.TanaClient") as MockClient:
        mock_client_instance = MockClient.return_value

        from logseq_converter.cli import convert_to_tana

        result = convert_to_tana(mock_logseq_dir, "INBOX", verbose=False, dry_run=True)

        assert result == 0
        mock_client_instance.send_nodes.assert_not_called()


def test_tana_conversion_missing_api_key(mock_logseq_dir, monkeypatch):
    """Test that missing API key is handled gracefully."""
    monkeypatch.delenv("TANA_API_KEY", raising=False)

    error_msg = "TANA_API_KEY environment variable is not set."
    with patch("logseq_converter.tana.client.TanaClient", side_effect=ValueError(error_msg)):
        from logseq_converter.cli import convert_to_tana

        result = convert_to_tana(mock_logseq_dir, "INBOX", verbose=False, dry_run=False)

        assert result == 1
