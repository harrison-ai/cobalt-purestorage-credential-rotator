""" Test Rotater Module """

from datetime import datetime
from unittest.mock import mock_open, patch

import pytest

import cobalt_purestorage.configuration as config
import cobalt_purestorage.rotator as rotator


def test_base64():
    """Test the base64 function"""

    result = rotator.base64("pytest")
    assert isinstance(result, str)
    assert result == "cHl0ZXN0"


@patch("cobalt_purestorage.configuration.config.access_key_min_age", 900)
@patch("cobalt_purestorage.configuration.config.access_key_age_variance", 60)
@patch("cobalt_purestorage.rotator.datetime")
def test_generate_aws_credentials(mock_dt, mock_credentials):
    """Test the generate_aws_credentials function."""

    mock_dt.utcnow.return_value = datetime(2000, 1, 1, 0, 0, 0)

    result = rotator.generate_aws_credentials(mock_credentials)

    assert "AccessKeyId" in result
    assert "SecretAccessKey" in result
    assert "SessionToken" in result
    assert "Expiration" in result

    expiration = datetime.fromisoformat(result["Expiration"].replace("Z", ""))
    assert expiration == datetime(2000, 1, 1, 0, 23, 30)


@patch("cobalt_purestorage.configuration.config.access_key_min_age", 3600)
@patch("cobalt_purestorage.configuration.config.access_key_age_variance", 10)
@pytest.mark.parametrize(
    "mock_keys", [(3500, True), (3600, False), (3700, False)], indirect=True
)
def test_key_too_recent(mock_keys):
    """Test the key_too_recent function."""

    assert rotator.key_too_recent(mock_keys[0]) == mock_keys[1]


@patch("cobalt_purestorage.rotator.update_k8s")
@patch("cobalt_purestorage.rotator.update_local")
def test_update_credentials(mock_update_local, mock_update_k8s):
    """Test the update_credentials function."""

    with patch("cobalt_purestorage.configuration.config.k8s_mode", False):
        rotator.update_credentials({}, "pytest")

    with patch("cobalt_purestorage.configuration.config.k8s_mode", True):
        rotator.update_credentials({}, "pytest")

    mock_update_local.assert_called_once()
    mock_update_local.assert_called_with({}, "pytest")
    mock_update_k8s.assert_called_once()
    mock_update_k8s.assert_called_with({}, "pytest")


@patch("cobalt_purestorage.configuration.config.k8s_namespace", "pytest")
@patch("cobalt_purestorage.configuration.config.k8s_secret_name", "secret")
@patch("cobalt_purestorage.configuration.config.k8s_secret_key", "data")
@patch("cobalt_purestorage.rotator.K8S")
def test_update_k8s(mock):
    """Test the update_k8s function"""

    k = mock.return_value
    rotator.update_k8s({"pytest": "pytest"}, "pytest")

    k.update_secret.assert_called_once()
    k.update_secret.assert_called_with(
        "pytest", "secret", "data", "eyJweXRlc3QiOiAicHl0ZXN0In0="
    )


@patch("cobalt_purestorage.configuration.config.credentials_output_path", "/out.json")
@patch("builtins.open", new_callable=mock_open)
def test_update_local(mock):
    """Test the update_local function"""

    rotator.update_local({"pytest": "pytest"}, "pytest")
    mock.assert_called_once_with("/out.json", "w")
    handle = mock()
    handle.write.assert_called_once_with('{"pytest": "pytest"}')


@patch("cobalt_purestorage.configuration.config.access_key_min_age", 3600)
@patch("cobalt_purestorage.configuration.config.access_key_age_variance", 90)
@patch("cobalt_purestorage.configuration.config.k8s_mode", True)
@patch("cobalt_purestorage.rotator.PureStorageFlashBlade")
@patch("cobalt_purestorage.rotator.update_k8s")
@pytest.mark.parametrize(
    "index,user_exists",
    [(0, True), (1, True), (2, True), (3, True), (4, True), (0, False)],
)
def test_main_key_actions(mock_k8s, mock_fb, index, user_exists, mock_data):
    """This test runs multiple times, using one user dict from the mock_data fixture in each iteration
    The index value is used to select the user dict from the mock_data list
    """

    mock_user = mock_data["users"][index]

    # sort keys as per tested function so we can
    # test the function call args
    sorted_keys = []
    if len(mock_user["access_keys"]) > 0:
        sorted_keys = sorted(mock_user["access_keys"], key=lambda d: d["created"])

    #   the pytest expected result actions are embedded into the test data to assert against
    #  convert to a set for easy comparison
    expected_results = set(mock_user["pytest_expected_results"])

    fb = mock_fb.return_value

    fb.get_access_keys_for_user.return_value = "xx"

    with patch(
        "cobalt_purestorage.configuration.config.interesting_users", [mock_user["name"]]
    ):
        # mock the response to indicate wether the user exists
        fb.object_store_user_exists.return_value = user_exists
        fb.get_access_keys_for_user.return_value = mock_user["access_keys"]
        rotator.main()

        if user_exists == False:
            fb.object_store_user_exists.assert_called_with(mock_user["name"])
            fb.delete_object_store_access_keys.assert_not_called()
            fb.post_object_store_access_keys.assert_not_called()

        if user_exists == True:
            fb.object_store_user_exists.assert_called_with(mock_user["name"])

            if expected_results == {"skip"}:
                fb.delete_object_store_access_keys.assert_not_called()
                fb.post_object_store_access_keys.assert_not_called()
                mock_k8s.assert_not_called()

            if expected_results == {"post"}:
                fb.delete_object_store_access_keys.assert_not_called()
                fb.post_object_store_access_keys.assert_called_once()
                fb.post_object_store_access_keys.assert_called_with(mock_user["name"])
                mock_k8s.assert_called_once()

            if expected_results == {"delete", "post"}:
                fb.post_object_store_access_keys.assert_called_once()
                fb.post_object_store_access_keys.assert_called_with(mock_user["name"])
                fb.delete_object_store_access_keys.assert_called_once()
                fb.delete_object_store_access_keys.assert_called_with(
                    [sorted_keys[0]["name"]]
                )
                mock_k8s.assert_called_once()

            if expected_results == {"error"}:
                fb.delete_object_store_access_keys.assert_not_called()
                fb.post_object_store_access_keys.assert_not_called()
                mock_k8s.assert_not_called()


@patch("cobalt_purestorage.configuration.config.interesting_users", set())
@patch("cobalt_purestorage.rotator.PureStorageFlashBlade")
def test_main_key_actions_no_users(mock_fb):
    """Test main function when no interesting users are configured"""

    fb = mock_fb.return_value
    rotator.main()
    fb.object_store_user_exists.assert_not_called()
    fb.get_access_keys_for_user.assert_not_called()
