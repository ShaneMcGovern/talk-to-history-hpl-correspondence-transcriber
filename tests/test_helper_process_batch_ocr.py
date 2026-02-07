"""Tests for helper.py batch OCR processor."""

from unittest.mock import Mock, patch

from helper import process_batch_ocr


@patch("helper.fetch_image_urls_from_manifest")
def test_process_batch_ocr_calls_transcriber(mock_fetch_urls):
    """Test batch OCR calls transcriber for each image."""
    mock_fetch_urls.return_value = ["https://example.com/img.jpg"]
    mock_transcriber = Mock()

    process_batch_ocr(pids=["bdr:123456"], transcribe_func=mock_transcriber)

    mock_transcriber.assert_called_once_with("https://example.com/img.jpg")
