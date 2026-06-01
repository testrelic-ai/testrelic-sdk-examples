"""DeepEval suite config.

testrelic-deepeval uploads to the **evals** API, which it reads from
``TESTRELIC_BASE_URL`` (note: a *different* env var than the pytest reporter's
``TESTRELIC_CLOUD_ENDPOINT``). We default it to prod here so a bare
``pytest evals/`` with a real key uploads to the right place; the seed/verify
scripts override it for staging / the local mock.

Project association: the eval uploader derives the cloud repo from git context
(``detect_git_context()`` -> ``remote.origin.url``), NOT from
``TESTRELIC_PROJECT_NAME`` (pytest-only) and NOT from ``TESTRELIC_REPO_GIT_ID``
(the eval path ignores it). When the repo has no git remote, that falls back to
``GITHUB_REPOSITORY`` and otherwise to ``"unknown"`` — which is why eval runs
otherwise land under a separate "unknown" repo in the dashboard. We pin
``GITHUB_REPOSITORY`` to the demo's project id so evals land in the SAME repo as
the pytest/playwright runs (``shoprelic-pytest-demo``).
"""

from __future__ import annotations

import os

os.environ.setdefault("TESTRELIC_BASE_URL", "https://platform.testrelic.ai/api/v1/evals")
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "1")
# Pin the eval run's repo to match the pytest/playwright project. Only takes
# effect when there is no real git remote (the usual demo case).
os.environ.setdefault("GITHUB_REPOSITORY", "shoprelic-pytest-demo")
os.environ.pop("CONFIDENT_API_KEY", None)  # ensure results land in TestRelic, not Confident AI
