"""DeepEval LLM-evaluation suite (hermetic) for the ShopRelic support assistant.

No real model is called — ``FixedScoreMetric`` supplies deterministic scores — but
DeepEval still builds a full TestRun (cases + metric_data), which the
testrelic-deepeval pytest plugin captures at session finish and uploads to the
TestRelic evals API. Run it on its own so the deepeval plugin owns the session:

    pytest evals/
"""

from __future__ import annotations

from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from evals.metrics import FixedScoreMetric


def test_refund_policy_answer() -> None:
    case = LLMTestCase(
        input="Can I get a refund 40 days after purchase?",
        actual_output="Our refund window is 30 days, so a 40-day-old order isn't eligible.",
        expected_output="Refunds are only available within 30 days of purchase.",
        retrieval_context=["Refund policy: refunds available within 30 days of purchase."],
    )
    assert_test(case, [
        FixedScoreMetric("Answer Relevancy", threshold=0.7, fixed_score=0.92),
        FixedScoreMetric("Faithfulness", threshold=0.8, fixed_score=0.97),
    ])


def test_order_status_answer() -> None:
    case = LLMTestCase(
        input="What's the status of order 9002?",
        actual_output="Order 9002 has shipped and is on its way.",
        expected_output="Order 9002 is SHIPPED.",
        retrieval_context=["Order 9002: status SHIPPED, total $213.00."],
    )
    assert_test(case, [
        FixedScoreMetric("Answer Relevancy", threshold=0.7, fixed_score=0.95),
        FixedScoreMetric("Faithfulness", threshold=0.8, fixed_score=0.90),
    ])
