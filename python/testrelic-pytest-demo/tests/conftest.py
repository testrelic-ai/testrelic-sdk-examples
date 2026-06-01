"""Shared fixtures for the testrelic-pytest demo suites.

The ShopRelic API is started **in-process** (a uvicorn server on a daemon thread)
the first time a suite needs it, unless one is already reachable at SHOPRELIC_URL.
This makes ``pytest tests/`` self-contained and lets the seed script simply set
chaos env vars + run pytest for each "deploy".
"""

from __future__ import annotations

import os
import threading
import time
from typing import Iterator

import httpx
import pytest

BASE_URL = os.environ.get("SHOPRELIC_URL", "http://127.0.0.1:8000")
# 4s client timeout vs the 6s FLAKY_INVENTORY server delay = the mechanism that
# turns "slow search" into a recorded ReadTimeout failure.
CLIENT_TIMEOUT = float(os.environ.get("SHOPRELIC_CLIENT_TIMEOUT", "4.0"))


def _reachable(url: str) -> bool:
    try:
        httpx.get(f"{url}/api/health", timeout=1.0)
        return True
    except Exception:
        return False


@pytest.fixture(scope="session", autouse=True)
def _app_server() -> Iterator[None]:
    """Ensure a ShopRelic API is reachable for the whole session."""
    if _reachable(BASE_URL):
        yield
        return

    import uvicorn

    from shoprelic_api.main import app

    port = int(BASE_URL.rsplit(":", 1)[-1]) if ":" in BASE_URL else 8000
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.time() + 15
    while time.time() < deadline and not _reachable(BASE_URL):
        time.sleep(0.2)
    if not _reachable(BASE_URL):
        pytest.fail("ShopRelic API failed to start for the test session")

    try:
        yield
    finally:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.fixture
def app_url() -> str:
    # Named app_url (not base_url) to avoid colliding with pytest-base-url's
    # session-scoped `base_url` fixture, which pytest-playwright pulls in.
    return BASE_URL


@pytest.fixture
def client() -> Iterator[httpx.Client]:
    """An httpx client bound to the app. httpx is auto-instrumented by the
    testrelic-pytest plugin, so any call here is recorded as a `rest` API call."""
    with httpx.Client(base_url=BASE_URL, timeout=CLIENT_TIMEOUT) as c:
        yield c


@pytest.fixture
def auth_token(client: httpx.Client) -> str:
    resp = client.post("/api/login", json={"email": "demo@shoprelic.com", "password": "password123"})
    resp.raise_for_status()
    return resp.json()["token"]
