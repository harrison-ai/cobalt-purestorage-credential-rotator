""" Test FB Module """

from unittest.mock import Mock, patch

import pytest
import requests
from pypureclient.flashblade import Client

from cobalt_purestorage.pure_storage import PureStorageFlashBlade

MOCK_FB_URL = "169.254.99.99"


def mock_api_version_response():
    """This is the actual response obtained from https://<flashblade fqdn>/api/api_version"""

    resp = {
        "versions": [
            "1.0",
            "1.1",
            "1.2",
            "1.3",
            "1.4",
            "1.5",
            "1.6",
            "1.7",
            "1.8",
            "1.8.1",
            "1.9",
            "1.10",
            "1.11",
            "1.12",
            "2.0",
            "2.1",
            "2.2",
            "2.3",
            "2.4",
        ]
    }

    return resp


def mock_api_response(items, status_code):
    """Mock out the FB API response."""

    resp = {
        "status_code": status_code,
        "headers": None,
    }

    if status_code == 200:
        resp["continuation_token"] = None
        resp["total_item_count"] = len(items)
        resp["items"] = items

    if status_code == 400:
        resp["errors"] = [{}]

    return resp


@patch("cobalt_purestorage.pure_storage.Client")
def test_init_ok(mock, requests_mock):
    """Test the class initialisation."""

    requests_mock.get(
        f"https://{MOCK_FB_URL}/api/api_version", json=mock_api_version_response()
    )

    fb = PureStorageFlashBlade()
    mock.assert_called_once()
    mock.assert_called_with(MOCK_FB_URL, api_token="mock-token", timeout=1)
    assert isinstance(fb, PureStorageFlashBlade)


def test_init_conn_failure(requests_mock):
    """Test the class initialisation error handing
    where there is a connection failure.
    """

    requests_mock.get(
        f"https://{MOCK_FB_URL}/api/api_version",
        exc=requests.exceptions.ConnectTimeout,
    )

    with pytest.raises(RuntimeError):
        fb = PureStorageFlashBlade()


# pypureclient generates a warning:
# warnings.warn(pytest.PytestUnraisableExceptionWarning(msg))
# we ignore it
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
def test_init_pure_failure(requests_mock):
    """Test the class initialisation error handing
    where the Py Pure Client errors.
    """

    requests_mock.get(
        f"https://{MOCK_FB_URL}/api/api_version", json=mock_api_version_response()
    )
    # mock that the api token is incorrect
    requests_mock.post(f"https://{MOCK_FB_URL}/api/login", status_code=401)

    with pytest.raises(RuntimeError):
        fb = PureStorageFlashBlade()


@patch("cobalt_purestorage.pure_storage.Client")
@pytest.mark.parametrize(
    "items, status_code, expected",
    [(["pytest"], 200, True), ([], 200, False), ([], 400, False)],
)
def test_object_store_user_exists(mock, items, status_code, expected):
    """Test the object_store_user_exists function"""

    fb = PureStorageFlashBlade()
    fb.client.get_object_store_users.return_value.to_dict = Mock(
        return_value=mock_api_response(items, status_code)
    )
    result = fb.object_store_user_exists("test")
    assert result == expected


@patch("cobalt_purestorage.pure_storage.Client")
@pytest.mark.parametrize(
    "items, status_code, expected",
    [
        ([{"pytest": "pytest"}], 200, [{"pytest": "pytest"}]),
        ([], 200, []),
        ([], 400, None),
    ],
)
def test_get_access_keys_for_user(mock, items, status_code, expected):
    """Test the get_access_keys_for_user method"""

    fb = PureStorageFlashBlade()
    fb.client.get_object_store_access_keys.return_value.to_dict = Mock(
        return_value=mock_api_response(items, status_code)
    )

    result = fb.get_access_keys_for_user("test")
    assert result == expected


@patch("cobalt_purestorage.pure_storage.Client")
@pytest.mark.parametrize(
    "items, status_code, expected",
    [([{"k": "v"}], 400, None), ([{"k": "v"}], 200, {"k": "v"})],
)
def test_post_object_store_access_keys(mock, items, status_code, expected):
    """Test the post_object_store_access_keys method"""

    fb = PureStorageFlashBlade()
    fb.client.post_object_store_access_keys.return_value.to_dict = Mock(
        return_value=mock_api_response(items, status_code)
    )

    result = fb.post_object_store_access_keys("pytest")
    assert result == expected


@patch("cobalt_purestorage.pure_storage.Client")
@pytest.mark.parametrize("status_code,expected", [(200, True), (400, False)])
def test_delete_object_store_access_keys(mock, status_code, expected, caplog):
    """Test the delete_object_store_access_keys method"""

    fb = PureStorageFlashBlade()
    fb.client.delete_object_store_access_keys.return_value.to_dict = Mock(
        return_value=mock_api_response([], status_code)
    )

    result = fb.delete_object_store_access_keys([])
    assert result == expected
