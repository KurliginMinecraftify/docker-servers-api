import logging

LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


def configure_logging():
    logging.basicConfig(level="INFO", format=LOG_FORMAT_DEBUG)


__all__ = ["configure_logging"]
