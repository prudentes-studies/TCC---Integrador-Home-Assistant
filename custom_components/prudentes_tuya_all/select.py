"""Select para DPs enumerados."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .helpers import build_device_info, extract_datapoints


async def async_setup_entry(hass, entry, async_add_entities):
  coordinator = hass.data[DOMAIN][entry.entry_id]
  entities = []
  for device_id, payload in coordinator.data.items():
    datapoints = extract_datapoints(payload)
    for code, value in datapoints.items():
      if isinstance(value, str):
        entities.append(TuyaAllSelect(coordinator, device_id, code, value))
  async_add_entities(entities)


class TuyaAllSelect(CoordinatorEntity, SelectEntity):
  _attr_has_entity_name = True

  def __init__(self, coordinator, device_id, code, initial_value):
    super().__init__(coordinator)
    self._device_id = device_id
    self._code = code
    self._attr_unique_id = f"{device_id}_{code}_select"
    self._attr_name = f"{code}"
    self._attr_device_info = build_device_info(device_id)
    self._attr_options = [initial_value]

  @property
  def current_option(self):
    datapoints = extract_datapoints(self.coordinator.data.get(self._device_id, {}))
    value = datapoints.get(self._code)
    if value and value not in self._attr_options:
      self._attr_options.append(value)
    return value

  async def async_select_option(self, option: str):
    await self.coordinator.client.send_commands(self._device_id, [{"code": self._code, "value": option}])
    await self.coordinator.async_request_refresh()
