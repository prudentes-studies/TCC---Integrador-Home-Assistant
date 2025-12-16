"""Numbers para DPs numéricos."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
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
      if definition.get("type") in ("value", "integer", "float") and definition.get("writable"):
        entities.append(TuyaAllNumber(coordinator, device_id, code, definition, detail))
  async_add_entities(entities)


class TuyaAllNumber(CoordinatorEntity, NumberEntity):
  _attr_has_entity_name = True

  def __init__(self, coordinator, device_id, code, definition, detail):
    super().__init__(coordinator)
    self._device_id = device_id
    self._code = code
    meta = parse_value_metadata(definition)
    self._attr_native_min_value = meta.get("min")
    self._attr_native_max_value = meta.get("max")
    self._attr_native_step = meta.get("step") or meta.get("scale") or 1
    self._attr_unique_id = f"{device_id}_{code}_number"
    self._attr_name = f"{code}"
    self._attr_device_info = build_device_info(device_id, detail)

  @property
  def native_value(self):
    datapoints = extract_datapoints(self.coordinator.data.get(self._device_id, {}))
    return datapoints.get(self._code)

  async def async_set_native_value(self, value):
    await self.coordinator.client.send_commands(self._device_id, [{"code": self._code, "value": value}])
    await self.coordinator.async_request_refresh()
