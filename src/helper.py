"""Batch OCR processor for Brown Digital Repository IIIF collections."""

import json
import logging
import sys
from pathlib import Path
from typing import Callable

import requests
from requests.adapters import HTTPAdapter
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

import transcriber

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

METADATA_DIR = Path("metadata")
REQUEST_TIMEOUT = (3.05, 30)
RETRYABLE_HTTP_CODES = {408, 429, 500, 502, 503, 504}

_session: requests.Session | None = None


class RetryableHTTPError(Exception):
    """HTTP errors that warrant retry attempts."""


def get_session() -> requests.Session:
    """Get or create requests session with connection pooling.

    Returns:
        Configured requests Session with HTTPAdapter for connection pooling.
    """
    global _session
    if _session is None:
        _session = requests.Session()
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20)
        _session.mount("https://", adapter)
        _session.mount("http://", adapter)
    return _session


def parse_manifest_for_image_urls(manifest_data: dict) -> list[str]:
    """Extract image resource URLs from IIIF manifest data.

    Pure function for parsing manifest structure - no I/O, easy to test.

    Args:
        manifest_data: Parsed IIIF Presentation API manifest JSON.

    Returns:
        List of image resource URLs (@id values from canvas images).
    """
    sequences = manifest_data.get("sequences", [])
    if not sequences:
        return []

    canvases = sequences[0].get("canvases", [])
    if not canvases:
        return []

    image_urls: list[str] = [
        image_resource.get("resource", {}).get("@id")
        for canvas in canvases
        for image_resource in canvas.get("images", [])
        if image_resource.get("resource", {}).get("@id")
    ]

    return image_urls


def fetch_pids_from_metadata(metadata_dir: Path = METADATA_DIR) -> list[str]:
    """Extract Brown Digital Repository PIDs from all JSON metadata files.

    Reads all JSON files in the metadata directory and extracts PID values
    from the 'mods_id_bdr_pid_ssim' field.

    Args:
        metadata_dir: Directory containing JSON metadata files.

    Returns:
        List of extracted PID strings.
    """
    pids: list[str] = []

    if not metadata_dir.exists():
        logger.warning(f"Metadata directory not found: {metadata_dir}")
        return pids

    for metadata_file in metadata_dir.glob("*.json"):
        if not metadata_file.is_file():
            continue

        try:
            with metadata_file.open(encoding="utf-8") as file_handle:
                metadata = json.load(file_handle)

            pid_list = metadata.get("mods_id_bdr_pid_ssim")
            if pid_list and isinstance(pid_list, list) and pid_list:
                pids.append(pid_list[0])

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in {metadata_file.name}: {e}")
        except (IndexError, KeyError) as e:
            logger.debug(f"Missing or malformed PID in {metadata_file.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error reading {metadata_file.name}: {e}")

    logger.info(f"Found {len(pids)} PIDs from metadata files")
    return pids


@retry(
    stop=stop_after_attempt(5),
    wait=wait_random_exponential(multiplier=1, min=1, max=60),
    retry=retry_if_exception_type(
        (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            RetryableHTTPError,
        )
    ),
    reraise=True,
)
def fetch_image_urls_from_manifest(bdr_pid: str) -> list[str]:
    """Fetch all image resource URLs from a IIIF manifest with retry logic.

    Retrieves the IIIF Presentation manifest for a given BDR PID and extracts
    all image resource URLs from the manifest's canvases.

    Args:
        bdr_pid: Brown Digital Repository persistent identifier.

    Returns:
        List of image resource URLs (@id values from canvas images).

    Raises:
        RetryableHTTPError: Server returned retryable error code.
        requests.HTTPError: Non-retryable HTTP error occurred.
        requests.RequestException: Network or connection error.
    """
    manifest_url = (
        f"https://repository.library.brown.edu/iiif/presentation/"
        f"{bdr_pid}/manifest.json"
    )
    logger.info(f"Fetching manifest: {manifest_url}")

    session = get_session()
    response = session.get(manifest_url, timeout=REQUEST_TIMEOUT)

    if response.status_code in RETRYABLE_HTTP_CODES:
        raise RetryableHTTPError(f"HTTP {response.status_code} for {bdr_pid}")

    response.raise_for_status()
    logger.debug(f"Response status: {response.status_code}")

    try:
        manifest_data = response.json()
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in manifest for {bdr_pid}: {e}")
        return []

    image_urls = parse_manifest_for_image_urls(manifest_data)
    logger.info(f"Extracted {len(image_urls)} image URLs from {bdr_pid}")

    return image_urls


def process_batch_ocr(
    pids: list[str] | None = None,
    transcribe_func: Callable[[str], None] = transcriber.main,
) -> None:
    """Execute batch OCR on all images from metadata PIDs.

    Orchestrates the complete pipeline:
    1. Extract PIDs from metadata files (or use provided PIDs)
    2. Fetch image URLs from IIIF manifests
    3. Transcribe each image using OCR

    Continues processing on errors to maximize successful transcriptions.

    Args:
        pids: List of PIDs to process. If None, fetches from metadata directory.
        transcribe_func: Function to call for transcription (injectable for testing).
    """
    if pids is None:
        pids = fetch_pids_from_metadata()

    if not pids:
        logger.error("No PIDs found in metadata directory")
        return

    total_processed = 0
    total_failed = 0

    for pid_index, pid in enumerate(pids, start=1):
        logger.info(f"Processing PID {pid_index}/{len(pids)}: {pid}")

        try:
            image_urls = fetch_image_urls_from_manifest(pid)
        except requests.RequestException as e:
            logger.error(f"Failed to fetch manifest for {pid}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error fetching manifest for {pid}: {e}")
            continue

        if not image_urls:
            logger.warning(f"No images found for {pid}, skipping")
            continue

        for image_index, image_url in enumerate(image_urls, start=1):
            logger.info(
                f"Processing image {image_index}/{len(image_urls)} "
                f"from {pid}: {image_url}"
            )

            try:
                transcribe_func(image_url)
                total_processed += 1
            except Exception as e:
                logger.error(f"Failed to process image {image_url}: {e}", exc_info=True)
                total_failed += 1
                continue

        logger.info(f"Completed processing all images for {pid}")
        break

    logger.info(
        f"Batch OCR complete. Processed: {total_processed}, Failed: {total_failed}"
    )


def main() -> int:
    """Entry point for batch OCR processing.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    try:
        process_batch_ocr()
        return 0
    except KeyboardInterrupt:
        logger.info("Batch processing interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Fatal error in batch processing: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
