"""Playwright UI smoke suite — captured by the testrelic-playwright reporter
(navigation timeline, network, screenshots) and uploaded to /runs.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
def test_landing_loads(page: Page, app_url: str) -> None:
    page.goto(app_url)
    expect(page.locator("#store-title")).to_have_text("ShopRelic")


@pytest.mark.ui
def test_catalog_renders(page: Page, app_url: str) -> None:
    page.goto(app_url)
    expect(page.locator(".product-card").first).to_be_visible()
    assert page.locator(".product-card").count() == 12
