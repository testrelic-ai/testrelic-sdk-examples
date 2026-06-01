"""Kafka streaming protocol suite (synthetic / manual mode — no broker needed).

Drives the ``testrelic_kafka`` fixture directly so the run carries realistic
``apiProtocol=kafka`` + ``streamingMetadata`` (topics/partitions/offsets/lag) +
``protocolAssertions`` (received / ordering / lag) without a live cluster.
"""

from __future__ import annotations

import pytest


@pytest.mark.streaming
@pytest.mark.nightly
def test_order_events_published(testrelic_kafka) -> None:
    k = testrelic_kafka
    k.set_consumer_group("orders-test-cg")
    k.produce("orders.v1", {"id": "ord-42", "total": 19.99}, key="ord-42", partition=1, offset=1043)
    k.produce("orders.v1", {"id": "ord-43", "total": 5.00}, key="ord-43", partition=2, offset=988)
    k.consume("orders.v1", value={"id": "ord-42"}, key="ord-42", partition=1, offset=1043)
    k.consume("orders.v1", value={"id": "ord-43"}, key="ord-43", partition=2, offset=988)
    k.assert_message_received("orders.v1", key="ord-42")
    k.assert_ordering("orders.v1", partition=1)
    k.set_consumer_lag(0)
    k.assert_consumer_lag_below(1)


@pytest.mark.streaming
@pytest.mark.nightly
def test_dead_letter_queue_empty(testrelic_kafka) -> None:
    k = testrelic_kafka
    k.set_consumer_group("orders-test-cg")
    k.assert_no_messages("orders.dlq")
