"""Appium suite config — the driver fixture cleanly SKIPS when no Appium server /
device is reachable, so the demo passes everywhere. With a running Appium server
(``APPIUM_SERVER_URL``, default http://127.0.0.1:4723) and a configured device,
the testrelic-appium plugin captures the mobile session automatically.
"""

from __future__ import annotations

import os
import socket
from typing import Iterator
from urllib.parse import urlparse

import pytest

APPIUM_URL = os.environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")


def _server_reachable(url: str) -> bool:
    parsed = urlparse(url)
    host, port = parsed.hostname or "127.0.0.1", parsed.port or 4723
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


@pytest.fixture
def driver() -> Iterator[object]:
    pytest.importorskip("appium", reason="testrelic-appium[Appium-Python-Client] not installed")
    if not _server_reachable(APPIUM_URL):
        pytest.skip(f"no Appium server reachable at {APPIUM_URL}")

    from appium import webdriver  # noqa: PLC0415
    from appium.options.android import UiAutomator2Options  # noqa: PLC0415

    options = UiAutomator2Options()
    options.platform_name = os.environ.get("APPIUM_PLATFORM", "Android")
    options.device_name = os.environ.get("APPIUM_DEVICE", "emulator-5554")
    app_pkg = os.environ.get("APPIUM_APP")
    if app_pkg:
        options.app = app_pkg

    drv = webdriver.Remote(APPIUM_URL, options=options)
    try:
        yield drv
    finally:
        drv.quit()
