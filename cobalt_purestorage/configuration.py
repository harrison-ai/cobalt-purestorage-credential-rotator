"""Config Module"""

from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration Management"""

    log_level: str = Field("INFO", description="Set python logging level")

    fb_url: str | None = Field(
        None,
        description="FQDN or IP Address of PureStorage array, without schema",
    )

    fb_timeout: int = Field(15, description="PureStorage connection timeout")

    verify_fb_tls: bool = Field(
        False,
        description="Toggle TLS verification to PureStorage Array",
    )

    api_token: str | None = Field(None, description="PureStorage api token")

    interesting_users: set[str] = Field(
        default_factory=set,
        description="Object Store user names of interest",
    )

    k8s_mode: bool = Field(False, description="Toggle k8s or local mode")

    credentials_output_path: str = Field(
        "/app/.credentials.json",
        description="Path to write out credentials in local mode",
    )

    access_key_min_age: int = Field(
        43200,
        description="Minimum age of Access Keys in seconds",
    )

    access_key_age_variance: int = Field(
        900,
        description="An allowance to the minimum age to allow for scheduling and runtime variances",
    )

    k8s_namespace: str | None = Field(
        None,
        description="The k8s namespace of the target secret exists",
    )

    k8s_secret_name: str | None = Field(None, description="The k8s secret to update")

    k8s_secret_key: str | None = Field(
        None, description="The key within the secret to update"
    )

    kubeconfig: str | None = Field(None, description="Path to kubeconfig file")

    @model_validator(mode="after")
    def _validate(self) -> Self:
        self.log_level = self.log_level.upper()
        return self


config = Settings()
