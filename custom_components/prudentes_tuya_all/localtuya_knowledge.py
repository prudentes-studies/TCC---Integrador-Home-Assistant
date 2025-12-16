"""Leitura dos mapeamentos do hass-localtuya para auxiliar classificação."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


class LocalTuyaKnowledge:
  def __init__(self, mapping_path: Path | None = None) -> None:
    base = Path(__file__).resolve().parent
    self.mapping_path = mapping_path or (base / "data" / "localtuya_mappings.json")
    self._data: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    self.source = ""
    self.generated_at = ""
    self._load()

  def _load(self) -> None:
    if not self.mapping_path.exists():
      return
    payload = json.loads(self.mapping_path.read_text(encoding="utf-8"))
    self.source = payload.get("source", "")
    self.generated_at = payload.get("generated_at", "")
    self._data = payload.get("categories", {}) or {}

  def platforms_for_dp(self, category: str | None, dp_code: str | None) -> List[Dict[str, Any]]:
    if not category or not dp_code:
      return []
    category_map = self._data.get(category, {}) if isinstance(self._data, dict) else {}
    results: List[Dict[str, Any]] = []
    for platform, entities in category_map.items():
      for entity in entities:
        if dp_code in entity.get("dp_codes", []):
          results.append({"platform": platform, "entity": entity})
    return results

  def combos_for_device(self, category: str | None, available_codes: Iterable[str]) -> List[Dict[str, Any]]:
    if not category:
      return []
    category_map = self._data.get(category, {}) if isinstance(self._data, dict) else {}
    available_set = {code for code in available_codes if code}
    combos: List[Dict[str, Any]] = []
    for platform, entities in category_map.items():
      for entity in entities:
        entity_codes = set(entity.get("dp_codes", []))
        if entity_codes and entity_codes.issubset(available_set):
          combos.append({"platform": platform, "entity": entity, "dp_codes": sorted(entity_codes)})
    return combos


__all__ = ["LocalTuyaKnowledge"]
