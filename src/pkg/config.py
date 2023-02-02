""" Config Module """

import os

import yaml


class Config:
    """Global configuration class"""

    _CONFIG_FILE = os.getenv("CONFIG_FILE", default="config.yml")

    cfg = {}

    if os.path.exists(_CONFIG_FILE):
        with open(_CONFIG_FILE, "r") as f:
            cfg = yaml.safe_load(f)

    log_level = cfg.get("log_level", "INFO").upper()
    fb_url = cfg.get("fb_url", None)
    api_token = cfg.get("api_token", None)
    excluded_user_names = cfg.get("excluded_user_names", [])
    interesting_object_accounts = cfg.get("interesting_object_accounts", [])
    k8s_mode = cfg.get("k8s_mode", False)
    credentials_output_path = cfg.get(
        "credentials_output_path", "/output/credentials.json"
    )
    access_key_min_age = cfg.get("access_key_min_age", 43200)
    access_key_age_variance = cfg.get("access_key_age_variance", 900)
    k8s_namespace = cfg.get("k8s_namespace", "default")
    k8s_secret_name = cfg.get("k8s_secret_name", None)
    k8s_secret_key = cfg.get("k8s_secret_key", None)
    kubeconfig = cfg.get("kubeconfig", None)
