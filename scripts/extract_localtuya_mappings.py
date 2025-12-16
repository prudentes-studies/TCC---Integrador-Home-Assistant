"""Extrai mapeamentos do hass-localtuya para uso offline."""
from __future__ import annotations

import json
import sys
import types
from datetime import datetime
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
VENDOR_PATH = ROOT / "custom_components" / "prudentes_tuya_all" / "vendor" / "hass_localtuya"
OUTPUT = ROOT / "custom_components" / "prudentes_tuya_all" / "data" / "localtuya_mappings.json"


def _stub_homeassistant() -> None:
  """Cria módulos "homeassistant" mínimos para importar o vendor."""
  ha = types.ModuleType("homeassistant")
  const = types.ModuleType("homeassistant.const")

  class _EnumFallback:
    def __getattr__(self, name: str) -> str:
      return name.lower()

  class _PlatformMeta(type):
    def __getattr__(cls, name: str):  # type: ignore[misc]
      return Platform(name.lower())

  class Platform(str, metaclass=_PlatformMeta):
    # Enum simplificado apenas para expor .value
    def __new__(cls, value: str):
      obj = str.__new__(cls, value)
      obj.value = value
      return obj

  const.Platform = Platform
  const.CONF_FRIENDLY_NAME = "friendly_name"
  const.CONF_ICON = "icon"
  const.CONF_ENTITY_CATEGORY = "entity_category"
  const.CONF_DEVICE_CLASS = "device_class"
  const.CONF_PLATFORM = "platform"
  const.CONF_ID = "id"
  const.CONF_TEMPERATURE_UNIT = "temperature_unit"
  const.CONF_BRIGHTNESS = "brightness"
  const.CONF_COLOR_TEMP = "color_temp"
  const.CONF_SCENE = "scene"
  const.CONF_STATE_CLASS = "state_class"
  const.EntityCategory = _EnumFallback()

  class UnitOfTime:
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"

  const.UnitOfTime = UnitOfTime

  class _DynamicUnit:
    def __getattr__(self, name: str) -> str:  # type: ignore[misc]
      return name.lower()

  const.UnitOfPower = _DynamicUnit()
  const.UnitOfElectricCurrent = _DynamicUnit()
  const.UnitOfElectricPotentialDifference = _DynamicUnit()
  const.UnitOfEnergy = _DynamicUnit()
  const.UnitOfTemperature = _DynamicUnit()
  const.UnitOfVolumetricFlowRate = _DynamicUnit()
  const.UnitOfLength = _DynamicUnit()
  const.UnitOfElectricPotential = _DynamicUnit()
  const.UnitOfVolume = _DynamicUnit()
  const.UnitOfMass = _DynamicUnit()
  const.UnitOfPressure = _DynamicUnit()
  const.UnitOfSpeed = _DynamicUnit()
  const.UnitOfIlluminance = _DynamicUnit()
  const.UnitOfSoundPressure = _DynamicUnit()
  const.UnitOfVolumetricFlowRate = _DynamicUnit()
  const.UnitOfPercentage = _DynamicUnit()
  const.UnitOfApparentPower = _DynamicUnit()
  def _const_getattr(name: str) -> str:
    return name.lower()

  const.__getattr__ = _const_getattr

  sys.modules.setdefault("homeassistant", ha)
  sys.modules.setdefault("homeassistant.const", const)

  def _with_dynamic(name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__getattr__ = lambda _, attr: attr.lower()
    return mod

  components = {
      "alarm_control_panel": ["AlarmControlPanelState"],
      "binary_sensor": ["BinarySensorDeviceClass"],
      "switch": ["SwitchDeviceClass"],
      "fan": ["DIRECTION_FORWARD", "DIRECTION_REVERSE"],
      "humidifier": ["HumidifierDeviceClass", "HumidifierEntityFeature"],
      "number": ["NumberDeviceClass"],
      "sensor": ["SensorStateClass", "SensorDeviceClass"],
      "climate": ["HVACMode", "HVACAction"],
      "water_heater": ["WaterHeaterEntityFeature"],
      "cover": ["CoverDeviceClass"],
  }
  for comp, attrs in components.items():
    mod = types.ModuleType(f"homeassistant.components.{comp}")
    for attr in attrs:
      setattr(mod, attr, _EnumFallback())
    def _module_getattr(name: str) -> str:
      return name.lower()

    mod.__getattr__ = _module_getattr
    sys.modules.setdefault(f"homeassistant.components.{comp}", mod)

  helpers = types.ModuleType("homeassistant.helpers")
  sys.modules.setdefault("homeassistant.helpers", helpers)


def _register_package(name: str, path: Path) -> None:
  module = types.ModuleType(name)
  module.__path__ = [str(path)]
  sys.modules[name] = module


def _normalize_dp_values(value: Any) -> Iterable[str]:
  if value is None:
    return []
  if isinstance(value, tuple):
    items: list[str] = []
    for item in value:
      items.extend(_normalize_dp_values(item))
    return items
  if hasattr(value, "value"):
    return [str(getattr(value, "value"))]
  return [str(value)]


def main() -> int:
  _stub_homeassistant()
  _register_package("custom_components", ROOT / "custom_components")
  _register_package("custom_components.localtuya", VENDOR_PATH)
  _register_package("custom_components.localtuya.core", VENDOR_PATH)
  select_mod = types.ModuleType("custom_components.localtuya.select")
  select_mod.CONF_OPTIONS = "options"
  sys.modules[select_mod.__name__] = select_mod
  data_path = VENDOR_PATH / "ha_entities" / "__init__.py"
  if not data_path.exists():
    raise SystemExit(f"ha_entities não encontrado em {data_path}")

  const_path = VENDOR_PATH / "const.py"
  const_spec = spec_from_file_location(
      "custom_components.localtuya.const",
      const_path,
      submodule_search_locations=[str(VENDOR_PATH)],
  )
  assert const_spec and const_spec.loader
  const_module = module_from_spec(const_spec)
  const_module.__path__ = [str(VENDOR_PATH)]
  sys.modules[const_spec.name] = const_module
  const_spec.loader.exec_module(const_module)

  spec = spec_from_file_location(
      "custom_components.localtuya.core.ha_entities",
      data_path,
      submodule_search_locations=[str(VENDOR_PATH / "ha_entities")],
  )
  assert spec and spec.loader
  module = module_from_spec(spec)
  module.__path__ = [str(VENDOR_PATH / "ha_entities")]
  sys.modules[spec.name] = module
  spec.loader.exec_module(module)

  catalog: dict[str, dict[str, list[dict[str, Any]]]] = {}
  for platform, categories in module.DATA_PLATFORMS.items():
    platform_name = getattr(platform, "value", str(platform))
    for category, entities in categories.items():
      cat_bucket = catalog.setdefault(category, {}).setdefault(platform_name, [])
      for entity in entities:
        dp_codes: list[str] = []
        for v in getattr(entity, "localtuya_conf", {}).values():
          dp_codes.extend(_normalize_dp_values(v))
        cat_bucket.append({
            "name": getattr(entity, "name", ""),
            "dp_codes": sorted(set(dp_codes)),
        })

  OUTPUT.parent.mkdir(parents=True, exist_ok=True)
  payload = {
      "generated_at": datetime.utcnow().isoformat() + "Z",
      "source": "hass-localtuya/xZetsubou",
      "categories": catalog,
  }
  OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
  print(f"Mapping salvo em {OUTPUT}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
