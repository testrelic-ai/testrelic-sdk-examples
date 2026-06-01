"""MCP (Model Context Protocol) tool-call suite (synthetic / manual mode).

Records an AI tool invocation so the run carries an `mcp` protocol interaction +
a tool-status assertion — the "modern AI protocol" surface.
"""

from __future__ import annotations

import pytest


@pytest.mark.api
@pytest.mark.nightly
def test_search_orders_tool(testrelic_mcp) -> None:
    m = testrelic_mcp
    m.tool_call("search_orders", status="ok", result_bytes=88, summary="3 results")
    m.assert_tool_ok("search_orders")
