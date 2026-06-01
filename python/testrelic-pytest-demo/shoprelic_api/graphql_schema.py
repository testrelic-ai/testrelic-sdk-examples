"""Minimal real GraphQL schema (strawberry) mounted at POST /graphql.

Kept tiny on purpose — just enough surface for the GraphQL test suite to issue a
genuine query / mutation over HTTP (so testrelic-pytest's httpx auto-detection
records a real request/response). Honours the same chaos flags as REST.
"""

from __future__ import annotations

import time
from typing import Optional

import strawberry

from shoprelic_api import chaos, data


@strawberry.type
class Product:
    id: int
    name: str
    price: float
    category: str
    description: str


@strawberry.type
class Order:
    id: int
    total: float
    status: str


def _to_product(row: dict) -> Product:
    return Product(
        id=row["id"], name=row["name"], price=row["price"],
        category=row["category"], description=row["description"],
    )


@strawberry.type
class Query:
    @strawberry.field
    def products(self, search: Optional[str] = None) -> list[Product]:
        if search and chaos.flaky_inventory():
            # 50% chance of a slow path -> client read-timeout (flaky search story)
            import random
            if random.random() < 0.5:
                time.sleep(6)
        return [_to_product(p) for p in data.search_products(search)]

    @strawberry.field
    def product(self, id: int) -> Optional[Product]:
        row = data.product_by_id(id)
        return _to_product(row) if row else None

    @strawberry.field
    def order(self, id: int) -> Optional[Order]:
        row = data.ORDERS.get(id)
        return Order(id=row["id"], total=row["total"], status=row["status"]) if row else None

    @strawberry.field
    def my_orders(self, user_id: str) -> list[Order]:
        if chaos.break_profile():
            return []  # regression: profile/orders silently empty
        return [
            Order(id=o["id"], total=o["total"], status=o["status"])
            for o in data.orders_for_user(user_id)
        ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def place_order(self, user_id: str, product_id: int, qty: int = 1) -> Order:
        order = data.create_order(user_id, [{"productId": product_id, "qty": qty}])
        return Order(id=order["id"], total=order["total"], status=order["status"])


schema = strawberry.Schema(query=Query, mutation=Mutation)
