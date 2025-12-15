"""Integração Tuya que expõe todos os datapoints."""
from __future__ import annotations

import asyncio
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, DEFAULT_POLLING
from .coordinator import TuyaCoordinator
from .tuya_client import TuyaClient


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
  """Configura a integração a partir de uma entry."""
  hass.data.setdefault(DOMAIN, {})
  client = TuyaClient(
      access_id=entry.data.get("access_id"),
      access_secret=entry.data.get("access_secret"),
      base_url=entry.data.get("base_url"),
      region=entry.data.get("region"),
  )
  coordinator = TuyaCoordinator(hass, client, entry)
  await coordinator.async_config_entry_first_refresh()
  hass.data[DOMAIN][entry.entry_id] = coordinator

  await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
  return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
  """Descarrega a entry e plataformas."""
  unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
  if unload_ok:
    hass.data[DOMAIN].pop(entry.entry_id)
  return unload_ok
