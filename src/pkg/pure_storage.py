"""  Pure Storage FlashBlade Module """

import logging

import urllib3
import requests
from pypureclient.exceptions import PureError
from pypureclient.flashblade import Client, ObjectStoreAccessKeyPost

from pkg.config import Config
from pkg.logging_utils import format_stacktrace


urllib3.disable_warnings()

logging.basicConfig(level=Config.log_level)
logger = logging.getLogger(__name__)


class PureStorageFlashBlade:
    """Service class for the PureStorage FlashBlade API"""

    def __init__(self):

        logger.debug("Istantiating PureStorageFlashBlade instance")
        client = self._create_client(Config.fb_url, Config.api_token)

        if client is None:
            raise RuntimeError("could not istantiate Pure client")

        self.client = client
        logger.debug("PureStorageFlashBlade Client istantiated OK")

    def _create_client(self, url, token):
        """Create the client"""

        try:
            client = Client(url, api_token=token)
            return client

        except requests.exceptions.ConnectionError:
            logger.error(format_stacktrace())
            return None

        except PureError:
            logger.error(format_stacktrace())
            return None

    def get_object_store_accounts(self, limit=10):
        """Get all object store accounts, returning only the accounts"""

        accounts = []
        kwargs = {"limit": limit}

        while True:

            logger.debug("in function")

            resp = self.client.get_object_store_accounts(**kwargs).to_dict()

            logger.debug(resp)

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
        """xx"""

        resp = self.client.post_object_store_access_keys(
            object_store_access_key=ObjectStoreAccessKeyPost(user={"id": user_id})
        ).to_dict()

        if resp["status_code"] == 200:

            return resp["items"][0]

        print("an error occured creating a key...")
        print(resp)
        return None

    def delete_object_store_access_keys(self, key_names):
        """Given a list of key names, delete them"""

        resp = self.client.delete_object_store_access_keys(names=key_names).to_dict()
        if resp["status_code"] == 200:

            return

        print("an error occured deleting a key...")
        print(resp)
