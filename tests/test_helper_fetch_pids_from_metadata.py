"""Tests for helper.py batch OCR processor."""

import json

from helper import fetch_pids_from_metadata


def test_fetch_pids_from_metadata_with_valid_files(tmp_path):
    """Test fetching PIDs from valid JSON metadata files."""
    metadata_dir = tmp_path / "metadata"
    metadata_dir.mkdir()

    (metadata_dir / "doc.json").write_text(
        json.dumps({"mods_id_bdr_pid_ssim": ["bdr:123456"]})
    )

    pids = fetch_pids_from_metadata(metadata_dir)

    assert "bdr:123456" in pids


def test_fetch_pids_from_metadata_skips_invalid_files(tmp_path):
    """Test fetch_pids_from_metadata handles various file errors."""
    metadata_dir = tmp_path / "metadata"
    metadata_dir.mkdir()

    (metadata_dir / "invalid.json").write_text("invalid json{")
    (metadata_dir / "valid.json").write_text(
        json.dumps({"mods_id_bdr_pid_ssim": ["bdr:123456"]})
    )

    pids = fetch_pids_from_metadata(metadata_dir)

    assert "bdr:123456" in pids
