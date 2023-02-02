""" CLI Module """

import logging

import click

import pkg.rotator as rotator
from pkg.config import Config

logging.basicConfig(level=Config.log_level)
logger = logging.getLogger(__name__)


@click.command()
def rotate():
    logger.info("FlashBlade Credentials Rotator starting...")
    rotator.main()
