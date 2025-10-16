import logging


def setup_logging(level: str = "INFO") -> None:
    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    datefmt = "%Y-%m-%dT%H:%M:%S%z"
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO), format=fmt, datefmt=datefmt
    )
