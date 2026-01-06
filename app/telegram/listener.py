from __future__ import annotations

from typing import Callable, Awaitable, Optional
from telethon import TelegramClient, events

from app.config import Settings

MessageHandler = Callable[[str], Awaitable[None]]


def build_client(settings: Settings) -> TelegramClient:
    return TelegramClient("session", settings.tg_api_id, settings.tg_api_hash)


def attach_channel_listener(
    client: TelegramClient,
    settings: Settings,
    on_message: Optional[MessageHandler] = None,
) -> None:
    # ✅ اینجا multi-channel شد: settings.tg_channels (لیست)
    @client.on(events.NewMessage(chats=settings.tg_channels))
    async def _handler(event):
        text = event.raw_text or ""
        if on_message:
            await on_message(text)
        else:
            print("\n===== NEW MESSAGE =====")
            print(text)
