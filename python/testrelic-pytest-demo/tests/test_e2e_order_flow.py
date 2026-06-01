"""End-to-end order journey spanning multiple protocols in a single test:
REST checkout (live HTTP) -> Kafka order-event (synthetic) -> WebSocket status
stream (synthetic). Demonstrates a multi-protocol test in one node.
"""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.streaming
def test_order_placed_then_streamed(client: httpx.Client, testrelic_kafka, testrelic_ws) -> None:
    # 1) REST: place the order (fails under BREAK_PAYMENT).
    resp = client.post("/api/checkout", json={"userId": "u-1001", "items": [{"productId": 8, "qty": 1}]})
    assert resp.status_code == 201
    order_id = resp.json()["id"]

    # 2) Kafka: the order-placed event is produced and consumed.
    k = testrelic_kafka
    k.set_consumer_group("fulfilment")
    k.produce("orders.v1", {"id": order_id, "event": "placed"}, key=str(order_id), partition=0, offset=1)
    k.consume("orders.v1", value={"id": order_id}, key=str(order_id), partition=0, offset=1)
    k.assert_message_received("orders.v1", key=str(order_id))

    # 3) WebSocket: client observes the status transitions.
    w = testrelic_ws
    w.send(f"subscribe:{order_id}", url="ws://127.0.0.1:8000/ws/orders")
    w.receive(f"order:{order_id}:CONFIRMED", url="ws://127.0.0.1:8000/ws/orders")
    w.receive(f"order:{order_id}:SHIPPED", url="ws://127.0.0.1:8000/ws/orders")
    w.close(1000)
    w.assert_received(2)
    w.assert_clean_close()
