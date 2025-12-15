"""Numbers para DPs numéricos."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .helpers import build_device_info, extract_datapoints


async def async_setup_entry(hass, entry, async_add_entities):
  coordinator = hass.data[DOMAIN][entry.entry_id]
  entities = []
  for device_id, payload in coordinator.data.items():
    datapoints = extract_datapoints(payload)
    for code, value in datapoints.items():
      if isinstance(value, (int, float)):
        entities.append(TuyaAllNumber(coordinator, device_id, code))
  async_add_entities(entities)


class TuyaAllNumber(CoordinatorEntity, NumberEntity):
  _attr_has_entity_name = True

  def __init__(self, coordinator, device_id, code):
    super().__init__(coordinator)
    self._device_id = device_id
    self._code = code
    self._attr_unique_id = f"{device_id}_{code}_number"
    self._attr_name = f"{code}"
    self._attr_device_info = build_device_info(device_id)

  @property
  def native_value(self):
    datapoints = extract_datapoints(self.coordinator.data.get(self._device_id, {}))
    return datapoints.get(self._code)

  async def async_set_native_value(self, value):
    await self.coordinator.client.send_commands(self._device_id, [{"code": self._code, "value": value}])
    await self.coordinator.async_request_refresh()
