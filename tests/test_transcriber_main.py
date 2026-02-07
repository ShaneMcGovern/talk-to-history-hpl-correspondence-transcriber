"""Tests for transcriber.py OCR pipeline."""

from unittest.mock import Mock, patch

import pytest

from transcriber import main


@patch("transcriber.fetch_image_from_url")
@patch("transcriber.encode_image_to_base64")
@patch("transcriber.transcribe_image_text")
@patch("transcriber.save_transcription_to_file")
def test_main_success(mock_save, mock_transcribe, mock_encode, mock_fetch):
    """Test main pipeline executes successfully."""
    mock_image = Mock()
    mock_fetch.return_value = mock_image
    mock_encode.return_value = "base64_data"
    mock_transcribe.return_value = "Transcription"

    main("https://repository.library.brown.edu/iiif/image/bdr:123456/image.jpg")

    mock_save.assert_called_once_with("Transcription", "123456")
    mock_image.close.assert_called_once()


@patch("transcriber.fetch_image_from_url")
def test_main_handles_request_exception(mock_fetch):
    """Test main exits on request exception."""
    mock_fetch.side_effect = Exception("Network error")

    with pytest.raises(SystemExit) as exc_info:
        main("https://example.com/image.jpg")

    assert exc_info.value.code == 1
