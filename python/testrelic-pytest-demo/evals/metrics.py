"""A deterministic DeepEval metric — no LLM/API key required.

Returns a fixed score so the eval suite is hermetic and reproducible while still
producing a real DeepEval ``TestRun`` (cases + metric scores) that the
testrelic-deepeval plugin captures and uploads to /api/v1/evals. Modelled on the
SDK's own ``sdk-verification/tests/test_sample_eval.py``.

IMPORTANT: every ``__init__`` argument is stored under an attribute of the SAME
name, because DeepEval's ``copy_metrics`` reconstructs a metric by reading
``vars(metric)`` for the ``__init__`` parameter names. A mismatch (e.g. storing
``name`` as ``self._name``) raises ``TypeError: __init__() missing 1 required
positional argument`` during ``assert_test``.
"""

from __future__ import annotations

from deepeval.metrics import BaseMetric


class FixedScoreMetric(BaseMetric):
    """A BaseMetric that scores a preset value (deterministic, offline)."""

    def __init__(
        self,
        metric_name: str = "FixedScore",
        threshold: float = 0.7,
        fixed_score: float = 0.9,
    ) -> None:
        # Stored under the same names as the __init__ params (copy_metrics-safe).
        self.metric_name = metric_name
        self.threshold = threshold
        self.fixed_score = fixed_score
        # Standard BaseMetric result/instrumentation attributes.
        self.score = fixed_score
        self.success = fixed_score >= threshold
        self.reason = f"deterministic stub score {fixed_score:.2f} (threshold {threshold:.2f})"
        self.evaluation_model = "deterministic-stub"
        self.evaluation_cost = 0.0
        self.strict_mode = False
        self.async_mode = False  # force the sync measure() path (no event loop)
        self._include_reason = True

    @property
    def __name__(self) -> str:  # deepeval reads this as the metric display name
        return self.metric_name

    def measure(self, test_case, *args, **kwargs) -> float:  # noqa: ANN001
        self.score = self.fixed_score
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case, *args, **kwargs) -> float:  # noqa: ANN001
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return bool(self.success)
