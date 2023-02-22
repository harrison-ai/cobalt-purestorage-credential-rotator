""" Test Config Module """

import os
from unittest.mock import patch

from cobalt_purestorage.configuration import Settings, config


def test_config():
    """Test that configuration values are being set"""

    assert isinstance(config, Settings)


@patch.dict(os.environ, {"ACCESS_KEY_MIN_AGE": "3600"})
@patch.dict(
    os.environ, {"INTERESTING_USERS": '["account/pytest-one","account/pytest-two"]'}
)
def test_env_var_config():
    """Test that configuration values can be derived
    from env vars
    """

    pytest_config = Settings()
    assert pytest_config.access_key_min_age == 3600
    assert pytest_config.interesting_users == {
        "account/pytest-one",
        "account/pytest-two",
    }
