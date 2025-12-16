"""Select para DPs enumerados."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .helpers import build_device_info, extract_datapoints, extract_definitions, parse_value_metadata, extract_detail


async def async_setup_entry(hass, entry, async_add_entities):
  coordinator = hass.data[DOMAIN][entry.entry_id]
  entities = []
  for device_id, payload in coordinator.data.items():
    definitions = extract_definitions(payload)
    datapoints = extract_datapoints(payload)
    detail = extract_detail(payload)
    for code, definition in definitions.items():
      if definition.get("type") in ("enum", "string") and definition.get("writable"):
        meta = parse_value_metadata(definition)
        options = meta.get("range") or []
        entities.append(TuyaAllSelect(coordinator, device_id, code, options, detail))
  async_add_entities(entities)


class TuyaAllSelect(CoordinatorEntity, SelectEntity):
  _attr_has_entity_name = True

  def __init__(self, coordinator, device_id, code, options, detail):
    super().__init__(coordinator)
    self._device_id = device_id
    self._code = code
    self._attr_unique_id = f"{device_id}_{code}_select"
    self._attr_name = f"{code}"
    self._attr_device_info = build_device_info(device_id, detail)
    self._attr_options = options or []

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
