""" CLI Module """

import logging

import click

import pkg.rotator as rotator
from pkg.config import config

logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)


@click.command()
def rotate():
    logger.info("FlashBlade Credentials Rotator starting...")
    rotator.main()
