"""Tests for transcriber.py OCR pipeline."""

from unittest.mock import Mock, patch

import pytest

from transcriber import encode_image_to_base64


def test_encode_image_to_base64():
    """Test encoding PIL Image to base64 string."""
    mock_image = Mock()
    mock_image.format = "JPEG"

    with patch.object(mock_image, "save") as mock_save:

        def save_side_effect(buffer, format):
            buffer.write(b"test_data")

        mock_save.side_effect = save_side_effect

        result = encode_image_to_base64(mock_image)

        assert result == "dGVzdF9kYXRh"


def test_encode_image_to_base64_handles_save_error():
    """Test encode_image_to_base64 handles save errors."""
    mock_image = Mock()
    mock_image.format = "JPEG"
    mock_image.save.side_effect = Exception("Save failed")

    with pytest.raises(Exception):
        encode_image_to_base64(mock_image)
