"""Pipeline de descoberta completa de entidades Tuya Cloud."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Tuple

from .localtuya_knowledge import LocalTuyaKnowledge


def _safe_get(result: Any, key: str, default=None):
  if isinstance(result, dict):
    return result.get(key, default)
  return default


def _result(payload: Any) -> Any:
  if isinstance(payload, dict):
    return payload.get("result", payload)
  return payload


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
      "json": "json",
      "integer": "value",
  }
  return aliases.get(lowered, lowered)


def parse_values(values: Any) -> Tuple[Any, Dict[str, Any]]:
  if values is None:
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


def _status_map(status_payload: Any) -> Dict[str, Any]:
  payload = _result(status_payload)
  if isinstance(payload, list):
    return {item.get("code"): item.get("value") for item in payload if isinstance(item, dict) and item.get("code")}
  if isinstance(payload, dict):
    return payload
  return {}


def parse_value_schema(values: Dict[str, Any]) -> Dict[str, Any]:
  if not isinstance(values, dict):
    return {}
  parsed: Dict[str, Any] = {}
  for key in ("range", "min", "max", "step", "scale", "unit"):
    if key in values:
      parsed[key] = values.get(key)
  if "enum" in values:
    parsed["range"] = values.get("enum")
  return parsed


def merge_spec_and_shadow(specification: Any, shadow: Any) -> Tuple[str | None, List[Dict[str, Any]]]:
  spec_result = _result(specification) or {}
  category = spec_result.get("category")
  status_values = _status_map(shadow)

  mapping: Dict[str, Dict[str, Any]] = {}

  for item in spec_result.get("status", []) if isinstance(spec_result, dict) else []:
    code = item.get("code")
    if not code:
      continue
    values_raw, values = parse_values(item.get("values"))
    mapping[code] = {
        "dpCode": code,
        "dpId": item.get("dp_id") or item.get("dpId"),
        "dpType": normalize_dp_type(item.get("type")),
        "valuesRaw": values_raw,
        "typeSpec": {**parse_value_schema(values)},
        "name": item.get("name"),
        "access": {"read": True, "write": False, "accessMode": "ro"},
    }

  for item in spec_result.get("functions", []) if isinstance(spec_result, dict) else []:
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
        "typeSpec": {**current.get("typeSpec", {}), **parse_value_schema(values)},
        "name": item.get("name") or current.get("name"),
        "access": {"read": True, "write": True, "accessMode": "rw"},
    }

  for code, value in status_values.items():
    current = mapping.get(code, {"dpCode": code})
    mapping[code] = {**current, "dpCode": code, "currentValue": value}

  entities: List[Dict[str, Any]] = []
  for detail in mapping.values():
    entities.append({
        **detail,
        "dpId": detail.get("dpId"),
        "dpCode": detail.get("dpCode"),
        "dpType": detail.get("dpType", "unknown"),
        "typeSpec": detail.get("typeSpec", {}),
        "currentValue": detail.get("currentValue"),
        "access": detail.get("access", {"read": True, "write": False, "accessMode": "ro"}),
    })
  return category, entities


def _feature_hints(code_l: str) -> List[str]:
  hints: List[str] = []
  if "bright" in code_l:
    hints.append("brightness")
  if "temp" in code_l:
    hints.append("color_temp")
  if "colour_data" in code_l or "color_data" in code_l:
    hints.append("hs_color")
  if "scene_data" in code_l:
    hints.append("effect")
  if "work_mode" in code_l:
    hints.append("preset_mode")
  if "countdown" in code_l:
    hints.append("timer")
  return hints


def classify_entity(code: str, detail: Dict[str, Any], category: str | None, knowledge: LocalTuyaKnowledge) -> Tuple[str, float, List[str]]:
  dp_type = detail.get("dpType", "").lower()
  type_spec = detail.get("typeSpec", {}) if isinstance(detail.get("typeSpec"), dict) else {}
  access = detail.get("access", {}) if isinstance(detail.get("access"), dict) else {}
  code_l = (code or "").lower()
  reason: List[str] = []
  suggestions = knowledge.platforms_for_dp(category, code)
  if suggestions:
    suggested_platform = suggestions[0]["platform"]
    reason.append(f"Mapeado via hass-localtuya ({suggestions[0]['entity'].get('name', '')})")
    return suggested_platform, 0.8, reason

  if any(prefix in code_l for prefix in ("switch", "relay", "outlet")):
    return "switch", 0.7, ["Código contém switch/relay/outlet"]
  if code_l == "work_mode" or "work_mode" in code_l:
    return "select", 0.55, ["Enum de modo de operação"]
  if any(sub in code_l for sub in ("bright", "brightness")):
    return "light", 0.72, ["Ajuste de brilho identificado"]
  if any(sub in code_l for sub in ("temp_value", "colour_temp", "color_temp")):
    return "light", 0.7, ["Controle de temperatura de cor"]
  if "colour_data" in code_l or "color_data" in code_l:
    return "light", 0.75, ["Dados de cor encontrados"]
  if "scene_data" in code_l:
    return "light", 0.6, ["Cena/efeito detectado"]
  if "countdown" in code_l:
    return "number", 0.5, ["Contador regressivo"]
  if any(key in code_l for key in ("temp", "humidity", "co2", "pm25", "voc", "battery")):
    return "sensor", 0.7, ["Sensor ambiental identificado"]
  if "fan" in code_l or "speed" in code_l:
    return "fan", 0.6, ["Velocidade/ventilador"]
  if "percent" in code_l or code_l in {"position", "control"}:
    return "cover", 0.55, ["Controle percentual/posição"]
  if any(key in code_l for key in ("current_temp", "temperature")) and not access.get("write", True):
    return "sensor", 0.4, ["Leitura de temperatura somente leitura"]
  if dp_type in {"value", "float", "double"}:
    return "number", 0.4, ["DP numérico"]
  if dp_type == "enum" and type_spec.get("range"):
    return "select", 0.45, ["Enum com opções"]
  return "unknown", 0.15, ["Sem heurística aplicada"]


async def discover_project_devices(client, page_size: int = 200) -> List[Dict[str, Any]]:
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
            "productId": item.get("product_id") or item.get("productId"),
            "online": item.get("online") if "online" in item else item.get("isOnline"),
            "raw": item,
        })
    last_id = result.get("last_row_key") or result.get("last_id")
    if not result.get("has_more") and not last_id:
      break
  return devices


async def discover_device_entities(client, device: Dict[str, Any], knowledge: LocalTuyaKnowledge) -> Dict[str, Any]:
  device_id = device["deviceId"]
  spec_task = asyncio.create_task(client.get_specification(device_id))
  shadow_task = asyncio.create_task(client.get_device_shadow(device_id))

  spec = await spec_task
  shadow = await shadow_task

  category, merged = merge_spec_and_shadow(spec, shadow)
  dp_codes = [item.get("dpCode") for item in merged]
  combos = knowledge.combos_for_device(category or device.get("category"), dp_codes)

  entities: List[Dict[str, Any]] = []
  for dp in merged:
    code = dp.get("dpCode") or ""
    entity_type, confidence, reason = classify_entity(code, dp, category or device.get("category"), knowledge)
    entity_id = f"{device_id}__{code or dp.get('dpId')}"
    features = _feature_hints(code.lower())
    for combo in combos:
      if code in combo.get("dp_codes", []) and combo.get("platform") == entity_type:
        features.append("combo:" + ",".join(combo.get("dp_codes", [])))
    entities.append({
        "entity_id": entity_id,
        "dp_id": dp.get("dpId"),
        "dp_code": code,
        "tuya_type": dp.get("dpType", "unknown"),
        "current_value": dp.get("currentValue"),
        "spec": {
            "name": dp.get("name"),
            "type": dp.get("dpType"),
            **dp.get("typeSpec", {}),
            "values": dp.get("valuesRaw"),
        },
        "ha": {
            "suggested_platform": entity_type,
            "suggested_device_class": None,
            "suggested_unit_of_measurement": dp.get("typeSpec", {}).get("unit"),
            "features": sorted(set(features)),
            "confidence": confidence,
            "reason": reason,
        },
    })

  return {
      **device,
      "category": category or device.get("category"),
      "entities": entities,
      "spec": spec,
      "shadow": shadow,
  }


async def fetch_categories(client) -> Dict[str, str]:
  response = await client.get_device_categories()
  result = _result(response)
  mapping: Dict[str, str] = {}
  for item in result.get("list", []) if isinstance(result, dict) else []:
    code = item.get("category") or item.get("code")
    name = item.get("name") or item.get("category_name")
    if code:
      mapping[code] = name or ""
  return mapping


async def discover_all_entities(client, include_sub_devices: bool = True, concurrency: int = 3) -> Dict[str, Any]:
  knowledge = LocalTuyaKnowledge()
  categories = await fetch_categories(client)
  devices = await discover_project_devices(client)

  sem = asyncio.Semaphore(concurrency)
  results: List[Dict[str, Any]] = []
  errors: List[Dict[str, Any]] = []

  async def _run(device: Dict[str, Any]):
    async with sem:
      try:
        enriched = await discover_device_entities(client, device, knowledge)
        code = enriched.get("category")
        enriched["category_name"] = categories.get(code)
        results.append(enriched)
      except Exception as exc:  # noqa: BLE001 - queremos capturar qualquer falha de rede/API
        errors.append({"deviceId": device["deviceId"], "error": str(exc)})

  await asyncio.gather(*[_run(device) for device in devices])

  return {
      "generatedAt": datetime.now(timezone.utc).isoformat(),
      "project": {
          "source_type": "tuya_cloud",
          "source_id": client.access_id,
          "region": getattr(client, "region", None),
      },
      "categories": categories,
      "devices": results,
      "errors": errors,
  }


def summarize(devices: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
  device_list = list(devices)
  total_entities = sum(len(device.get("entities", [])) for device in device_list)
  return {"totalDevices": len(device_list), "totalEntities": total_entities}
