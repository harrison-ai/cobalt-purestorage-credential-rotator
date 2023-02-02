""" Rotator Module """

import json
import logging
import time
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta, timezone

from pkg.config import Config
from pkg.k8s import K8S
from pkg.pure_storage import PureStorageFlashBlade

logging.basicConfig(level=Config.log_level)
logger = logging.getLogger(__name__)


def base64(input):
    """Given a string, return a base64 encoded string"""

    in_bytes = input.encode("utf-8")
    b64_bytes = urlsafe_b64encode(in_bytes)

    return b64_bytes.decode("utf-8")


def get_interesting_accounts(all_accounts):
    """Given a list of accounts, return only those of interest"""

    interesting_accounts = []

    if Config.interesting_object_accounts:
        interesting_accounts = [
            x for x in all_accounts if x["name"] in Config.interesting_object_accounts
        ]

    return interesting_accounts


def get_interesting_users(interesting_accounts, all_users):
    """Given a list of users, return only those of interest."""

    interesting_account_ids = [x["id"] for x in interesting_accounts]
    excluded_user_ids = [
        x["id"] for x in all_users if x["name"] in Config.excluded_user_names
    ]
    interesting_users = [
        x
        for x in all_users
        if x["account"]["id"] in interesting_account_ids
        if x["id"] not in excluded_user_ids
    ]

    return interesting_users


def get_keys_per_user(user_id, all_keys):
    """Given a user id and a list of all access keys,
    return the keys associated with the user.
    """

    ls = [x for x in all_keys if x["user"]["id"] == user_id]

    return ls


def key_too_recent(keys):
    """Given a list of keys,
    check if any are younger than minimum allowable age.
    """

    curr_ts = int(time.time())

    # to allow for scheduling variances, we take a variance factor off the
    # min key age
    min_allowable_age = Config.access_key_min_age - Config.access_key_age_variance
    logger.debug(f"min allowable age: {min_allowable_age}")
    ls = [x for x in keys if (curr_ts - (x["created"] / 1000)) < min_allowable_age]

    if ls:

        return True

    return False


def generate_aws_credentials(credentials):
    """
    Given FlashBlade credentials, return the credentials
    in the format expected by the AWS SDK.
    """

    #  to allow time for credentials to be distributed,
    #  add a buffer to their expiry time
    expiry_offset = int(
        Config.access_key_min_age
        + (Config.access_key_min_age / 2)
        + Config.access_key_age_variance
    )

    logger.debug(f"Credentials will expire in {expiry_offset} seconds.")

    # RFC3339 UTC datetime string
    expiry_ts = (
        datetime.utcnow().replace(microsecond=0) + timedelta(seconds=expiry_offset)
    ).isoformat()

    _d = {
        "Version": 1,
        "AccessKeyId": credentials["name"],
        "SecretAccessKey": credentials["secret_access_key"],
        "SessionToken": "",
        "Expiration": f"{expiry_ts}Z",
    }

    return _d


def update_credentials(refreshed_credentials):
    """Select the update method."""

    if Config.k8s_mode:
        print("in k8s mode...")
        update_k8s(refreshed_credentials)

    else:
        print("in loocal mode...")
        update_local(refreshed_credentials)


def update_k8s(refreshed_credentials):
    """Given a credentials dict, update the k8s secret."""

    encoded_secret_data = base64(json.dumps(refreshed_credentials))

    k8s = K8S()
    k8s.update_secret(
        Config.k8s_namespace,
        Config.k8s_secret_name,
        Config.k8s_secret_key,
        encoded_secret_data,
    )


def update_local(refreshed_credentials):
    """Given a credentials dict, write it out to the local filesystem."""

    with open(Config.credentials_output_path, "w") as f:
        f.write(json.dumps(refreshed_credentials))


def main():
    """Main logic flow."""

    fb = PureStorageFlashBlade()

    # retrieve the data req'd from the flashblade
    all_accounts = fb.get_object_store_accounts()
    all_users = fb.get_object_store_users()
    all_access_keys = fb.get_object_store_access_keys()

    #  filter out the unwanted users
    interesting_accounts = get_interesting_accounts(all_accounts)
    interesting_users = get_interesting_users(interesting_accounts, all_users)

    if not interesting_users:
        logger.warning("No interesting users found")

    for user in interesting_users:

        user_name = user["name"]
        user_id = user["id"]
        logger.info(f"Begin key operations. User: {user_name}")

        # get the keys associated with the user
        keys = get_keys_per_user(user_id, all_access_keys)

        if keys:

            # sort keys to identify the oldest key for deletion
            sorted_keys = sorted(keys, key=lambda d: d["created"])

            # if existing key not too young create a new key
            if len(keys) == 1:

                logger.info(f"One key found. User: {user_name}")

                if not key_too_recent(keys):

                    credentials = fb.post_object_store_access_keys(user_id)
                    if credentials:

                        logger.info(
                            f"New key created. User: {user_name}, Key: {credentials['name']}"
                        )
                        refreshed_credentials = generate_aws_credentials(credentials)
                        update_credentials(refreshed_credentials)
                        logger.info(f"Updated k8s. User: {user_name}")
                else:

                    logger.warning(f"Keys are too young, ignoring. User: {user_name}")

            # if existing keys not too young, delete oldest then create new
            if len(keys) == 2:

                logger.info(f"Two keys found. User: {user_name}")

                if not key_too_recent(keys):

                    fb.delete_object_store_access_keys([sorted_keys[0]["name"]])
                    logger.info(
                        f"Oldest key deleted. User: {user_name}, Key: {sorted_keys[0]['name']}"
                    )
                    credentials = fb.post_object_store_access_keys(user_id)

                    if credentials:
                        logger.info(
                            f"New key created. User: {user_name}, Key: {credentials['name']}"
                        )
                        refreshed_credentials = generate_aws_credentials(credentials)
                        update_credentials(refreshed_credentials)
                        logger.info(f"Updated k8s. User: {user_name}")

                else:

                    logger.warning(f"Keys are too young, ignoring. User: {user_name}")

            # hmmm, the FlashBlade only allows a max of two keys per user
            if len(keys) > 2:

                logger.warning(f"More than two keys found. User: {user_name}")

        else:

            # no keys, create a new one
            logger.info(f"No keys found. User: {user_name}")
            credentials = fb.post_object_store_access_keys(user_id)

            if credentials:

                logger.info(
                    f"New key created. User: {user_name}, Key: {credentials['name']}"
                )
                refreshed_credentials = generate_aws_credentials(credentials)
                update_credentials(refreshed_credentials)
                logger.info(f"Updated k8s. User: {user_name}")
