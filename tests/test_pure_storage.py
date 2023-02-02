""" Test FB Module """

from unittest.mock import Mock, patch

import pytest
import requests
from pypureclient.flashblade import Client

from pkg.pure_storage import PureStorageFlashBlade


def mock_api_response(param):
    """Mock out the FB API response."""

    items = [{"item": x} for x in range(10)]

    resp = {
        "status_code": 200,
        "headers": None,
        "continuation_token": "token",
        "total_item_count": 20,
        "items": items,
    }

    if param["token"] == False:
        resp["continuation_token"] = None
        resp["items"] = []

    return resp


@patch("pkg.pure_storage.config.fb_url", "10.10.10.10")
@patch("pkg.pure_storage.config.api_token", "mock-token")
@patch("pkg.pure_storage.Client")
def test_init_ok(mock):
    """Test the class initialisation."""

    fb = PureStorageFlashBlade()
    mock.assert_called_once()
    mock.assert_called_with("10.10.10.10", api_token="mock-token")
    assert isinstance(fb, PureStorageFlashBlade)


@patch("pkg.pure_storage.config.fb_url", "10.10.10.10")
@patch("pkg.pure_storage.config.api_token", "mock-token")
def test_init_conn_failure():
    """Test the class initialisation error handing
    where there is a connection failure.
    """

    with pytest.raises(RuntimeError):
        fb = PureStorageFlashBlade()


@patch("pkg.pure_storage.config.fb_url", "10.10.10.10")
@patch("pkg.pure_storage.config.api_token", "mock-token")
@patch("pkg.pure_storage.requests.get")
def test_init_pure_failure(mock):
    """Test the class initialisation error handing
    where the Py Pure Client errors.
    """

    with pytest.raises(RuntimeError):
        fb = PureStorageFlashBlade()


@patch("pkg.pure_storage.config.fb_url", "10.10.10.10")
@patch("pkg.pure_storage.config.api_token", "mock-token")
@patch("pkg.pure_storage.Client")
def test_get_object_store_accounts(mock):
    """Test the get_object_store_accounts method."""

    fb = PureStorageFlashBlade()
    fb.client.get_object_store_accounts.return_value.to_dict = Mock(
        side_effect=[
            mock_api_response({"token": True}),
            mock_api_response({"token": True}),
            mock_api_response({"token": False}),
        ]
    )

    result = fb.get_object_store_accounts()

    assert len(result) == 20


@patch("pkg.pure_storage.config.fb_url", "10.10.10.10")
@patch("pkg.pure_storage.config.api_token", "mock-token")
@patch("pkg.pure_storage.Client")
def test_get_object_store_users(mock):
    """Test the get_object_store_users method."""

    fb = PureStorageFlashBlade()
    fb.client.get_object_store_users.return_value.to_dict = Mock(
        side_effect=[
            mock_api_response({"token": True}),
            mock_api_response({"token": True}),
            mock_api_response({"token": False}),
        ]
    )

    result = fb.get_object_store_users()

    assert len(result) == 20


@patch("pkg.pure_storage.config.fb_url", "10.10.10.10")
@patch("pkg.pure_storage.config.api_token", "mock-token")
@patch("pkg.pure_storage.Client")
def test_get_object_store_access_keys(mock):
    """Test the gget_object_store_access_keys method."""

    fb = PureStorageFlashBlade()
    fb.client.get_object_store_access_keys.return_value.to_dict = Mock(
        side_effect=[
            mock_api_response({"token": True}),
            mock_api_response({"token": True}),
            mock_api_response({"token": False}),
        ]
    )

    result = fb.get_object_store_access_keys()

    assert len(result) == 20
