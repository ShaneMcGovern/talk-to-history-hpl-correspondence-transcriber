"""Application entry point for OCR transcription pipeline."""

import argparse
import sys

import src.transcriber as transcriber


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    """Parse and validate command-line arguments.

    Args:
        args: Command-line arguments to parse. Defaults to sys.argv[1:].

    Returns:
        Parsed arguments as a Namespace object.
    """
    parser = argparse.ArgumentParser(
        description="Optical character recognition (OCR) for images",
        prog="n'kai-transcriber",
    )
    parser.add_argument(
        "--image-url",
        required=True,
        help="URL of image to transcribe using OCR",
        dest="image_url",
    )
    return parser.parse_args(args)


def main() -> int:
    """Execute OCR pipeline: fetch, transcribe, and save image text.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    try:
        args = parse_arguments()
        transcriber.main(args.image_url)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
