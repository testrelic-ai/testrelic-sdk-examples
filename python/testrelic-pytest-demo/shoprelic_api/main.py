"""ShopRelic API — FastAPI app (REST + GraphQL + a WebSocket order stream).

Endpoints back the testrelic-pytest demo suites. Chaos flags (see chaos.py) make
specific endpoints fail/flake so the seed script can tell a regression story.
"""

from __future__ import annotations

import asyncio
import random
import time
from typing import Any

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse

from shoprelic_api import chaos, data

app = FastAPI(title="ShopRelic API", version="1.0.0")

# GraphQL is optional at import time so the REST surface still boots if strawberry
# is not installed (keeps the minimal offline-verify install light).
try:
    from strawberry.fastapi import GraphQLRouter

    from shoprelic_api.graphql_schema import schema as _gql_schema

    app.include_router(GraphQLRouter(_gql_schema), prefix="/graphql")
    _GRAPHQL_ENABLED = True
except Exception:  # pragma: no cover - only when strawberry is absent
    _GRAPHQL_ENABLED = False


# ── landing page (gives Playwright a real page to drive) ─────────────────────
@app.get("/", response_class=HTMLResponse)
def index() -> str:
    cards = "".join(
        f'<li class="product-card" data-id="{p["id"]}">{p["name"]} '
        f'<span class="price">${p["price"]:.2f}</span></li>'
        for p in data.PRODUCTS
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>ShopRelic</title></head><body>
<h1 id="store-title">ShopRelic</h1>
<p>The TestRelic pytest demo storefront.</p>
<ul id="product-list">{cards}</ul>
</body></html>"""


# ── health (seed script polls this) ──────────────────────────────────────────
@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "graphql": _GRAPHQL_ENABLED, "chaos": chaos.snapshot()}


# ── catalog ──────────────────────────────────────────────────────────────────
@app.get("/api/products")
def list_products(search: str | None = None, category: str | None = None) -> list[dict[str, Any]]:
    if search and chaos.flaky_inventory() and random.random() < 0.5:
        time.sleep(6)  # slow path -> client read-timeout (flaky search)
    results = data.search_products(search)
    if category:
        results = [p for p in results if p["category"] == category]
    return results


@app.get("/api/products/{product_id}")
def get_product(product_id: int) -> dict[str, Any]:
    if product_id == 7 and random.random() < 0.3:
        time.sleep(random.uniform(3, 5))  # naturally-slow product (occasional flake)
    product = data.product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# ── auth ─────────────────────────────────────────────────────────────────────
@app.post("/api/login")
async def login(request: Request) -> dict[str, Any]:
    body = await request.json()
    if body.get("email") == data.DEMO_USER["email"] and body.get("password") == data.DEMO_USER["password"]:
        return {"token": "demo-session-token", "userId": data.DEMO_USER["id"]}
    raise HTTPException(status_code=401, detail="Invalid credentials")


# ── cart ─────────────────────────────────────────────────────────────────────
@app.post("/api/cart")
async def add_to_cart(request: Request) -> dict[str, Any]:
    body = await request.json()
    sid = body.get("sessionId", "default")
    data.CARTS.setdefault(sid, []).append(
        {"productId": int(body["productId"]), "qty": int(body.get("qty", 1))}
    )
    return {"sessionId": sid, "items": data.CARTS[sid], "subtotal": data.cart_subtotal(sid)}


@app.get("/api/cart/{session_id}")
def get_cart(session_id: str) -> dict[str, Any]:
    return {"sessionId": session_id, "items": data.CARTS.get(session_id, []),
            "subtotal": data.cart_subtotal(session_id)}


# ── checkout (BREAK_PAYMENT) ─────────────────────────────────────────────────
@app.post("/api/checkout")
async def checkout(request: Request) -> JSONResponse:
    if chaos.break_payment():
        return JSONResponse(
            status_code=500,
            content={"error": "Payment processing failed: Gateway timeout"},
        )
    body = await request.json()
    order = data.create_order(body.get("userId", data.DEMO_USER["id"]), body.get("items", []))
    return JSONResponse(status_code=201, content=order)


# ── orders / profile (BREAK_PROFILE) ─────────────────────────────────────────
@app.get("/api/orders/{order_id}")
def get_order(order_id: int) -> dict[str, Any]:
    order = data.ORDERS.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/api/profile/{user_id}/orders")
def profile_orders(user_id: str) -> list[dict[str, Any]]:
    if chaos.break_profile():
        return []  # regression: history silently empty
    return data.orders_for_user(user_id)


# ── coupon (intentionally bugged, untested — coverage-gap story) ─────────────
@app.post("/api/coupons/apply")
async def apply_coupon(request: Request) -> dict[str, Any]:
    body = await request.json()
    subtotal = float(body.get("subtotal", 0))
    # BUG: silently returns success with a 0% discount regardless of the code.
    return {"success": True, "code": body.get("code"), "discountAmount": 0.0,
            "newSubtotal": round(subtotal, 2)}


# ── websocket order stream (optional real target for the WS suite) ───────────
@app.websocket("/ws/orders")
async def ws_orders(ws: WebSocket) -> None:
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            if msg == "ping":
                await ws.send_text("pong")
            elif msg.startswith("subscribe:"):
                order_id = msg.split(":", 1)[1]
                for status in ("CONFIRMED", "SHIPPED", "DELIVERED"):
                    await ws.send_text(f"order:{order_id}:{status}")
                    await asyncio.sleep(0.01)
            elif msg == "close":
                await ws.close(code=1000)
                return
    except WebSocketDisconnect:
        return
