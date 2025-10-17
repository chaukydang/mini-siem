"""Load & access rule config from YAML (typed)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, cast

import yaml

from backend.core.config import settings


class RulesConfig:
    def __init__(self, path: str | None = None) -> None:
        default = "backend/core/rules.yaml"
        # settings.RULES_CONFIG_PATH có thể là Any, ép kiểu về str cho mypy
        chosen: str = path or cast(str, getattr(settings, "RULES_CONFIG_PATH", default))
        self._path: Path = Path(chosen)
        self._data: dict[str, Any] = {}

    def load(self) -> None:
        with self._path.open("r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f) or {}

    def get(self, rule_id: str) -> Mapping[str, Any]:
        # Trả về cấu hình rule dưới dạng Mapping; dùng cast để thỏa mypy
        return cast(Mapping[str, Any], self._data.get(rule_id, {}))

    def all(self) -> Mapping[str, Any]:
        return self._data


rules_config = RulesConfig()
