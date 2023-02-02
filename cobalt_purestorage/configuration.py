""" Config Module """

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    log_level: str = Field("INFO", env="LOG_LEVEL")
    fb_url: str = Field(None, env="FB_URL")
    verify_fb_tls: bool = Field(False, env="VERIFY_FB_TLS")
    api_token: str = Field(None, env="API_TOKEN")
    excluded_user_names: set[str] = Field(set(), env="EXCLUDED_USER_NAMES")
    interesting_object_accounts: set[str] = Field(
        set(), env="INTERESTING_OBJECT_ACCOUNTS"
    )
    k8s_mode: bool = Field(False, env="K8S_MODE")
    credentials_output_path: str = Field(
        "/output/credentials.json", env="CREDENTIALS_OUTPUT_PATH"
    )
    access_key_min_age: int = Field(43200, env="ACCESS_KEY_MIN_AGE")
    access_key_age_variance: int = Field(900, env="ACCESS_KEY_AGE_VARIANCE")
    k8s_namespace: str = Field(None, env="K8S_NAMESPACE")
    k8s_secret_name: str = Field(None, env="K8S_SECRET_NAME")
    k8s_secret_key: str = Field(None, env="K8S_SECRET_KEY")
    kubeconfig: str = Field(None, env="KUBECONFIG")

    class Config:
        case_sensitive = True


config = Settings()
