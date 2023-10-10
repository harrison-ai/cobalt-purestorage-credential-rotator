""" Test Kubernetes Module """

from unittest.mock import Mock, patch

import kubernetes
import pytest
import base64

from cobalt_purestorage.k8s import K8S


def mock_api_response(items=[]):
    """Mock the kubernetes api response for list request"""

    resp = {"kind": "SecretList", "apiVersion": "v1", "items": items}

    return resp


@patch("cobalt_purestorage.configuration.config.kubeconfig", "/app/kube")
@patch("cobalt_purestorage.configuration.config.k8s_mode", True)
@patch("cobalt_purestorage.k8s.kubernetes.config")
def test_create_client_kubeconfig(mock_config):
    """Test the _create_client method"""

    k8s = K8S()

    mock_config.load_kube_config.assert_called_with(config_file="/app/kube")
    mock_config.load_incluster_config.assert_not_called()


@patch("cobalt_purestorage.configuration.config.kubeconfig", None)
@patch("cobalt_purestorage.configuration.config.k8s_mode", True)
@patch("cobalt_purestorage.k8s.kubernetes.config")
def test_create_client_incluster(mock_config):
    """Test the _create_client method"""

    k8s = K8S()

    mock_config.load_incluster_config.assert_called_once()
    mock_config.load_kube_config.assert_not_called()


@patch("cobalt_purestorage.configuration.config.k8s_mode", True)
@patch("cobalt_purestorage.configuration.config.kubeconfig", None)
@patch("cobalt_purestorage.k8s.kubernetes.config")
@patch("cobalt_purestorage.k8s.kubernetes.client.CoreV1Api")
@pytest.mark.parametrize(
    "input,expected",
    [([{"metadata": {"name": "pytest"}}], True), ([], False)],
)
def test_secret_exist(mock_v1, mock_config, input, expected):
    """Test the _secret_exist method"""

    k8s = K8S()

    k8s.v1.list_namespaced_secret.return_value.to_dict = Mock(
        return_value=mock_api_response(items=input)
    )

    result = k8s._secret_exist("pytest", "pytest")

    assert result == expected
    mock_v1.assert_called_once()
    mock_config.load_incluster_config.assert_called_once()


@patch("cobalt_purestorage.configuration.config.k8s_mode", True)
@patch("cobalt_purestorage.configuration.config.kubeconfig", None)
@patch("cobalt_purestorage.k8s.kubernetes.config")
@patch("cobalt_purestorage.k8s.kubernetes.client.CoreV1Api")
@patch("cobalt_purestorage.k8s.K8S._secret_exist")
@pytest.mark.parametrize("expected", [True, False])
def test_update_secret(mock_exists, mock_v1, mock_config, expected):
    """Test the update_secret function"""

    namespace = "pytest"
    secret_name = "pytest"
    secret_key = "pytest"
    secret_body = "pytest"

    k8s = K8S()

    mock_exists.return_value = expected

    if expected:
        k8s.update_secret(namespace, secret_name, secret_key, secret_body)
        mock_exists.assert_called_with(namespace, secret_name)
        mock_config.load_incluster_config.assert_called_once()
        mock_v1.return_value.patch_namespaced_secret.assert_called_once()

    if not expected:
        with pytest.raises(ValueError):
            k8s.update_secret(namespace, secret_name, secret_key, secret_body)

        mock_exists.assert_called_with(namespace, secret_name)
        mock_config.load_incluster_config.assert_called_once()
        mock_v1.return_value.patch_namespaced_secret.assert_not_called()


@patch("cobalt_purestorage.configuration.config.k8s_mode", True)
@patch("cobalt_purestorage.configuration.config.kubeconfig", None)
@patch("cobalt_purestorage.k8s.kubernetes.config")
@patch("cobalt_purestorage.k8s.kubernetes.client.CoreV1Api")
@patch("cobalt_purestorage.k8s.K8S._secret_exist")
@pytest.mark.parametrize("exists", [True, False])
def test_get_secret(mock_exists, mock_v1, mock_config, exists):

    # Arrange
    namespace = "pytest"
    secret_name = "pytest"
    secret_key = "pytest"
    secret_body = "pytest"
    secret_body_encoded = base64.b64encode(secret_body.encode("utf-8")) # is it good practice to be dependent on base64 module like this?

    data = {secret_key: secret_body_encoded}

    k8s = K8S()

    k8s.v1.read_namespaced_secret.return_value.data = data # is this a good way to structure it? it isn't calling the function, we are mocking the entire response. 
    mock_exists.return_value = exists
   
    # Assert
    if exists:
        response = k8s.get_secret(namespace, secret_name, secret_key)
        assert isinstance(response, str)
        assert response == secret_body
    else:
        with pytest.raises(ValueError):
            response = k8s.get_secret(namespace, secret_name, secret_key)
    
    mock_exists.assert_called_once()
    mock_exists.assert_called_with(namespace,secret_name)
    mock_config.load_incluster_config.assert_called_once()
