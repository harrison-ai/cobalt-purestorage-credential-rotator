"""Test FB Module"""

from unittest.mock import Mock, patch

import pytest
import urllib3
from pypureclient.exceptions import PureError

from cobalt_purestorage.pure_storage import PureStorageFlashBlade

MOCK_FB_URL = "169.254.99.99"


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
def test_init_ok(mock):
    """Test the class initialisation."""

    fb = PureStorageFlashBlade()
    mock.assert_called_once()
    mock.assert_called_with(MOCK_FB_URL, api_token="mock-token", timeout=1)
    assert isinstance(fb, PureStorageFlashBlade)


@patch(
    "cobalt_purestorage.pure_storage.Client",
    side_effect=urllib3.exceptions.MaxRetryError(None, "/api/api_version"),
)
def test_init_conn_failure(mock):
    """Test the class initialisation error handing
    where there is a connection failure.
    """

    with pytest.raises(RuntimeError):
        PureStorageFlashBlade()


@patch(
    "cobalt_purestorage.pure_storage.Client",
    side_effect=PureError("mock login failure"),
)
def test_init_pure_failure(mock):
    """Test the class initialisation error handing
    where the Py Pure Client errors.
    """

    with pytest.raises(RuntimeError):
        PureStorageFlashBlade()


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
