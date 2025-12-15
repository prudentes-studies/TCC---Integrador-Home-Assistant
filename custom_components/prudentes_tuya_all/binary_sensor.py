"""Binary sensors para DPs booleanos (somente leitura)."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .helpers import build_device_info, extract_datapoints


async def async_setup_entry(hass, entry, async_add_entities):
  coordinator = hass.data[DOMAIN][entry.entry_id]
  entities = []
  for device_id, payload in coordinator.data.items():
    datapoints = extract_datapoints(payload)
    for code, value in datapoints.items():
      if isinstance(value, bool):
        entities.append(TuyaAllBinarySensor(coordinator, device_id, code))
  async_add_entities(entities)


class TuyaAllBinarySensor(CoordinatorEntity, BinarySensorEntity):
  _attr_has_entity_name = True

  def __init__(self, coordinator, device_id, code):
    super().__init__(coordinator)
    self._device_id = device_id
    self._code = code
    self._attr_unique_id = f"{device_id}_{code}_binary"
    self._attr_name = f"{code} estado"
    self._attr_device_info = build_device_info(device_id)

  @property
  def is_on(self):
    datapoints = extract_datapoints(self.coordinator.data.get(self._device_id, {}))
    return bool(datapoints.get(self._code))
