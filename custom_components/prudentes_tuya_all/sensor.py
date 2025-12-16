"""Sensores para cada DP e diagnóstico."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .helpers import build_device_info, extract_datapoints, extract_definitions, extract_detail


async def async_setup_entry(hass, entry, async_add_entities):
  coordinator = hass.data[DOMAIN][entry.entry_id]
  entities = []
  for device_id, payload in coordinator.data.items():
    datapoints = extract_datapoints(payload)
    definitions = extract_definitions(payload)
    detail = extract_detail(payload)
    for code, value in datapoints.items():
      entities.append(TuyaAllSensor(coordinator, device_id, code, definitions.get(code, {}), detail))
    entities.append(TuyaDiagnosticSensor(coordinator, device_id, detail))
  async_add_entities(entities)


class TuyaAllSensor(CoordinatorEntity, SensorEntity):
  _attr_has_entity_name = True

  def __init__(self, coordinator, device_id, code, definition, detail):
    super().__init__(coordinator)
    self._device_id = device_id
    self._code = code
    self._definition = definition
    self._attr_unique_id = f"{device_id}_{code}_sensor"
    self._attr_name = f"{definition.get('name', code)}"
    self._attr_device_info = build_device_info(device_id, detail)

  @property
  def native_value(self):
    payload = self.coordinator.data.get(self._device_id, {})
    datapoints = extract_datapoints(payload)
    return datapoints.get(self._code)


class TuyaDiagnosticSensor(CoordinatorEntity, SensorEntity):
  _attr_has_entity_name = True
  _attr_name = "diagnostic"

  def __init__(self, coordinator, device_id, detail):
    super().__init__(coordinator)
    self._device_id = device_id
    self._attr_unique_id = f"{device_id}_diagnostic"
    self._attr_device_info = build_device_info(device_id, detail)

  @property
  def native_value(self):
    return "ok"

  @property
  def extra_state_attributes(self):
    return self.coordinator.data.get(self._device_id, {})
