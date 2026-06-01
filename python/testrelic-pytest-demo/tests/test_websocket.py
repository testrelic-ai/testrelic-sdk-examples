"""WebSocket protocol suite.

Primary test is synthetic (``testrelic_ws`` manual mode) so it always runs. A
second test drives the app's real ``/ws/orders`` endpoint when the ``websockets``
client is installed (``testrelic-pytest[websocket]``), otherwise it skips.
"""

from __future__ import annotations

import pytest


@pytest.mark.streaming
@pytest.mark.nightly
def test_order_stream_synthetic(testrelic_ws) -> None:
    w = testrelic_ws
    w.send("subscribe:9001", url="ws://127.0.0.1:8000/ws/orders")
    w.receive("order:9001:CONFIRMED", url="ws://127.0.0.1:8000/ws/orders")
    w.receive("order:9001:SHIPPED", url="ws://127.0.0.1:8000/ws/orders")
    w.receive("order:9001:DELIVERED", url="ws://127.0.0.1:8000/ws/orders")
    w.close(1000)
    w.assert_received(3)
    w.assert_clean_close()


@pytest.mark.streaming
@pytest.mark.nightly
def test_order_stream_live(testrelic_ws, app_url: str) -> None:
    connect = pytest.importorskip("websockets.sync.client").connect
    ws_url = app_url.replace("http", "ws") + "/ws/orders"
    w = testrelic_ws
    with connect(ws_url) as conn:
        conn.send("ping")
        reply = conn.recv()
        w.send("ping", url=ws_url)
        w.receive(reply, url=ws_url)
        conn.send("close")
    w.close(1000)
    w.assert_received(1)
    assert reply == "pong"
