from __future__ import annotations

import base64
from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse

from app.storage.sqlite_store import SQLiteConfigStore


def create_app(store: SQLiteConfigStore) -> FastAPI:
    app = FastAPI(title="FNET00 Subscription")

    @app.get("/sub", response_class=PlainTextResponse)
    async def subscription(
        b64: bool = Query(True, description="Base64 output"),
        limit: int | None = Query(None, ge=1, description="Max configs"),
    ):
        configs = await store.get_latest(limit=limit)

        payload = "\n".join(configs)

        if b64:
            payload = base64.b64encode(payload.encode()).decode()

        return payload

    return app
