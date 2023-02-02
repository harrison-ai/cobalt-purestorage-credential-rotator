# Cobalt PureStorage Credential Rotator


## Overview

A Python package to periodically rotate or refresh PureStorage FlashBlade Object Store Credentials.

At the time of writing, the PureStorage FlashBlade array only supports creating Object Store Access Keys that don't expire.  This may not be desirable for a number of reasons.  This package, when run on a regular schedule, will rotate these keys by creating new Access Keys and deleting older Access Keys for selected Object Store Users, in effect creating short lived or temporary credentials.

This package leverages the open source [Pure Storage Python Client](https://pure-storage-py-pure-client.readthedocs-hosted.com/en/latest/) to interact with a PureStorage FlashBlade device.

As the FlashBlade Object Store interface is S3 compatible, this package assumes that the user will be using standard AWS tooling such as the AWS CLI and SDK's to interact with it.  The credentials this package produces are in the format as described in this [AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sourcing-external.html).

To not interfere with long running Object Store operations that may extend past the lifetime of a single Access Key, the credentials should be presented to the user in a manner that causes the AWS SDK's to regard them as refreshable.  As such, an AWS SDK consumer will automatically refresh the credentials as and when required without any application refresh logic.  At the time of writing, this includes credentials obtained from the EC2 IMDS and an external process.

Note that this has only been tested with the Python AWS SDK, `boto3`.


## Credential Output Format:

```json
{
  "Version": 1,
  "AccessKeyId": "access key",
  "SecretAccessKey": "secret access key",
  "SessionToken": "",
  "Expiration": "ISO8601 timestamp when the credentials expire"
}
```

There are two options for outputting the generated credentials, `local` mode or `k8s` mode.  By default the package will operate in `local` mode.  To enable `k8s` mode, configure the `K8S_MODE` environment variable

```bash
K8S_MODE=True
```

## Local Mode:

The generated credentials will be written out to local disk, at the location specified in the `CREDENTIALS_OUTPUT_PATH` environment variable.


## Kubernetes Mode:

A pre-existing Kubernetes secret will be updated with the generated credentials.  Three environment variables are required:

- `K8S_NAMESPACE`:  The k8s namespace in which the secret is located.
- `K8S_SECRET_NAME`: The secret name
- `K8S_SECRET_KEY`: The name of the key within the secret which will contain the credentials

In this mode, k8s credentials can be sourced from either a `kubeconfig` file, or from within the k8s cluster if this package is running in k8s.

To supply a `kubeconfig` file, configure the `KUBECONFIG` environment variable.  If this variable is not present, in-cluster authentication will be used.

```bash
KUBECONFIG="/path/to/kubeconfig.yaml"
```


## Scheduling and Access Key lifetimes

It is envisaged this package will be run periodically via a cron like mechanism.  A Kubernetes CronJob for example.

The lifetime of the generated credentials is a function of the `ACCESS_KEY_MIN_AGE` setting and the scheduling interval.  Also note that the FlashBlade only allows for a max of two Access Keys per Object Store user.  To avoid interrupting service, both Access Keys need to be configured.  The `ACCESS_KEY_AGE_VARIANCE` variable is intended to act as a buffer to cater for scheduling and runtime variances, and to cater for the fact that Kubernetes secrets take a short period of time to update.

If any of the Access Keys for a given user are younger than `ACCESS_KEY_MIN_AGE` less `ACCESS_KEY_AGE_VARIANCE`, no action is taken during that execution.

The `Expiration` value of the generated credentials is calculated as follows:

```
ACCESS_KEY_MIN_AGE + (ACCESS_KEY_MIN_AGE / 2) + ACCESS_KEY_AGE_VARIANCE
```

Suppose the values below are configured, the effective lifetime of the Access Key would be 33,300 seconds or 9.25 hours.

```bash
ACCESS_KEY_MIN_AGE=21600
ACCESS_KEY_AGE_VARIANCE=900
```

It is suggested that the schedule interval is at least half the time of `ACCESS_KEY_MIN_AGE`.  This is primarily to introduce a pseudo retry mechanism in case of failures.  The rotation process is best illustrated by means of an example

In our example, we set `ACCESS_KEY_MIN_AGE` to `3600` (one hour) and schedule this package to run every 30 mins.  Assume no Access Keys are present.

```bash
ACCESS_KEY_MIN_AGE=3600
ACCESS_KEY_AGE_VARIANCE=120
```

| Time  | Action Taken |
| ---   | ---     |
| 01:00 | Access Key #1 created with Expiration set to 02:32. This key is presented to users.                                                                     |
| 01:30 | No action taken as `ACCESS_KEY_MIN_AGE` of 3600 has not been reached.                                                                                   |
| 02:00 | Access Key #2 created with Expiration set to 03:32.  This key is presented to users and is now the "active" key.                                        |
| 02:30 | No action taken as key #2 is younger than `ACCESS_KEY_MIN_AGE` of 3600                                                                                  |
| 03:00 | Access Key #3 created with Expiration set to 04:32. This key is presented to users and is now the "active" key.  Key #1 is deleted from the FlashBlade  |
| 03:30 | No action taken as key #3 is younger than `ACCESS_KEY_MIN_AGE` of 3600                                                                                  |
| 04:00 | Access Key #4 created with Expiration set to 05:32. This key is presented to users and is now the "active" key.  Key #2 is deleted from the FlashBlade  |


## Configuration

Configuration is via Environment Variables.  See the `Settings` class in [configuration.py](cobalt_purestorage/configuration.py) for the full list of configuration items.  Certain items such as `interesting_object_accounts` are list types and the environment variable value should be a JSON encoded string.

```bash
 INTERESTING_OBJECT_ACCOUNTS='{"foo","bar"}'
 ```


## Usage

Once installed, configure the required environment variables and execute the `rotate-fb-creds` command


## Requirements

- docker
- [Docker Compose](https://github.com/docker/compose)
- Make


## An example of how to present credentials to users

In Kubernetes, credentials are outputted to a secret, which is in turn mounted into a pod.  Assume this mount is at `/var/run/secrets/purestorage`.  Configure the AWS Shared Configuration file as shown:

```toml
[profile purestorage]
credential_process = cat /var/run/secrets/purestorage/credentials.json
```

This will also work in `local` mode, by writing the credentials out to disk rather than outputting to a secret.


## Botocore References

- https://github.com/boto/botocore/blob/develop/botocore/credentials.py#L499

