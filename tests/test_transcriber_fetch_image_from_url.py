"""Tests for transcriber.py OCR pipeline."""

from unittest.mock import Mock, patch

import pytest

from transcriber import RetryableHTTPError, fetch_image_from_url


@patch("transcriber.get_session")
def test_fetch_image_from_url_success(mock_get_session):
    """Test fetching image from URL."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"fake_image_data"

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_get_session.return_value = mock_session

    with patch("transcriber.Image.open") as mock_image_open:
        mock_image = Mock()
        mock_image_open.return_value = mock_image

        result = fetch_image_from_url("https://example.com/image.jpg")

        assert result == mock_image


@patch("transcriber.get_session")
def test_fetch_image_from_url_raises_on_retryable_error(mock_get_session):
    """Test raises RetryableHTTPError on 503 status."""
    mock_response = Mock()
    mock_response.status_code = 503

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_get_session.return_value = mock_session

    with pytest.raises(RetryableHTTPError):
        fetch_image_from_url("https://example.com/image.jpg")


@patch("transcriber.get_session")
def test_fetch_image_from_url_handles_decode_error(mock_get_session):
    """Test fetch_image_from_url handles image decode errors."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"invalid_image_data"

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_get_session.return_value = mock_session

    with patch("transcriber.Image.open") as mock_image_open:
        mock_image_open.side_effect = Exception("Invalid image")

        with pytest.raises(Exception):
            fetch_image_from_url("https://example.com/bad.jpg")
