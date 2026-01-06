from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    tg_api_id: int
    tg_api_hash: str
    tg_channels: list[str]      # ✅ multi-channel
    fixed_name: str
    max_items: int
    db_path: str


def _normalize_channel(ch: str) -> str:
    ch = ch.strip()
    if not ch:
        return ""

    if ch.startswith("https://t.me/"):
        ch = ch.replace("https://t.me/", "")
    if ch.startswith("@"):
        ch = ch[1:]

    # خروجی نهایی با @
    return "@" + ch


def load_settings() -> Settings:
    tg_api_id = int(os.getenv("TG_API_ID", "0"))
    tg_api_hash = os.getenv("TG_API_HASH", "").strip()

    # ✅ چند کانال: با کاما جدا
    raw_channels = os.getenv("TG_CHANNELS", "@ConfigsHub").strip()
    channels_raw = [c.strip() for c in raw_channels.split(",") if c.strip()]
    tg_channels = [_normalize_channel(c) for c in channels_raw]
    tg_channels = [c for c in tg_channels if c]  # حذف خالی‌ها

    fixed_name = os.getenv("FIXED_NAME", "📱Telegram | @FNET00").strip()
    max_items = int(os.getenv("MAX_ITEMS", "1000"))
    db_path = os.getenv("DB_PATH", "configs.db").strip()

    if tg_api_id <= 0:
        raise RuntimeError("TG_API_ID معتبر نیست. داخل .env درستش کن.")
    if not tg_api_hash:
        raise RuntimeError("TG_API_HASH خالیه. داخل .env درستش کن.")
    if not tg_channels:
        raise RuntimeError("TG_CHANNELS خالیه. داخل .env درستش کن.")
    if not db_path:
        raise RuntimeError("DB_PATH خالیه. داخل .env درستش کن.")

    if max_items < 1 or max_items > 100000:
        raise RuntimeError("MAX_ITEMS باید بین 1 تا 100000 باشه.")

    return Settings(
        tg_api_id=tg_api_id,
        tg_api_hash=tg_api_hash,
        tg_channels=tg_channels,
        fixed_name=fixed_name,
        max_items=max_items,
        db_path=db_path,
    )
