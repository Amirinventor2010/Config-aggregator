from __future__ import annotations
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    tg_api_id: int
    tg_api_hash: str
    tg_channel: str
    fixed_name: str
    max_items: int
    db_path: str


def load_settings() -> Settings:
    tg_api_id = int(os.getenv("TG_API_ID", "0"))
    tg_api_hash = os.getenv("TG_API_HASH", "").strip()
    tg_channel = os.getenv("TG_CHANNEL", "@ConfigsHub").strip()

    fixed_name = os.getenv("FIXED_NAME", "📱Telegram | @FNET00").strip()
    max_items = int(os.getenv("MAX_ITEMS", "1000"))
    db_path = os.getenv("DB_PATH", "configs.db").strip()

    if tg_api_id <= 0:
        raise RuntimeError("TG_API_ID معتبر نیست.")
    if not tg_api_hash:
        raise RuntimeError("TG_API_HASH خالیه.")
    if not tg_channel:
        raise RuntimeError("TG_CHANNEL خالیه.")
    if not db_path:
        raise RuntimeError("DB_PATH خالیه.")

    if max_items < 1 or max_items > 100000:
        raise RuntimeError("MAX_ITEMS باید بین 1 تا 100000 باشه.")

    # normalize channel
    if tg_channel.startswith("https://t.me/"):
        tg_channel = tg_channel.replace("https://t.me/", "")
        tg_channel = "@" + tg_channel
    if not tg_channel.startswith("@"):
        tg_channel = "@" + tg_channel

    return Settings(
        tg_api_id=tg_api_id,
        tg_api_hash=tg_api_hash,
        tg_channel=tg_channel,
        fixed_name=fixed_name,
        max_items=max_items,
        db_path=db_path,
    )
