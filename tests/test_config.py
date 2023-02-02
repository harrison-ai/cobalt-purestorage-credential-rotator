""" Test Config Module """

from importlib import reload
import os
from unittest.mock import patch

import pytest

import pkg.config as config


@patch.dict(os.environ, {"CONFIG_FILE": "tests/fixtures/config.yml"})
def test_config_file_env_var():
    """Test that the config file env var is handled correctly if set"""

    #  config.py is read during pytest collecting stage,
    #  meaning the default values are read in.
    #  a reload is required to set the patched values correctly
    reload(config)

    assert config.Config._CONFIG_FILE == "tests/fixtures/config.yml"

    assert config.Config.interesting_object_accounts == ["mock_hai"]
    assert config.Config.api_token == "pytest"


@patch.dict(os.environ, {"CONFIG_FILE": "fake.yml"})
def test_default_config():
    """
    Test that the default config values are applied
    if a config file is not found
    """

    #  config.py is read during pytest collecting stage,
    #  meaning the default values are read in.
    #  a reload is required to set the patched values correctly
    reload(config)

    assert config.Config._CONFIG_FILE == "fake.yml"
    assert not os.path.exists(config.Config._CONFIG_FILE)
    assert config.Config.interesting_object_accounts == []
    assert config.Config.api_token == None
