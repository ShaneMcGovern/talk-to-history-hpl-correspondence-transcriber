"""Tests for transcriber.py OCR pipeline."""

from unittest.mock import Mock, patch

import pytest

from transcriber import transcribe_image_text


@patch("transcriber.ChatOllama")
def test_transcribe_image_text_with_string_response(mock_chat_ollama):
    """Test transcription with string response from model."""
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.content = "Transcribed text"
    mock_llm.invoke.return_value = mock_response
    mock_chat_ollama.return_value = mock_llm

    result = transcribe_image_text("fake_base64_image")

    assert result == "Transcribed text"


@patch("transcriber.ChatOllama")
def test_transcribe_image_text_with_list_response(mock_chat_ollama):
    """Test transcription with list response from model."""
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.content = ["Part 1", {"text": "Part 2"}]
    mock_llm.invoke.return_value = mock_response
    mock_chat_ollama.return_value = mock_llm

    result = transcribe_image_text("fake_base64_image")

    assert result == "Part 1\nPart 2"


@patch("transcriber.ChatOllama")
def test_transcribe_image_text_handles_connection_error(mock_chat_ollama):
    """Test transcribe_image_text handles Ollama connection errors."""
    mock_chat_ollama.side_effect = Exception("Connection refused")

    with pytest.raises(ConnectionError):
        transcribe_image_text("fake_base64_image")


@patch("transcriber.ChatOllama")
def test_transcribe_image_text_reraises_connection_error(mock_chat_ollama):
    """Test transcribe_image_text re-raises ConnectionError from invoke."""
    mock_llm = Mock()
    mock_llm.invoke.side_effect = ConnectionError("Ollama unavailable")
    mock_chat_ollama.return_value = mock_llm

    with pytest.raises(ConnectionError):
        transcribe_image_text("fake_base64_image")


@patch("transcriber.ChatOllama")
def test_transcribe_image_text_handles_invocation_error(mock_chat_ollama):
    """Test transcribe_image_text handles model invocation errors."""
    mock_llm = Mock()
    mock_llm.invoke.side_effect = Exception("Model error")
    mock_llm.model = "qwen2.5vl:3b"
    mock_chat_ollama.return_value = mock_llm

    with pytest.raises(Exception):
        transcribe_image_text("fake_base64_image")
