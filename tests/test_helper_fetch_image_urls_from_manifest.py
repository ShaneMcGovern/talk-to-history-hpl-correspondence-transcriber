"""Tests for helper.py batch OCR processor."""

from unittest.mock import Mock, patch

import pytest

from helper import RetryableHTTPError, fetch_image_urls_from_manifest


@patch("helper.get_session")
def test_fetch_image_urls_from_manifest_success(mock_get_session):
    """Test fetching image URLs from manifest."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "sequences": [
            {
                "canvases": [
                    {"images": [{"resource": {"@id": "https://example.com/img.jpg"}}]}
                ]
            }
        ]
    }

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_get_session.return_value = mock_session

    urls = fetch_image_urls_from_manifest("bdr:123456")

    assert urls[0] == "https://example.com/img.jpg"


@patch("helper.get_session")
def test_fetch_image_urls_from_manifest_raises_on_retryable_error(mock_get_session):
    """Test fetching raises RetryableHTTPError on 503 status."""
    mock_response = Mock()
    mock_response.status_code = 503

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_get_session.return_value = mock_session

    with pytest.raises(RetryableHTTPError):
        fetch_image_urls_from_manifest("bdr:123456")
