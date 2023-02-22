""" Rotator Module """

import json
import logging
import time
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta

from cobalt_purestorage.configuration import config
from cobalt_purestorage.k8s import K8S
from cobalt_purestorage.pure_storage import PureStorageFlashBlade

logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)


def base64(input):
    """Given a string, return a base64 encoded string"""

    in_bytes = input.encode("utf-8")
    b64_bytes = urlsafe_b64encode(in_bytes)

    return b64_bytes.decode("utf-8")


def key_too_recent(keys):
    """Given a list of keys,
    check if any are younger than minimum allowable age.
    """

    curr_ts = int(time.time())

    # to allow for scheduling variances, we take a variance factor off the
    # min key age
    min_allowable_age = config.access_key_min_age - config.access_key_age_variance
    logger.debug(f"min allowable age: {min_allowable_age}")
    ls = [x for x in keys if (curr_ts - (x["created"] / 1000)) < min_allowable_age]

    if ls:
        return True

    return False


def generate_aws_credentials(credentials):
    """Given FlashBlade credentials, return the credentials
    in the format expected by the AWS SDK.
    """

    #  to allow time for credentials to be distributed,
    #  add a buffer to their expiry time
    expiry_offset = int(
        config.access_key_min_age
        + (config.access_key_min_age / 2)
        + config.access_key_age_variance
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


def update_credentials(refreshed_credentials, user_name):
    """Select the update method."""

    if config.k8s_mode:
        update_k8s(refreshed_credentials, user_name)

    else:
        update_local(refreshed_credentials, user_name)


def update_k8s(refreshed_credentials, user_name):
    """Given a credentials dict, update the k8s secret."""

    encoded_secret_data = base64(json.dumps(refreshed_credentials))

    k8s = K8S()
    k8s.update_secret(
        config.k8s_namespace,
        config.k8s_secret_name,
        config.k8s_secret_key,
        encoded_secret_data,
    )
    logger.info(f"Updated k8s. User: {user_name}")


def update_local(refreshed_credentials, user_name):
    """Given a credentials dict, write it out to the local filesystem."""

    with open(config.credentials_output_path, "w") as f:
        f.write(json.dumps(refreshed_credentials))
    logger.info(f"Updated local credentials file. User: {user_name}")


def main():
    """Main logic flow."""

    if not config.interesting_users:
        logger.error("No Interesting Users are configured, exiting...")
        return

    fb = PureStorageFlashBlade()

    for user_name in config.interesting_users:
        # check username is valid
        if not fb.object_store_user_exists(user_name):
            logger.error(f"User {user_name} does not appear to be a valid user...")
            continue

        keys = fb.get_access_keys_for_user(user_name)
        if keys:
            # sort keys to identify the oldest key for deletion
            sorted_keys = sorted(keys, key=lambda d: d["created"])
            # print(f"sorted: {sorted_keys}")

            # if existing key not too young create a new key
            if len(keys) == 1:
                logger.info(f"One key found. User: {user_name}")

                if not key_too_recent(keys):
                    credentials = fb.post_object_store_access_keys(user_name)
                    if credentials:
                        logger.info(
                            f"New key created. User: {user_name}, Key: {credentials['name']}"
                        )
                        refreshed_credentials = generate_aws_credentials(credentials)
                        update_credentials(refreshed_credentials, user_name)
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
                    credentials = fb.post_object_store_access_keys(user_name)

                    if credentials:
                        logger.info(
                            f"New key created. User: {user_name}, Key: {credentials['name']}"
                        )
                        refreshed_credentials = generate_aws_credentials(credentials)
                        update_credentials(refreshed_credentials, user_name)

                else:
                    logger.warning(f"Keys are too young, ignoring. User: {user_name}")

            # hmmm, the FlashBlade only allows a max of two keys per user
            if len(keys) > 2:
                logger.warning(f"More than two keys found. User: {user_name}")

        else:
            # no keys, create a new one
            logger.info(f"No keys found. User: {user_name}")
            credentials = fb.post_object_store_access_keys(user_name)

            if credentials:
                logger.info(
                    f"New key created. User: {user_name}, Key: {credentials['name']}"
                )
                refreshed_credentials = generate_aws_credentials(credentials)
                update_credentials(refreshed_credentials, user_name)
