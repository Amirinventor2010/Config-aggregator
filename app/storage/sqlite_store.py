from __future__ import annotations

import asyncio
import time
from typing import List, Tuple, Optional

import aiosqlite


class SQLiteConfigStore:
    """
    Dedup بر اساس dedupe_key (UUID).
    """

    def __init__(self, db_path: str, max_items: int):
        self.db_path = db_path
        self.max_items = max_items
        self._lock = asyncio.Lock()

    async def init(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS configs (
                    dedupe_key TEXT PRIMARY KEY,
                    uri        TEXT NOT NULL,
                    ts         INTEGER NOT NULL
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_configs_ts ON configs(ts)")
            await db.commit()

    async def add_many(
        self,
        items: List[Tuple[str, str]],  # (dedupe_key, uri)
        ts: Optional[int] = None
    ) -> Tuple[int, int, int]:
        """
        خروجی: (new, updated, total)
        """
        if not items:
            total = await self.count()
            return 0, 0, total

        if ts is None:
            ts = int(time.time())

        async with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                new = 0
                updated = 0

                for key, uri in items:
                    cur = await db.execute(
                        "SELECT 1 FROM configs WHERE dedupe_key = ?",
                        (key,)
                    )
                    exists = await cur.fetchone()

                    if exists:
                        updated += 1
                    else:
                        new += 1

                    await db.execute(
                        "INSERT OR REPLACE INTO configs (dedupe_key, uri, ts) VALUES (?, ?, ?)",
                        (key, uri, ts)
                    )

                await db.execute(f"""
                    DELETE FROM configs
                    WHERE dedupe_key NOT IN (
                        SELECT dedupe_key FROM configs
                        ORDER BY ts DESC
                        LIMIT {int(self.max_items)}
                    )
                """)
                await db.commit()

            total = await self.count()
            return new, updated, total

    async def get_latest(self, limit: Optional[int] = None) -> List[str]:
        if limit is None:
            limit = self.max_items

        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "SELECT uri FROM configs ORDER BY ts DESC LIMIT ?",
                (int(limit),)
            )
            rows = await cur.fetchall()

        return [r[0] for r in rows][::-1]

    async def count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute("SELECT COUNT(*) FROM configs")
            (n,) = await cur.fetchone()
        return int(n)
