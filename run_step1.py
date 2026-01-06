import asyncio
from dotenv import load_dotenv
import uvicorn

from app.config import load_settings
from app.telegram.listener import build_client, attach_channel_listener
from app.parser import process_message, make_dedupe_key
from app.storage.sqlite_store import SQLiteConfigStore
from app.http_server import create_app


async def main():
    load_dotenv()
    settings = load_settings()

    # Storage
    store = SQLiteConfigStore(settings.db_path, settings.max_items)
    await store.init()

    # Telegram
    client = build_client(settings)

    async def on_message(text: str) -> None:
        configs = process_message(text, settings.fixed_name)
        if not configs:
            return

        items = [(make_dedupe_key(c), c) for c in configs]
        new, updated, total = await store.add_many(items)

        print(f"[STORE] new={new} updated={updated} | total={total}/{settings.max_items}")

    attach_channel_listener(client, settings, on_message)

    # HTTP Server
    app = create_app(store)

    async def start_http():
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
        server = uvicorn.Server(config)
        await server.serve()

    await client.start()
    print("Telegram listener started")
    print("Listening on channels:", ", ".join(settings.tg_channels))
    print("HTTP server on http://127.0.0.1:8000/sub")

    await asyncio.gather(
        client.run_until_disconnected(),
        start_http(),
    )


if __name__ == "__main__":
    asyncio.run(main())
