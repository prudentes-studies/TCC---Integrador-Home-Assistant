"""Validação opcional da descoberta de dispositivos Tuya via CI.

Executa a listagem de devices apenas quando as variáveis de ambiente
TUYA_ACCESS_ID, TUYA_ACCESS_SECRET e TUYA_REGION estão definidas.
"""
from __future__ import annotations

import asyncio
import os
import sys
from typing import Any

from custom_components.prudentes_tuya_all.const import DEFAULT_BASE_URL, CONF_REGION
from custom_components.prudentes_tuya_all.tuya_client import TuyaClient


async def _run_discovery() -> int:
  access_id = os.getenv("TUYA_ACCESS_ID")
  access_secret = os.getenv("TUYA_ACCESS_SECRET")
  region = os.getenv("TUYA_REGION") or "us"
  base_url = os.getenv("TUYA_BASE_URL", DEFAULT_BASE_URL)

  if not access_id or not access_secret or not region:
    print(
        "[skip] Variáveis TUYA_ACCESS_ID, TUYA_ACCESS_SECRET e TUYA_REGION não foram preenchidas; "
        "pulando teste de descoberta."
    )
    return 0

  client = TuyaClient(access_id, access_secret, base_url, region)
  print(f"Iniciando descoberta Tuya em {base_url} ({region})...")
  try:
    discovery: Any = await client.list_devices()
  except Exception as exc:  # noqa: BLE001 - queremos capturar qualquer falha de rede/API
    print(f"[erro] Falha ao consultar dispositivos: {exc}")
    return 1

  if not isinstance(discovery, dict):
    print("[erro] Resposta inesperada da API Tuya (esperado dict)")
    return 1

  result = discovery.get("result", {})
  devices = result.get("list", []) if isinstance(result, dict) else []
  print(f"[ok] Dispositivos retornados: {len(devices)}")
  return 0


def main() -> int:
  return asyncio.run(_run_discovery())


if __name__ == "__main__":
  sys.exit(main())
