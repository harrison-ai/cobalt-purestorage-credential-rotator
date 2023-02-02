""" Smoketest Module """

import logging

from cobalt_purestorage.configuration import config

logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)


def main():
    """A simple smoketest function that can be exended.
    Intended to be used to verify docker image has been
    correctly built.
    """

    logger.debug("Running smoketest function")
    return None
