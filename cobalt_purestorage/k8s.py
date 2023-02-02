""" Kubernetes Service Module """

import logging

from kubernetes import client, config

from cobalt_purestorage.configuration import config
from cobalt_purestorage.logging_utils import format_stacktrace

logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)


class K8S:
    def __init__(self):
        if config.kubeconfig:
            config.load_kube_config(config_file=config.kubeconfig)

        else:
            try:
                config.load_incluster_config()

            except config.config_exception.ConfigException as err:
                logger.error(format_stacktrace())
                raise RuntimeError(err)

    def _secret_exist(self, namespace, secret):
        """Given a namespace and a secret name, check if the secret exists"""

        v1 = client.CoreV1Api()
        resp = v1.list_namespaced_secret(namespace)
        logger.debug(resp)
        secrets = [x.metadata.name for x in resp.items]

        if secret in secrets:
            return True

        return False

    def update_secret(self, namespace, secret_name, secret_key, secret_body):
        """update a pre-existing secret"""

        secret_exists = self._secret_exist(namespace, secret_name)

        if secret_exists:
            v1 = client.CoreV1Api()
            body = {"data": {secret_key: secret_body}}

            try:
                v1.patch_namespaced_secret(secret_name, namespace, body)

            except client.exceptions.ApiException as err:
                logger.error(format_stacktrace())
                raise RuntimeError("error updating k8s secret")

        else:
            logger.error("specified secret does not exist")
            raise ValueError("secret does not exist")

        #  update it
        # https://github.com/kubernetes-client/python/issues/618
        # https://kubernetes.io/docs/tasks/configmap-secret/managing-secret-using-config-file/#edit-secret
