""" Test Rotater Module """

from datetime import datetime
from unittest.mock import mock_open, patch

import pytest

# import pkg.config as config
import pkg.rotator as rotator


def test_base64():
    """Test the base64 function"""

    result = rotator.base64("pytest")
    assert isinstance(result, str)
    assert result == "cHl0ZXN0"


@patch("pkg.config.config.access_key_min_age", 900)
@patch("pkg.config.config.access_key_age_variance", 60)
@patch("pkg.rotator.datetime")
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


@patch("pkg.rotator.config.access_key_min_age", 3600)
@patch("pkg.rotator.config.access_key_age_variance", 10)
@pytest.mark.parametrize(
    "mock_keys", [(3500, True), (3600, False), (3700, False)], indirect=True
)
def test_key_too_recent(mock_keys):
    """Test the key_too_recent function."""

    assert rotator.key_too_recent(mock_keys[0]) == mock_keys[1]


@patch("pkg.rotator.config.interesting_object_accounts", '["mock_hai", "mock_ana"]')
def test_get_interesting_accounts(mock_data):
    """Test the get_interesting_accounts function."""

    mock_accounts = mock_data["accounts"]

    result = rotator.get_interesting_accounts(mock_accounts)
    names = [x["name"] for x in result]

    assert isinstance(result, list)
    assert len(result) == 2
    assert names == ["mock_hai", "mock_ana"]


#  fixme:  paarametrise this test to include no excluded users
@patch("pkg.rotator.config.interesting_object_accounts", '["mock_hai", "mock_ana"]')
@patch("pkg.rotator.config.excluded_user_names", '["mock_ana/two"]')
def test_get_interesting_users(mock_data):
    """Test the get_interesting_users function."""

    mock_accounts = mock_data["accounts"]
    mock_users = mock_data["users"]

    interesting_accounts = rotator.get_interesting_accounts(mock_accounts)
    result = rotator.get_interesting_users(interesting_accounts, mock_users)
    names = [x["name"] for x in result]

    assert isinstance(result, list)
    assert len(result) == 7
    assert names == [
        "mock_hai/one",
        "mock_hai/two",
        "mock_hai/three",
        "mock_hai/four",
        "mock_hai/five",
        "mock_ana/one",
        "mock_ana/three",
    ]


@patch("pkg.rotator.config.interesting_object_accounts", '["mock_hai", "mock_ana"]')
@patch("pkg.rotator.config.excluded_user_names", '["mock_ana/two"]')
def test_get_keys_per_user(mock_data):
    """Test the get_keys_per_user function."""

    mock_users = mock_data["users"]
    mock_access_keys = mock_data["access_keys"]

    for user in mock_users:
        result = rotator.get_keys_per_user(user["id"], mock_access_keys)
        assert len(result) == len(user["access_keys"])
        for key in user["access_keys"]:
            assert any(x["name"] == key["name"] for x in result)


@patch("pkg.rotator.update_k8s")
@patch("pkg.rotator.update_local")
def test_update_credentials(mock_update_local, mock_update_k8s):
    """Test the update_credentials function."""

    with patch("pkg.rotator.config.k8s_mode", False):
        rotator.update_credentials({})

    with patch("pkg.rotator.config.k8s_mode", True):
        rotator.update_credentials({})

    mock_update_local.assert_called_once()
    mock_update_local.assert_called_with({})
    mock_update_k8s.assert_called_once()
    mock_update_k8s.assert_called_with({})


@patch("pkg.config.config.k8s_namespace", "pytest")
@patch("pkg.config.config.k8s_secret_name", "secret")
@patch("pkg.config.config.k8s_secret_key", "data")
@patch("pkg.rotator.K8S")
def test_update_k8s(mock):
    """Test the update_k8s function"""

    k = mock.return_value
    rotator.update_k8s({"pytest": "pytest"})

    k.update_secret.assert_called_once()
    k.update_secret.assert_called_with(
        "pytest", "secret", "data", "eyJweXRlc3QiOiAicHl0ZXN0In0="
    )


@patch("pkg.config.config.credentials_output_path", "/out.json")
@patch("builtins.open", new_callable=mock_open)
def test_update_local(mock):
    """Test the update_local function"""

    rotator.update_local({"pytest": "pytest"})
    mock.assert_called_once_with("/out.json", "w")
    handle = mock()
    handle.write.assert_called_once_with('{"pytest": "pytest"}')


@patch("pkg.rotator.config.access_key_min_age", 3600)
@patch("pkg.rotator.config.access_key_age_variance", 90)
@patch("pkg.rotator.config.k8s_mode", True)
@patch("pkg.rotator.PureStorageFlashBlade")
@patch("pkg.rotator.get_interesting_users")
@patch("pkg.rotator.update_k8s")
@pytest.mark.parametrize(
    "mock_data, index", [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)], indirect=["mock_data"]
)
def test_main_key_actions(
    mock_k8s, mock_interesting_users, mock_fb, mock_data, index, mock_credentials
):
    """This test runs multiple times, using one user dict from the mock_data fixture in each iteration
    The index value is used to select the user dict from the mock_data list
    This parametrized test accepts the mock_data fixture as is by virtue of the indirect argument
    The tuples in the decorator are requred to pass both the mock_data fixture and an index value into the test
    The first tuple value isn't actually passed into the test.  The indirect arg means the mock_data fixture
    is returned instead
    """

    #  the function will take a user and find all associated keys
    #  from the list of all available keys

    #  all access keys
    mock_access_keys = mock_data["access_keys"]

    # the specific user we are teting against
    mock_user = mock_data["users"][index]

    # sort keys as per tested function so we can
    # test the function call args
    sorted_keys = []
    if len(mock_user["access_keys"]) > 0:
        sorted_keys = sorted(mock_user["access_keys"], key=lambda d: d["created"])

    #  the pytest expected result actions are embedded into the test data to assert against
    expected_results = mock_user["pytest_expected_results"]

    #  convert to a set for easy comparison
    expected_results = set(mock_user["pytest_expected_results"])

    fb = mock_fb.return_value
    fb.get_object_store_access_keys.return_value = mock_access_keys
    fb.post_object_store_access_keys.return_value = mock_credentials

    # we patch the get_interesting_users function so that we
    # are only testing a single specified user - in real usage
    # the function will loop over all users
    mock_interesting_users.return_value = [mock_user]

    rotator.main()

    if expected_results == {"skip"}:
        fb.delete_object_store_access_keys.assert_not_called()
        fb.post_object_store_access_keys.assert_not_called()

    if expected_results == {"post"}:
        fb.delete_object_store_access_keys.assert_not_called()
        fb.post_object_store_access_keys.assert_called_once()
        fb.post_object_store_access_keys.assert_called_with(mock_user["id"])
        mock_k8s.assert_called_once()

    if expected_results == {"delete", "post"}:
        fb.delete_object_store_access_keys.assert_called_once()
        fb.delete_object_store_access_keys.assert_called_with([sorted_keys[0]["name"]])
        fb.post_object_store_access_keys.assert_called_once()
        fb.post_object_store_access_keys.assert_called_with(mock_user["id"])
        mock_k8s.assert_called_once()

    if expected_results == {"error"}:
        fb.delete_object_store_access_keys.assert_not_called()
        fb.post_object_store_access_keys.assert_not_called()
