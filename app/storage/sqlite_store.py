from __future__ import annotations

import asyncio
import time
from typing import List, Tuple, Optional

import aiosqlite


class SQLiteConfigStore:
    """
    ذخیره‌سازی کانفیگ‌ها با dedupe و محدودیت ظرفیت.
    - uri به صورت PRIMARY KEY => تکراری‌ها جایگزین می‌شن
    - ts آخرین زمان دیده‌شدن
    """

    def __init__(self, db_path: str, max_items: int):
        self.db_path = db_path
        self.max_items = max_items
        self._lock = asyncio.Lock()

    async def init(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS configs (
                    uri TEXT PRIMARY KEY,
                    ts  INTEGER NOT NULL
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_configs_ts ON configs(ts)")
            await db.commit()

    async def add_many(self, uris: List[str], ts: Optional[int] = None) -> Tuple[int, int]:
        """
        uris: لیست کانفیگ‌های نهایی (rename شده)
        ts: timestamp (اگر ندی، زمان فعلی)
        خروجی: (added_or_updated, total_after)
        """
        if not uris:
            total = await self.count()
            return 0, total

        if ts is None:
            ts = int(time.time())

        async with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                # dedupe با PRIMARY KEY: INSERT OR REPLACE
                await db.executemany(
                    "INSERT OR REPLACE INTO configs (uri, ts) VALUES (?, ?)",
                    [(u, ts) for u in uris]
                )

                # trim: فقط max_items تا جدیدترین نگه می‌داریم
                await db.execute(f"""
                    DELETE FROM configs
                    WHERE uri NOT IN (
                        SELECT uri FROM configs
                        ORDER BY ts DESC
                        LIMIT {int(self.max_items)}
                    )
                """)

                await db.commit()

            total = await self.count()
            return len(uris), total

    async def get_latest(self, limit: Optional[int] = None) -> List[str]:
        """
        جدیدترین‌ها بر اساس ts. خروجی را از قدیمی->جدید برمی‌گرداند (برای ساب قشنگ‌تره).
        """
        if limit is None:
            limit = self.max_items

        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "SELECT uri FROM configs ORDER BY ts DESC LIMIT ?",
                (int(limit),)
            )
            rows = await cur.fetchall()

        # reverse: قدیمی->جدید
        return [r[0] for r in rows][::-1]

    async def count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute("SELECT COUNT(*) FROM configs")
            (n,) = await cur.fetchone()
        return int(n)
