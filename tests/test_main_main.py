"""Tests for main.py OCR entry point."""

import argparse
from unittest.mock import patch

from main import main


@patch("main.transcriber.main")
def test_main_success(mock_transcriber_main):
    """Test main returns 0 on successful execution."""
    mock_transcriber_main.return_value = None

    with patch("main.parse_arguments") as mock_parse:
        mock_parse.return_value = argparse.Namespace(
            image_url="https://example.com/image.png"
        )
        exit_code = main()

    assert exit_code == 0
    mock_transcriber_main.assert_called_once_with("https://example.com/image.png")


@patch("main.transcriber.main")
def test_main_handles_exception(mock_transcriber_main, capsys):
    """Test main returns 1 and prints error when exception occurs."""
    mock_transcriber_main.side_effect = ValueError("Invalid image format")

    with patch("main.parse_arguments") as mock_parse:
        mock_parse.return_value = argparse.Namespace(
            image_url="https://example.com/bad.png"
        )
        exit_code = main()

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: Invalid image format" in captured.err
