"""Executa discovery completo de entidades Tuya e exporta JSON consolidado."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from custom_components.prudentes_tuya_all.const import DEFAULT_BASE_URL
from custom_components.prudentes_tuya_all.discovery import discover_all_entities, summarize
from custom_components.prudentes_tuya_all.tuya_client import TuyaClient

ARTIFACT_PATH = Path("artifacts/tuya-entities-map.json")


def _load_env() -> tuple[str, str, str, str]:
  access_id = os.getenv("TUYA_ACCESS_ID")
  access_secret = os.getenv("TUYA_ACCESS_SECRET")
  region = os.getenv("TUYA_REGION", "us")
  base_url = os.getenv("TUYA_BASE_URL", DEFAULT_BASE_URL)
  if not access_id or not access_secret:
    raise SystemExit("Preencha TUYA_ACCESS_ID e TUYA_ACCESS_SECRET para executar o discovery.")
  return access_id, access_secret, region, base_url


def _print_summary(payload: dict[str, Any]) -> None:
  summary = summarize(payload.get("devices", []))
  print("=== Resumo Discovery ===")
  print(f"Dispositivos: {summary['totalDevices']} | Entidades: {summary['totalEntities']}")
  if payload.get("errors"):
    print("Avisos/erros por device:")
    for item in payload["errors"]:
      print(f"- {item['deviceId']}: {item['error']}")


def _mask_client_id(client_id: str) -> str:
  return f"{client_id[:4]}***{client_id[-4:]}" if client_id else ""


async def _run() -> int:
  access_id, access_secret, region, base_url = _load_env()
  concurrency = int(os.getenv("TUYA_CONCURRENCY", "3"))
  include_sub = os.getenv("TUYA_INCLUDE_SUB", "true").lower() != "false"
  client = TuyaClient(access_id, access_secret, base_url, region)

  print(f"Iniciando discovery Tuya em {base_url} (região {region}) com {concurrency} conexões...")
  payload = await discover_all_entities(client, include_sub_devices=include_sub, concurrency=concurrency)
  payload["project"]["clientId"] = _mask_client_id(payload["project"].get("clientId"))

  ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
  ARTIFACT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
  _print_summary(payload)
  print(f"Artefato salvo em {ARTIFACT_PATH.relative_to(Path.cwd())}")
  return 0


def main() -> int:
  try:
    return asyncio.run(_run())
  except SystemExit as exc:
    print(exc)
    return 1


if __name__ == "__main__":
  raise SystemExit(main())
