"""Cliente mínimo para Tuya OpenAPI com paginação completa."""
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


class TuyaApiError(Exception):
  """Erro de comunicação com a Tuya Cloud."""


class TuyaClient:
  def __init__(self, access_id: str, access_secret: str, base_url: str, region: str) -> None:
    self.access_id = access_id
    self.access_secret = access_secret.encode()
    self.base_url = base_url.rstrip("/")
    self.region = region
    self._access_token: Optional[str] = None
    self._refresh_token: Optional[str] = None
    self._expire_at: float = 0

  async def close(self) -> None:
    return None

  def _build_signature(self, method: str, path: str, body_json: str, timestamp: str, access_token: str | None) -> str:
    payload = f"{method.upper()}\n{hashlib.sha256(body_json.encode()).hexdigest()}\n\n{path}"
    base = f"{self.access_id}{access_token or ''}{timestamp}{payload}"
    return hmac.new(self.access_secret, base.encode(), hashlib.sha256).hexdigest().upper()

  def _should_retry(self, status: int) -> bool:
    return status in (429, 500, 502, 503, 504)

  async def _ensure_token(self) -> None:
    now = time.time()
    if self._access_token and now < self._expire_at - 30:
      return

    token_response = await self._request("GET", "/v1.0/token?grant_type=1", include_token=False)
    result = token_response.get("result", {}) if isinstance(token_response, dict) else {}
    self._access_token = result.get("access_token")
    self._refresh_token = result.get("refresh_token")
    expires_in = result.get("expire_time", 3600)
    self._expire_at = now + expires_in
    LOGGER.debug("Token Tuya atualizado, expira em %s segundos", expires_in)

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
    body_json = json.dumps(body or {}) if body is not None else ""
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
            if resp.status == 401 and include_token:
              LOGGER.warning("Token inválido, forçando renovação e retry")
              self._access_token = None
              self._expire_at = 0
              if attempt <= retries:
                await asyncio.sleep(backoff * attempt)
                await self._ensure_token()
                continue
            if resp.status >= 400 and not self._should_retry(resp.status):
              text = await resp.text()
              raise TuyaApiError(f"HTTP {resp.status}: {text}")
            if resp.status >= 400:
              wait_for = backoff * attempt
              LOGGER.warning(
                  "Tuya request falhou com %s, retry em %.1fs (tentativa %s/%s)",
                  resp.status,
                  wait_for,
                  attempt,
                  retries,
              )
              if attempt > retries:
                text = await resp.text()
                raise TuyaApiError(f"HTTP {resp.status}: {text}")
              await asyncio.sleep(wait_for)
              continue
            return await resp.json()
      except aiohttp.ClientResponseError as exc:  # noqa: PERF203 - queremos retries explícitos
        if attempt > retries or not self._should_retry(exc.status):
          raise TuyaApiError(str(exc))
        wait_for = backoff * attempt
        LOGGER.warning("Tuya request falhou com %s, retry em %.1fs (tentativa %s/%s)", exc.status, wait_for, attempt, retries)
        await asyncio.sleep(wait_for)

  async def _request_paginated(
      self, path: str, page_size: int = 20, last_id: str | None = None
  ) -> Tuple[Any, Optional[str], bool]:
    params: Dict[str, Any] = {"page_size": page_size}
    if last_id:
      params["last_row_key"] = last_id
    response = await self._request("GET", path, params=params)
    result = response.get("result", {}) if isinstance(response, dict) else {}
    next_id = result.get("last_row_key") or result.get("last_id")
    has_more = bool(result.get("has_more", False)) or bool(next_id)
    return response, next_id, has_more

  async def list_devices(self, page_size: int = 20, last_id: str | None = None) -> Any:
    response, _, _ = await self._request_paginated("/v1.3/iot-03/devices", page_size, last_id)
    return response

  async def list_devices_paginated(self, page_size: int = 20):
    last_id = None
    while True:
      response, last_id, has_more = await self._request_paginated("/v1.3/iot-03/devices", page_size, last_id)
      yield response
      if not has_more:
        break

  async def get_device_detail(self, device_id: str) -> Any:
    return await self._request("GET", f"/v2.0/cloud/thing/{device_id}")

  async def get_device_shadow(self, device_id: str) -> Any:
    return await self._request("GET", f"/v2.0/cloud/thing/{device_id}/shadow/properties")

  async def get_specification(self, device_id: str) -> Any:
    return await self._request("GET", f"/v1.0/iot-03/devices/{device_id}/specification")

  async def get_device_categories(self) -> Any:
    return await self._request("GET", "/v1.0/iot-03/device-categories")

  async def send_commands(self, device_id: str, commands):
    return await self._request("POST", f"/v1.0/iot-03/devices/{device_id}/commands", body={"commands": commands})
