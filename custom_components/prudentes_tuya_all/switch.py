"""Switches para DPs booleanos."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .helpers import build_device_info, extract_datapoints, extract_definitions, extract_detail


async def async_setup_entry(hass, entry, async_add_entities):
  coordinator = hass.data[DOMAIN][entry.entry_id]
  entities = []
  for device_id, payload in coordinator.data.items():
    definitions = extract_definitions(payload)
    datapoints = extract_datapoints(payload)
    detail = extract_detail(payload)
    for code, definition in definitions.items():
      if definition.get("type") == "bool" and definition.get("writable"):
        entities.append(TuyaAllSwitch(coordinator, device_id, code, detail))
  async_add_entities(entities)


class TuyaAllSwitch(CoordinatorEntity, SwitchEntity):
  _attr_has_entity_name = True

  def __init__(self, coordinator, device_id, code, detail):
    super().__init__(coordinator)
    self._device_id = device_id
    self._code = code
    self._attr_unique_id = f"{device_id}_{code}_switch"
    self._attr_name = f"{code}"
    self._attr_device_info = build_device_info(device_id, detail)

  @property
  def is_on(self):
    datapoints = extract_datapoints(self.coordinator.data.get(self._device_id, {}))
    return bool(datapoints.get(self._code))

  async def async_turn_on(self, **kwargs):
    await self._send(True)

  async def async_turn_off(self, **kwargs):
    await self._send(False)

  async def _send(self, value):
    await self.coordinator.client.send_commands(self._device_id, [{"code": self._code, "value": value}])
    await self.coordinator.async_request_refresh()
