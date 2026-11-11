"""CLI Module"""

import logging

import click

from cobalt_purestorage import rotator, smoketest
from cobalt_purestorage.configuration import config

logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)


@click.command()
def rotate_entrypoint():
    logger.info("FlashBlade Credentials Rotator starting...")
    rotator.main()


@click.command()
def smoketest_entrypoint():
    logger.info("Starting smoketest...")
    smoketest.main()
