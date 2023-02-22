""" Config Module """

import yaml
from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Configuration Management"""

    log_level: str = Field(
        "INFO", env="LOG_LEVEL", description="Set python logging level"
    )

    fb_url: str = Field(
        None,
        env="FB_URL",
        description="FQDN or IP Address of PureStorage array, without schema",
    )

    fb_timeout: int = Field(
        15, env="FB_TIMEOUT", description="PureStorage connection timeout"
    )

    verify_fb_tls: bool = Field(
        False,
        env="VERIFY_FB_TLS",
        description="Toggle TLS verification to PureStorage Array",
    )

    api_token: str = Field(None, env="API_TOKEN", description="PureStorage api token")

    interesting_users: set[str] = Field(
        set(),
        env="INTERESTING_USERS",
        description="Object Store user names of interest",
    )

    k8s_mode: bool = Field(
        False, env="K8S_MODE", description="Toggle k8s or local mode"
    )

    credentials_output_path: str = Field(
        "/app/.credentials.json",
        env="CREDENTIALS_OUTPUT_PATH",
        description="Path to write out credentials in local mode",
    )

    access_key_min_age: int = Field(
        43200,
        env="ACCESS_KEY_MIN_AGE",
        description="Minimum age of Access Keys in seconds",
    )

    access_key_age_variance: int = Field(
        900,
        env="ACCESS_KEY_AGE_VARIANCE",
        description="An allowance to the minimum age to allow for scheduling and runtime variances",
    )

    k8s_namespace: str = Field(
        None,
        env="K8S_NAMESPACE",
        description="The k8s namespace of the target secret exists",
    )

    k8s_secret_name: str = Field(
        None, env="K8S_SECRET_NAME", description="The k8s secret to update"
    )

    k8s_secret_key: str = Field(
        None, env="K8S_SECRET_KEY", description="The key within the secret to update"
    )

    kubeconfig: str = Field(
        None, env="KUBECONFIG", description="Path to kubeconfig file"
    )

    @validator("log_level")
    def uppercase_logging_level(cls, v):
        return v.upper()

    class Config:
        case_sensitive = True


config = Settings()
