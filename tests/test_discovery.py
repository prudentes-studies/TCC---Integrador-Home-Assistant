from __future__ import annotations

import asyncio
import importlib
import json
import sys
import types
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

# Stubs mínimos para evitar dependência real do Home Assistant durante os testes
homeassistant = types.ModuleType("homeassistant")
homeassistant.config_entries = types.SimpleNamespace(ConfigEntry=object)
homeassistant.core = types.SimpleNamespace(HomeAssistant=object)
homeassistant.helpers = types.ModuleType("helpers")
homeassistant.helpers.update_coordinator = types.SimpleNamespace(DataUpdateCoordinator=object)
sys.modules.setdefault("homeassistant", homeassistant)
sys.modules.setdefault("homeassistant.config_entries", homeassistant.config_entries)
sys.modules.setdefault("homeassistant.core", homeassistant.core)
sys.modules.setdefault("homeassistant.helpers", homeassistant.helpers)
sys.modules.setdefault("homeassistant.helpers.update_coordinator", homeassistant.helpers.update_coordinator)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
DISCOVERY_PATH = ROOT / "custom_components" / "prudentes_tuya_all" / "discovery.py"
importlib.import_module("custom_components.prudentes_tuya_all")
_spec = spec_from_file_location(
    "custom_components.prudentes_tuya_all.discovery",
    DISCOVERY_PATH,
    submodule_search_locations=[str(DISCOVERY_PATH.parent)],
)
discovery = module_from_spec(_spec)
discovery.__package__ = "custom_components.prudentes_tuya_all"
sys.modules[_spec.name] = discovery
assert _spec and _spec.loader
_spec.loader.exec_module(discovery)


class FakeClient:
  def __init__(self):
    self._page = 0

  async def list_devices(self, page_size: int = 20, last_id: str | None = None):
    self._page += 1
    if self._page == 1:
      return {
          "result": {
              "list": [{"id": "dev1", "name": "Lamp"}],
              "last_row_key": "token",
              "has_more": True,
          }
      }
    return {"result": {"list": [{"id": "dev2", "name": "Fan"}]}}

  async def get_specification(self, device_id: str):
    return {
        "result": {
            "category": "dj",
            "status": [{"code": "switch_led", "dp_id": 1, "type": "Boolean", "name": "Liga"}],
            "functions": [
                {
                    "code": "bright_value",
                    "dpId": 20,
                    "type": "Integer",
                    "values": json.dumps({"min": 10, "max": 1000, "scale": 0}),
                }
            ],
        }
    }

  async def get_device_shadow(self, device_id: str):
    return {"result": [{"code": "switch_led", "value": True}, {"code": "bright_value", "value": 500}]}


def _load_knowledge():
  from custom_components.prudentes_tuya_all.localtuya_knowledge import LocalTuyaKnowledge

  # Usa o JSON gerado pelo script de extração real
  return LocalTuyaKnowledge()


class DiscoveryTest(unittest.TestCase):
  def test_pagination_collects_all_devices(self):
    client = FakeClient()
    devices = asyncio.run(discovery.discover_project_devices(client, page_size=1))
    self.assertEqual(2, len(devices))
    self.assertEqual({"dev1", "dev2"}, {d["deviceId"] for d in devices})

  def test_merge_normalizes_dp_id_and_values(self):
    spec = {
        "result": {
            "category": "dj",
            "status": [{"code": "switch", "dp_id": 1, "type": "Boolean"}],
            "functions": [{"code": "switch", "dpId": 1, "type": "Boolean", "values": "{}"}],
        }
    }
    shadow = {"result": [{"code": "switch", "value": True}]}

    category, entities = discovery.merge_spec_and_shadow(spec, shadow)
    self.assertEqual("dj", category)
    self.assertEqual(1, len(entities))
    entity = entities[0]
    self.assertEqual(1, entity["dpId"])
    self.assertEqual("bool", entity["dpType"])
    self.assertEqual({}, entity["typeSpec"])
    self.assertTrue(entity["currentValue"])
    self.assertEqual("rw", entity["access"]["accessMode"])

  def test_classification_heuristics_and_knowledge(self):
    knowledge = _load_knowledge()
    dp = {"dpType": "value", "access": {"read": True, "write": True}, "typeSpec": {"range": ["eco", "white"]}}
    entity_type, confidence, reason = discovery.classify_entity("bright_value", dp, "dj", knowledge)
    self.assertEqual("light", entity_type)
    self.assertGreater(confidence, 0.5)
    self.assertTrue(any("brilho" in r.lower() or "hass" in r.lower() for r in reason))

    entity_type, confidence, _ = discovery.classify_entity("humidity", {"dpType": "value", "access": {"read": True, "write": False}}, None, knowledge)
    self.assertEqual("sensor", entity_type)
    self.assertGreater(confidence, 0.3)

  def test_discover_device_entities_shapes_output(self):
    client = FakeClient()
    knowledge = _load_knowledge()
    device = {"deviceId": "dev1", "name": "Lamp", "category": "dj"}
    result = asyncio.run(discovery.discover_device_entities(client, device, knowledge))
    self.assertEqual("dev1", result["deviceId"])
    self.assertEqual(2, len(result["entities"]))
    entity_ids = {e["entity_id"] for e in result["entities"]}
    self.assertIn("dev1__switch_led", entity_ids)
    self.assertTrue(any(e["ha"]["suggested_platform"] == "light" for e in result["entities"]))


if __name__ == "__main__":
  unittest.main()
