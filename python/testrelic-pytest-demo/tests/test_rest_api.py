"""REST / HTTP protocol suite — runs against the live ShopRelic API.

These tests make real ``httpx`` calls, so the testrelic-pytest plugin's HTTP
auto-detection records each one as a `rest` API call (method/url/status +
request/response detail) with **no fixture required**. A couple of tests also use
the explicit ``testrelic_rest`` fixture to show curated request/response capture.

Chaos coupling:
  * test_checkout_places_order / test_full_purchase_flow  -> fail under BREAK_PAYMENT
  * test_profile_shows_order_history                      -> fail under BREAK_PROFILE
  * test_search_products                                  -> flakes under FLAKY_INVENTORY
"""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.smoke
@pytest.mark.api
def test_get_product(client: httpx.Client) -> None:
    resp = client.get("/api/products/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Relic Runner Sneakers"


@pytest.mark.smoke
@pytest.mark.api
def test_list_products(client: httpx.Client) -> None:
    resp = client.get("/api/products")
    assert resp.status_code == 200
    assert len(resp.json()) == 12


@pytest.mark.regression
@pytest.mark.api
def test_search_products(client: httpx.Client) -> None:
    # Under FLAKY_INVENTORY this has a 50% chance of a 6s server delay, which
    # exceeds the 4s client timeout -> ReadTimeout (recorded flaky failure).
    resp = client.get("/api/products", params={"search": "watch"})
    assert resp.status_code == 200
    assert any("Watch" in p["name"] for p in resp.json())


@pytest.mark.smoke
@pytest.mark.api
def test_checkout_places_order(client: httpx.Client, auth_token: str) -> None:
    resp = client.post(
        "/api/checkout",
        json={"userId": "u-1001", "items": [{"productId": 1, "qty": 1}]},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    # Fails under BREAK_PAYMENT (500 "Payment processing failed: Gateway timeout").
    assert resp.status_code == 201
    assert resp.json()["status"] == "CONFIRMED"


@pytest.mark.regression
@pytest.mark.api
def test_profile_shows_order_history(client: httpx.Client) -> None:
    resp = client.get("/api/profile/u-1001/orders")
    assert resp.status_code == 200
    # Fails under BREAK_PROFILE (history silently empty).
    assert len(resp.json()) >= 1


@pytest.mark.regression
@pytest.mark.api
def test_full_purchase_flow(client: httpx.Client) -> None:
    login = client.post("/api/login", json={"email": "demo@shoprelic.com", "password": "password123"})
    assert login.status_code == 200
    cart = client.post("/api/cart", json={"sessionId": "e2e", "productId": 4, "qty": 1})
    assert cart.status_code == 200
    assert cart.json()["subtotal"] == 149.0
    order = client.post("/api/checkout", json={"userId": "u-1001", "items": [{"productId": 4, "qty": 1}]})
    assert order.status_code == 201  # fails under BREAK_PAYMENT


@pytest.mark.api
@pytest.mark.parametrize("product_id,expected", [(1, 200), (5, 200), (999, 404)])
def test_product_status_matrix(client: httpx.Client, product_id: int, expected: int) -> None:
    resp = client.get(f"/api/products/{product_id}")
    assert resp.status_code == expected


@pytest.mark.api
def test_explicit_rest_capture(testrelic_rest) -> None:
    """Curated request/response capture via the explicit fixture (no live call)."""
    r = testrelic_rest
    r.call(
        "GET", "/api/orders/9001", status=200, status_text="OK",
        request_bytes=0, response_bytes=180, duration_ms=42.0,
        request_headers={"Accept": "application/json"},
        response_headers={"Content-Type": "application/json"},
        response_body='{"id": 9001, "status": "DELIVERED", "total": 89.99}',
    )
    r.assert_status(200, url="/api/orders/9001")
