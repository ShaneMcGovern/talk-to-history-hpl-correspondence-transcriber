"""Tests for transcriber.py OCR pipeline."""

from transcriber import save_transcription_to_file


def test_save_transcription_to_file(tmp_path):
    """Test saving transcription to file."""
    output_dir = tmp_path / "output"

    save_transcription_to_file("Test content", "123456", output_dir)

    assert (output_dir / "123456.txt").read_text() == "Test content"
