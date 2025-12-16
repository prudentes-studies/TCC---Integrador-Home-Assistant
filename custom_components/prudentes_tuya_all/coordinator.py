"""Coordinator que reúne todos os datapoints por device."""
from __future__ import annotations

from datetime import timedelta
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_POLLING, CONF_DEVICE_IDS


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
    devices = self.entry.options.get(CONF_DEVICE_IDS, self.entry.data.get(CONF_DEVICE_IDS, []))
    if not devices:
      devices = await self._autodiscover_devices()
      await self._persist_device_list(devices)
    results = {}
    for device_id in devices:
      detail = await self.client.get_device_detail(device_id)
      spec = await self.client.get_specification(device_id)
      shadow = await self.client.get_device_shadow(device_id)
      results[device_id] = {"detail": detail, "shadow": shadow, "spec": spec}
    return results

  async def _autodiscover_devices(self):
    devices = []
    last_id = None
    while True:
      response = await self.client.list_devices(last_id=last_id)
      result = response.get("result", {}) if isinstance(response, dict) else {}
      for item in result.get("list", []):
        device_id = item.get("id") or item.get("device_id")
        if device_id:
          devices.append(device_id)
      last_id = result.get("last_row_key") or result.get("last_id")
      if not last_id:
        break
    return devices

  async def _persist_device_list(self, devices):
    if not devices or devices == self._known_devices:
      return
    self._known_devices = devices
    options = {**self.entry.options, CONF_DEVICE_IDS: devices}
    self.hass.config_entries.async_update_entry(self.entry, options=options)
