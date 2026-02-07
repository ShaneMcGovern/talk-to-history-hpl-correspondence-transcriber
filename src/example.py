from sys import stderr
import logging

logging.basicConfig(level=logging.DEBUG, stream=stderr)

logger = logging.getLogger(__name__)


class Example:
    def __init__(self):
        pass

    def func(self) -> None:
        logger.debug("Hello World!")


def main():
    instance = Example()
    instance.func()


if __name__ == "__main__":
    main()
