"""Utilidades para gerar entidades dinamicamente."""
from __future__ import annotations

import json
from typing import Any, Dict

from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN


def build_device_info(device_id: str, detail: Dict[str, Any] | None = None):
  name = detail.get("name") if detail else None
  manufacturer = detail.get("product_name") if detail else None
  return DeviceInfo(
      identifiers={(DOMAIN, device_id)},
      name=name or f"Tuya {device_id}",
      manufacturer=manufacturer,
  )


def extract_datapoints(data):
  shadow = data.get("shadow", {}).get("result", {}) if isinstance(data, dict) else {}
  properties = shadow.get("properties") if isinstance(shadow, dict) else None
  if isinstance(properties, list):
    return {item.get("code"): item.get("value") for item in properties if item.get("code")}

  status = data.get("status", {}).get("result", {}) or data.get("status", {})
  if isinstance(status, dict):
    return status
  if isinstance(status, list):
    return {item.get("code"): item.get("value") for item in status if item.get("code")}
  return {}


def extract_definitions(data) -> Dict[str, Dict[str, Any]]:
  spec = data.get("spec", {}).get("result", {}) if isinstance(data, dict) else {}
  functions = spec.get("functions", []) if isinstance(spec, dict) else []
  statuses = spec.get("status", []) if isinstance(spec, dict) else []
  mapping: Dict[str, Dict[str, Any]] = {}

  for item in statuses:
    code = item.get("code")
    if code:
      mapping[code] = {**item, "writable": False}

  for item in functions:
    code = item.get("code")
    if code:
      existing = mapping.get(code, {})
      mapping[code] = {**existing, **item, "writable": True}
  return mapping


def parse_value_metadata(definition: Dict[str, Any]) -> Dict[str, Any]:
  raw_values = definition.get("values")
  if not raw_values:
    return {}
  if isinstance(raw_values, dict):
    return raw_values
  try:
    return json.loads(raw_values)
  except Exception:
    return {}


def extract_detail(data: Dict[str, Any]) -> Dict[str, Any]:
  detail = data.get("detail", {}) if isinstance(data, dict) else {}
  if isinstance(detail, dict) and "result" in detail:
    inner = detail.get("result")
    if isinstance(inner, dict):
      return inner
  return detail if isinstance(detail, dict) else {}
