""" Kubernetes Service Module """

import logging

import kubernetes

import base64

from cobalt_purestorage.configuration import config
from cobalt_purestorage.logging_utils import format_stacktrace

logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)


class K8S:
    """Service class for the kubernetes client"""

    def __init__(self):
        logger.debug("Instantiating Kubernetes Client")
        self.v1 = self._create_client(config.kubeconfig)

    def _create_client(self, kubeconfig):
        """Create the kubernetes client"""

        if kubeconfig:
            kubernetes.config.load_kube_config(config_file=kubeconfig)
        else:
            try:
                kubernetes.config.load_incluster_config()

            except kubernetes.config.config_exception.ConfigException as err:
                logger.error(format_stacktrace())
                raise RuntimeError(err)

        return kubernetes.client.CoreV1Api()

    def _secret_exist(self, namespace, secret):
        """Given a namespace and a secret name, check if the secret exists"""

        resp = self.v1.list_namespaced_secret(namespace).to_dict()
        secrets = [x["metadata"]["name"] for x in resp["items"]]

        return secret in secrets

    def update_secret(self, namespace, secret_name, secret_key, secret_body):
        """update a pre-existing secret"""

        secret_exists = self._secret_exist(namespace, secret_name)

        if secret_exists:
            body = {"data": {secret_key: secret_body}}

            try:
                self.v1.patch_namespaced_secret(secret_name, namespace, body)
                logger.info(
                    f"Patched secret: Namespace: {namespace} Secret: {secret_name}"
                )

            except kubernetes.client.exceptions.ApiException as err:
                logger.error(format_stacktrace())
                raise RuntimeError("error updating k8s secret")

        else:
            logger.error("specified secret does not exist")
            raise ValueError("secret does not exist")

    def get_secret(self, namespace, secret_name, secret_key):
        """get pre-existing secret"""

        secret_exists = self._secret_exist(namespace, secret_name)

        if secret_exists:
            try:
                data = self.v1.read_namespaced_secret(secret_name, namespace).data
                decoded = base64.b64decode(data.get(secret_key)).decode("utf-8")
                return decoded

            except kubernetes.client.exceptions.ApiException:
                logger.error(format_stacktrace())
                raise RuntimeError("error getting k8s secret")
            
        else:
            logger.error("specified secret does not exist")
            raise ValueError("secret does not exist")