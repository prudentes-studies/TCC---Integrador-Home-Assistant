from __future__ import annotations

import asyncio
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

DISCOVERY_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "prudentes_tuya_all" / "discovery.py"
_spec = spec_from_file_location("prudentes_discovery", DISCOVERY_PATH)
discovery = module_from_spec(_spec)
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
          }
      }
    return {"result": {"list": [{"id": "dev2", "name": "Fan"}]}}


class DiscoveryTest(unittest.TestCase):
  def test_pagination_collects_all_devices(self):
    client = FakeClient()
    devices = asyncio.run(discovery.discover_project_devices(client, page_size=1))
    self.assertEqual(2, len(devices))
    self.assertEqual({"dev1", "dev2"}, {d["deviceId"] for d in devices})

  def test_merge_normalizes_dp_id_and_values(self):
    spec = {
        "result": {
            "status": [{"code": "switch", "dp_id": 1, "type": "Boolean"}],
            "functions": [{"code": "switch", "dpId": 1, "type": "Boolean", "values": "{}"}],
        }
    }
    model = {"result": {"model": json.dumps({"services": [{"properties": [{"code": "switch", "typeSpec": {"type": "Boolean"}, "accessMode": "rw", "abilityId": 99}]}]})}}
    status = {"result": [{"code": "switch", "value": True}]}

    entities = discovery.merge_sources(spec, model, status)
    self.assertEqual(1, len(entities))
    entity = entities[0]
    self.assertEqual(1, entity["dpId"])
    self.assertEqual("bool", entity["dpType"])
    self.assertEqual({"type": "Boolean"}, entity["typeSpec"])
    self.assertTrue(entity["currentValue"])
    self.assertEqual("rw", entity["access"]["accessMode"])

  def test_classification_heuristics(self):
    entity_type, confidence, reason = discovery.classify_entity("bright_value", {"dpType": "value", "access": {"read": True, "write": True}})
    self.assertEqual("light", entity_type)
    self.assertGreater(confidence, 0.5)
    self.assertIn("brilho", reason.lower())

    entity_type, confidence, _ = discovery.classify_entity("humidity", {"dpType": "value", "access": {"read": True, "write": False}})
    self.assertEqual("sensor", entity_type)
    self.assertGreater(confidence, 0.3)


if __name__ == "__main__":
  unittest.main()
