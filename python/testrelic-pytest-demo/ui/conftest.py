"""Playwright suite config — starts the ShopRelic API in-process (like tests/)
and points the browser at it. Requires ``testrelic-playwright`` + a browser
(`playwright install chromium`).
"""

from __future__ import annotations

import os
import threading
import time
from typing import Iterator

import httpx
import pytest

BASE_URL = os.environ.get("SHOPRELIC_URL", "http://127.0.0.1:8000")


def _reachable(url: str) -> bool:
    try:
        httpx.get(f"{url}/api/health", timeout=1.0)
        return True
    except Exception:
        return False


@pytest.fixture(scope="session", autouse=True)
def _app_server() -> Iterator[None]:
    if _reachable(BASE_URL):
        yield
        return
    import uvicorn

    from shoprelic_api.main import app

    port = int(BASE_URL.rsplit(":", 1)[-1])
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 15
    while time.time() < deadline and not _reachable(BASE_URL):
        time.sleep(0.2)
    if not _reachable(BASE_URL):
        pytest.fail("ShopRelic API failed to start for the Playwright session")
    try:
        yield
    finally:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.fixture
def app_url() -> str:
    return BASE_URL
