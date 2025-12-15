"""Cliente mínimo para Tuya OpenAPI."""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import time
from typing import Any

import aiohttp


class TuyaClient:
  def __init__(self, access_id: str, access_secret: str, base_url: str, region: str) -> None:
    self.access_id = access_id
    self.access_secret = access_secret.encode()
    self.base_url = base_url
    self.region = region

  async def _request(self, method: str, path: str, params=None, body=None):
    timestamp = str(int(time.time() * 1000))
    url = f"{self.base_url}{path}"
    body_json = json.dumps(body) if body else ''
    string_to_sign = f"{self.access_id}{timestamp}{method.upper()}{path}{body_json}"
    signature = hmac.new(self.access_secret, string_to_sign.encode(), hashlib.sha256).hexdigest().upper()
    headers = {
        "t": timestamp,
        "client_id": self.access_id,
        "sign": signature,
        "sign_method": "HMAC-SHA256",
        "Content-Type": "application/json",
    }
    async with aiohttp.ClientSession() as session:
      async with session.request(method, url, headers=headers, params=params, data=body_json) as resp:
        resp.raise_for_status()
        return await resp.json()

  async def get_specification(self, device_id: str) -> Any:
    return await self._request("GET", f"/v1.0/iot-03/devices/{device_id}/specification")

  async def get_functions(self, device_id: str) -> Any:
    return await self._request("GET", f"/v1.0/iot-03/devices/{device_id}/functions")

  async def get_device_status(self, device_id: str) -> Any:
    return await self._request("GET", f"/v1.0/devices/{device_id}")

  async def send_commands(self, device_id: str, commands):
    return await self._request("POST", f"/v1.0/iot-03/devices/{device_id}/commands", body={"commands": commands})
