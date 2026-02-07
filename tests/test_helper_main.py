"""Tests for helper.py batch OCR processor."""

from unittest.mock import patch

from helper import main


@patch("helper.process_batch_ocr")
def test_main_returns_zero_on_success(mock_process):
    """Test main returns 0 on successful execution."""
    exit_code = main()

    assert exit_code == 0
    mock_process.assert_called_once()


@patch("helper.process_batch_ocr")
def test_main_returns_one_on_exception(mock_process):
    """Test main returns 1 when exception occurs."""
    mock_process.side_effect = ValueError("Processing failed")

    exit_code = main()

    assert exit_code == 1


@patch("helper.process_batch_ocr")
def test_main_returns_130_on_keyboard_interrupt(mock_process):
    """Test main returns 130 when user interrupts."""
    mock_process.side_effect = KeyboardInterrupt()

    exit_code = main()

    assert exit_code == 130
