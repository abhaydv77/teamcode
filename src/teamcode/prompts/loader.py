from __future__ import annotations

import importlib.resources as resources

_PROMPT_PACKAGE = "teamcode.prompts"
_FALLBACK_PROMPT = "You are a helpful AI engineering assistant."


def load(role: str) -> str:
    try:
        return resources.files(_PROMPT_PACKAGE).joinpath(f"{role}.md").read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError):
        return _FALLBACK_PROMPT
