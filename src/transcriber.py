"""
Optical Character Recognition (OCR) for documents using vision model.
"""

import base64
import logging
import re
import sys
from io import BytesIO
from pathlib import Path

import requests
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from PIL import Image
from requests.adapters import HTTPAdapter
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

logging.basicConfig(level=logging.INFO, stream=sys.stdout, filename="transcriber.log")
logger = logging.getLogger(__name__)


RETRYABLE_HTTP_CODES = {408, 429, 500, 502, 503, 504}
REQUEST_TIMEOUT = (3.05, 30)

# Reusable session with connection pooling
_session: requests.Session | None = None


def get_session() -> requests.Session:
    """
    Get or create requests session with connection pooling.

    Returns:
        Configured requests Session with HTTPAdapter
    """
    global _session
    if _session is None:
        _session = requests.Session()
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20)
        _session.mount("https://", adapter)
    return _session


class RetryableHTTPError(Exception):
    """HTTP errors that warrant retry attempts."""


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
def fetch_image_from_url(image_url: str) -> Image.Image:
    """
    Fetch image with exponential backoff to avoid overwhelming remote server.

    Args:
        image_url: URL of the image to fetch

    Returns:
        PIL Image object

    Raises:
        RetryableHTTPError: Server returned retryable error code
        requests.HTTPError: Non-retryable HTTP error occurred
        requests.RequestException: Network or connection error
        PIL.UnidentifiedImageError: Response content is not a valid image
    """
    session = get_session()
    response = session.get(image_url, timeout=REQUEST_TIMEOUT)

    if response.status_code in RETRYABLE_HTTP_CODES:
        raise RetryableHTTPError(f"HTTP {response.status_code}")

    response.raise_for_status()

    try:
        return Image.open(BytesIO(response.content))
    except Exception as e:
        logger.error(f"Failed to decode image from {image_url}: {e}")
        raise


def encode_image_to_base64(image: Image.Image) -> str:
    """
    Encode PIL Image to base64 string.

    Args:
        image: PIL Image object to encode

    Returns:
        Base64-encoded string representation of the image

    Raises:
        IOError: If image encoding fails
    """
    buffer = BytesIO()
    image_format = image.format or "JPEG"

    try:
        image.save(buffer, format=image_format)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to encode image to base64: {e}")
        raise


def transcribe_image_text(base64_encoded_image: str) -> str:
    """
    Transcribe text from image using vision model via Ollama.

    Args:
        base64_encoded_image: Base64-encoded image string

    Returns:
        Transcribed text from the image

    Raises:
        ConnectionError: If Ollama service is unavailable
        ValueError: If model returns unexpected format
        Exception: If model invocation fails
    """
    try:
        llm = ChatOllama(
            model="qwen2.5vl:3b",
            seed=18900820,
            temperature=0.0,
            top_p=0.05,
            repeat_penalty=1.0,
            num_predict=1048,
            stop=[
                "\n\nCorrection",
                "**Correction",
                "Notes:",
                "Analysis:",
            ],
            base_url="http://localhost:11434",
        )
    except Exception as e:
        logger.error(
            "Failed to initialize Ollama client. "
            "Ensure Ollama is running with: ollama serve"
        )
        raise ConnectionError(f"Cannot connect to Ollama: {e}") from e

    messages = [
        SystemMessage(
            content=(
                """
You are an expert paleographer specializing in early 20th century 
American correspondence. You are transcribing letters written by 
H.P. Lovecraft (1890-1937), a Providence-based author known for 
archaic writing influenced by 18th-century British prose. 

INSTRUCTIONS (MANDATORY):
1. OUTPUT ONLY the final transcribed text — no headers, no headings, no inside address, 
   no pagination, no footers, no notes, no explanations, no marginalia
2. Preserve original spelling, punctuation, line breaks, and paragraph structure exactly
3. If a word is unclear, provide your best guess IN-LINE without marking it
4. Do NOT "correct" archaic spellings or modernize language
5. Do NOT add any commentary, analysis, or metadata
6. Do NOT include sections titled "Correction Notes", "Analysis", or similar
7. Your entire response must be the transcription itself

VIOLATION PENALTY: Any deviation from these rules will result in invalid output.
"""
            )
        ),
        HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_encoded_image}",
                },
                {
                    "type": "text",
                    "text": "Transcribe text from this image.",
                },
            ]
        ),
    ]

    try:
        response = llm.invoke(messages)

        # Handle str or list return types from ChatOllama
        if isinstance(response.content, str):
            return response.content
        elif isinstance(response.content, list):
            text_parts = []
            for item in response.content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
            return "\n".join(text_parts)
        else:
            raise ValueError(
                f"Unexpected response content type: {type(response.content)}"
            )
    except ConnectionError:
        raise
    except Exception as e:
        logger.error(f"Model invocation failed: {e} -> try: `ollama pull {llm.model}`")
        raise


def extract_image_identifier_from_url(url: str) -> str | None:
    """
    Extract Brown Digital Repository identifier from URL.

    Args:
        url: Image URL potentially containing 'bdr:' identifier

    Returns:
        Numeric identifier if found, None otherwise
    """
    match = re.search(r"bdr:(\d+)", url)
    return match.group(1) if match else None


def save_transcription_to_file(
    transcription: str,
    identifier: str,
    output_dir: Path = Path("output"),
) -> None:
    """
    Save transcribed text to file in output directory.

    Args:
        transcription: Text content to save
        identifier: Unique identifier for filename
        output_dir: Directory path for output files

    Raises:
        IOError: If file cannot be written
        PermissionError: If insufficient permissions for operations
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / f"{identifier}.txt"
        filepath.write_text(transcription, encoding="utf-8")
        logger.info(f"Transcription saved to {filepath}")
    except (IOError, PermissionError) as e:
        logger.error(f"Failed to write file: {e}")
        raise


def main(image_url: str) -> None:
    """Execute OCR pipeline: fetch, resize, transcribe, and save image text."""
    image = None

    try:
        logger.info(f"Fetching image from {image_url}")
        image = fetch_image_from_url(image_url)

        logger.info("Encoding image to base64")
        base64_image = encode_image_to_base64(image)

        logger.info("Transcribing image text using vision model")
        transcription = transcribe_image_text(base64_image)

        identifier = extract_image_identifier_from_url(image_url)
        if identifier:
            save_transcription_to_file(transcription, identifier)
        else:
            logger.warning("No identifier found in URL, displaying transcription:")
            print(transcription)

    except requests.RequestException as e:
        logger.error(f"Failed to fetch image: {e}")
        sys.exit(1)
    except ConnectionError as e:
        logger.error(f"Ollama service error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"OCR pipeline failed: {e}")
        sys.exit(1)
    finally:
        # Cleanup image resources
        if image is not None:
            image.close()


if __name__ == "__main__":
    main(sys.argv[0])
