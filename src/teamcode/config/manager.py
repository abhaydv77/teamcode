"""Persistent configuration manager — reads/writes TOML config files."""

from __future__ import annotations

import json
import os
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

CONFIG_DIR = Path.home() / ".config" / "teamcode"
CONFIG_FILE = CONFIG_DIR / "config.toml"
ROLES_FILE = CONFIG_DIR / "roles.toml"
MODELS_CACHE_FILE = CONFIG_DIR / "models.cache.json"

API_KEY_REGEX = re.compile(r"^sk-or-v1-[A-Za-z0-9]{32,}$")

SHIPPED_PROMPTS: dict[str, str] = {
    "product_manager": (
        "You are a product manager responsible for defining requirements "
        "and specifications. Focus on user needs, business value, and "
        "incremental delivery."
    ),
    "coordinator": (
        "You are a coordinator responsible for breaking down tasks and "
        "delegating to the appropriate agent."
    ),
    "architect": (
        "You are a software architect responsible for designing system "
        "structure and making technology decisions."
    ),
    "developer": (
        "You are a junior engineer responsible for implementing features "
        "according to specifications."
    ),
    "reviewer": (
        "You are a code reviewer responsible for finding bugs, security "
        "issues, and suggesting improvements."
    ),
    "tester": (
        "You are a tester responsible for writing tests and verifying "
        "correctness."
    ),
}

SHIPPED_MODELS: dict[str, str] = {
    "product_manager": "openrouter/openai/gpt-4o",
    "coordinator": "openrouter/anthropic/claude-sonnet-4-20250514",
    "architect": "openrouter/anthropic/claude-sonnet-4-20250514",
    "developer": "openrouter/openai/gpt-4o",
    "reviewer": "openrouter/anthropic/claude-sonnet-4-20250514",
    "tester": "openrouter/anthropic/claude-3-haiku-20240307",
}

ROLE_NAMES = [
    "product_manager",
    "coordinator",
    "architect",
    "developer",
    "reviewer",
    "tester",
]

CURRENT_SCHEMA = 1


def _write_toml(path: Path, data: dict[str, Any]) -> None:
    """Write a dict as TOML to a file with 0o600 permissions."""

    def _serialize(
        obj: Any,
        key_path: str = "",
        indent: int = 0,
    ) -> str:
        lines: list[str] = []
        prefix = "  " * indent
        if isinstance(obj, dict):
            for key, val in obj.items():
                if isinstance(val, dict):
                    if indent == 0:
                        lines.append(f"[{key}]")
                    else:
                        lines.append(f"[{key_path}.{key}]")
                    lines.append(_serialize(val, key, indent + 1))
                elif isinstance(val, list):
                    lines.append(f"{prefix}{key} = [")
                    for item in val:
                        if isinstance(item, str):
                            lines.append(f'{prefix}  "{item}",')
                        elif isinstance(item, (int, float)):
                            lines.append(f"{prefix}  {item},")
                        elif item is None:
                            lines.append(f"{prefix}  'null',")
                    lines.append(f"{prefix}]")
                elif isinstance(val, str):
                    escaped = val.replace('"', '\\"')
                    lines.append(f'{prefix}{key} = "{escaped}"')
                elif isinstance(val, bool):
                    lines.append(f"{prefix}{key} = {'true' if val else 'false'}")
                elif isinstance(val, (int, float)):
                    lines.append(f"{prefix}{key} = {val}")
                elif val is None:
                    lines.append(f"{prefix}{key} = ''")
                else:
                    lines.append(f'{prefix}{key} = "{val}"')
        return "\n".join(lines)

    path.parent.mkdir(parents=True, exist_ok=True)
    content = _serialize(data)
    path.write_text(content + "\n")
    path.chmod(0o600)


class ConfigManager:
    def __init__(self, settings: Any = None) -> None:
        self._settings = settings
        self._config: dict[str, Any] = {}
        self._roles: dict[str, Any] = {}
        self._models_cache: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "rb") as f:
                self._config = tomllib.load(f)
        if not self._config:
            self._config = {"version": {"schema": CURRENT_SCHEMA}}

        if ROLES_FILE.exists():
            with open(ROLES_FILE, "rb") as f:
                self._roles = tomllib.load(f)
        if not self._roles:
            self._roles = {}

        if MODELS_CACHE_FILE.exists():
            with open(MODELS_CACHE_FILE) as f:
                self._models_cache = json.load(f)
        if not self._models_cache:
            self._models_cache = {"fetched_at": None, "models": []}

    def save(self) -> None:
        _write_toml(CONFIG_FILE, self._config)

    def _save_roles(self) -> None:
        _write_toml(ROLES_FILE, self._roles)

    # ── API key ──

    def get_api_key(self) -> str | None:
        key = self._config.get("openrouter", {}).get("api_key")
        if key:
            return key
        if self._settings and getattr(self._settings, "openrouter_api_key", None):
            return self._settings.openrouter_api_key
        return None

    def set_api_key(self, key: str) -> None:
        self._config.setdefault("openrouter", {})["api_key"] = key
        self.save()
        os.environ["OPENROUTER_API_KEY"] = key

    def validate_api_key(self, key: str) -> bool:
        return bool(API_KEY_REGEX.match(key))

    # ── Connection testing ──

    def test_connection(self) -> bool:
        key = self.get_api_key()
        if not key:
            return False
        try:
            resp = httpx.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10,
            )
            ok = resp.status_code == 200
        except Exception:
            ok = False
        self._config.setdefault("openrouter", {})["connection_ok"] = ok
        self._config.setdefault("openrouter", {})["last_tested"] = (
            datetime.now(UTC).isoformat()
        )
        self.save()
        return ok

    def get_connection_status(self) -> dict[str, Any]:
        or_cfg = self._config.get("openrouter", {})
        return {
            "last_tested": or_cfg.get("last_tested"),
            "connection_ok": or_cfg.get("connection_ok", False),
        }

    # ── Default model ──

    def get_default_model(self) -> str:
        return self._config.get("defaults", {}).get("model", "gpt-4o")

    def set_default_model(self, model: str) -> None:
        self._config.setdefault("defaults", {})["model"] = model
        self.save()

    # ── Per-role config ──

    def get_role_config(self, role: str) -> dict[str, str]:
        role_cfg = self._roles.get("roles", {}).get(role, {})
        return {
            "model": role_cfg.get("model", SHIPPED_MODELS.get(role, "gpt-4o")),
            "system_prompt": role_cfg.get(
                "system_prompt", SHIPPED_PROMPTS.get(role, "")
            ),
        }

    def set_role_config(self, role: str, cfg: dict[str, str]) -> None:
        self._roles.setdefault("roles", {})[role] = cfg
        self._save_roles()

    def list_roles(self) -> dict[str, dict[str, str]]:
        result: dict[str, dict[str, str]] = {}
        for name in ROLE_NAMES:
            result[name] = self.get_role_config(name)
        return result

    def reset_role(self, role: str) -> None:
        if role in self._roles.get("roles", {}):
            del self._roles["roles"][role]
            self._save_roles()

    # ── Model cache ──

    def get_cached_models(self) -> list[dict[str, Any]]:
        return self._models_cache.get("models", [])

    def set_cached_models(self, models: list[dict[str, Any]]) -> None:
        self._models_cache["models"] = models
        self._models_cache["fetched_at"] = datetime.now(UTC).isoformat()
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(MODELS_CACHE_FILE, "w") as f:
            json.dump(self._models_cache, f, indent=2)
        MODELS_CACHE_FILE.chmod(0o600)

    def fetch_models(self) -> list[dict[str, Any]]:
        key = self.get_api_key()
        if not key:
            raise ValueError("No API key set")
        resp = httpx.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        models: list[dict[str, Any]] = []
        for m in data.get("data", []):
            mid = m.get("id", "")
            models.append({
                "id": mid,
                "name": m.get("name", mid),
                "provider": mid.split("/")[0] if mid else "",
                "description": m.get("description", ""),
                "context_length": m.get("context_length", 0),
            })
        return models

    def refresh_models(self) -> list[dict[str, Any]]:
        models = self.fetch_models()
        self.set_cached_models(models)
        return models

    def get_cache_info(self) -> dict[str, Any]:
        return {
            "fetched_at": self._models_cache.get("fetched_at"),
            "count": len(self._models_cache.get("models", [])),
        }
