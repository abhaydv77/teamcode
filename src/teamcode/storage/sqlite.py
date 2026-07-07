from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from teamcode.storage.base import BaseStorage

log = logging.getLogger(__name__)


class SQLiteStorage(BaseStorage):
    def __init__(self, db_path: str | Path = "teamcode.db") -> None:
        self._db_path = str(db_path)
        self._conn: Any = None

    async def _ensure_conn(self) -> Any:
        if self._conn is None:
            import aiosqlite

            self._conn = await aiosqlite.connect(self._db_path)
            await self._conn.execute(
                "CREATE TABLE IF NOT EXISTS storage ("
                "  collection TEXT,"
                "  key TEXT,"
                "  value TEXT,"
                "  PRIMARY KEY (collection, key)"
                ")"
            )
            await self._conn.commit()
        return self._conn

    async def save(self, collection: str, key: str, data: dict[str, Any]) -> None:
        conn = await self._ensure_conn()
        await conn.execute(
            "INSERT OR REPLACE INTO storage (collection, key, value) VALUES (?, ?, ?)",
            (collection, key, json.dumps(data)),
        )
        await conn.commit()

    async def load(self, collection: str, key: str) -> dict[str, Any] | None:
        conn = await self._ensure_conn()
        cursor = await conn.execute(
            "SELECT value FROM storage WHERE collection = ? AND key = ?",
            (collection, key),
        )
        row = await cursor.fetchone()
        return json.loads(row[0]) if row else None

    async def delete(self, collection: str, key: str) -> None:
        conn = await self._ensure_conn()
        await conn.execute(
            "DELETE FROM storage WHERE collection = ? AND key = ?",
            (collection, key),
        )
        await conn.commit()

    async def list(self, collection: str) -> list[dict[str, Any]]:
        conn = await self._ensure_conn()
        cursor = await conn.execute(
            "SELECT value FROM storage WHERE collection = ?",
            (collection,),
        )
        rows = await cursor.fetchall()
        return [json.loads(row[0]) for row in rows]
