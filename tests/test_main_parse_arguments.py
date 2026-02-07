"""Tests for main.py OCR entry point."""

import pytest

from main import parse_arguments


def test_parse_arguments_with_valid_url():
    """Test parse_arguments accepts valid image URL."""
    args = parse_arguments(["--image-url", "https://example.com/image.png"])
    assert args.image_url == "https://example.com/image.png"


def test_parse_arguments_missing_required_argument():
    """Test parse_arguments fails when image-url is missing."""
    with pytest.raises(SystemExit):
        parse_arguments([])


def test_parse_arguments_with_hyphen_flag():
    """Test parse_arguments correctly handles hyphenated flag."""
    args = parse_arguments(["--image-url", "http://test.com/img.jpg"])
    assert hasattr(args, "image_url")
