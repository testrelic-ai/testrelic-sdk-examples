"""Plain pytest suite (no HTTP) — exercises the non-protocol metric surface:
markers, parametrize ids, xfail/xpass, an intentionally-flaky test, and warnings.
"""

from __future__ import annotations

import warnings

import pytest

from shoprelic_api import chaos, data


@pytest.mark.smoke
def test_line_total() -> None:
    assert data.line_total(89.99, 2) == 179.98


@pytest.mark.smoke
@pytest.mark.parametrize(
    "code,subtotal,expected",
    [
        ("SAVE20", 100.0, 80.0),
        ("WELCOME10", 50.0, 45.0),
        ("UNKNOWN", 30.0, 30.0),
        ("save20", 200.0, 160.0),  # case-insensitive
    ],
)
def test_apply_discount(code: str, subtotal: float, expected: float) -> None:
    assert data.apply_discount(subtotal, code) == expected


@pytest.mark.xfail(reason="known float-rounding edge case on thirds; tracked in SHOP-412")
def test_known_rounding_bug() -> None:
    # 0.1 * 3 != 0.3 — documents a known gap (shows up as xfailed in the report).
    assert 0.1 * 3 == 0.3


def test_emits_deprecation_warning() -> None:
    warnings.warn("apply_discount() will require an explicit currency in v2", DeprecationWarning)
    assert data.apply_discount(10.0, "WELCOME10") == 9.0


@pytest.mark.flaky
def test_inventory_sync_flaky() -> None:
    """Deterministically flaky under FLAKY_UNIT (the seed arc toggles this)."""
    if chaos.flaky_unit():
        import random
        assert random.random() > 0.5, "inventory sync race (simulated flake)"
    else:
        assert True
