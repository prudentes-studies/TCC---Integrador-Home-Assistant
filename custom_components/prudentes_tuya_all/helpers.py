"""Utilidades para gerar entidades dinamicamente."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN


def build_device_info(device_id: str):
  return DeviceInfo(identifiers={(DOMAIN, device_id)}, name=f"Tuya {device_id}")


def extract_datapoints(data):
  status = data.get("status", {}).get("result", {}) or data.get("status", {})
  if isinstance(status, dict):
    return status
  if isinstance(status, list):
    return {item.get("code"): item.get("value") for item in status if item.get("code")}
  return {}
