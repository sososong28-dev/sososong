import hashlib
import json
import time
from typing import Any

import httpx

from ...config import get_settings


class WdtClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def build_common_params(self, service_name: str) -> dict[str, Any]:
        return {
            "app_key": self.settings.wdt_app_key,
            "format": self.settings.wdt_format,
            "version": self.settings.wdt_version,
            "timestamp": int(time.time()),
            "service": service_name,
        }

    def sign(self, params: dict[str, Any]) -> str:
        raw = "".join(f"{key}={params[key]}" for key in sorted(params)) + self.settings.wdt_app_secret
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    async def call(self, service_name: str, biz_params: dict[str, Any]) -> dict[str, Any]:
        common = self.build_common_params(service_name)
        payload = {**common, "data": json.dumps(biz_params, ensure_ascii=False)}
        payload["sign"] = self.sign(payload)

        async with httpx.AsyncClient(timeout=self.settings.wdt_timeout_seconds) as client:
            response = await client.post(self.settings.wdt_base_url, data=payload)
            response.raise_for_status()
            return response.json()
