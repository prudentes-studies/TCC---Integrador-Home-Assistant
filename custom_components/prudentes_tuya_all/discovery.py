"""Pipeline de descoberta completa de entidades Tuya Cloud."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple

def _safe_get(result: Any, key: str, default=None):
  if isinstance(result, dict):
    return result.get(key, default)
  return default


def normalize_dp_type(raw_type: str | None) -> str:
  if not raw_type:
    return "unknown"
  lowered = raw_type.lower()
  aliases = {
      "boolean": "bool",
      "bool": "bool",
      "string": "string",
      "enum": "enum",
      "value": "value",
      "raw": "raw",
      "bitmap": "bitmap",
      "struct": "struct",
      "array": "array",
      "double": "double",
      "float": "float",
      "json": "struct",
  }
  return aliases.get(lowered, lowered)


def parse_values(values: Any) -> Tuple[Any, Dict[str, Any]]:
  if not values:
    return values, {}
  if isinstance(values, dict):
    return json.dumps(values), values
  if isinstance(values, str):
    try:
      parsed = json.loads(values)
      return values, parsed if isinstance(parsed, dict) else {}
    except Exception:
      return values, {}
  return values, {}


def parse_model(result: Dict[str, Any]) -> Dict[str, Any]:
  raw_model = result.get("model") if isinstance(result, dict) else None
  if isinstance(raw_model, dict):
    return raw_model
  if isinstance(raw_model, str):
    try:
      return json.loads(raw_model)
    except Exception:
      return {}
  return {}


def _status_map(status_payload: Any) -> Dict[str, Any]:
  if isinstance(status_payload, dict):
    payload = status_payload.get("result", status_payload)
  else:
    payload = status_payload
  if isinstance(payload, list):
    return {item.get("code"): item.get("value") for item in payload if isinstance(item, dict) and item.get("code")}
  if isinstance(payload, dict):
    return payload
  return {}


def merge_sources(specification: Any, model: Any, status: Any) -> List[Dict[str, Any]]:
  spec_result = _safe_get(specification, "result", {})
  model_result = parse_model(_safe_get(model, "result", {}))
  status_values = _status_map(_safe_get(status, "result", status))

  mapping: Dict[str, Dict[str, Any]] = {}

  for item in spec_result.get("status", []):
    code = item.get("code")
    if not code:
      continue
    values_raw, values = parse_values(item.get("values"))
    mapping[code] = {
        "dpCode": code,
        "dpId": item.get("dp_id") or item.get("dpId"),
        "dpType": normalize_dp_type(item.get("type")),
        "valuesRaw": values_raw,
        "typeSpec": values,
        "access": {"read": True, "write": False, "accessMode": "ro"},
    }

  for item in spec_result.get("functions", []):
    code = item.get("code")
    if not code:
      continue
    values_raw, values = parse_values(item.get("values"))
    current = mapping.get(code, {"dpCode": code})
    mapping[code] = {
        **current,
        "dpCode": code,
        "dpId": current.get("dpId") or item.get("dp_id") or item.get("dpId"),
        "dpType": normalize_dp_type(item.get("type") or current.get("dpType")),
        "valuesRaw": values_raw or current.get("valuesRaw"),
        "typeSpec": values or current.get("typeSpec", {}),
        "access": {"read": True, "write": True, "accessMode": "rw"},
    }

  for service in model_result.get("services", []) if isinstance(model_result, dict) else []:
    for prop in service.get("properties", []):
      code = prop.get("code")
      if not code:
        continue
      current = mapping.get(code, {"dpCode": code})
      type_spec = prop.get("typeSpec") or {}
      mapping[code] = {
          **current,
          "dpCode": code,
          "dpId": current.get("dpId"),
          "dpType": normalize_dp_type(type_spec.get("type") or prop.get("type")),
          "typeSpec": type_spec or current.get("typeSpec", {}),
          "abilityId": prop.get("abilityId"),
          "access": _merge_access(current.get("access"), prop.get("accessMode")),
      }

  for code, value in status_values.items():
    current = mapping.get(code, {"dpCode": code, "access": {"read": True, "write": False, "accessMode": "ro"}})
    mapping[code] = {**current, "currentValue": value}

  entities = []
  for code, item in mapping.items():
    entity_type, confidence, reason = classify_entity(code, item)
    entities.append({
        **item,
        "entityType": entity_type,
        "confidence": confidence,
        "reason": reason,
    })
  return entities


def _merge_access(existing: Dict[str, Any] | None, access_mode: str | None) -> Dict[str, Any]:
  base = existing or {"read": True, "write": False, "accessMode": "ro"}
  if not access_mode:
    return base
  mode = access_mode.lower()
  return {
      "read": "r" in mode,
      "write": ("w" in mode and ("rw" in mode or mode == "wr")) or mode == "rw",
      "accessMode": mode,
  }


def classify_entity(code: str, detail: Dict[str, Any]) -> Tuple[str, float, str]:
  dp_type = detail.get("dpType", "").lower()
  type_spec = detail.get("typeSpec", {}) if isinstance(detail.get("typeSpec"), dict) else {}
  access = detail.get("access", {}) if isinstance(detail.get("access"), dict) else {}
  code_l = code.lower()

  rules: List[Tuple[str, float, str]] = []
  if any(prefix in code_l for prefix in ("bright", "colour", "color", "temp")):
    rules.append(("light", 0.72, "DP indica ajuste de brilho/cor"))
  if code_l.startswith("switch") or "relay" in code_l:
    rules.append(("switch", 0.65, "DP inicia com switch/relay"))
  if "percent" in code_l or code_l in {"position", "control"}:
    rules.append(("cover", 0.55, "Possui controle percentual/posição"))
  if "fan" in code_l or "speed" in code_l:
    rules.append(("fan", 0.6, "Contém fan/speed"))
  if any(key in code_l for key in ("temp", "mode", "work_mode")) and "set" in code_l:
    rules.append(("climate", 0.62, "Combina temperatura e modo"))
  if any(key in code_l for key in ("current_temp", "humidity", "pm25", "co2", "battery", "pir", "illum")):
    rules.append(("sensor", 0.68, "Código típico de leitura ambiente"))
  if dp_type in {"value", "float", "double"}:
    rules.append(("number", 0.4, "Tipo numérico com min/max"))
  if dp_type == "enum" and type_spec.get("range"):
    rules.append(("select", 0.45, "Enum com opções"))
  if not access.get("write", True) and access.get("read"):
    rules.append(("sensor", 0.35, "Apenas leitura"))

  if rules:
    best = max(rules, key=lambda item: item[1])
    return best
  return "unknown", 0.15, "Sem heurística aplicada"


async def discover_project_devices(client, page_size: int = 20) -> List[Dict[str, Any]]:
  devices: List[Dict[str, Any]] = []
  last_id = None
  while True:
    response = await client.list_devices(page_size=page_size, last_id=last_id)
    result = _safe_get(response, "result", {})
    for item in result.get("list", []) if isinstance(result, dict) else []:
      device_id = item.get("id") or item.get("device_id")
      if device_id:
        devices.append({
            "deviceId": device_id,
            "name": item.get("name") or item.get("customName"),
            "category": item.get("category"),
            "productId": item.get("productId"),
            "isOnline": item.get("isOnline"),
            "raw": item,
        })
    last_id = result.get("last_row_key") or result.get("last_id")
    if not last_id:
      break
  return devices


async def discover_device_entities(client, device: Dict[str, Any]) -> Dict[str, Any]:
  device_id = device["deviceId"]
  spec_task = asyncio.create_task(client.get_specification(device_id))
  model_task = asyncio.create_task(client.get_model(device_id))
  status_task = asyncio.create_task(client.get_status(device_id))
  detail_task = asyncio.create_task(client.get_device_detail(device_id))

  spec = await spec_task
  model = await model_task
  status = await status_task
  detail = await detail_task

  entities = merge_sources(spec, model, status)
  return {
      **device,
      "entities": entities,
      "spec": spec,
      "model": model,
      "status": status,
      "detail": detail,
  }


async def discover_all_entities(client, include_sub_devices: bool = True, concurrency: int = 3) -> Dict[str, Any]:
  devices = await discover_project_devices(client)
  if include_sub_devices:
    devices = await _maybe_include_sub_devices(client, devices)

  sem = asyncio.Semaphore(concurrency)
  results: List[Dict[str, Any]] = []
  errors: List[Dict[str, Any]] = []

  async def _run(device: Dict[str, Any]):
    async with sem:
      try:
        results.append(await discover_device_entities(client, device))
      except Exception as exc:  # noqa: BLE001 - queremos capturar qualquer falha de rede/API
        errors.append({"deviceId": device["deviceId"], "error": str(exc)})

  await asyncio.gather(*[_run(device) for device in devices])

  return {
      "generatedAt": datetime.utcnow().isoformat() + "Z",
      "project": {"region": getattr(client, "region", None), "clientId": client.access_id},
      "devices": results,
      "errors": errors,
  }


async def _maybe_include_sub_devices(client, devices: List[Dict[str, Any]]):
  seen = {device["deviceId"] for device in devices}
  enriched = list(devices)
  for device in list(devices):
    detail = device.get("raw", {})
    if detail.get("sub") or detail.get("is_sub"):
      continue
    try:
      subs = await client.get_sub_devices(device["deviceId"])
    except Exception:
      continue
    result = _safe_get(subs, "result", {})
    for item in result.get("list", []) if isinstance(result, dict) else []:
      sub_id = item.get("id") or item.get("device_id")
      if sub_id and sub_id not in seen:
        seen.add(sub_id)
        enriched.append({
            "deviceId": sub_id,
            "name": item.get("name") or item.get("customName"),
            "category": item.get("category"),
            "productId": item.get("productId"),
            "isOnline": item.get("isOnline"),
            "raw": item,
        })
  return enriched


def summarize(devices: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
  device_list = list(devices)
  total_entities = sum(len(device.get("entities", [])) for device in device_list)
  return {"totalDevices": len(device_list), "totalEntities": total_entities}
