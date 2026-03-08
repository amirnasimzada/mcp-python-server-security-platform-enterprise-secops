import base64
import json
from functools import lru_cache
from typing import Any

import boto3
from botocore.exceptions import ClientError

from src.config import get_settings


class SecretsManagerAdapter:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = boto3.client("secretsmanager", region_name=settings.AWS_REGION)

    def get_secret(self, secret_name: str) -> str:
        response = self.client.get_secret_value(SecretId=secret_name)
        if "SecretString" in response:
            return response["SecretString"]
        if "SecretBinary" in response:
            return base64.b64decode(response["SecretBinary"]).decode("utf-8")
        raise RuntimeError(f"Secret has no retrievable value: {secret_name}")

    def get_json_secret(self, secret_name: str) -> Any:
        return json.loads(self.get_secret(secret_name))


@lru_cache
def get_secrets_adapter() -> SecretsManagerAdapter:
    return SecretsManagerAdapter()
