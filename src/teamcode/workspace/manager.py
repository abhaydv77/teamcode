from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)


class WorkspaceManager:
    def __init__(self, root: str | Path | None = None) -> None:
        self._root = Path(root).resolve() if root else Path.cwd().resolve()

    @property
    def root(self) -> Path:
        return self._root

    def read_file(self, path: str | Path) -> str:
        return self._resolve(path).read_text(encoding="utf-8")

    def write_file(self, path: str | Path, content: str) -> None:
        full = self._resolve(path)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")

    def file_exists(self, path: str | Path) -> bool:
        return self._resolve(path).exists()

    def glob(self, pattern: str) -> list[Path]:
        return sorted(self._root.glob(pattern))

    def _resolve(self, path: str | Path) -> Path:
        p = Path(path)
        return p if p.is_absolute() else self._root / p
