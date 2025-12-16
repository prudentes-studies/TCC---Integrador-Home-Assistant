"""Fluxo de configuração UI."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_ACCESS_ID,
    CONF_ACCESS_SECRET,
    CONF_BASE_URL,
    CONF_DEVICE_IDS,
    CONF_POLLING_INTERVAL,
    CONF_REGION,
    DEFAULT_BASE_URL,
    DEFAULT_POLLING,
)
from .tuya_client import TuyaClient

class TuyaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
  """Fluxo principal de configuração."""

  VERSION = 1

  async def async_step_user(self, user_input=None) -> FlowResult:
    errors = {}
    if user_input is not None:
      device_raw = user_input.get(CONF_DEVICE_IDS, "")
      device_ids = [item.strip() for item in device_raw.split(',') if item.strip()]
      if not device_ids:
        try:
          client = TuyaClient(
              user_input[CONF_ACCESS_ID], user_input[CONF_ACCESS_SECRET], user_input[CONF_BASE_URL], user_input[CONF_REGION]
          )
          discovery = await client.list_devices()
          result = discovery.get("result", {}) if isinstance(discovery, dict) else {}
          device_ids = [item.get("id") or item.get("device_id") for item in result.get("list", []) if item.get("id") or item.get("device_id")]
        except Exception:
          errors["base"] = "cannot_connect"
      if not errors:
        user_input[CONF_DEVICE_IDS] = device_ids
        return self.async_create_entry(title="Prudentes Tuya All", data=user_input)

    schema = vol.Schema(
        {
            vol.Required(CONF_ACCESS_ID): str,
            vol.Required(CONF_ACCESS_SECRET): str,
            vol.Optional(CONF_REGION, default="us"): str,
            vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
            vol.Optional(CONF_DEVICE_IDS, default=""): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING): int,
        }
    )
    return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

  async def async_step_import(self, user_input=None):
    return await self.async_step_user(user_input)

  @staticmethod
  def async_get_options_flow(config_entry):
    return TuyaOptionsFlowHandler(config_entry)


class TuyaOptionsFlowHandler(config_entries.OptionsFlow):
  def __init__(self, config_entry):
    super().__init__(config_entry)

  @staticmethod
  def _normalize_device_ids(value):
    if isinstance(value, str):
      return [item.strip() for item in value.split(',') if item.strip()]
    if isinstance(value, list):
      return [str(item).strip() for item in value if str(item).strip()]
    return []

  async def async_step_init(self, user_input=None):
    return await self.async_step_options(user_input)

  async def async_step_options(self, user_input=None):
    errors = {}
    if user_input is not None:
      device_ids = [item.strip() for item in user_input.get(CONF_DEVICE_IDS, '').split(',') if item.strip()]
      user_input[CONF_DEVICE_IDS] = device_ids
      return self.async_create_entry(title="Opções", data=user_input)

    defaults = {**self.config_entry.data, **self.config_entry.options}
    default_devices = self._normalize_device_ids(defaults.get(CONF_DEVICE_IDS, []))
    schema = vol.Schema(
        {
            vol.Optional(CONF_DEVICE_IDS, default=','.join(default_devices)): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=defaults.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING)): int,
        }
    )
    return self.async_show_form(step_id="options", data_schema=schema, errors=errors)
