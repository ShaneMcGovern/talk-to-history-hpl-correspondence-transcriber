"""Tests for helper.py batch OCR processor."""

from helper import parse_manifest_for_image_urls


def test_parse_manifest_for_image_urls_with_valid_manifest():
    """Test parsing valid IIIF manifest returns image URLs."""
    manifest_data = {
        "sequences": [
            {
                "canvases": [
                    {"images": [{"resource": {"@id": "https://example.com/image.jpg"}}]}
                ]
            }
        ]
    }

    urls = parse_manifest_for_image_urls(manifest_data)

    assert urls[0] == "https://example.com/image.jpg"


def test_parse_manifest_for_image_urls_with_empty_manifest():
    """Test parsing empty manifest returns empty list."""
    assert parse_manifest_for_image_urls({"sequences": []}) == []
