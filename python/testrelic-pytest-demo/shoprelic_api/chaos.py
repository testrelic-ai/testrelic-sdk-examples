"""Chaos injection driven by environment variables.

The seed script restarts the app between runs with different flags to manufacture
a regression story. Flags are read once at process start (mirrors the JS demo's
``server.js`` behaviour) so each seeded run is a clean deploy.

Flags
-----
BREAK_PAYMENT      POST /api/checkout returns 500 "Payment processing failed: Gateway timeout"
BREAK_PROFILE      GET /api/profile/{uid}/orders (and GraphQL myOrders) returns empty history
FLAKY_INVENTORY    Search has a 50% chance of a 6s delay (turns into a client-side timeout)
FLAKY_UNIT         Makes the pure-unit "flaky" test fail ~50% of the time (seedable)

The coupon endpoint is *always* bugged (returns success with a 0% discount) — an
intentional, untested coverage gap, mirroring the JS demo's /api/apply-coupon.
"""

from __future__ import annotations

import os


def _flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def break_payment() -> bool:
    return _flag("BREAK_PAYMENT")


def break_profile() -> bool:
    return _flag("BREAK_PROFILE")


def flaky_inventory() -> bool:
    return _flag("FLAKY_INVENTORY")


def flaky_unit() -> bool:
    return _flag("FLAKY_UNIT")


def snapshot() -> dict[str, bool]:
    """Current chaos configuration (exposed on /api/health for debugging)."""
    return {
        "BREAK_PAYMENT": break_payment(),
        "BREAK_PROFILE": break_profile(),
        "FLAKY_INVENTORY": flaky_inventory(),
        "FLAKY_UNIT": flaky_unit(),
    }
