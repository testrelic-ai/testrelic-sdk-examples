"""GraphQL protocol suite — real GraphQL-over-HTTP against POST /graphql.

The queries go out via ``httpx`` so they're captured as API calls (the request
body shows the GraphQL document). One test additionally tags the interaction with
the explicit ``testrelic_graphql`` fixture so the cloud can render it under the
GraphQL protocol with an operation + subscription event.

Chaos coupling:
  * test_graphql_my_orders -> fails under BREAK_PROFILE
  * test_graphql_search    -> flakes under FLAKY_INVENTORY
"""

from __future__ import annotations

import httpx
import pytest


def _gql(client: httpx.Client, query: str, variables: dict | None = None) -> dict:
    resp = client.post("/graphql", json={"query": query, "variables": variables or {}})
    resp.raise_for_status()
    payload = resp.json()
    assert "errors" not in payload, payload.get("errors")
    return payload["data"]


@pytest.mark.smoke
@pytest.mark.api
def test_graphql_product_query(client: httpx.Client) -> None:
    data = _gql(client, "query($id:Int!){ product(id:$id){ id name price } }", {"id": 1})
    assert data["product"]["name"] == "Relic Runner Sneakers"


@pytest.mark.regression
@pytest.mark.api
def test_graphql_search(client: httpx.Client) -> None:
    data = _gql(client, 'query{ products(search:"watch"){ id name } }')
    assert any("Watch" in p["name"] for p in data["products"])


@pytest.mark.regression
@pytest.mark.api
def test_graphql_my_orders(client: httpx.Client) -> None:
    data = _gql(client, 'query{ myOrders(userId:"u-1001"){ id status total } }')
    assert len(data["myOrders"]) >= 1  # empty under BREAK_PROFILE


@pytest.mark.smoke
@pytest.mark.api
def test_graphql_place_order_mutation(client: httpx.Client) -> None:
    data = _gql(
        client,
        "mutation($u:String!,$p:Int!){ placeOrder(userId:$u, productId:$p){ id status } }",
        {"u": "u-1001", "p": 2},
    )
    assert data["placeOrder"]["status"] == "CONFIRMED"


@pytest.mark.api
def test_graphql_operation_tagged(testrelic_graphql) -> None:
    """Explicitly tag a GraphQL operation + subscription event for the protocol UI."""
    g = testrelic_graphql
    g.operation("GetOrder", kind="query", status="ok", response_bytes=420)
    g.subscription_event("OrderUpdated", summary="status=SHIPPED")
    g.assert_ok("GetOrder")
