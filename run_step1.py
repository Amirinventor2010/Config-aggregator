import asyncio
from dotenv import load_dotenv

from app.config import load_settings
from app.telegram.listener import build_client, attach_channel_listener
from app.parser import process_message
from app.storage.sqlite_store import SQLiteConfigStore


async def main():
    load_dotenv()

    settings = load_settings()
    store = SQLiteConfigStore(db_path=settings.db_path, max_items=settings.max_items)
    await store.init()

    client = build_client(settings)

    async def on_message(text: str) -> None:
        configs = process_message(text, settings.fixed_name)
        if not configs:
            return

        added, total = await store.add_many(configs)
        print(f"\n[STORE] +{added}  | total={total}/{settings.max_items}")

        # برای تست: آخرین 3 تا رو نشون بده
        latest3 = await store.get_latest(limit=3)
        print("[STORE] latest 3:")
        for c in latest3:
            print(c)

    attach_channel_listener(client, settings, on_message=on_message)

    await client.start()
    print(f"Listening on {settings.tg_channel} ... (Ctrl+C to stop)")
    print(f"DB: {settings.db_path} | MAX_ITEMS={settings.max_items}")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
