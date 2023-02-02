""" Test Config Module """

import os
from unittest.mock import patch

import pkg.config
from pkg.config import config


def test_config():
    """Test that configuration values are being set"""

    assert isinstance(config, pkg.config.Settings)


@patch.dict(os.environ, {"ACCESS_KEY_MIN_AGE": "3600"})
def test_env_var_config():
    """Test that configuration values can be derived
    from env vars
    """

    pytest_config = pkg.config.Settings()
    assert pytest_config.access_key_min_age == 3600
