"""gRPC streaming protocol suite (synthetic / manual mode — no gRPC server).

Records a server-streaming RPC and its status so the run carries a gRPC protocol
interaction + a status assertion.
"""

from __future__ import annotations

import pytest


@pytest.mark.streaming
@pytest.mark.nightly
def test_inventory_server_stream(testrelic_grpc) -> None:
    g = testrelic_grpc
    g.call(
        "inventory.InventoryService/StreamStock",
        kind="server_stream",
        sent=1,
        received=5,
        status="OK",
    )
    g.assert_ok("inventory.InventoryService/StreamStock")
