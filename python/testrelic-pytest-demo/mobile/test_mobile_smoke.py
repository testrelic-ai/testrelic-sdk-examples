"""Appium mobile smoke suite — auto-skips without an Appium server/device.

When a device is present, the testrelic-appium plugin captures the mobile session
(command timeline, device logs, screenshots) and uploads it to /runs.
"""

from __future__ import annotations

import pytest


@pytest.mark.appium
def test_app_launches(driver) -> None:  # noqa: ANN001
    assert driver.session_id is not None


@pytest.mark.appium
def test_login_screen_visible(driver) -> None:  # noqa: ANN001
    # Placeholder native assertion — real selectors depend on the AUT.
    assert driver.current_package is not None
