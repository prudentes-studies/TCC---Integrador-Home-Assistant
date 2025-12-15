"""Coordinator que reúne todos os datapoints por device."""
from __future__ import annotations

from datetime import timedelta
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_POLLING


class TuyaCoordinator(DataUpdateCoordinator):
  """Faz polling da Tuya Cloud e agrupa DPs."""

  def __init__(self, hass: HomeAssistant, client, entry: ConfigEntry) -> None:
    self.client = client
    self.entry = entry
    polling = entry.options.get("polling_interval", entry.data.get("polling_interval", DEFAULT_POLLING))
    super().__init__(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_interval=timedelta(seconds=polling),
    )

  async def _async_update_data(self):
    devices = self.entry.data.get("device_ids", [])
    results = {}
    for device_id in devices:
      status = await self.client.get_device_status(device_id)
      spec = await self.client.get_specification(device_id)
      results[device_id] = {"status": status, "spec": spec}
    return results
