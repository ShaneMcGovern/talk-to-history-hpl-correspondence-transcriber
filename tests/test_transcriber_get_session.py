"""Tests for transcriber.py OCR pipeline."""

import requests

from transcriber import get_session


def test_get_session_creates_new_session():
    """Test get_session creates session on first call."""
    import transcriber

    transcriber._session = None

    session = get_session()

    assert session is not None
    assert isinstance(session, requests.Session)


def test_get_session_reuses_existing_session():
    """Test get_session reuses existing session."""
    first_session = get_session()
    second_session = get_session()

    assert first_session is second_session
