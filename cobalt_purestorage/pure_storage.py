"""  PureStorage FlashBlade Module """

import logging
import warnings

import requests
import urllib3
from pypureclient.exceptions import PureError
from pypureclient.flashblade import Client, ObjectStoreAccessKeyPost

from cobalt_purestorage.configuration import config
from cobalt_purestorage.logging_utils import format_stacktrace

logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)


class PureStorageFlashBlade:
    """Service class for the PureStorage FlashBlade API"""

    def __init__(self):
        logger.debug("Instantiating FlashBlade Client")
        self.client = self._create_client(
            config.fb_url, config.api_token, config.fb_timeout
        )
        logger.debug("FlashBlade Client instantiated OK")

    def _create_client(self, url, token, timeout):
        """Create the client"""

        with warnings.catch_warnings():
            if not config.verify_fb_tls:
                warnings.simplefilter(
                    "ignore", urllib3.exceptions.InsecureRequestWarning
                )

            try:
                client = Client(url, api_token=token, timeout=timeout)
                return client

            except requests.exceptions.ConnectionError:
                logger.error(format_stacktrace())
                raise RuntimeError("Could not instantiate FlashBlade client")

            except PureError:
                logger.error(format_stacktrace())
                raise RuntimeError("Could not instantiate FlashBlade Client")

    def object_store_user_exists(self, name):
        """Given an Object Store User name,
        check if the user exists on the FB array
        """

        with warnings.catch_warnings():
            if not config.verify_fb_tls:
                warnings.simplefilter(
                    "ignore", urllib3.exceptions.InsecureRequestWarning
                )

            resp = self.client.get_object_store_users(filter=f'name="{name}"').to_dict()

        if (status := resp.get("status_code")) != 200:
            logger.error(
                f"Failed to fetch object store users with status code {status}"
            )
        return bool(resp.get("items"))

    def get_access_keys_for_user(self, name):
        """Given an Object Store User name,
        return the keys associated that that user
        """

        with warnings.catch_warnings():
            if not config.verify_fb_tls:
                warnings.simplefilter(
                    "ignore", urllib3.exceptions.InsecureRequestWarning
                )

            resp = self.client.get_object_store_access_keys(
                filter=f'user.name="{name}"'
            ).to_dict()

        if resp["status_code"] == 200:
            return resp["items"]

        return None

    def post_object_store_access_keys(self, user_name):
        """Create a new object store access key"""

        with warnings.catch_warnings():
            if not config.verify_fb_tls:
                warnings.simplefilter(
                    "ignore", urllib3.exceptions.InsecureRequestWarning
                )

            resp = self.client.post_object_store_access_keys(
                object_store_access_key=ObjectStoreAccessKeyPost(
                    user={"name": user_name}
                )
            ).to_dict()

        if resp["status_code"] == 200:
            return resp["items"][0]

        logger.error(f"An error occured creating a key for user {user_name}")
        return None

    def delete_object_store_access_keys(self, key_names):
        """Given a list of key names, delete them"""

        with warnings.catch_warnings():
            if not config.verify_fb_tls:
                warnings.simplefilter(
                    "ignore", urllib3.exceptions.InsecureRequestWarning
                )

            resp = self.client.delete_object_store_access_keys(
                names=key_names
            ).to_dict()

        if resp["status_code"] == 200:
            return True

        logger.error(f"An error occured deleting keys {key_names}")
        return False
