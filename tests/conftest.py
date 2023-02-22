""" Pytest Setup Module """

import random
import string
import time
from unittest.mock import patch

import pytest
import yaml

import cobalt_purestorage.configuration as configuration


@pytest.fixture(scope="session", autouse=True)
def mock_fb_url():
    with patch("cobalt_purestorage.configuration.config.fb_url", "169.254.99.99"):
        yield


@pytest.fixture(scope="session", autouse=True)
def mock_api_token():
    with patch("cobalt_purestorage.configuration.config.api_token", "mock-token"):
        yield


@pytest.fixture(scope="session", autouse=True)
def mock_fb_timeout():
    with patch("cobalt_purestorage.configuration.config.fb_timeout", 1):
        yield


@pytest.fixture
def mock_credentials():
    creds = {"name": "pytest", "access_key": "pytest", "secret_access_key": "pytest"}

    return creds


@pytest.fixture
def mock_data():
    with open("tests/fixtures/mock-data.yml", "r") as f:
        data = yaml.safe_load(f)

    accounts = []
    users = []
    access_keys = []

    ts = int(time.time())

    for account in data["accounts"]:
        account_dict = {
            "name": account["name"],
            "id": account["id"],
            "created": account["created"],
            "object_count": 1234567890,
            "space": {
                "data_reduction": 1.1,
                "snapshots": 0,
                "total_physical": 1234567890,
                "unique": 1234567890,
                "virtual": 1234567890,
            },
        }
        accounts.append(account_dict)

        for user in account["users"]:
            user_dict = {
                "name": user["name"],
                "id": user["id"],
                "access_keys": [],
                "account": {
                    "id": account["id"],
                    "name": account["name"],
                    "resource_type": "object-store-accounts",
                },
                "created": 1667813698000,
            }

            if "pytest_expected_results" in user:
                user_dict["pytest_expected_results"] = user["pytest_expected_results"]

            if user["access_keys"]:
                for access_key in user["access_keys"]:
                    created = int((ts - access_key["age"]) * 1000)

                    r = "".join(random.choices(string.ascii_uppercase, k=31))
                    key = f"PSFB{r}EXAMPLE"

                    user_access_key_dict = {
                        "id": None,
                        "name": key,
                        "created": created,
                        "resource_type": "object-store-access-keys",
                    }

                    user_dict["access_keys"].append(user_access_key_dict)

                    access_key_dict = {
                        "name": key,
                        "created": created,
                        "enabled": access_key["enabled"],
                        "secret_access_key": "***",
                        "user": {
                            "id": user["id"],
                            "name": user["name"],
                            "resource_type": "object-store-users",
                        },
                    }
                    access_keys.append(access_key_dict)

            users.append(user_dict)

    mock_data = {"accounts": accounts, "users": users, "access_keys": access_keys}

    return mock_data


@pytest.fixture
def mock_keys(request):
    created_at = (int(time.time()) - request.param[0]) * 1000

    keys = [
        {
            "name": "PSFB",
            "created": created_at,
            "enabled": True,
            "secret_access_key": "***",
            "user": {
                "id": "pytest",
                "name": "mock_fake/pytest",
                "resource_type": "object-store-users",
            },
        },
        {
            "name": "PSFB",
            "created": created_at,
            "enabled": True,
            "secret_access_key": "***",
            "user": {
                "id": "pytest",
                "name": "mock_fake/pytest",
                "resource_type": "object-store-users",
            },
        },
    ]

    return (keys, request.param[1])
