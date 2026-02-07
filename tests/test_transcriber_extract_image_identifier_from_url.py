"""Tests for transcriber.py OCR pipeline."""

from transcriber import extract_image_identifier_from_url


def test_extract_image_identifier_from_url_with_valid_bdr():
    """Test extracting BDR identifier from URL."""
    url = "https://repository.library.brown.edu/iiif/image/bdr:123456/full/full/0/default.jpg"

    identifier = extract_image_identifier_from_url(url)

    assert identifier == "123456"


def test_extract_image_identifier_from_url_without_bdr():
    """Test returns None when no BDR identifier in URL."""
    identifier = extract_image_identifier_from_url("https://example.com/image.jpg")

    assert identifier is None
