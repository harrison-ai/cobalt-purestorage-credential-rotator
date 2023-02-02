""" CLI Module """

import logging

import click

import cobalt_purestorage.rotator as rotator
from cobalt_purestorage.configuration import config

logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)


@click.command()
def rotate():
    logger.info("FlashBlade Credentials Rotator starting...")
    rotator.main()
