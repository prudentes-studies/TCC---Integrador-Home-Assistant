"""Coordinator que reúne todos os datapoints por device."""
from __future__ import annotations

from datetime import timedelta
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_POLLING, CONF_DEVICE_IDS
from .discovery import discover_device_entities, discover_project_devices


class TuyaCoordinator(DataUpdateCoordinator):
  """Faz polling da Tuya Cloud e agrupa DPs."""

  def __init__(self, hass: HomeAssistant, client, entry: ConfigEntry) -> None:
    self.client = client
    self.entry = entry
    self._known_devices = entry.options.get(CONF_DEVICE_IDS, entry.data.get(CONF_DEVICE_IDS, []))
    polling = entry.options.get("polling_interval", entry.data.get("polling_interval", DEFAULT_POLLING))
    super().__init__(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_interval=timedelta(seconds=polling),
    )

  async def _async_update_data(self):
    device_ids = self.entry.options.get(CONF_DEVICE_IDS, self.entry.data.get(CONF_DEVICE_IDS, []))
    discovered = []
    if not device_ids:
      discovered = await discover_project_devices(self.client)
      device_ids = [item["deviceId"] for item in discovered]
      await self._persist_device_list(device_ids)

    results = {}
    for device_id in device_ids:
      base = next((d for d in discovered if d["deviceId"] == device_id), {"deviceId": device_id})
      discovery = await discover_device_entities(self.client, base)
      shadow = await self.client.get_device_shadow(device_id)
      results[device_id] = {**discovery, "shadow": shadow}
    return results

  async def _persist_device_list(self, devices):
    if not devices or devices == self._known_devices:
      return
    self._known_devices = devices
    options = {**self.entry.options, CONF_DEVICE_IDS: devices}
    self.hass.config_entries.async_update_entry(self.entry, options=options)
