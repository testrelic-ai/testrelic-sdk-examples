"""In-memory data store for ShopRelic API (no database — resets on restart)."""

from __future__ import annotations

from typing import Any, Optional

DEMO_USER = {"id": "u-1001", "email": "demo@shoprelic.com", "password": "password123"}

PRODUCTS: list[dict[str, Any]] = [
    {"id": 1, "name": "Relic Runner Sneakers", "price": 89.99, "category": "footwear",
     "description": "Lightweight everyday running shoes."},
    {"id": 2, "name": "Heritage Denim Jacket", "price": 129.0, "category": "apparel",
     "description": "Classic mid-wash denim jacket."},
    {"id": 3, "name": "Artifact Backpack", "price": 64.5, "category": "accessories",
     "description": "20L water-resistant daypack."},
    {"id": 4, "name": "Strata Wireless Earbuds", "price": 149.0, "category": "electronics",
     "description": "ANC earbuds with 30h battery."},
    {"id": 5, "name": "Monolith Water Bottle", "price": 24.0, "category": "accessories",
     "description": "Insulated 1L stainless bottle."},
    {"id": 6, "name": "Excavator Cargo Pants", "price": 74.0, "category": "apparel",
     "description": "Durable ripstop cargo pants."},
    {"id": 7, "name": "Sediment Smart Watch", "price": 199.0, "category": "electronics",
     "description": "Fitness watch with GPS."},
    {"id": 8, "name": "Bedrock Hiking Boots", "price": 159.0, "category": "footwear",
     "description": "Waterproof all-terrain boots."},
    {"id": 9, "name": "Fossil Leather Wallet", "price": 39.0, "category": "accessories",
     "description": "Slim bifold leather wallet."},
    {"id": 10, "name": "Quarry Hoodie", "price": 59.0, "category": "apparel",
     "description": "Heavyweight fleece hoodie."},
    {"id": 11, "name": "Terra Sunglasses", "price": 49.0, "category": "accessories",
     "description": "Polarized UV400 sunglasses."},
    {"id": 12, "name": "Geode Bluetooth Speaker", "price": 89.0, "category": "electronics",
     "description": "Portable 360° speaker."},
]

# Coupons the storefront advertises. SAVE20 *should* give 20% off — but the
# apply-coupon endpoint is intentionally bugged (always 0%), and no test covers it.
COUPONS = {"SAVE20": 0.20, "WELCOME10": 0.10}

# Seeded order history for the demo user so the profile endpoint has something to
# return (and BREAK_PROFILE has something to suppress).
ORDERS: dict[int, dict[str, Any]] = {
    9001: {"id": 9001, "userId": "u-1001", "total": 89.99, "status": "DELIVERED",
           "items": [{"productId": 1, "qty": 1}]},
    9002: {"id": 9002, "userId": "u-1001", "total": 213.0, "status": "SHIPPED",
           "items": [{"productId": 4, "qty": 1}, {"productId": 3, "qty": 1}]},
}

# Mutable cart store keyed by session id.
CARTS: dict[str, list[dict[str, Any]]] = {}

_next_order_id = 1001


def product_by_id(pid: int) -> Optional[dict[str, Any]]:
    return next((p for p in PRODUCTS if p["id"] == pid), None)


def search_products(query: Optional[str]) -> list[dict[str, Any]]:
    if not query:
        return list(PRODUCTS)
    q = query.lower()
    return [p for p in PRODUCTS if q in p["name"].lower() or q in p["category"].lower()]


def cart_subtotal(session_id: str) -> float:
    items = CARTS.get(session_id, [])
    total = 0.0
    for line in items:
        p = product_by_id(line["productId"])
        if p:
            total += p["price"] * line.get("qty", 1)
    return round(total, 2)


def create_order(user_id: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    global _next_order_id
    oid = _next_order_id
    _next_order_id += 1
    total = 0.0
    for line in items:
        p = product_by_id(line["productId"])
        if p:
            total += p["price"] * line.get("qty", 1)
    order = {"id": oid, "userId": user_id, "total": round(total, 2),
             "status": "CONFIRMED", "items": items}
    ORDERS[oid] = order
    return order


def orders_for_user(user_id: str) -> list[dict[str, Any]]:
    return [o for o in ORDERS.values() if o["userId"] == user_id]


# ── Pure pricing helpers (exercised by the unit-test suite, no HTTP) ──────────
def line_total(price: float, qty: int) -> float:
    return round(price * qty, 2)


def apply_discount(subtotal: float, code: str) -> float:
    """Correct discount math — used by unit tests. (The HTTP endpoint is bugged.)"""
    rate = COUPONS.get(code.upper(), 0.0)
    return round(subtotal * (1 - rate), 2)
