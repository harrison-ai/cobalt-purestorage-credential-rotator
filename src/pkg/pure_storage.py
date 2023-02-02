"""  PureStorage FlashBlade Module """

import logging
import warnings

import requests
import urllib3
from pypureclient.exceptions import PureError
from pypureclient.flashblade import Client, ObjectStoreAccessKeyPost

from pkg.config import config
from pkg.logging_utils import format_stacktrace

logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)


class PureStorageFlashBlade:
    """Service class for the PureStorage FlashBlade API"""

    def __init__(self):
        logger.debug("Instantiating FlashBlade Client")
        self.client = self._create_client(config.fb_url, config.api_token)

        # if client is None:
        #     raise RuntimeError("could not instantiate Pure client")

        # self.client = client
        logger.debug("FlashBlade Client instantiated OK")

    def _create_client(self, url, token):
        """Create the client"""

        with warnings.catch_warnings():
            if not config.verify_fb_tls:
                warnings.simplefilter(
                    "ignore", urllib3.exceptions.InsecureRequestWarning
                )

            try:
                client = Client(url, api_token=token)
                return client

            except requests.exceptions.ConnectionError:
                logger.error(format_stacktrace())
                raise RuntimeError("Could not instantiate FlashBlade client")

            except PureError:
                logger.error(format_stacktrace())
                raise RuntimeError("Could not instantiate FlashBlade Client")

    def get_object_store_accounts(self, limit=10):
        """Get all object store accounts, returning only the accounts"""

        accounts = []
        kwargs = {"limit": limit}

        with warnings.catch_warnings():
            if not config.verify_fb_tls:
                warnings.simplefilter(
                    "ignore", urllib3.exceptions.InsecureRequestWarning
                )

            while True:
                resp = self.client.get_object_store_accounts(**kwargs).to_dict()

                for account in resp["items"]:
                    accounts.append(account)

                if resp["continuation_token"] is not None:
                    kwargs["continuation_token"] = resp["continuation_token"]

                else:
                    break

            return accounts

    def get_object_store_users(self, limit=10):
        """Get all object store users, returning only the users"""

        users = []
        kwargs = {"limit": limit}

        with warnings.catch_warnings():
            if not config.verify_fb_tls:
                warnings.simplefilter(
                    "ignore", urllib3.exceptions.InsecureRequestWarning
                )

            while True:
                resp = self.client.get_object_store_users(**kwargs).to_dict()

                for user in resp["items"]:
                    users.append(user)

                if resp["continuation_token"] is not None:
                    kwargs["continuation_token"] = resp["continuation_token"]

                else:
                    break

            return users

    def get_object_store_access_keys(self, limit=10):
        """Get all object store keys, returning only the keys"""

        keys = []
        kwargs = {"limit": limit}

        with warnings.catch_warnings():
            if not config.verify_fb_tls:
                warnings.simplefilter(
                    "ignore", urllib3.exceptions.InsecureRequestWarning
                )

            while True:
                resp = self.client.get_object_store_access_keys(**kwargs).to_dict()

                for key in resp["items"]:
                    keys.append(key)

                if resp["continuation_token"] is not None:
                    kwargs["continuation_token"] = resp["continuation_token"]

                else:
                    break

            return keys

    def post_object_store_access_keys(self, user_id):
        """Create a new object store access key"""

        with warnings.catch_warnings():
            if not config.verify_fb_tls:
                warnings.simplefilter(
                    "ignore", urllib3.exceptions.InsecureRequestWarning
                )

            resp = self.client.post_object_store_access_keys(
                object_store_access_key=ObjectStoreAccessKeyPost(user={"id": user_id})
            ).to_dict()

        if resp["status_code"] == 200:
            return resp["items"][0]

        logger.error(f"An error occured creating a key for user {user_id}")
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
            return

        logger.error(f"An error occured deleting keys {key_names}")
        return None
