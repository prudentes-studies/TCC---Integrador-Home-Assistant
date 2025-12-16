"""Cliente mínimo para Tuya OpenAPI."""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import time
from typing import Any, Dict, Optional, Tuple

import aiohttp

LOGGER = logging.getLogger(__name__)


class TuyaClient:
  def __init__(self, access_id: str, access_secret: str, base_url: str, region: str) -> None:
    self.access_id = access_id
    self.access_secret = access_secret.encode()
    self.base_url = base_url
    self.region = region
    self._access_token: Optional[str] = None
    self._expire_at: float = 0

  async def _ensure_token(self) -> None:
    now = time.time()
    if self._access_token and now < self._expire_at - 30:
      return
    token_response = await self._request("GET", "/v1.0/token?grant_type=1", include_token=False)
    result = token_response.get("result", {}) if isinstance(token_response, dict) else {}
    self._access_token = result.get("access_token")
    expires_in = result.get("expire_time", 3600)
    self._expire_at = now + expires_in
    LOGGER.debug("Token Tuya atualizado, expira em %s segundos", expires_in)

  def _build_signature(self, method: str, path: str, body_json: str, timestamp: str, access_token: str | None) -> str:
    base = f"{self.access_id}{access_token or ''}{timestamp}{method.upper()}{path}{body_json}"
    return hmac.new(self.access_secret, base.encode(), hashlib.sha256).hexdigest().upper()

  def _should_retry(self, status: int) -> bool:
    return status in (429, 500, 502, 503, 504)

  async def _request(
      self,
      method: str,
      path: str,
      params: Optional[Dict[str, Any]] = None,
      body: Optional[Dict[str, Any]] = None,
      include_token: bool = True,
      retries: int = 3,
      backoff: float = 0.5,
  ):
    if include_token:
      await self._ensure_token()

    timestamp = str(int(time.time() * 1000))
    url = f"{self.base_url}{path}"
    body_json = json.dumps(body) if body else ""
    access_token = self._access_token if include_token else None
    signature = self._build_signature(method, path, body_json, timestamp, access_token)
    headers = {
        "t": timestamp,
        "client_id": self.access_id,
        "sign": signature,
        "sign_method": "HMAC-SHA256",
        "Content-Type": "application/json",
    }
    if access_token:
      headers["access_token"] = access_token

    attempt = 0
    while True:
      attempt += 1
      try:
        async with aiohttp.ClientSession() as session:
          async with session.request(method, url, headers=headers, params=params, data=body_json) as resp:
            resp.raise_for_status()
            return await resp.json()
      except aiohttp.ClientResponseError as exc:  # noqa: PERF203 - queremos retries explícitos
        if attempt > retries or not self._should_retry(exc.status):
          raise
        wait_for = backoff * attempt
        LOGGER.warning("Tuya request falhou com %s, retry em %.1fs (tentativa %s/%s)", exc.status, wait_for, attempt, retries)
        await asyncio.sleep(wait_for)

  async def _request_paginated(
      self, path: str, page_size: int = 20, last_id: str | None = None
  ) -> Tuple[Any, Optional[str]]:
    params: Dict[str, Any] = {"page_size": page_size}
    if last_id:
      params["last_row_key"] = last_id
    response = await self._request("GET", path, params=params)
    result = response.get("result", {}) if isinstance(response, dict) else {}
    next_id = result.get("last_row_key") or result.get("last_id")
    return response, next_id

  async def list_devices(self, page_size: int = 20, last_id: str | None = None) -> Any:
    response, _ = await self._request_paginated("/v2.0/cloud/thing/device", page_size, last_id)
    return response

  async def list_devices_paginated(self, page_size: int = 20):
    last_id = None
    while True:
      response, last_id = await self._request_paginated("/v2.0/cloud/thing/device", page_size, last_id)
      yield response
      if not last_id:
        break

  async def get_device_detail(self, device_id: str) -> Any:
    return await self._request("GET", f"/v2.0/cloud/thing/{device_id}")

  async def get_device_shadow(self, device_id: str) -> Any:
    return await self._request("GET", f"/v2.0/cloud/thing/{device_id}/shadow/properties")

  async def get_specification(self, device_id: str) -> Any:
    return await self._request("GET", f"/v1.1/devices/{device_id}/specifications")

  async def get_functions(self, device_id: str) -> Any:
    return await self._request("GET", f"/v1.0/iot-03/devices/{device_id}/functions")

  async def get_model(self, device_id: str) -> Any:
    return await self._request("GET", f"/v2.0/cloud/thing/{device_id}/model")

  async def get_status(self, device_id: str) -> Any:
    return await self._request("GET", f"/v1.0/iot-03/devices/{device_id}/status")

  async def get_sub_devices(self, device_id: str) -> Any:
    return await self._request("GET", f"/v1.0/iot-03/devices/{device_id}/sub-devices")

  async def send_commands(self, device_id: str, commands):
    return await self._request("POST", f"/v1.0/iot-03/devices/{device_id}/commands", body={"commands": commands})
